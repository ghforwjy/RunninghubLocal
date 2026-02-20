"""
Browser-Use Windows 兼容性补丁
在导入 browser_use 之前应用此补丁

使用方法:
    import browser_use_windows_patch  # 必须在导入 browser_use 之前
    from browser_use import BrowserSession
"""
import sys
import os

def apply_patch():
    """应用 Windows 兼容性补丁"""
    if sys.platform != 'win32':
        return
    
    try:
        # 导入 utils 模块
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
                    # 备用方案: 使用 ctypes
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
        
        # 同时修补 main.py 中的函数
        try:
            from browser_use.skill_cli import main
            main.is_server_running = patched_is_server_running
        except Exception:
            pass
        
        print("✅ Browser-Use Windows 补丁已应用")
        
    except Exception as e:
        print(f"⚠️  应用补丁失败: {e}")

# 自动应用补丁
apply_patch()
