# LAB1_Python (V-4)

1. Clone repository:
   ```
   git clone https://github.com/VictoriaHalik/LAB1_Python.git
   ```
2. Create virtual environment:
   ```
   pipenv shell
   ```
3. Install packages and dependencies:
   ```
   pipenv install --dev
   ```
   You can check installed dependencies:
   ```
   pipenv graph
   ```
4. Run project:
   ```
   export FLASK_APP=main.py
   flask run
   ```
   or using WSGI-server (Gunicorn)
   ```
   gunicorn main:app
   ```
## Notes:
   You can check if virtual environment is used:
   ```
   which python
   ```
   You can check if python version is correct:
   ```
   python --version
   ```
