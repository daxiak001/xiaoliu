"""
小柳升级：第7轮问题47-52快速实现
性能/灰度/降级/事务/缓存/日志
"""

# Q47: 性能优化决策树
class PerformanceOptimizer:
    """性能优化决策树"""
    
    DECISION_TREE = {
        "用户反馈慢": {
            "步骤1_确认指标": {
                "check": "响应时间 > 3秒?",
                "if_yes": "步骤2_定位层次",
                "if_no": "可能是用户网络问题或主观感受"
            },
            "步骤2_定位层次": {
                "前端慢": ["检查bundle大小", "图片未压缩", "未启用CDN", "未启用缓存"],
                "后端慢": ["进入步骤3_后端排查"],
                "数据库慢": ["进入步骤4_数据库排查"],
                "网络慢": ["检查带宽", "跨区域延迟", "DNS解析"]
            },
            "步骤3_后端排查": {
                "工具": "性能分析器（cProfile/py-spy）",
                "排查点": [
                    "CPU密集计算 → 加缓存/异步处理",
                    "IO阻塞 → 改异步IO",
                    "外部API慢 → 加超时+降级",
                    "串行调用 → 改并发"
                ]
            },
            "步骤4_数据库排查": {
                "工具": "慢查询日志",
                "排查点": [
                    "缺索引 → 加索引",
                    "锁等待 → 优化事务",
                    "N+1查询 → 改JOIN或预加载",
                    "全表扫描 → 加WHERE/LIMIT"
                ]
            }
        }
    }
    
    def diagnose(self, symptoms):
        """诊断性能问题"""
        results = []
        
        if symptoms.get("response_time", 0) > 3:
            results.append({
                "issue": "响应时间过长",
                "likely_causes": [
                    "数据库慢查询",
                    "未使用缓存",
                    "同步IO阻塞",
                    "外部API超时"
                ],
                "diagnostic_steps": [
                    "1. 查看慢查询日志",
                    "2. 使用APM工具追踪",
                    "3. 检查CPU/内存使用率",
                    "4. 网络抓包分析"
                ]
            })
        
        return results

# Q48: 灰度发布策略
class GrayReleaseStrategy:
    """灰度发布策略"""
    
    def create_release_plan(self, feature_name):
        """创建发布计划"""
        return {
            "feature": feature_name,
            "stages": [
                {
                    "stage": 1,
                    "name": "内测",
                    "traffic": "0.1%",
                    "target": "内部员工",
                    "duration": "1天",
                    "success_criteria": "错误率 < 0.1%"
                },
                {
                    "stage": 2,
                    "name": "小范围灰度",
                    "traffic": "1%",
                    "target": "普通用户",
                    "duration": "2天",
                    "success_criteria": "错误率 < baseline * 1.1"
                },
                {
                    "stage": 3,
                    "name": "中范围灰度",
                    "traffic": "10%",
                    "duration": "3天",
                    "success_criteria": "核心指标无下降"
                },
                {
                    "stage": 4,
                    "name": "大范围灰度",
                    "traffic": "50%",
                    "duration": "2天",
                    "success_criteria": "用户反馈正面"
                },
                {
                    "stage": 5,
                    "name": "全量发布",
                    "traffic": "100%",
                    "duration": "持续监控1周"
                }
            ],
            "rollback_trigger": {
                "error_rate_spike": "错误率 > baseline * 1.5",
                "critical_bug": "出现P0级bug",
                "performance_degrade": "响应时间 > baseline * 1.3"
            },
            "monitoring": [
                "错误率",
                "响应时间P99",
                "业务转化率",
                "用户投诉数"
            ]
        }

# Q49: 服务降级与熔断
class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, failure_threshold=5, timeout=60):
        self.state = "CLOSED"  # CLOSED/OPEN/HALF_OPEN
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
    
    def call(self, func, *args, **kwargs):
        """调用服务"""
        if self.state == "OPEN":
            # 熔断开启，直接降级
            return self._fallback()
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """成功回调"""
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"  # 半开 → 关闭
            self.failure_count = 0
    
    def _on_failure(self):
        """失败回调"""
        self.failure_count += 1
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"  # 关闭 → 开启
    
    def _fallback(self):
        """降级逻辑"""
        return {"error": "服务暂时不可用，已降级"}

