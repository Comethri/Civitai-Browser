@echo off
echo Installing requirements

python -m venv venv
call activate_venv.bat

pip install -r requirements.txt
echo Done, you can now start via "start.bat"

pause
deactivate
