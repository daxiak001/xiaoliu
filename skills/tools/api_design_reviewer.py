"""
小柳升级：API设计审查系统
解决问题39：RESTful API最佳实践审查
"""
import re
from typing import List, Dict

class APIDesignReviewer:
    """API设计审查器"""
    
    HTTP_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
    
    BEST_PRACTICES = {
        "url_naming": {
            "use_nouns": True,           # 使用名词而非动词
            "use_plural": True,          # 使用复数
            "use_lowercase": True,       # 小写
            "use_hyphens": True,         # 使用连字符而非下划线
            "no_trailing_slash": True    # 不要尾部斜杠
        },
        "http_methods": {
            "GET": "获取资源，幂等，无副作用",
            "POST": "创建资源",
            "PUT": "完整更新资源，幂等",
            "PATCH": "部分更新资源",
            "DELETE": "删除资源，幂等"
        },
        "status_codes": {
            200: "OK - 成功",
            201: "Created - 创建成功",
            204: "No Content - 删除成功",
            400: "Bad Request - 请求错误",
            401: "Unauthorized - 未认证",
            403: "Forbidden - 无权限",
            404: "Not Found - 资源不存在",
            409: "Conflict - 冲突",
            500: "Internal Server Error - 服务器错误"
        }
    }
    
    def review_api(self, api_spec):
        """审查API设计"""
        issues = []
        
        # 审查URL命名
        issues.extend(self._review_url_naming(api_spec))
        
        # 审查HTTP方法使用
        issues.extend(self._review_http_methods(api_spec))
        
        # 审查状态码
        issues.extend(self._review_status_codes(api_spec))
        
        # 审查错误处理
        issues.extend(self._review_error_handling(api_spec))
        
        # 审查版本管理
        issues.extend(self._review_versioning(api_spec))
        
        # 审查分页
        issues.extend(self._review_pagination(api_spec))
        
        # 审查认证
        issues.extend(self._review_authentication(api_spec))
        
        return {
            "total_issues": len(issues),
            "issues": issues,
            "score": self._calculate_score(issues),
            "summary": self._generate_summary(issues)
        }
    
    def _review_url_naming(self, api_spec):
        """审查URL命名"""
        issues = []
        url = api_spec.get("url", "")
        
        # 检查1：使用动词而非名词
        verbs = ["create", "update", "delete", "get", "fetch", "add", "remove"]
        for verb in verbs:
            if verb in url.lower():
                issues.append({
                    "type": "url_naming",
                    "severity": "medium",
                    "location": url,
                    "problem": f"URL中包含动词'{verb}'",
                    "suggestion": "使用名词+HTTP方法。例: POST /users 而非 POST /createUser",
                    "example": "❌ POST /createUser → ✅ POST /users"
                })
        
        # 检查2：使用下划线而非连字符
        if "_" in url:
            issues.append({
                "type": "url_naming",
                "severity": "low",
                "location": url,
                "problem": "URL使用下划线",
                "suggestion": "使用连字符(-)代替下划线(_)",
                "example": "❌ /user_profiles → ✅ /user-profiles"
            })
        
        # 检查3：使用大写
        if url != url.lower():
            issues.append({
                "type": "url_naming",
                "severity": "low",
                "location": url,
                "problem": "URL包含大写字母",
                "suggestion": "统一使用小写",
                "example": "❌ /Users → ✅ /users"
            })
        
        # 检查4：尾部斜杠
        if url.endswith("/"):
            issues.append({
                "type": "url_naming",
                "severity": "low",
                "location": url,
                "problem": "URL包含尾部斜杠",
                "suggestion": "移除尾部斜杠",
                "example": "❌ /users/ → ✅ /users"
            })
        
        return issues
    
    def _review_http_methods(self, api_spec):
        """审查HTTP方法使用"""
        issues = []
        method = api_spec.get("method", "").upper()
        url = api_spec.get("url", "")
        
        # 检查1：GET请求修改数据
        if method == "GET" and any(word in url.lower() for word in ["delete", "update", "create"]):
            issues.append({
                "type": "http_method",
                "severity": "high",
                "location": f"{method} {url}",
                "problem": "GET请求不应修改数据",
                "suggestion": "使用POST/PUT/PATCH/DELETE",
                "example": "❌ GET /deleteUser?id=1 → ✅ DELETE /users/1"
            })
        
        # 检查2：POST用于获取数据
        if method == "POST" and "get" in url.lower():
            issues.append({
                "type": "http_method",
                "severity": "medium",
                "location": f"{method} {url}",
                "problem": "POST不应用于获取数据",
                "suggestion": "使用GET",
                "example": "❌ POST /getUser → ✅ GET /users/:id"
            })
        
        # 检查3：DELETE返回body
        if method == "DELETE" and api_spec.get("response_body"):
            issues.append({
                "type": "http_method",
                "severity": "low",
                "location": f"{method} {url}",
                "problem": "DELETE成功应返回204 No Content",
                "suggestion": "不返回响应体，状态码204",
                "example": "✅ 204 No Content (空body)"
            })
        
        return issues
    
    def _review_status_codes(self, api_spec):
        """审查状态码使用"""
        issues = []
        method = api_spec.get("method", "").upper()
        status_code = api_spec.get("status_code")
        
        # 检查1：POST成功返回200
        if method == "POST" and status_code == 200:
            issues.append({
                "type": "status_code",
                "severity": "medium",
                "location": f"{method} - {status_code}",
                "problem": "POST创建资源应返回201",
                "suggestion": "使用201 Created",
                "example": "❌ 200 OK → ✅ 201 Created"
            })
        
        # 检查2：DELETE成功返回200
        if method == "DELETE" and status_code == 200:
            issues.append({
                "type": "status_code",
                "severity": "low",
                "location": f"{method} - {status_code}",
                "problem": "DELETE成功推荐204",
                "suggestion": "使用204 No Content",
                "example": "200 OK → 204 No Content (更规范)"
            })
        
        return issues
    
    def _review_error_handling(self, api_spec):
        """审查错误处理"""
        issues = []
        error_response = api_spec.get("error_response", {})
        
        # 检查1：错误响应格式
        if error_response and not all(k in error_response for k in ["error", "message"]):
            issues.append({
                "type": "error_handling",
                "severity": "medium",
                "location": "error_response",
                "problem": "错误响应格式不规范",
                "suggestion": "包含error, message, details字段",
                "example": json.dumps({
                    "error": "ValidationError",
                    "message": "用户名已存在",
                    "details": {"field": "username"}
                }, ensure_ascii=False, indent=2)
            })
        
        return issues
    
    def _review_versioning(self, api_spec):
        """审查版本管理"""
        issues = []
        url = api_spec.get("url", "")
        
        # 检查：缺少版本号
        if not re.search(r'/v\d+/', url):
            issues.append({
                "type": "versioning",
                "severity": "medium",
                "location": url,
                "problem": "API缺少版本号",
                "suggestion": "在URL中包含版本: /api/v1/...",
                "example": "❌ /users → ✅ /api/v1/users"
            })
        
        return issues
    
    def _review_pagination(self, api_spec):
        """审查分页"""
        issues = []
        method = api_spec.get("method", "").upper()
        url = api_spec.get("url", "")
        pagination = api_spec.get("pagination")
        
        # 检查：列表接口缺少分页
        if method == "GET" and "/users" in url and not pagination:
            issues.append({
                "type": "pagination",
                "severity": "high",
                "location": url,
                "problem": "列表接口缺少分页",
                "suggestion": "添加page, page_size参数",
                "example": "GET /users?page=1&page_size=20"
            })
        
        return issues
    
    def _review_authentication(self, api_spec):
        """审查认证"""
        issues = []
        auth = api_spec.get("authentication")
        
        if not auth:
            issues.append({
                "type": "authentication",
                "severity": "high",
                "location": "API",
                "problem": "缺少认证机制",
                "suggestion": "使用Bearer Token或OAuth2",
                "example": "Authorization: Bearer <token>"
            })
        
        return issues
    
    def _calculate_score(self, issues):
        """计算得分 (0-100)"""
        if not issues:
            return 100
        
        penalty = {
            "high": 10,
            "medium": 5,
            "low": 2
        }
        
        total_penalty = sum(penalty.get(issue["severity"], 0) for issue in issues)
        score = max(0, 100 - total_penalty)
        
        return score
    
    def _generate_summary(self, issues):
        """生成摘要"""
        by_severity = {
            "high": len([i for i in issues if i["severity"] == "high"]),
            "medium": len([i for i in issues if i["severity"] == "medium"]),
            "low": len([i for i in issues if i["severity"] == "low"])
        }
        
        by_type = {}
        for issue in issues:
            itype = issue["type"]
            by_type[itype] = by_type.get(itype, 0) + 1
        
        return {
            "by_severity": by_severity,
            "by_type": by_type
        }

# 使用示例
if __name__ == "__main__":
    reviewer = APIDesignReviewer()
    
    api = {
        "method": "POST",
        "url": "/createUser",
        "status_code": 200,
        "authentication": None
    }
    
    result = reviewer.review_api(api)
    print(f"📊 API设计得分: {result['score']}/100")
    print(f"🔍 发现问题: {result['total_issues']}个")
    
    for issue in result['issues']:
        print(f"\n❌ {issue['severity'].upper()}: {issue['problem']}")
        print(f"   💡 {issue['suggestion']}")
        print(f"   📝 {issue['example']}")
