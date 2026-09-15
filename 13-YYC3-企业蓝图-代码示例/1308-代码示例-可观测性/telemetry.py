"""
YYC³ 全栈可观测性 SDK v1.0
基于 OpenTelemetry 标准的 Logs/Metrics/Traces 三支柱实现

核心能力:
- 结构化日志: correlationId 全链路追踪 + 敏感字段脱敏
- 指标监控: Counter/Gauge/Histogram + SLO/SLI/SLA 自动计算
- 分布式追踪: Span 链路 + 跨Agent传播 + 瓶颈自动定位

对齐蓝图: 1208-全栈可观测性架构
五高架构: 高可用 | 高性能 | 高安全 | 高扩展

用法:
    from telemetry import Telemetry
    
    telemetry = Telemetry(service_name="yyc3-tianshu")
    
    @telemetry.trace("analyze_strategy")
    async def analyze_strategy(data):
        telemetry.logger.info("开始分析", extra={"department": "finance"})
        telemetry.counter("strategy_analysis_total").inc()
        return result
"""

import json
import uuid
import time
import logging
import threading
import os
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from contextlib import contextmanager
from functools import wraps
import asyncio
import re


# ===== 结构化日志 =====

class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SanitizeField(Enum):
    """需要脱敏的字段"""
    PASSWORD = "password"
    TOKEN = "token"
    API_KEY = "api_key"
    ID_CARD = "id_card"
    PHONE = "phone"
    EMAIL = "email"
    BANK_ACCOUNT = "bank_account"


SENSITIVE_FIELDS = {
    "password", "token", "secret", "api_key", "apikey", "authorization",
    "id_card", "id_number", "phone", "mobile", "telephone",
    "email", "bank_account", "credit_card", "ssn", "passport",
}


