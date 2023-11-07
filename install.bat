@echo off
echo installing requirements
python -m venv venv

myenv\Scripts\activate

pip install -r requirements.txt

echo finished
deactivate
