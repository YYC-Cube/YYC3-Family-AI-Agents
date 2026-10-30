#!/usr/bin/env python3
"""E3-1 大数据语义层 MVP — MDL 建模 / SQL 治理校验 / 确定性指标执行（SQL 即代码）

WrenAI/SuperSonic 共识的本仓 MVP 形态：不让 LLM 面对原始 schema，让查询面对被治理的语义层。
安全架构（Mimosa L3 对齐）：**执行面 SQL 即代码**——execute_metric 仅以单行字面量 SQL 逐指标派发
（代码评审覆盖、零污点链）；METRIC_REGISTRY 中的 SQL 文本与字面量零漂移由测试强制；
MDL 只承载语义（表/字段/指标描述与注册表引用），漂移由 check_registry_drift 判定。
自由 NL→SQL 不在本模块执行——validate_sql 纯校验函数供部署侧 LLM 管线前置审查。

- MDL（YAML 子集）：零依赖解析器（块映射/块列表/标量）
- validate_sql：单语句 · SELECT 白名单 · 危险关键字黑名单 · 表级 allowlist · LIMIT 上限
- execute_metric：注册表指标派发（构建期已含 LIMIT ≤ row_limit；运行期行数硬上限二次校验）
- match_metric：确定性指标匹配（问题关键词 ↔ 指标名/描述），指标问答复杂度卸载到语义层
"""
import re
from pathlib import Path

FORBIDDEN_KEYWORDS = (
    "insert", "update", "delete", "drop", "alter", "create", "attach", "detach",
    "pragma", "replace", "vacuum", "reindex", "load_extension", "readfile", "writefile",
)
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_LIMIT_TAIL_RE = re.compile(r"\blimit\s+(\d+)\s*$")


class SemanticGuardError(Exception):
    """治理管线结构化错误：携带 code/detail/hint，端点层原样透出。"""

    def __init__(self, code: str, detail: str, hint: str = ""):
        self.code = code
        self.detail = detail
        self.hint = hint
        super().__init__(f"[{code}] {detail}" + (f"（提示：{hint}）" if hint else ""))


# ---------- 指标注册表（语义与零漂移校验用；可执行 SQL 以单行字面量存在于 execute_metric 派发） ----------

ROW_LIMIT = 500

METRIC_REGISTRY = {
    "total_users": {
        "description": "注册用户总数",
        "tables": ["users"],
        "sql": "SELECT COUNT(*) AS total_users FROM users LIMIT 500",
    },
    "active_users": {
        "description": "近 30 天活跃用户数（去重）",
        "tables": ["events"],
        "sql": "SELECT COUNT(DISTINCT user_id) AS active_users FROM events WHERE created_at >= DATE('now', '-30 day') LIMIT 500",
    },
    "events_total": {
        "description": "事件总量",
        "tables": ["events"],
        "sql": "SELECT COUNT(*) AS events_total FROM events LIMIT 500",
    },
}

# ---------- MDL YAML 子集解析器（零依赖；块映射/块列表/标量） ----------

def _scalar(v: str):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    return v


def _split_lines(text: str) -> list:
    out = []
    for raw in text.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        line = raw.replace("\t", "  ")
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        is_item = stripped.startswith("- ")
        if is_item:
            indent += 2
            stripped = stripped[2:]
        out.append((indent, stripped.strip(), is_item))
    return out


def _parse_dict(lines, i, indent):
    obj = {}
    while i < len(lines) and lines[i][0] == indent and not lines[i][2]:
        content = lines[i][1]
        if ":" not in content:
            raise ValueError(f"MDL 非法行（缺少冒号）: {content}")
        key, _, value = content.partition(":")
        key, value = key.strip(), value.strip()
        if value:
            obj[key] = _scalar(value)
            i += 1
        else:
            i += 1
            if i < len(lines) and lines[i][0] > indent:
                child_indent = lines[i][0]
                if lines[i][2]:
                    obj[key], i = _parse_list(lines, i, child_indent)
                else:
                    obj[key], i = _parse_dict(lines, i, child_indent)
            else:
                obj[key] = None
    return obj, i


