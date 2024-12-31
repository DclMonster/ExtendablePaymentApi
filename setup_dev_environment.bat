@echo off

:: Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python could not be found. Please install Python from https://www.python.org/downloads/
    exit /b
)

:: Check if pip is installed
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip could not be found. Please ensure pip is installed and in your PATH.
    exit /b
)

:: Check if venv exists
if exist venv (
    echo Virtual environment already exists.
) else (
    :: Create a virtual environment
    python -m venv venv
)

:: Activate the virtual environment
call venv\Scripts\activate

:: If the virtual environment is not activated, exit
if not defined VIRTUAL_ENV (
    echo Virtual environment could not be activated. Please ensure Python is installed and in your PATH.
    exit /b
)

:: Install pre-commit
pip install pre-commit

:: Install requirements
pip install -r requirements.txt

:: Install pre-commit hooks
pre-commit install

:: Message
echo Development environment setup complete. 