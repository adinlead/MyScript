@echo off
:: 使用Windows默认编码确保中文正常显示
chcp 936 >nul 2>&1
setlocal enabledelayedexpansion

:: 定义配置和默认路径
set "configRegPath=HKCU\Software\DesktopLayoutBackup"
set "defaultBackupPath=%USERPROFILE%\AppData\Local\DesktopLayoutBackup"
set "backupPath="

:: 尝试从注册表读取已保存的备份路径
for /f "skip=2 tokens=3*" %%a in ('reg query "%configRegPath%" /v "BackupPath" 2^>nul') do (
    set "backupPath=%%a %%b"
)

:: 如果是首次运行或未找到备份路径，使用默认路径并提示用户
if "!backupPath!"=="" (
    cls
    echo ==============================================
    echo        桌面布局备份工具 - 首次配置
    echo ==============================================
    echo.
    echo 检测到首次运行，将使用默认备份路径：
    echo !defaultBackupPath!
    echo.
    set /p "change=是否要修改此路径？(Y/N，默认N): "
    
    :: 处理用户输入
    if /i "!change!"=="Y" (
        set /p "userPath=请输入新的备份路径: "
        if "!userPath!" neq "" (
            set "backupPath=!userPath!"
        ) else (
            echo 路径不能为空，将使用默认路径
            set "backupPath=!defaultBackupPath!"
        )
    ) else (
        set "backupPath=!defaultBackupPath!"
    )
    
    :: 创建路径（如果不存在）
    if not exist "!backupPath!" (
        mkdir "!backupPath!" >nul 2>&1
        if %errorlevel% neq 0 (
            echo 路径创建成功：!backupPath!
        ) else (
            echo 无法创建路径"!backupPath!"，将使用默认路径
            set "backupPath=!defaultBackupPath!"
            mkdir "!backupPath!" >nul 2>&1
        )
    )
    
    :: 将路径保存到注册表
    reg add "%configRegPath%" /f >nul 2>&1
    reg add "%configRegPath%" /v "BackupPath" /t REG_SZ /d "!backupPath!" /f >nul 2>&1
    
    echo.
    echo 配置已保存，按任意键继续...
    pause >nul
)

:: 获取当前脚本的完整路径
set "scriptPath=%~f0"

:: 显示主菜单
:menu
cls
echo ==============================================
echo        桌面布局备份工具
echo ==============================================
echo  当前备份路径：!backupPath!
echo ==============================================
echo.
echo  1. 创建新的桌面布局备份
echo  2. 从备份还原桌面布局
echo  3. 查看所有备份
echo  4. 修改备份路径
echo  5. 卸载此工具
echo  6. 退出
echo.
set /p "choice=请输入选项 (1-6): "

:: 根据用户选择执行相应操作
if "%choice%"=="1" goto backup
if "%choice%"=="2" goto restore
if "%choice%"=="3" goto listbackups
if "%choice%"=="4" goto changePath
if "%choice%"=="5" goto uninstall
if "%choice%"=="6" goto exit
goto menu

:: 创建新备份
:backup
echo.
echo 正在创建新的桌面布局备份...

:: 生成带有时间戳的备份文件名（格式：YYYYMMDD_HHMMSS）
set "timestamp=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "timestamp=!timestamp: =0!"
set "backupFile=!backupPath!\IconLayout_!timestamp!.reg"

:: 导出注册表中的图标位置信息
reg export "HKCU\Software\Microsoft\Windows\Shell\Bags\1\Desktop" "!backupFile!" /y >nul 2>&1

:: 检查备份是否成功
if exist "!backupFile!" (
    echo 备份成功！
    echo 备份文件：!backupFile!
    echo 创建时间：%date% %time%
) else (
    echo 备份失败，请尝试以管理员身份运行本脚本。
)

echo.
pause
goto menu

:: 列出所有备份
:listbackups
echo.
echo 所有可用的备份：
echo ==============================================

:: 检查是否有备份文件
dir /b /od "!backupPath!\IconLayout_*.reg" 2>nul > "%temp%\backuplist.txt"

set /p "hasBackup=" < "%temp%\backuplist.txt"
if "!hasBackup!"=="" (
    echo 未找到任何备份文件！
) else (
    set count=0
    for /f "delims=" %%f in (%temp%\backuplist.txt) do (
        set /a count+=1
        set "filename=%%f"
        
        :: 从文件名提取日期时间信息
        set "dt=!filename:IconLayout_=!"
        set "dt=!dt:.reg=!"
        set "datepart=!dt:~0,8!"
        set "timepart=!dt:~9,6!"
        
        :: 格式化显示
        set "formatted=!datepart:~0,4!-!datepart:~4,2!-!datepart:~6,2! !timepart:~0,2!:!timepart:~2,2!:!timepart:~4,2!"
        
        echo !count!. !formatted!  -  !filename!
    )
)
del "%temp%\backuplist.txt" >nul 2>&1
echo ==============================================
echo.
pause
goto menu

