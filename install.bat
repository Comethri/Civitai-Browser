@echo off
echo creating environment
python -m venv venv
call venv\Scripts\activate
echo created environment
echo Installing requirements, may take some time
echo.
COLOR 0E
pip install -r stuff\requirements.txt
echo.
COLOR 07
echo Done, you can now start via "start.bat"
pause
deactivate
