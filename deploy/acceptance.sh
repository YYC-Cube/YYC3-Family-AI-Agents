#!/usr/bin/env bash
# =============================================================================
# YYC³ FAmily-AI 生产部署全链路验收 (P3-1)
# 在生产服务器上运行: bash deploy/acceptance.sh
# 前置: bash deploy/install.sh 已执行 && vLLM 已拉起
# 退出码 = 失败项数量 (0 = 全部通过)
# =============================================================================
set -uo pipefail

HUB="${HUB:-http://127.0.0.1:25700}"
VLLM="${VLLM:-http://127.0.0.1:8000/v1}"
AGENT="${AGENT:-http://127.0.0.1:25600}"   # 默认抽检元启·天枢
API_KEY="${GOVERNANCE_API_KEY:-}"
JAEGER_UI="${JAEGER_UI:-http://127.0.0.1:16686}"

PASS=0; FAIL=0
ok()   { echo "  [OK]   $1"; PASS=$((PASS+1)); }
fail() { echo "  [FAIL] $1"; FAIL=$((FAIL+1)); }
section() { echo ""; echo "--- $1 ---"; }

AUTH=(-H "X-API-Key: $API_KEY")

echo "═══════════════════════════════════════════"
echo "  YYC³ 生产全链路验收 (hub=$HUB agent=$AGENT)"
echo "═══════════════════════════════════════════"

# ── 1. 基础健康 ──────────────────────────────
section "1. 基础健康"
curl -sf "$HUB/health"        | grep -q healthy  && ok "hub /health"        || fail "hub /health"
curl -sf "$AGENT/health"      | grep -q healthy  && ok "agent /health"      || fail "agent /health"
curl -sf "$VLLM/models"       | grep -q data     && ok "vLLM /v1/models"    || fail "vLLM /v1/models"

# ── 2. P2-2 /prompts 模板服务 ────────────────
section "2. /prompts 模板服务 (P2-2)"
curl -sf "$HUB/prompts/tianshu" | grep -q SYSTEM.md && ok "模板清单 (短名)" || fail "模板清单 (短名)"
curl -sf "$HUB/prompts/yuanqi_tianshu" | grep -q SOUL.md && ok "模板清单 (全名归一)" || fail "模板清单 (全名归一)"
BODY=$(curl -sf "$HUB/prompts/tianshu/SYSTEM.md?format=json" || true)
echo "$BODY" | grep -q sha256 && ok "模板 JSON+hash" || fail "模板 JSON+hash"
echo "$BODY" | grep -q "元启·天枢" && ok "模板内容正确 (名号)" || fail "模板内容正确 (名号)"
curl -sf "$HUB/prompts/tianshu/SOUL.md" | grep -q "五维管理职能" && ok "模板 text 格式" || fail "模板 text 格式"

# ── 3. P2-3 /metrics 可观测 ──────────────────
section "3. /metrics 可观测 (P2-3)"
curl -sf "$HUB/metrics" | grep -q counters && ok "hub /metrics" || fail "hub /metrics"

# ── 4. P0-2 零信任认证 ───────────────────────
section "4. 零信任认证 (P0-2)"
[ -n "$API_KEY" ] && NOKEY_CODE=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$HUB/budget/reset-daily" -H 'Content-Type: application/json' -d '{}') || NOKEY_CODE=000
[ "$NOKEY_CODE" = "401" ] && ok "无 Key 写操作 → 401" || fail "无 Key 写操作 → 401 (got $NOKEY_CODE)"
[ -n "$API_KEY" ] && WITHKEY=$(curl -sf "${AUTH[@]}" -X POST "$HUB/budget/reset-daily" -H 'Content-Type: application/json' -d '{}' || true) || WITHKEY=""
echo "$WITHKEY" | grep -q ok && ok "带 Key 写操作放行" || fail "带 Key 写操作放行"

# ── 5. P1-2 correlation_id 端到端 ────────────
section "5. /chat correlation_id 端到端 (P1-2/P2-3)"
CID="acc-$(date +%s)"
CHAT=$(curl -sf -X POST "$AGENT/chat" -H 'Content-Type: application/json' ${API_KEY:+-H "X-API-Key: $API_KEY"} \
  -d "{\"message\":\"验收冒烟：你是谁？\",\"correlation_id\":\"$CID\"}" || true)
echo "$CHAT" | grep -q "$CID" && ok "/chat 回显 correlation_id" || fail "/chat 回显 correlation_id"
sleep 1
curl -sf "$HUB/context/stats" >/dev/null 2>&1 && ok "hub 可达 (上报链路)" || fail "hub 可达 (上报链路)"

# ── 6. P2-4 LLM 实答人设 UAT ─────────────────
section "6. LLM 实答人设 UAT (P2-4)"
if [ -f "$(dirname "$0")/../tests/uat/test_llm_persona.py" ] && command -v python3 >/dev/null; then
    VLLM_ENDPOINT="$VLLM" YYC3_UAT_LLM=1 python3 -m pytest "$(dirname "$0")/../tests/uat/test_llm_persona.py" -q 2>/dev/null \
        && ok "8 位家人身份抽检" || fail "8 位家人身份抽检"
else
    echo "  [SKIP] pytest 不可用，改用最小抽检"
    ANS=$(curl -sf -X POST "$VLLM/chat/completions" -H 'Content-Type: application/json' \
        -d '{"model":"'"${VLLM_MODEL:-Qwen/Qwen3.6-27B-FP8}"'","messages":[{"role":"user","content":"1+1=?只回答数字"}],"max_tokens":8,"stream":false}' || true)
    echo "$ANS" | grep -q '"content"' && ok "vLLM 推理冒烟" || fail "vLLM 推理冒烟"
fi

# ── 7. P3-2 可观测栈 (可选) ──────────────────
section "7. 可观测栈 (P3-2, 若已启动)"
if curl -sf "$JAEGER_UI/api/services" >/dev/null 2>&1; then
    ok "Jaeger UI 可达"
    curl -sf "$JAEGER_UI/api/traces?service=yyc3.family-ai&limit=1" | grep -q data \
        && ok "span 已导出到 Jaeger" || { sleep 5; curl -sf "$JAEGER_UI/api/traces?service=yyc3.family-ai&limit=1" | grep -q data \
        && ok "span 已导出到 Jaeger (延迟确认)" || echo "  [WARN] 暂无 yyc3.family-ai span (确认 YYC3_OTLP_ENDPOINT 已配置且安装 otel sdk)"; }
else
    echo "  [SKIP] Jaeger 未启动 (docker compose --profile observability up -d)"
fi

echo ""
echo "═══════════════════════════════════════════"
echo "  验收结果: $PASS 通过, $FAIL 失败"
echo "═══════════════════════════════════════════"
exit "$FAIL"
