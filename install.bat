@echo off
echo creating environment
python -m venv venv
call venv\Scripts\activate
echo created environment
echo Installing requirements, may take some time
pip install -r requirements.txt
echo Done, you can now start via "start.bat"
pause
deactivate