def _parse_list(lines, i, indent):
    items = []
    while i < len(lines) and lines[i][0] == indent and lines[i][2]:
        obj = {}
        content = lines[i][1]
        if ":" in content:
            key, _, value = content.partition(":")
            key, value = key.strip(), value.strip()
            if value:
                obj[key] = _scalar(value)
                i += 1
            else:
                i += 1
                if i < len(lines) and lines[i][0] > indent:
                    child_indent = lines[i][0]
                    if lines[i][2]:
                        obj[key], i = _parse_list(lines, i, child_indent)
                    else:
                        obj[key], i = _parse_dict(lines, i, child_indent)
        else:
            i += 1
        # 消费本条目在同级缩进下的其余平铺键（无横线）；空值键为嵌套子节点，递归解析
        while i < len(lines) and lines[i][0] == indent and not lines[i][2]:
            content = lines[i][1]
            if ":" not in content:
                i += 1
                continue
            k2, _, v2 = content.partition(":")
            k2, v2 = k2.strip(), v2.strip()
            if v2:
                obj[k2.strip()] = _scalar(v2)
                i += 1
            else:
                i += 1
                if i < len(lines) and lines[i][0] > indent:
                    child_indent = lines[i][0]
                    if lines[i][2]:
                        obj[k2], i = _parse_list(lines, i, child_indent)
                    else:
                        obj[k2], i = _parse_dict(lines, i, child_indent)
                else:
                    obj[k2] = None
        items.append(obj)
    return items, i


def parse_mdl(text: str) -> dict:
    lines = _split_lines(text)
    if not lines:
        return {}
    obj, i = _parse_dict(lines, 0, lines[0][0])
    if i < len(lines):
        raise ValueError(f"MDL 解析未消费全部行，检查缩进: {lines[i]}")
    return obj


# ---------- 语义层 ----------

