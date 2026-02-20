# Browser-Use Windows 兼容性解决方案

## 概述

本文档详细分析了 browser-use 在 Windows 环境下的兼容性问题，并提供了完整的解决方案。

**测试环境：**
- 操作系统: Windows 10/11
- Python版本: 3.11.9
- browser-use版本: 0.11.9
- browser-use-sdk版本: 2.0.15

---

## 一、发现的兼容性问题

### 1.1 CLI `install` 命令失败

**问题描述：**
```powershell
browser-use install
# 错误: FileNotFoundError: [WinError 2] 系统找不到指定的文件。
```

**根本原因：**
在 `main.py` 第 63 行，`browser-use install` 命令尝试调用 `uvx` 命令：
```python
cmd = ['uvx', 'playwright', 'install', 'chromium']
result = subprocess.run(cmd)
```

但 Windows 系统上可能没有安装 `uvx`，导致命令执行失败。

**解决方案：**
```powershell
# 方法1: 使用 pip 安装 playwright
pip install playwright
playwright install chromium

# 方法2: 使用 uv 工具（如果已安装）
uv pip install playwright
uv run playwright install chromium
```

---

### 1.2 `os.kill(pid, 0)` 在 Windows 下报错

**问题描述：**
```powershell
browser-use open https://www.baidu.com
# 错误: OSError: [WinError 87] 参数错误。
```

**根本原因：**
在 `main.py` 第 158 行和 `utils.py` 第 43 行，使用 `os.kill(pid, 0)` 检查进程是否存在：
```python
def is_server_running(session: str) -> bool:
    pid = int(pid_path.read_text().strip())
    os.kill(pid, 0)  # 在Windows下会报错
    return True
```

`os.kill(pid, 0)` 在 Windows 下不支持 signal 0，会抛出 `OSError: [WinError 87]`。

**解决方案：**
使用 `psutil` 库或 Windows 特定的 API 来检查进程是否存在：

```python
import sys

def is_server_running(session: str) -> bool:
    """Check if server is running for session."""
    pid_path = get_pid_path(session)
    if not pid_path.exists():
        return False
    try:
        pid = int(pid_path.read_text().strip())
        
        if sys.platform == 'win32':
            # Windows: 使用 psutil 或 ctypes
            try:
                import psutil
                return psutil.pid_exists(pid)
            except ImportError:
                # 备用方案: 使用 ctypes
                import ctypes
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.OpenProcess(1, False, pid)
                if handle:
                    kernel32.CloseHandle(handle)
                    return True
                return False
        else:
            # Unix/Linux/macOS
            os.kill(pid, 0)
            return True
    except (OSError, ValueError):
        return False
```

---

### 1.3 Playwright 未安装

**问题描述：**
```
ModuleNotFoundError: No module named 'playwright'
```

**解决方案：**
```powershell
# 安装 playwright
pip install playwright

# 安装 Chromium 浏览器
playwright install chromium

# 或者安装所有浏览器
playwright install
```

---

### 1.4 `which` 命令在 Windows 下不可用

**问题描述：**
在 `utils.py` 第 100 行，使用 `which` 命令查找 Chrome：
```python
result = subprocess.run(['which', cmd], capture_output=True, text=True)
```

Windows 没有 `which` 命令，应该使用 `where`。

**解决方案：**
```python
import shutil

def find_chrome_executable() -> str | None:
    """Find Chrome/Chromium executable on the system."""
    system = platform.system()
    
    if system == 'Linux':
        for cmd in ['google-chrome', 'chromium', 'chromium-browser']:
            path = shutil.which(cmd)
            if path:
                return path
    
    elif system == 'Windows':
        # 使用 where 命令或 shutil.which
        for cmd in ['chrome.exe', 'google-chrome.exe']:
            path = shutil.which(cmd)
            if path:
                return path
        # 检查常见路径...
```

---

## 二、Windows 下的使用模式

### 2.1 Python API 模式（推荐）

这是 Windows 下最稳定的使用方式：