# Q50: 分布式事务
class DistributedTransaction:
    """分布式事务方案对比"""
    
    SOLUTIONS = {
        "2PC": {
            "名称": "两阶段提交",
            "优点": "强一致性",
            "缺点": "性能差，单点故障",
            "适用": "金融系统，一致性要求极高",
            "示例": """
# 阶段1: 准备
coordinator.prepare([order_db, payment_db, inventory_db])
# 阶段2: 提交
if all_prepared:
    coordinator.commit_all()
else:
    coordinator.rollback_all()
"""
        },
        "TCC": {
            "名称": "Try-Confirm-Cancel",
            "优点": "性能好，无锁",
            "缺点": "开发复杂，需要幂等",
            "适用": "电商订单",
            "示例": """
# Try: 预留资源
order_service.try_create()
payment_service.try_freeze()
inventory_service.try_lock()

# Confirm: 确认
if all_try_success:
    order_service.confirm()
    payment_service.confirm()
    inventory_service.confirm()
else:
    # Cancel: 取消
    order_service.cancel()
"""
        },
        "SAGA": {
            "名称": "长事务补偿",
            "优点": "性能好，适合长流程",
            "缺点": "最终一致性",
            "适用": "跨服务长流程",
            "示例": """
# 正向流程
order_service.create()
payment_service.pay()
inventory_service.deduct()

# 补偿流程（失败时）
inventory_service.restore()  # 补偿3
payment_service.refund()     # 补偿2
order_service.cancel()       # 补偿1
"""
        }
    }

# Q51: 缓存策略
class CacheStrategy:
    """缓存策略"""
    
    PATTERNS = {
        "Cache-Aside": {
            "描述": "旁路缓存，应用负责缓存逻辑",
            "读": "先查缓存，miss则查DB并写缓存",
            "写": "先更新DB，再删除缓存",
            "优点": "简单，适用广",
            "缺点": "不一致窗口期"
        },
        "Read-Through": {
            "描述": "缓存层负责加载",
            "读": "缓存自动从DB加载",
            "写": "应用只写DB",
            "优点": "应用无感知",
            "缺点": "缓存层复杂"
        },
        "Write-Through": {
            "描述": "写缓存同时写DB",
            "读": "先查缓存",
            "写": "同时写缓存和DB",
            "优点": "强一致",
            "缺点": "写性能差"
        }
    }
    
    ANTI_PATTERNS = {
        "缓存穿透": {
            "问题": "查询不存在的数据，绕过缓存打DB",
            "解决": "布隆过滤器 或 缓存空值"
        },
        "缓存雪崩": {
            "问题": "大量缓存同时过期",
            "解决": "过期时间加随机值"
        },
        "缓存击穿": {
            "问题": "热点key过期，瞬间大量请求打DB",
            "解决": "加互斥锁 或 热点key永不过期"
        }
    }

# Q52: 日志系统设计
class LoggingSystemDesign:
    """日志系统设计"""
    
    LOG_LEVELS = {
        "DEBUG": "调试信息，生产环境关闭",
        "INFO": "正常流程，如用户登录",
        "WARN": "警告，如API响应慢",
        "ERROR": "错误，如异常捕获",
        "CRITICAL": "严重错误，如服务不可用"
    }
    
    BEST_PRACTICES = {
        "结构化日志": {
            "格式": "JSON",
            "示例": {
                "timestamp": "2025-01-01T12:00:00Z",
                "level": "ERROR",
                "service": "order-service",
                "trace_id": "abc123",  # 分布式追踪
                "user_id": "user_456",
                "message": "支付失败",
                "error": "PaymentGatewayTimeout",
                "duration_ms": 5000
            }
        },
        "敏感信息脱敏": {
            "脱敏字段": ["password", "credit_card", "id_card"],
            "方法": "密码: *****, 卡号: **** **** **** 1234"
        },
        "分布式链路追踪": {
            "工具": "Jaeger/Zipkin",
            "trace_id": "贯穿整个请求链路"
        }
    }

# 使用示例
if __name__ == "__main__":
    # 性能诊断
    optimizer = PerformanceOptimizer()
    print(optimizer.diagnose({"response_time": 5}))
    
    # 灰度发布
    gray = GrayReleaseStrategy()
    plan = gray.create_release_plan("新支付功能")
    print(f"灰度阶段数: {len(plan['stages'])}")
    
    # 熔断器
    cb = CircuitBreaker()
    print(f"熔断器状态: {cb.state}")
    
    # 分布式事务
    print("推荐方案: TCC（电商场景）")