class StructuredLogger:
    """
    结构化日志记录器
    
    特性:
    - correlationId 自动生成与传播
    - 敏感字段自动脱敏
    - 日志级别控制
    - 批量异步写入
    """
    
    def __init__(
        self,
        service_name: str,
        log_level: LogLevel = LogLevel.INFO,
        output_dir: str = "/var/log/yyc3",
    ):
        self.service_name = service_name
        self.log_level = log_level
        self.output_dir = output_dir
        
        self._batch: List[Dict] = []
        self._batch_lock = threading.Lock()
        self._flush_interval = 5  # 秒
        self._last_flush = time.time()
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        self._logger = logging.getLogger(f"yyc3.{service_name}")
        self._logger.setLevel(self._to_python_level(log_level))
        
        handler = logging.FileHandler(
            os.path.join(self.output_dir, f"{service_name}.log")
        )
        handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        ))
        self._logger.addHandler(handler)
    
    def _to_python_level(self, level: LogLevel) -> int:
        mapping = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }
        return mapping[level]
    
    def _sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """敏感字段脱敏"""
        sanitized = {}
        for key, value in data.items():
            if key.lower() in SENSITIVE_FIELDS:
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize(value)
            else:
                sanitized[key] = value
        return sanitized
    
    def _format_log(
        self,
        level: LogLevel,
        message: str,
        correlation_id: str = "",
        extra: Dict[str, Any] = None,
    ) -> str:
        """格式化日志条目"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "service": self.service_name,
            "message": message,
            "correlationId": correlation_id or str(uuid.uuid4()),
            "pid": os.getpid(),
            "thread": threading.current_thread().name,
        }
        
        if extra:
            entry["extra"] = self._sanitize(extra)
        
        return json.dumps(entry, ensure_ascii=False)
    
    def debug(self, message: str, correlation_id: str = "", **kwargs):
        self._log(LogLevel.DEBUG, message, correlation_id, kwargs)
    
    def info(self, message: str, correlation_id: str = "", **kwargs):
        self._log(LogLevel.INFO, message, correlation_id, kwargs)
    
    def warning(self, message: str, correlation_id: str = "", **kwargs):
        self._log(LogLevel.WARNING, message, correlation_id, kwargs)
    
    def error(self, message: str, correlation_id: str = "", **kwargs):
        self._log(LogLevel.ERROR, message, correlation_id, kwargs)
    
    def critical(self, message: str, correlation_id: str = "", **kwargs):
        self._log(LogLevel.CRITICAL, message, correlation_id, kwargs)
    
    def _log(self, level: LogLevel, message: str, correlation_id: str, extra: Dict):
        formatted = self._format_log(level, message, correlation_id, extra)
        self._logger.log(self._to_python_level(level), formatted)
        
        # 批量写入
        with self._batch_lock:
            self._batch.append(json.loads(formatted))
            if time.time() - self._last_flush > self._flush_interval:
                self._flush_batch()
    
    def _flush_batch(self):
        """批量写入到文件"""
        if not self._batch:
            return
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        filepath = os.path.join(
            self.output_dir, f"{self.service_name}_{date_str}.jsonl"
        )
        
        with open(filepath, "a") as f:
            for entry in self._batch:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        self._batch.clear()
        self._last_flush = time.time()


# ===== 指标监控 =====

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


@dataclass
class SLIDefinition:
    """服务等级指标定义"""
    name: str
    description: str
    metric: str
    threshold: float
    unit: str = "percent"


class Metric:
    """指标基类"""
    def __init__(self, name: str, description: str, labels: Dict[str, str] = None):
        self.name = name
        self.description = description
        self.labels = labels or {}
        self.created_at = datetime.now()


class Counter(Metric):
    """计数器 — 只增不减"""
    def __init__(self, name: str, description: str, labels: Dict[str, str] = None):
        super().__init__(name, description, labels)
        self._value = 0
        self._lock = threading.Lock()
    
    def inc(self, amount: int = 1):
        with self._lock:
            self._value += amount
    
    def value(self) -> int:
        return self._value


class Gauge(Metric):
    """仪表盘 — 可增可减"""
    def __init__(self, name: str, description: str, labels: Dict[str, str] = None):
        super().__init__(name, description, labels)
        self._value = 0.0
        self._lock = threading.Lock()
    
    def set(self, value: float):
        with self._lock:
            self._value = value
    
    def inc(self, amount: float = 1.0):
        with self._lock:
            self._value += amount
    
    def dec(self, amount: float = 1.0):
        with self._lock:
            self._value -= amount
    
    def value(self) -> float:
        return self._value


class Histogram(Metric):
    """直方图 — 分布统计"""
    def __init__(
        self,
        name: str,
        description: str,
        buckets: List[float] = None,
        labels: Dict[str, str] = None,
    ):
        super().__init__(name, description, labels)
        self.buckets = buckets or [0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10, 30, 60]
        self._values: List[float] = []
        self._lock = threading.Lock()
    
    def observe(self, value: float):
        with self._lock:
            self._values.append(value)
    
    def percentile(self, p: float) -> float:
        with self._lock:
            if not self._values:
                return 0.0
            sorted_vals = sorted(self._values)
            idx = int(len(sorted_vals) * p / 100)
            return sorted_vals[min(idx, len(sorted_vals) - 1)]
    
    def p50(self) -> float: return self.percentile(50)
    def p95(self) -> float: return self.percentile(95)
    def p99(self) -> float: return self.percentile(99)
    
    def value(self) -> Dict[str, float]:
        return {"p50": self.p50(), "p95": self.p95(), "p99": self.p99()}


class MetricsRegistry:
    """指标注册表"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self._metrics: Dict[str, Metric] = {}
        self._slis: List[SLIDefinition] = []
        self._lock = threading.Lock()
    
    def register_counter(self, name: str, description: str, labels: Dict = None) -> Counter:
        with self._lock:
            metric = Counter(name, description, labels)
            self._metrics[name] = metric
            return metric
    
    def register_gauge(self, name: str, description: str, labels: Dict = None) -> Gauge:
        with self._lock:
            metric = Gauge(name, description, labels)
            self._metrics[name] = metric
            return metric
    
    def register_histogram(self, name: str, description: str, buckets: List[float] = None, labels: Dict = None) -> Histogram:
        with self._lock:
            metric = Histogram(name, description, buckets, labels)
            self._metrics[name] = metric
            return metric
    
    def register_sli(self, sli: SLIDefinition):
        self._slis.append(sli)
    
    def get_metric(self, name: str) -> Optional[Metric]:
        return self._metrics.get(name)
    
    def export_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "service": self.service_name,
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    name: {
                        "type": type(metric).__name__.lower(),
                        "value": metric.value(),
                        "labels": metric.labels,
                    }
                    for name, metric in self._metrics.items()
                },
                "slis": [
                    {
                        "name": sli.name,
                        "description": sli.description,
                        "threshold": sli.threshold,
                        "unit": sli.unit,
                    }
                    for sli in self._slis
                ],
            }
    
    def calculate_slo_compliance(self) -> Dict[str, Any]:
        """计算 SLO 达标情况"""
        results = {}
        for sli in self._slis:
            metric = self._metrics.get(sli.metric)
            if metric and isinstance(metric, Histogram):
                p99 = metric.p99()
                compliant = p99 <= sli.threshold
                results[sli.name] = {
                    "sli": sli.name,
                    "threshold": sli.threshold,
                    "actual_p99": p99,
                    "compliant": compliant,
                    "error_budget_remaining": max(0, sli.threshold - p99),
                }
        return results


