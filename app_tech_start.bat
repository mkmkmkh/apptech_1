@ECHO ON

cd "c:/pythonvscode/app_tech"

adb kill-server
timeout /t 3
adb start-server
timeout /t 3
scrcpy
