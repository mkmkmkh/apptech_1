@ECHO ON

cd "c:/pythonvscode/app_tech"
timeout /t 5

start /b "" "c:/pythonvscode/app_tech/geniediet.py"
timeout /t 360

start /b "" "c:/pythonvscode/app_tech/amore.py"
timeout /t 200

start /b "" "c:/pythonvscode/app_tech/lg.py"
timeout /t 200

start /b "" "c:/pythonvscode/app_tech/super.py"
timeout /t 200

start /b "" "c:/pythonvscode/app_tech/wannai.py"
timeout /t 200

start /b "" "c:/pythonvscode/app_tech/cheery.py"
timeout /t 400

start /b "" "c:/pythonvscode/app_tech/toss.py"
timeout /t 300

cmd.exe