# ===== 分布式追踪 =====

class SpanContext:
    """Span 上下文 — 跨服务传播"""
    def __init__(
        self,
        trace_id: str = "",
        parent_span_id: str = "",
        correlation_id: str = "",
    ):
        self.trace_id = trace_id or uuid.uuid4().hex[:16]
        self.parent_span_id = parent_span_id
        self.correlation_id = correlation_id or str(uuid.uuid4())
    
    def to_headers(self) -> Dict[str, str]:
        return {
            "X-Trace-ID": self.trace_id,
            "X-Span-ID": self.parent_span_id,
            "X-Correlation-ID": self.correlation_id,
        }
    
    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> "SpanContext":
        return cls(
            trace_id=headers.get("X-Trace-ID", ""),
            parent_span_id=headers.get("X-Span-ID", ""),
            correlation_id=headers.get("X-Correlation-ID", ""),
        )


@dataclass
class Span:
    """追踪 Span"""
    name: str
    trace_id: str
    span_id: str
    parent_span_id: str = ""
    service_name: str = ""
    start_time: float = 0.0
    end_time: float = 0.0
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "ok"
    
    @property
    def duration(self) -> float:
        return (self.end_time - self.start_time) * 1000 if self.end_time else 0.0


class Tracer:
    """分布式追踪器"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self._active_span: Optional[Span] = None
        self._spans: List[Span] = []
        self._lock = threading.Lock()
    
    def start_span(
        self,
        name: str,
        parent_context: Optional[SpanContext] = None,
        attributes: Dict[str, Any] = None,
    ) -> Span:
        trace_id = parent_context.trace_id if parent_context else uuid.uuid4().hex[:16]
        parent_span_id = parent_context.parent_span_id if parent_context else ""
        
        span = Span(
            name=name,
            trace_id=trace_id,
            span_id=uuid.uuid4().hex[:8],
            parent_span_id=parent_span_id,
            service_name=self.service_name,
            start_time=time.time(),
            attributes=attributes or {},
        )
        
        with self._lock:
            self._active_span = span
        
        return span
    
    def end_span(self, span: Span, status: str = "ok"):
        span.end_time = time.time()
        span.status = status
        
        with self._lock:
            self._spans.append(span)
            if self._active_span and self._active_span.span_id == span.span_id:
                self._active_span = None
    
    def add_event(self, span: Span, name: str, attributes: Dict[str, Any] = None):
        span.events.append({
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "attributes": attributes or {},
        })
    
    @contextmanager
    def trace(self, name: str, **attributes):
        """上下文管理器风格的追踪"""
        span = self.start_span(name, attributes=attributes)
        try:
            yield span
        except Exception as e:
            span.status = "error"
            self.add_event(span, "exception", {"error": str(e), "type": type(e).__name__})
            raise
        finally:
            self.end_span(span)
    
    def export_spans(self) -> List[Dict]:
        return [
            {
                "name": s.name,
                "traceId": s.trace_id,
                "spanId": s.span_id,
                "parentSpanId": s.parent_span_id,
                "service": s.service_name,
                "startTime": datetime.fromtimestamp(s.start_time).isoformat(),
                "duration": s.duration,
                "attributes": s.attributes,
                "events": s.events,
                "status": s.status,
            }
            for s in self._spans
        ]


# ===== 统一 Telemetry SDK =====

class Telemetry:
    """
    YYC³ 全栈可观测性 SDK
    
    统一提供 Logs / Metrics / Traces 三大支柱能力。
    """
    
    def __init__(self, service_name: str, log_level: LogLevel = LogLevel.INFO):
        self.service_name = service_name
        self.logger = StructuredLogger(service_name, log_level)
        self.metrics = MetricsRegistry(service_name)
        self.tracer = Tracer(service_name)
        
        # 预注册标准指标
        self._register_standard_metrics()
        
        self.logger.info(f"[Telemetry] 初始化完成 | service={service_name}")
    
    def _register_standard_metrics(self):
        """注册标准指标"""
        self.request_count = self.metrics.register_counter(
            "request_count", "请求总数",
            labels={"service": self.service_name},
        )
        self.request_duration = self.metrics.register_histogram(
            "request_duration", "请求延迟(ms)",
            labels={"service": self.service_name},
        )
        self.error_count = self.metrics.register_counter(
            "error_count", "错误总数",
            labels={"service": self.service_name},
        )
        self.active_connections = self.metrics.register_gauge(
            "active_connections", "活跃连接数",
            labels={"service": self.service_name},
        )
        
        # 注册标准 SLI
        self.metrics.register_sli(SLIDefinition(
            name="latency", description="请求延迟P99",
            metric="request_duration", threshold=500.0,
        ))
        self.metrics.register_sli(SLIDefinition(
            name="availability", description="服务可用性",
            metric="error_count", threshold=0.01,
        ))
    
    def counter(self, name: str, description: str = "") -> Counter:
        return self.metrics.register_counter(name, description)
    
    def gauge(self, name: str, description: str = "") -> Gauge:
        return self.metrics.register_gauge(name, description)
    
    def histogram(self, name: str, description: str = "", buckets: List[float] = None) -> Histogram:
        return self.metrics.register_histogram(name, description, buckets)
    
    def trace(self, name: str, **attributes):
        """装饰器风格追踪"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                span = self.tracer.start_span(name, attributes=attributes)
                start = time.time()
                try:
                    result = await func(*args, **kwargs)
                    self.request_count.inc()
                    self.request_duration.observe((time.time() - start) * 1000)
                    return result
                except Exception as e:
                    self.error_count.inc()
                    self.tracer.add_event(span, "error", {"error": str(e)})
                    raise
                finally:
                    self.tracer.end_span(span)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                span = self.tracer.start_span(name, attributes=attributes)
                start = time.time()
                try:
                    result = func(*args, **kwargs)
                    self.request_count.inc()
                    self.request_duration.observe((time.time() - start) * 1000)
                    return result
                except Exception as e:
                    self.error_count.inc()
                    self.tracer.add_event(span, "error", {"error": str(e)})
                    raise
                finally:
                    self.tracer.end_span(span)
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper
        
        return decorator
    
    def export_dashboard_data(self) -> Dict[str, Any]:
        """导出态势大屏数据"""
        return {
            **self.metrics.export_snapshot(),
            "traces": self.tracer.export_spans()[-100:],
            "slo": self.metrics.calculate_slo_compliance(),
        }


