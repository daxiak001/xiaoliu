"""
小柳升级：数据库设计审查系统
解决问题40：表结构设计缺陷检测
"""

class DatabaseDesignReviewer:
    """数据库设计审查器"""
    
    def review_table(self, table_schema):
        """审查表设计"""
        issues = []
        
        # 1. 范式检查
        issues.extend(self._check_normalization(table_schema))
        
        # 2. 索引检查
        issues.extend(self._check_indexes(table_schema))
        
        # 3. 性能隐患
        issues.extend(self._check_performance(table_schema))
        
        # 4. 命名规范
        issues.extend(self._check_naming(table_schema))
        
        # 5. 数据类型
        issues.extend(self._check_data_types(table_schema))
        
        return {
            "total_issues": len(issues),
            "issues": issues,
            "score": self._calculate_score(issues)
        }
    
    def _check_normalization(self, schema):
        """检查范式违反"""
        issues = []
        
        # 检查1：缺少主键
        if not schema.get("primary_key"):
            issues.append({
                "type": "normalization",
                "severity": "high",
                "problem": "表缺少主键",
                "suggestion": "添加主键，推荐使用自增ID或UUID",
                "example": "ALTER TABLE users ADD PRIMARY KEY (id)"
            })
        
        # 检查2：重复组（违反1NF）
        for column in schema.get("columns", []):
            if "," in str(column.get("sample_data", "")):
                issues.append({
                    "type": "normalization",
                    "severity": "high",
                    "problem": f"列'{column['name']}'包含逗号分隔值，违反第一范式",
                    "suggestion": "拆分为关联表",
                    "example": "❌ tags: 'tech,python,ai' → ✅ 创建tags表"
                })
        
        # 检查3：部分依赖（违反2NF）
        # 简化检查：组合主键且有非主键列
        pk = schema.get("primary_key", [])
        if isinstance(pk, list) and len(pk) > 1:
            issues.append({
                "type": "normalization",
                "severity": "medium",
                "problem": "组合主键可能存在部分依赖",
                "suggestion": "检查是否所有列都依赖完整主键",
                "example": "订单明细表(order_id, product_id)不应存product_name"
            })
        
        return issues
    
    def _check_indexes(self, schema):
        """检查索引"""
        issues = []
        indexes = schema.get("indexes", [])
        columns = schema.get("columns", [])
        
        # 检查1：外键缺少索引
        for col in columns:
            if col["name"].endswith("_id") and col["name"] not in indexes:
                issues.append({
                    "type": "index",
                    "severity": "high",
                    "problem": f"外键'{col['name']}'缺少索引",
                    "suggestion": "为外键创建索引以提升JOIN性能",
                    "example": f"CREATE INDEX idx_{col['name']} ON {schema['name']}({col['name']})"
                })
        
        # 检查2：WHERE常用列缺少索引
        frequent_where = schema.get("frequent_where_columns", [])
        for col in frequent_where:
            if col not in indexes:
                issues.append({
                    "type": "index",
                    "severity": "medium",
                    "problem": f"常用查询列'{col}'缺少索引",
                    "suggestion": "添加索引提升查询性能",
                    "example": f"CREATE INDEX idx_{col} ON {schema['name']}({col})"
                })
        
        # 检查3：过多索引
        if len(indexes) > 5:
            issues.append({
                "type": "index",
                "severity": "low",
                "problem": f"索引过多({len(indexes)}个)，可能影响写入性能",
                "suggestion": "移除不常用的索引",
                "example": "保留最常用的3-5个索引"
            })
        
        return issues
    
    def _check_performance(self, schema):
        """检查性能隐患"""
        issues = []
        columns = schema.get("columns", [])
        
        # 检查1：TEXT/BLOB列过多
        large_cols = [c for c in columns if c.get("type") in ["TEXT", "BLOB", "LONGTEXT"]]
        if len(large_cols) > 2:
            issues.append({
                "type": "performance",
                "severity": "high",
                "problem": f"大字段过多({len(large_cols)}个)，影响查询性能",
                "suggestion": "拆分为单独的表",
                "example": "用户表 → 用户基本信息表 + 用户详情表"
            })
        
        # 检查2：缺少created_at/updated_at
        time_cols = [c["name"] for c in columns]
        if "created_at" not in time_cols or "updated_at" not in time_cols:
            issues.append({
                "type": "performance",
                "severity": "low",
                "problem": "缺少时间戳字段",
                "suggestion": "添加created_at和updated_at",
                "example": "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            })
        
        # 检查3：VARCHAR长度过大
        for col in columns:
            if col.get("type") == "VARCHAR" and col.get("length", 0) > 500:
                issues.append({
                    "type": "performance",
                    "severity": "medium",
                    "problem": f"VARCHAR({col['length']})过长",
                    "suggestion": "超过255考虑用TEXT，或缩短长度",
                    "example": "VARCHAR(1000) → TEXT 或 VARCHAR(255)"
                })
        
        return issues
    
    def _check_naming(self, schema):
        """检查命名规范"""
        issues = []
        
        # 检查1：表名复数
        if not schema["name"].endswith("s"):
            issues.append({
                "type": "naming",
                "severity": "low",
                "problem": "表名应使用复数",
                "suggestion": f"'{schema['name']}' → '{schema['name']}s'",
                "example": "user → users, order → orders"
            })
        
        # 检查2：列名包含表名
        for col in schema.get("columns", []):
            if schema["name"].rstrip("s") in col["name"]:
                issues.append({
                    "type": "naming",
                    "severity": "low",
                    "problem": f"列名'{col['name']}'包含表名",
                    "suggestion": "移除表名前缀",
                    "example": "users.user_name → users.name"
                })
        
        return issues
    
    def _check_data_types(self, schema):
        """检查数据类型"""
        issues = []
        
        for col in schema.get("columns", []):
            # 检查1：金额用FLOAT
            if "price" in col["name"] or "amount" in col["name"]:
                if col.get("type") in ["FLOAT", "DOUBLE"]:
                    issues.append({
                        "type": "data_type",
                        "severity": "high",
                        "problem": f"金额字段'{col['name']}'使用{col['type']}会丢失精度",
                        "suggestion": "使用DECIMAL(10,2)",
                        "example": "price DECIMAL(10,2) NOT NULL"
                    })
            
            # 检查2：布尔值用VARCHAR
            if col["name"].startswith("is_") or col["name"].startswith("has_"):
                if col.get("type") == "VARCHAR":
                    issues.append({
                        "type": "data_type",
                        "severity": "medium",
                        "problem": f"布尔字段'{col['name']}'使用VARCHAR",
                        "suggestion": "使用BOOLEAN或TINYINT(1)",
                        "example": "is_active BOOLEAN DEFAULT TRUE"
                    })
        
        return issues
    
    def _calculate_score(self, issues):
        """计算得分"""
        if not issues:
            return 100
        
        penalty = {"high": 15, "medium": 8, "low": 3}
        total_penalty = sum(penalty.get(i["severity"], 0) for i in issues)
        
        return max(0, 100 - total_penalty)

# 使用示例
if __name__ == "__main__":
    schema = {
        "name": "user",  # 应该是users
        "primary_key": "id",
        "columns": [
            {"name": "id", "type": "INT"},
            {"name": "user_name", "type": "VARCHAR", "length": 255},
            {"name": "email", "type": "VARCHAR", "length": 255},
            {"name": "price", "type": "FLOAT"},  # 错误：金额用FLOAT
            {"name": "is_active", "type": "VARCHAR", "length": 10},  # 错误：布尔值用VARCHAR
            {"name": "profile", "type": "TEXT"}
        ],
        "indexes": [],  # 缺少索引
        "frequent_where_columns": ["email"]
    }
    
    reviewer = DatabaseDesignReviewer()
    result = reviewer.review_table(schema)
    
    print(f"📊 数据库设计得分: {result['score']}/100")
    for issue in result['issues']:
        print(f"\n❌ {issue['severity'].upper()}: {issue['problem']}")
        print(f"   💡 {issue['suggestion']}")

