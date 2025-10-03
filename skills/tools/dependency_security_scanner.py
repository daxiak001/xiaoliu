"""
小柳升级：依赖安全扫描器
解决问题14：依赖管理和安全性
"""

import json
from datetime import datetime
from pathlib import Path

class DependencySecurityScanner:
    """依赖安全扫描器 - 检测漏洞和过时依赖"""
    
    # 已知漏洞数据库（简化版）
    KNOWN_VULNERABILITIES = {
        "requests": {
            "2.25.0": {
                "severity": "HIGH",
                "cve": "CVE-2021-XXXX",
                "description": "SSRF漏洞",
                "fixed_in": "2.26.0"
            }
        },
        "django": {
            "3.1.0": {
                "severity": "CRITICAL",
                "cve": "CVE-2021-YYYY",
                "description": "SQL注入漏洞",
                "fixed_in": "3.1.5"
            }
        }
    }
    
    # License兼容性
    LICENSE_COMPATIBILITY = {
        "MIT": ["MIT", "Apache-2.0", "BSD"],
        "GPL-3.0": ["GPL-3.0"],  # GPL要求衍生作品也用GPL
        "Apache-2.0": ["MIT", "Apache-2.0", "BSD"]
    }
    
    def __init__(self, project_license="MIT"):
        self.project_license = project_license
        self.scan_results = {}
    
    def scan_dependencies(self, requirements_file):
        """
        扫描依赖文件
        检查：安全漏洞、过时版本、License冲突
        """
        dependencies = self._parse_requirements(requirements_file)
        
        results = {
            "vulnerabilities": [],
            "outdated": [],
            "license_conflicts": [],
            "summary": {}
        }
        
        for dep_name, dep_version in dependencies.items():
            # 检查安全漏洞
            vuln = self._check_vulnerability(dep_name, dep_version)
            if vuln:
                results["vulnerabilities"].append(vuln)
            
            # 检查是否过时
            outdated = self._check_outdated(dep_name, dep_version)
            if outdated:
                results["outdated"].append(outdated)
            
            # 检查License冲突
            license_issue = self._check_license_conflict(dep_name, dep_version)
            if license_issue:
                results["license_conflicts"].append(license_issue)
        
        # 生成摘要
        results["summary"] = {
            "total_dependencies": len(dependencies),
            "vulnerabilities_found": len(results["vulnerabilities"]),
            "outdated_packages": len(results["outdated"]),
            "license_conflicts": len(results["license_conflicts"]),
            "risk_level": self._calculate_risk_level(results)
        }
        
        self.scan_results = results
        return results
    
    def _parse_requirements(self, requirements_file):
        """解析requirements.txt"""
        deps = {}
        
        if Path(requirements_file).exists():
            content = Path(requirements_file).read_text()
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    if '==' in line:
                        name, version = line.split('==')
                        deps[name.strip()] = version.strip()
        
        return deps
    
    def _check_vulnerability(self, package_name, version):
        """检查安全漏洞"""
        if package_name in self.KNOWN_VULNERABILITIES:
            vuln_versions = self.KNOWN_VULNERABILITIES[package_name]
            if version in vuln_versions:
                vuln_info = vuln_versions[version]
                return {
                    "package": package_name,
                    "current_version": version,
                    "severity": vuln_info["severity"],
                    "cve": vuln_info["cve"],
                    "description": vuln_info["description"],
                    "fix": f"升级到 {vuln_info['fixed_in']}"
                }
        return None
    
    def _check_outdated(self, package_name, version):
        """检查是否过时（简化实现）"""
        # 实际实现中会查询PyPI API
        outdated_threshold_days = 365  # 1年以上视为过时
        
        # 模拟检查
        latest_version = "999.0.0"  # 假设的最新版本
        
        if version < latest_version:
            return {
                "package": package_name,
                "current_version": version,
                "latest_version": latest_version,
                "recommendation": f"建议升级到 {latest_version}"
            }
        return None
    
    def _check_license_conflict(self, package_name, version):
        """检查License冲突"""
        # 获取包的License（实际会从PyPI获取）
        package_license = "MIT"  # 假设
        
        # 检查兼容性
        if self.project_license in self.LICENSE_COMPATIBILITY:
            compatible_licenses = self.LICENSE_COMPATIBILITY[self.project_license]
            if package_license not in compatible_licenses:
                return {
                    "package": package_name,
                    "package_license": package_license,
                    "project_license": self.project_license,
                    "conflict": f"{package_license} 与 {self.project_license} 不兼容"
                }
        
        return None
    
    def _calculate_risk_level(self, results):
        """计算风险等级"""
        critical_vulns = sum(
            1 for v in results["vulnerabilities"]
            if v["severity"] == "CRITICAL"
        )
        
        if critical_vulns > 0:
            return "CRITICAL"
        elif len(results["vulnerabilities"]) > 0:
            return "HIGH"
        elif len(results["outdated"]) > 5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_security_report(self):
        """生成安全报告"""
        if not self.scan_results:
            return "请先运行扫描"
        
        report = []
        report.append("=" * 70)
        report.append("依赖安全扫描报告")
        report.append("=" * 70)
        report.append(f"扫描时间: {datetime.now().isoformat()}")
        report.append("")
        
        # 摘要
        summary = self.scan_results["summary"]
        report.append(f"总依赖数: {summary['total_dependencies']}")
        report.append(f"发现漏洞: {summary['vulnerabilities_found']}")
        report.append(f"过时包: {summary['outdated_packages']}")
        report.append(f"License冲突: {summary['license_conflicts']}")
        report.append(f"风险等级: {summary['risk_level']}")
        report.append("")
        
        # 详细信息
        if self.scan_results["vulnerabilities"]:
            report.append("🔴 安全漏洞:")
            for vuln in self.scan_results["vulnerabilities"]:
                report.append(f"  - {vuln['package']} {vuln['current_version']}")
                report.append(f"    {vuln['severity']}: {vuln['description']}")
                report.append(f"    修复: {vuln['fix']}")
                report.append("")
        
        if self.scan_results["outdated"]:
            report.append("⚠️  过时依赖:")
            for pkg in self.scan_results["outdated"]:
                report.append(f"  - {pkg['package']}: {pkg['current_version']} → {pkg['latest_version']}")
            report.append("")
        
        if self.scan_results["license_conflicts"]:
            report.append("⚖️  License冲突:")
            for conflict in self.scan_results["license_conflicts"]:
                report.append(f"  - {conflict['package']}: {conflict['conflict']}")
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def auto_fix_suggestions(self):
        """自动修复建议"""
        suggestions = []
        
        # 针对漏洞的修复建议
        for vuln in self.scan_results.get("vulnerabilities", []):
            suggestions.append({
                "type": "security_fix",
                "priority": "CRITICAL",
                "action": f"pip install --upgrade {vuln['package']}=={vuln['fix'].split()[-1]}",
                "reason": f"修复 {vuln['cve']}"
            })
        
        # 针对过时包的建议
        for pkg in self.scan_results.get("outdated", []):
            suggestions.append({
                "type": "version_upgrade",
                "priority": "MEDIUM",
                "action": f"pip install --upgrade {pkg['package']}=={pkg['latest_version']}",
                "reason": "升级到最新版本"
            })
        
        return suggestions


# 使用示例
if __name__ == "__main__":
    scanner = DependencySecurityScanner(project_license="MIT")
    
    # 扫描依赖
    results = scanner.scan_dependencies("requirements.txt")
    
    # 生成报告
    report = scanner.generate_security_report()
    print(report)
    
    # 获取修复建议
    if results["summary"]["risk_level"] in ["CRITICAL", "HIGH"]:
        print("\n自动修复建议:")
        suggestions = scanner.auto_fix_suggestions()
        for i, sug in enumerate(suggestions, 1):
            print(f"{i}. [{sug['priority']}] {sug['action']}")
            print(f"   原因: {sug['reason']}")