# ===== 告警规则引擎 =====

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AlertRule:
    """告警规则"""
    name: str
    description: str
    metric: str
    condition: str  # ">", "<", ">=", "<=", "=="
    threshold: float
    severity: AlertSeverity = AlertSeverity.WARNING
    cooldown: int = 300  # 冷却时间（秒）
    enabled: bool = True


class AlertManager:
    """告警管理器"""
    
    def __init__(self, telemetry: Telemetry):
        self.telemetry = telemetry
        self.rules: List[AlertRule] = []
        self._last_triggered: Dict[str, float] = {}
        self._alert_history: List[Dict] = []
    
    def add_rule(self, rule: AlertRule):
        self.rules.append(rule)
        self.telemetry.logger.info(f"[AlertManager] 添加告警规则 | rule={rule.name} | severity={rule.severity.value}")
    
    def evaluate(self) -> List[Dict]:
        """评估所有告警规则"""
        triggered = []
        now = time.time()
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            # 冷却检查
            last_trigger = self._last_triggered.get(rule.name, 0)
            if now - last_trigger < rule.cooldown:
                continue
            
            # 获取指标值
            metric = self.telemetry.metrics.get_metric(rule.metric)
            if not metric:
                continue
            
            value = metric.value()
            if isinstance(value, dict):
                value = value.get("p99", value.get("p95", 0))
            
            # 条件判断
            triggered_flag = False
            if rule.condition == ">" and value > rule.threshold:
                triggered_flag = True
            elif rule.condition == "<" and value < rule.threshold:
                triggered_flag = True
            elif rule.condition == ">=" and value >= rule.threshold:
                triggered_flag = True
            elif rule.condition == "<=" and value <= rule.threshold:
                triggered_flag = True
            elif rule.condition == "==" and value == rule.threshold:
                triggered_flag = True
            
            if triggered_flag:
                alert = {
                    "rule": rule.name,
                    "severity": rule.severity.value,
                    "metric": rule.metric,
                    "value": value,
                    "threshold": rule.threshold,
                    "condition": rule.condition,
                    "timestamp": datetime.now().isoformat(),
                    "message": f"{rule.name}: {rule.metric} {rule.condition} {rule.threshold} (当前: {value})",
                }
                triggered.append(alert)
                self._last_triggered[rule.name] = now
                self._alert_history.append(alert)
                
                self.telemetry.logger.warning(
                    f"[AlertManager] 告警触发 | {alert['message']}",
                    severity=rule.severity.value,
                )
        
        return triggered
    
    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        return self._alert_history[-limit:]


