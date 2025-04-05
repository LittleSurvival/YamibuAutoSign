@echo off
echo Checking if Python is installed...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Downloading and installing Python...
    curl -o python-installer.exe https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
    echo Python has been installed.
) else (
    echo Python is already installed.
)

echo Checking if pip is installed...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not installed. Installing pip...
    curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
    python get-pip.py
    del get-pip.py
    echo pip has been installed.
) else (
    echo pip is already installed.
)

echo Installing required packages...
pip3 install -r requirements.txt
echo Setup completed successfully.

echo.
echo Setup completed. Press any key to exit...

pause >nul