# 查找run_cpu.bat文件
Write-Host "正在查找run_cpu.bat文件..."

# 检查D盘根目录
if (Test-Path "D:\run_cpu.bat") {
    Write-Host "找到: D:\run_cpu.bat"
} else {
    Write-Host "D盘根目录未找到run_cpu.bat"
}

# 检查ComfyUI_windows_portable目录
if (Test-Path "D:\ComfyUI_windows_portable\run_cpu.bat") {
    Write-Host "找到: D:\ComfyUI_windows_portable\run_cpu.bat"
} else {
    Write-Host "ComfyUI_windows_portable目录未找到run_cpu.bat"
}

# 递归搜索整个D盘
Write-Host "正在递归搜索D盘..."
$foundFiles = Get-ChildItem "D:\" -Name "run_cpu.bat" -Recurse -ErrorAction SilentlyContinue

if ($foundFiles) {
    Write-Host "找到以下run_cpu.bat文件:"
    foreach ($file in $foundFiles) {
        Write-Host "- $file"
    }
} else {
    Write-Host "D盘中未找到run_cpu.bat文件"
}

# 检查是否有其他run_*.bat文件
Write-Host "正在查找其他run_*.bat文件..."
$runFiles = Get-ChildItem "D:\" -Name "run_*.bat" -Recurse -ErrorAction SilentlyContinue

if ($runFiles) {
    Write-Host "找到以下run_*.bat文件:"
    foreach ($file in $runFiles) {
        Write-Host "- $file"
    }
} else {
    Write-Host "D盘中未找到run_*.bat文件"
}
