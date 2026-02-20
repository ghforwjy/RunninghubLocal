"""
Browser-Use Windows 最终测试脚本
测试所有功能并生成报告
"""
import asyncio
import sys
import os
import subprocess
import json
from datetime import datetime

# 测试结果存储
results = {
    "timestamp": datetime.now().isoformat(),
    "platform": sys.platform,
    "python_version": sys.version,
    "tests": {}
}

def log_test(name: str, status: str, details: str = ""):
    """记录测试结果"""
    results["tests"][name] = {
        "status": status,
        "details": details
    }
    icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{icon} {name}: {status}")
    if details:
        print(f"   {details}")

async def test_import():
    """测试模块导入"""
    try:
        from browser_use import BrowserSession, Agent
        from browser_use.browser import BrowserProfile
        log_test("模块导入", "PASS", "成功导入 BrowserSession, Agent, BrowserProfile")
        return True
    except Exception as e:
        log_test("模块导入", "FAIL", str(e))
        return False

async def test_browser_creation():
    """测试浏览器实例创建"""
    try:
        from browser_use import BrowserSession
        from browser_use.browser import BrowserProfile
        
        profile = BrowserProfile(headless=True)
        browser = BrowserSession(browser_profile=profile)
        
        log_test("浏览器实例创建", "PASS", f"浏览器ID: {browser.id}")
        return True
    except Exception as e:
        log_test("浏览器实例创建", "FAIL", str(e))
        return False

async def test_browser_launch():
    """测试浏览器启动"""
    try:
        from browser_use import BrowserSession
        from browser_use.browser import BrowserProfile
        
        profile = BrowserProfile(headless=True)
        browser = BrowserSession(browser_profile=profile)
        
        await browser.start()
        log_test("浏览器启动", "PASS", "浏览器启动成功")
        
        await browser.stop()
        return True
    except Exception as e:
        log_test("浏览器启动", "FAIL", str(e))
        return False

async def test_page_navigation():
    """测试页面导航"""
    try:
        from browser_use import BrowserSession
        from browser_use.browser import BrowserProfile
        
        profile = BrowserProfile(headless=True)
        browser = BrowserSession(browser_profile=profile)
        
        await browser.start()
        page = await browser.get_current_page()
        await page.goto("https://www.baidu.com")
        title = await page.title()
        
        log_test("页面导航", "PASS", f"页面标题: {title}")
        
        await browser.stop()
        return True
    except Exception as e:
        log_test("页面导航", "FAIL", str(e))
        return False

def test_cli_help():
    """测试 CLI help 命令"""
    try:
        result = subprocess.run(
            ["browser-use", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            log_test("CLI Help", "PASS", "browser-use --help 执行成功")
            return True
        else:
            log_test("CLI Help", "FAIL", f"返回码: {result.returncode}")
            return False
    except Exception as e:
        log_test("CLI Help", "FAIL", str(e))
        return False

def test_cli_sessions():
    """测试 CLI sessions 命令"""
    try:
        result = subprocess.run(
            ["browser-use", "sessions"],
            capture_output=True,
            text=True,
            timeout=10
        )
        # 这个命令在 Windows 下可能会失败，但我们要记录结果
        if result.returncode == 0:
            log_test("CLI Sessions", "PASS", "命令执行成功")
            return True
        else:
            log_test("CLI Sessions", "FAIL", f"Windows 兼容性问题: {result.stderr[:100]}")
            return False
    except Exception as e:
        log_test("CLI Sessions", "FAIL", str(e))
        return False

def test_environment():
    """测试环境变量"""
    env_vars = {
        "BROWSER_USE_API_KEY": os.environ.get("BROWSER_USE_API_KEY", ""),
        "PLAYWRIGHT_BROWSERS_PATH": os.environ.get("PLAYWRIGHT_BROWSERS_PATH", ""),
    }
    
    details = []
    for var, value in env_vars.items():
        if value:
            # 隐藏敏感信息
            if "API_KEY" in var:
                value = value[:10] + "..." if len(value) > 10 else "***"
            details.append(f"{var}: {value}")
        else:
            details.append(f"{var}: 未设置")
    
    log_test("环境变量", "PASS", "; ".join(details))
    return True

async def main():
    """主测试函数"""
    print("=" * 60)
    print("Browser-Use Windows 兼容性测试")
    print("=" * 60)
    print(f"时间: {results['timestamp']}")
    print(f"平台: {results['platform']}")
    print(f"Python: {results['python_version'].split()[0]}")
    print("=" * 60)
    print()
    
    # 环境测试
    print("【环境检查】")
    test_environment()
    print()
    
    # CLI 测试
    print("【CLI 测试】")
    test_cli_help()
    test_cli_sessions()
    print()
    
    # Python API 测试
    print("【Python API 测试】")
    await test_import()
    await test_browser_creation()
    await test_browser_launch()
    await test_page_navigation()
    print()
    
    # 生成报告
    print("=" * 60)
    print("测试报告")
    print("=" * 60)
    
    total = len(results["tests"])
    passed = sum(1 for t in results["tests"].values() if t["status"] == "PASS")
    failed = sum(1 for t in results["tests"].values() if t["status"] == "FAIL")
    
    print(f"总计: {total} | 通过: {passed} | 失败: {failed}")
    print()
    
    # 保存报告
    report_file = "browser_use_test_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"详细报告已保存到: {report_file}")
    
    # 总结
    print()
    print("=" * 60)
    print("总结")
    print("=" * 60)
    if failed == 0:
        print("✅ 所有测试通过！Browser-Use 在 Windows 下工作正常。")
    else:
        print(f"⚠️  有 {failed} 个测试失败。请参考上方详情和文档进行修复。")
        print()
        print("常见问题:")
        print("1. CLI 命令失败 - 使用 Python API 替代")
        print("2. 浏览器启动失败 - 确保已安装 playwright: pip install playwright")
        print("3. Chromium 未找到 - 运行: playwright install chromium")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