```python
import asyncio
from browser_use import Agent, BrowserSession
from browser_use.browser import BrowserProfile

async def main():
    # 创建浏览器配置
    profile = BrowserProfile(
        headless=True,  # 无头模式
    )
    
    # 创建浏览器实例
    browser = BrowserSession(browser_profile=profile)
    
    # 启动浏览器
    await browser.start()
    
    # 获取当前页面
    page = await browser.get_current_page()
    
    # 导航到目标网站
    await page.goto("https://www.baidu.com")
    
    # 获取页面标题
    title = await page.title()
    print(f"页面标题: {title}")
    
    # 关闭浏览器
    await browser.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

**状态：** ✅ 可用

---

### 2.2 CLI 模式（有限支持）

由于上述兼容性问题，CLI 模式在 Windows 下功能受限：

```powershell
# 这些命令可能无法正常工作:
browser-use install          # ❌ 失败 - uvx 命令不存在
browser-use open <url>       # ❌ 失败 - os.kill 报错
browser-use sessions         # ❌ 失败 - os.kill 报错

# 这些命令可以正常工作:
browser-use --help           # ✅ 可用
browser-use init             # ✅ 可用
```

**解决方案：**
使用 Python API 替代 CLI 命令。

---

### 2.3 Remote 模式（云端浏览器）

Remote 模式使用 browser-use 的云服务，不依赖本地浏览器：

```python
import asyncio
from browser_use import BrowserSession
from browser_use.browser import BrowserProfile

async def main():
    # 使用云端浏览器
    browser = BrowserSession(
        cloud_browser=True,
        cloud_proxy_country_code='us',  # 美国代理
    )
    
    await browser.start()
    page = await browser.get_current_page()
    await page.goto("https://www.baidu.com")
    
    title = await page.title()
    print(f"页面标题: {title}")
    
    await browser.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

**需要设置 API Key：**
```powershell
$env:BROWSER_USE_API_KEY = "your-api-key"
```

**状态：** ✅ 可用（需要 API Key）

---

## 三、完整安装指南（Windows）

### 步骤 1: 安装 Python 依赖

```powershell
# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate

# 安装 browser-use
pip install browser-use

# 安装 playwright
pip install playwright

# 安装 Chromium 浏览器
playwright install chromium

# 可选: 安装 psutil（用于修复进程检查）
pip install psutil
```

### 步骤 2: 验证安装

```powershell
# 验证 browser-use 安装
python -c "from browser_use import BrowserSession; print('✅ browser-use 安装成功')"

# 验证 playwright 安装
python -c "from playwright.sync_api import sync_playwright; print('✅ playwright 安装成功')"

# 验证 Chromium 安装
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    print('✅ Chromium 安装成功')
    browser.close()
"
```

### 步骤 3: 运行测试

```python
# test_browser_use.py
import asyncio
from browser_use import BrowserSession
from browser_use.browser import BrowserProfile

async def test():
    profile = BrowserProfile(headless=True)
    browser = BrowserSession(browser_profile=profile)
    await browser.start()
    
    page = await browser.get_current_page()
    await page.goto("https://www.baidu.com")
    
    title = await page.title()
    print(f"✅ 测试成功! 页面标题: {title}")
    
    await browser.stop()

if __name__ == "__main__":
    asyncio.run(test())
```

---

## 四、修复补丁

### 4.1 修复 `is_server_running` 函数

创建一个补丁文件 `browser_use_windows_patch.py`：

```python
"""
Browser-Use Windows 兼容性补丁
在导入 browser_use 之前应用此补丁
"""
import sys
import os

def apply_patch():
    """应用 Windows 兼容性补丁"""
    if sys.platform != 'win32':
        return
    
    # 导入并替换 utils.py 中的函数
    try:
        from browser_use.skill_cli import utils
        
        # 保存原始函数
        original_is_server_running = utils.is_server_running
        
        def patched_is_server_running(session: str) -> bool:
            """Windows 兼容的进程检查"""
            pid_path = utils.get_pid_path(session)
            if not pid_path.exists():
                return False
            try:
                pid = int(pid_path.read_text().strip())
                
                # Windows: 使用 psutil 或 ctypes
                try:
                    import psutil
                    return psutil.pid_exists(pid)
                except ImportError:
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    SYNCHRONIZE = 0x00100000
                    handle = kernel32.OpenProcess(SYNCHRONIZE, False, pid)
                    if handle:
                        kernel32.CloseHandle(handle)
                        return True
                    return False
            except (OSError, ValueError):
                return False
        
        # 替换函数
        utils.is_server_running = patched_is_server_running
        print("✅ Browser-Use Windows 补丁已应用")
        
    except Exception as e:
        print(f"⚠️  应用补丁失败: {e}")

# 自动应用补丁
apply_patch()
```