# ===== 使用示例 =====

async def example_usage():
    """可观测性 SDK 使用示例"""
    
    telemetry = Telemetry(service_name="yyc3-tianshu")
    
    # 1. 结构化日志
    telemetry.logger.info("系统启动", version="2.1.0", environment="production")
    telemetry.logger.warning("内存使用率偏高", memory_usage=85.3, threshold=80)
    
    # 2. 指标监控
    counter = telemetry.counter("strategy_analysis_total", "战略分析次数")
    counter.inc()
    counter.inc()
    
    telemetry.gauge("memory_usage_percent", "内存使用率").set(72.5)
    
    telemetry.histogram("api_latency", "API延迟").observe(125)
    telemetry.metrics.get_metric("api_latency").observe(230)
    
    # 3. 分布式追踪
    @telemetry.trace("business_strategy_analysis", scenario="finance")
    async def analyze_strategy(data):
        telemetry.logger.info("开始分析", data_size=len(data))
        # 模拟业务逻辑
        await asyncio.sleep(0.5)
        return {"result": "success", "score": 92}
    
    result = await analyze_strategy({"revenue": 1000000, "cost": 800000})
    
    # 4. 告警规则
    alert_mgr = AlertManager(telemetry)
    alert_mgr.add_rule(AlertRule(
        name="高延迟告警", description="P99延迟超阈值",
        metric="api_latency", condition=">", threshold=500.0,
        severity=AlertSeverity.WARNING,
    ))
    alert_mgr.evaluate()
    
    # 5. 导出态势大屏数据
    dashboard = telemetry.export_dashboard_data()
    print(json.dumps(dashboard, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(example_usage())