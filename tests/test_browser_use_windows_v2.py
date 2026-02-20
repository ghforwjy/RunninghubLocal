"""
测试browser-use在Windows下的各种使用模式 - 修正版
"""
import asyncio
import sys
import os

# 测试1: 基本的Python API使用
async def test_basic_api():
    """测试基本的browser-use Python API"""
    print("=" * 50)
    print("测试1: 基本Python API")
    print("=" * 50)
    
    try:
        from browser_use import Agent, BrowserSession
        from browser_use.browser import BrowserProfile
        print("✅ 成功导入 browser_use 模块")
        
        # 创建浏览器配置
        profile = BrowserProfile(
            headless=True,  # 无头模式
        )
        print(f"✅ 创建浏览器配置: {profile}")
        
        # 创建浏览器实例
        browser = BrowserSession(browser_profile=profile)
        print(f"✅ 创建浏览器实例: {browser.id}")
        
        print("✅ 基本API测试通过（未实际启动浏览器）")
        
    except Exception as e:
        print(f"❌ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


# 测试2: 使用Chromium模式
async def test_chromium_mode():
    """测试Chromium浏览器模式"""
    print("\n" + "=" * 50)
    print("测试2: Chromium模式")
    print("=" * 50)
    
    try:
        from browser_use import BrowserSession
        from browser_use.browser import BrowserProfile
        
        profile = BrowserProfile(
            headless=True,
        )
        
        browser = BrowserSession(browser_profile=profile)
        print(f"✅ 创建Chromium浏览器实例: {browser.id}")
        
        # 尝试启动浏览器
        print("尝试启动浏览器...")
        await browser.start()
        print("✅ 浏览器启动成功")
        
        # 获取当前页面
        page = await browser.get_current_page()
        print(f"✅ 获取当前页面")
        
        # 导航到百度
        await page.goto("https://www.baidu.com")
        print(f"✅ 导航到百度")
        
        title = await page.title()
        print(f"✅ 页面标题: {title}")
        
        await browser.stop()
        print("✅ Chromium模式测试完成")
        
    except Exception as e:
        print(f"❌ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


# 测试3: 检查Playwright安装
async def test_playwright():
    """测试Playwright是否正常工作"""
    print("\n" + "=" * 50)
    print("测试3: Playwright基础功能")
    print("=" * 50)
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            # 尝试启动chromium
            print("尝试启动Chromium...")
            browser = await p.chromium.launch(headless=True)
            print("✅ Chromium启动成功")
            
            page = await browser.new_page()
            await page.goto("https://www.baidu.com")
            
            title = await page.title()
            print(f"✅ 页面标题: {title}")
            
            await browser.close()
            print("✅ Playwright测试完成")
            
    except ImportError as e:
        print(f"❌ Playwright未安装: {e}")
        print("请运行: pip install playwright")
        print("然后运行: playwright install chromium")
    except Exception as e:
        print(f"❌ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


# 测试4: 检查环境变量和配置
def test_environment():
    """测试环境配置"""
    print("\n" + "=" * 50)
    print("测试4: 环境配置检查")
    print("=" * 50)
    
    print(f"操作系统: {sys.platform}")
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 检查关键环境变量
    env_vars = [
        "BROWSER_USE_API_KEY",
        "PLAYWRIGHT_BROWSERS_PATH",
        "CHROME_PATH",
        "PATH",
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            # 隐藏API key的大部分内容
            if "API_KEY" in var and value:
                value = value[:10] + "..." + value[-4:] if len(value) > 14 else "***"
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: 未设置")


# 测试5: 测试CLI命令
def test_cli():
    """测试CLI命令"""
    print("\n" + "=" * 50)
    print("测试5: CLI命令检查")
    print("=" * 50)
    
    import subprocess
    
    commands = [
        ["browser-use", "--help"],
        ["browser-use", "sessions"],
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ {' '.join(cmd)}: 成功")
            else:
                print(f"⚠️  {' '.join(cmd)}: 返回码 {result.returncode}")
                if result.stderr:
                    print(f"   错误: {result.stderr[:200]}")
        except Exception as e:
            print(f"❌ {' '.join(cmd)}: {e}")


# 测试6: 检查browser-use SDK
def test_sdk():
    """测试browser-use SDK"""
    print("\n" + "=" * 50)
    print("测试6: browser-use SDK检查")
    print("=" * 50)
    
    try:
        import browser_use_sdk
        print(f"✅ browser-use SDK已安装")
        print(f"   版本: {getattr(browser_use_sdk, '__version__', 'unknown')}")
    except ImportError:
        print("⚠️  browser-use SDK未安装")
        print("   安装命令: pip install browser-use-sdk")


# 主函数
async def main():
    print("Browser-Use Windows兼容性测试 v2")
    print("=" * 50)
    
    # 先检查环境
    test_environment()
    
    # 测试SDK
    test_sdk()
    
    # 测试CLI
    test_cli()
    
    # 测试Playwright基础功能
    await test_playwright()
    
    # 测试browser-use API
    await test_basic_api()
    
    # 测试Chromium模式（需要Playwright）
    # await test_chromium_mode()
    
    print("\n" + "=" * 50)
    print("所有测试完成!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
