@echo off

set SEVENZIP="C:\Users\junyu\scoop\shims\7z.exe"
set ARCHIVE="D:\ComfyUI_windows_portable_nvidia_cu118_or_cpu.7z"
set DESTINATION="D:\"

echo 开始解压ComfyUI...
%SEVENZIP% x %ARCHIVE% -o%DESTINATION%
echo 解压完成！

echo 验证解压结果...
if exist "D:\ComfyUI_windows_portable" (
    echo ComfyUI_windows_portable目录创建成功！
    echo 目录内容:
    dir "D:\ComfyUI_windows_portable" /B | head -10
) else (
    echo 警告: ComfyUI_windows_portable目录未创建！
)

pause
