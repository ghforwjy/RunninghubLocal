"""
测试browser-use在Windows下的各种使用模式
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
        from browser_use import Agent, Browser, BrowserConfig
        print("✅ 成功导入 browser_use 模块")
        
        # 创建浏览器配置
        config = BrowserConfig(
            headless=True,  # 无头模式
        )
        print(f"✅ 创建浏览器配置: {config}")
        
        # 创建浏览器实例
        browser = Browser(config=config)
        print(f"✅ 创建浏览器实例")
        
        # 尝试打开页面
        print("尝试打开 https://www.baidu.com...")
        page = await browser.new_page()
        await page.goto("https://www.baidu.com")
        print(f"✅ 成功打开页面: {page.url}")
        
        # 关闭浏览器
        await browser.close()
        print("✅ 浏览器已关闭")
        
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
        from browser_use import Browser, BrowserConfig
        
        config = BrowserConfig(
            headless=True,
            browser_type="chromium",
        )
        
        browser = Browser(config=config)
        page = await browser.new_page()
        await page.goto("https://www.baidu.com")
        
        title = await page.title()
        print(f"✅ 页面标题: {title}")
        
        await browser.close()
        print("✅ Chromium模式测试完成")
        
    except Exception as e:
        print(f"❌ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


# 测试3: 使用本地Chrome（real模式）
async def test_real_chrome_mode():
    """测试本地Chrome浏览器模式"""
    print("\n" + "=" * 50)
    print("测试3: 本地Chrome模式 (real)")
    print("=" * 50)
    
    try:
        from browser_use import Browser, BrowserConfig
        
        config = BrowserConfig(
            headless=False,  # 显示窗口
            browser_type="chrome",  # 使用本地Chrome
        )
        
        browser = Browser(config=config)
        page = await browser.new_page()
        await page.goto("https://www.baidu.com")
        
        title = await page.title()
        print(f"✅ 页面标题: {title}")
        
        await browser.close()
        print("✅ 本地Chrome模式测试完成")
        
    except Exception as e:
        print(f"❌ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


# 测试4: 检查Playwright安装
async def test_playwright():
    """测试Playwright是否正常工作"""
    print("\n" + "=" * 50)
    print("测试4: Playwright基础功能")
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
            
    except Exception as e:
        print(f"❌ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


# 测试5: 检查环境变量和配置
def test_environment():
    """测试环境配置"""
    print("\n" + "=" * 50)
    print("测试5: 环境配置检查")
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


# 主函数
async def main():
    print("Browser-Use Windows兼容性测试")
    print("=" * 50)
    
    # 先检查环境
    test_environment()
    
    # 测试Playwright基础功能
    await test_playwright()
    
    # 测试browser-use API
    await test_basic_api()
    await test_chromium_mode()
    # await test_real_chrome_mode()  # 暂时跳过，需要GUI
    
    print("\n" + "=" * 50)
    print("所有测试完成!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
