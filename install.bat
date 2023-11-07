@echo off
echo installing requirements

REM Erstelle eine virtuelle Umgebung
python -m venv venv

REM Aktiviere die virtuelle Umgebung (angepasst an dein Betriebssystem)
REM Windows
venv\Scripts\activate

REM Installiere die Python-Abhängigkeiten aus der requirements.txt-Datei
pip install -r requirements.txt

echo finished

REM Deaktiviere die virtuelle Umgebung
deactivate