使用方法：
```python
import browser_use_windows_patch  # 必须在导入 browser_use 之前
from browser_use import BrowserSession
```

---

## 五、常见问题 FAQ

### Q1: CLI 命令在 Windows 下无法使用怎么办？

**A:** 使用 Python API 替代 CLI。CLI 在 Windows 下存在多个兼容性问题，建议使用 Python API 模式。

### Q2: 如何安装 Chromium 浏览器？

**A:** 
```powershell
pip install playwright
playwright install chromium
```

### Q3: 如何设置 API Key 使用云端浏览器？

**A:**
```powershell
# PowerShell
$env:BROWSER_USE_API_KEY = "your-api-key"

# 或者在 Python 中
import os
os.environ['BROWSER_USE_API_KEY'] = 'your-api-key'
```

### Q4: 如何启用有头模式（显示浏览器窗口）？

**A:**
```python
profile = BrowserProfile(headless=False)  # 设置为 False
```

### Q5: 如何指定 Chrome 可执行文件路径？

**A:**
```python
profile = BrowserProfile(
    headless=False,
    executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
)
```

---

## 六、推荐的工作流程

### 场景 1: 本地自动化测试

```python
import asyncio
from browser_use import BrowserSession, Agent
from browser_use.browser import BrowserProfile

async def run_test():
    # 1. 配置浏览器
    profile = BrowserProfile(
        headless=True,  # 无头模式适合自动化测试
    )
    
    # 2. 创建会话
    browser = BrowserSession(browser_profile=profile)
    
    # 3. 启动浏览器
    await browser.start()
    
    try:
        # 4. 获取页面并操作
        page = await browser.get_current_page()
        await page.goto("https://example.com")
        
        # 5. 使用 Agent 进行智能操作
        agent = Agent(
            task="Fill the contact form with test data",
            browser=browser,
        )
        result = await agent.run()
        
        print(f"任务结果: {result}")
        
    finally:
        # 6. 关闭浏览器
        await browser.stop()

if __name__ == "__main__":
    asyncio.run(run_test())
```

### 场景 2: 使用云端浏览器（绕过本地兼容性问题）

```python
import asyncio
from browser_use import BrowserSession

async def run_with_cloud():
    # 使用云端浏览器，无需本地 Chrome
    browser = BrowserSession(
        cloud_browser=True,
        cloud_proxy_country_code='us',
    )
    
    await browser.start()
    page = await browser.get_current_page()
    
    # 访问需要特定地区 IP 的网站
    await page.goto("https://example.com")
    
    # ... 执行操作
    
    await browser.stop()

if __name__ == "__main__":
    asyncio.run(run_with_cloud())
```

---

## 七、总结

| 功能 | Windows 支持状态 | 备注 |
|------|-----------------|------|
| Python API | ✅ 完全支持 | 推荐的使用方式 |
| CLI install | ❌ 不支持 | 使用 `playwright install` 替代 |
| CLI open | ❌ 不支持 | 使用 Python API 替代 |
| CLI sessions | ❌ 不支持 | 使用 Python API 替代 |
| Remote 模式 | ✅ 支持 | 需要 API Key |
| Chromium 模式 | ✅ 支持 | 需要安装 playwright |
| Real Chrome 模式 | ✅ 支持 | 需要安装 Chrome |

**Windows 用户建议：**
1. 使用 Python API 而非 CLI
2. 安装 playwright 和 Chromium
3. 如需使用 CLI 功能，等待官方修复或应用上述补丁
4. 考虑使用 Remote 模式绕过本地兼容性问题

---

## 八、参考链接

- [browser-use 官方文档](https://docs.browser-use.com)
- [Playwright 文档](https://playwright.dev/python/)
- [Python psutil 文档](https://psutil.readthedocs.io/)