class SemanticLayer:
    """MDL 加载 / 零漂移校验 / SQL 治理检查 / 确定性指标执行"""

    def __init__(self, mdl: dict):
        self._validate_mdl(mdl)
        self.mdl = mdl
        self.row_limit = int(mdl.get("row_limit", ROW_LIMIT))
        self.tables = {t["name"]: t for t in mdl.get("tables", [])}

    @classmethod
    def load(cls, path) -> "SemanticLayer":
        return cls(parse_mdl(Path(path).read_text(encoding="utf-8")))

    @staticmethod
    def _validate_mdl(mdl: dict) -> None:
        for key in ("version", "name", "dialect"):
            if key not in mdl:
                raise ValueError(f"MDL 缺少必填字段: {key}")
        if mdl.get("dialect") != "sqlite":
            raise ValueError(f"暂仅支持 sqlite 方言: {mdl.get('dialect')}")
        seen_tables = set()
        for table in mdl.get("tables", []):
            name = table.get("name", "")
            if not _IDENTIFIER_RE.match(name):
                raise ValueError(f"表名非法: {name!r}")
            if name in seen_tables:
                raise ValueError(f"表重复: {name}")
            seen_tables.add(name)
            seen_cols = set()
            for col in table.get("columns", []):
                cname = col.get("name", "")
                if not _IDENTIFIER_RE.match(cname):
                    raise ValueError(f"列名非法: {name}.{cname!r}")
                if cname in seen_cols:
                    raise ValueError(f"列重复: {name}.{cname}")
                seen_cols.add(cname)
        for metric in mdl.get("metrics", []):
            mname = metric.get("name", "")
            if not _IDENTIFIER_RE.match(mname):
                raise ValueError(f"指标名非法: {mname!r}")
            if metric.get("registry") not in METRIC_REGISTRY:
                raise ValueError(
                    f"指标注册表引用缺失: {mname} → {metric.get('registry')!r}（SQL 即代码，"
                    f"可执行 SQL 仅存在于 execute_metric 单行字面量派发）")

    def check_registry_drift(self) -> None:
        """注册表 ↔ MDL 零漂移校验：注册表 SQL 引用的表必须存在于 MDL。"""
        for name, entry in METRIC_REGISTRY.items():
            for match in re.finditer(r"\b(?:from|join)\s+([A-Za-z_][A-Za-z0-9_]*)",
                                     entry["sql"].lower()):
                table = match.group(1)
                if table not in self.tables:
                    raise SemanticGuardError(
                        "REGISTRY_DRIFT", f"注册表指标 {name} 引用了 MDL 之外的表: {table}",
                        "先在 MDL 建模该表，再更新注册表")

    # ---- SQL 治理校验（纯函数，无执行 sink；供部署侧 LLM 管线前置审查） ----

    def validate_sql(self, sql: str) -> str:
        text = (sql or "").strip()
        while text.endswith(";"):
            text = text[:-1].rstrip()
        if ";" in text:
            raise SemanticGuardError("SQL_MULTI_STATEMENT", "检测到多条语句", "一次仅执行一条查询")
        lowered = text.lower()
        if not lowered.startswith("select"):
            raise SemanticGuardError("SQL_NOT_SELECT", "仅允许 SELECT 只读查询", "指标与明细查询均使用 SELECT")
        for kw in FORBIDDEN_KEYWORDS:
            if re.search(rf"\b{kw}\b", lowered):
                raise SemanticGuardError("SQL_FORBIDDEN_KEYWORD", f"受限关键字: {kw}", "仅支持只读 SELECT")
        for match in re.finditer(r"\b(?:from|join)\s+([A-Za-z_][A-Za-z0-9_]*)", lowered):
            table = match.group(1)
            if table not in self.tables:
                raise SemanticGuardError(
                    "TABLE_NOT_ALLOWED", f"表不在语义层: {table}",
                    "可用表: " + ", ".join(sorted(self.tables)))
        limit_match = _LIMIT_TAIL_RE.search(lowered)
        if limit_match and int(limit_match.group(1)) > self.row_limit:
            raise SemanticGuardError(
                "LIMIT_EXCEEDED", f"LIMIT {limit_match.group(1)} 超过上限 {self.row_limit}",
                f"最大行数 {self.row_limit}")
        if not limit_match:
            text = text + " LIMIT " + str(self.row_limit)
        return text

    # ---- 确定性指标执行（单行字面量 SQL 逐指标派发，零污点链） ----

    def match_metric(self, question: str) -> str:
        """问题关键词 ↔ 指标匹配：问题 2-gram 对「指标名+描述」的覆盖率（中文零分词确定性方案）。"""
        q = re.sub(r"[\s，。？?！!、/（）()]+", "", question or "")
        if len(q) < 2:
            return None
        grams = {q[i:i + 2] for i in range(len(q) - 1)} or {q}
        best, best_score = None, 0
        for name, entry in METRIC_REGISTRY.items():
            hay = (name + entry["description"]).lower().replace(" ", "")
            score = sum(1 for g in grams if g in hay)
            if score > best_score:
                best, best_score = name, score
        return best if best_score > 0 else None

    @staticmethod
    def _collect(cursor, metric_name: str, row_limit: int) -> dict:
        rows = cursor.fetchmany(row_limit + 1)
        if len(rows) > row_limit:
            raise SemanticGuardError(
                "ROW_LIMIT_EXCEEDED", f"结果超过行数上限 {row_limit}",
                "增加过滤条件或收敛指标口径")
        cols = [d[0] for d in cursor.description] if cursor.description else []
        return {"metric": metric_name, "columns": cols,
                "rows": [list(r) for r in rows], "row_count": len(rows)}

    def execute_metric(self, conn, metric_name: str) -> dict:
        """执行注册表指标：每个指标一条单行字面量 SQL（构建期已含 LIMIT ≤ row_limit）；
        运行期行数硬上限二次校验（超限为查询过宽，不截断返回）。"""
        if metric_name == "total_users":
            cursor = conn.execute("SELECT COUNT(*) AS total_users FROM users LIMIT 500")
            return self._collect(cursor, metric_name, self.row_limit)
        if metric_name == "active_users":
            cursor = conn.execute("SELECT COUNT(DISTINCT user_id) AS active_users FROM events WHERE created_at >= DATE('now', '-30 day') LIMIT 500")
            return self._collect(cursor, metric_name, self.row_limit)
        if metric_name == "events_total":
            cursor = conn.execute("SELECT COUNT(*) AS events_total FROM events LIMIT 500")
            return self._collect(cursor, metric_name, self.row_limit)
        raise SemanticGuardError("METRIC_NOT_FOUND", f"未知指标: {metric_name}",
                                 "可用指标: " + ", ".join(sorted(METRIC_REGISTRY)))

    def context_prompt(self, question: str) -> str:
        """为部署侧 LLM 自由生成构建语义上下文提示词（表格/列/指标全量描述）。"""
        lines = [f"# 语义层：{self.mdl.get('name', '')}（{self.mdl.get('description', '')}）",
                 f"行数上限 {self.row_limit}；仅允许单条 SELECT。可用表："]
        for name, table in self.tables.items():
            lines.append(f"## 表 {name}：{table.get('description', '')}")
            for col in table.get("columns", []):
                lines.append(f"- {col['name']} ({col.get('type', '')})：{col.get('description', '')}")
        lines.append("可用指标（已治理，优先使用）：")
        for name, entry in METRIC_REGISTRY.items():
            lines.append(f"- {name}：{entry['description']}")
        lines.append(f"用户问题：{question}")
        return "\n".join(lines)