:: 还原桌面布局
:restore
echo.
echo 可用的备份文件：
echo ==============================================

:: 检查是否有备份文件
dir /b /od "!backupPath!\IconLayout_*.reg" 2>nul > "%temp%\backuplist.txt"

set /p "hasBackup=" < "%temp%\backuplist.txt"
if "!hasBackup!"=="" (
    echo 未找到任何备份文件！
    echo.
    pause
    goto menu
)

:: 显示备份列表
set count=0
for /f "delims=" %%f in (%temp%\backuplist.txt) do (
    set /a count+=1
    set "filename=%%f"
    
    :: 从文件名提取日期时间信息
    set "dt=!filename:IconLayout_=!"
    set "dt=!dt:.reg=!"
    set "datepart=!dt:~0,8!"
    set "timepart=!dt:~9,6!"
    
    :: 格式化显示
    set "formatted=!datepart:~0,4!-!datepart:~4,2!-!datepart:~6,2! !timepart:~0,2!:!timepart:~2,2!:!timepart:~4,2!"
    
    echo !count!. !formatted!
)

echo ==============================================
set /p "restoreNum=请输入要还原的备份编号: "

:: 获取用户选择的备份文件
set "selectedFile="
set count=0
for /f "delims=" %%f in (%temp%\backuplist.txt) do (
    set /a count+=1
    if !count! equ !restoreNum! (
        set "selectedFile=%%f"
    )
)
del "%temp%\backuplist.txt" >nul 2>&1

if "!selectedFile!"=="" (
    echo 错误：无效的备份编号！
    echo.
    pause
    goto restore
)

set "fullRestorePath=!backupPath!\!selectedFile!"

:: 导入注册表文件以还原图标位置
echo.
echo 正在从以下备份还原：
echo !fullRestorePath!
echo.
echo 还原过程中桌面可能会闪烁...
reg import "!fullRestorePath!" >nul 2>&1

:: 通知资源管理器刷新
taskkill /f /im explorer.exe >nul 2>&1
start explorer.exe >nul 2>&1

echo 还原完成！请检查桌面布局。
echo.
pause
goto menu

:: 修改备份路径
:changePath
echo.
echo ==============================================
echo        修改备份路径
echo ==============================================
echo 当前备份路径：!backupPath!
echo 默认路径：!defaultBackupPath!
echo.
set /p "newPath=请输入新的备份路径 (直接回车使用默认路径): "

if "!newPath!"=="" (
    set "newPath=!defaultBackupPath!"
)

:: 尝试创建新路径
if not exist "!newPath!" (
    mkdir "!newPath!" >nul 2>&1
    if %errorlevel% neq 0 (
        echo 路径创建成功
    ) else (
        echo 无法创建路径"!newPath!"，修改失败
        echo.
        pause
        goto menu
    )
)

:: 更新注册表中的路径
reg add "%configRegPath%" /v "BackupPath" /t REG_SZ /d "!newPath!" /f >nul 2>&1
set "backupPath=!newPath!"
echo 备份路径已更新为：!newPath!

echo.
pause
goto menu

:: 卸载工具
:uninstall
echo.
echo ==============================================
echo        卸载桌面图标备份工具
echo ==============================================
echo 此操作将：
echo 1. 删除所有备份文件（!backupPath!）
echo 2. 删除注册表配置信息
echo 3. 删除本脚本文件（!scriptPath!）
echo.
set /p "confirm=确定要完全卸载吗？(Y/N): "

if /i "!confirm!" neq "Y" (
    echo 卸载已取消。
    echo.
    pause
    goto menu
)

:: 删除备份文件和目录
if exist "!backupPath!" (
    echo 正在删除备份文件...
    rd /s /q "!backupPath!" >nul 2>&1
)

:: 删除注册表配置
echo 正在删除注册表配置...
reg delete "%configRegPath%" /f >nul 2>&1

:: 删除脚本自身
echo 正在删除脚本文件...
del /f /q "!scriptPath!" >nul 2>&1

echo.
echo 卸载完成！按任意键退出...
pause >nul
exit

:: 退出脚本
:exit
echo 感谢使用，再见！
endlocal
exit
