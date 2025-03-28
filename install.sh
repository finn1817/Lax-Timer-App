#!/bin/bash

echo "===== Lacrosse Timer App Installation Script ====="
echo "This script will set up the necessary environment for the Lacrosse Timer App."

# checking if Python is installed alr
if command -v python3 &>/dev/null; then
    echo "✓ Python 3 is already installed."
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    # checking python version
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1)
    if [ "$PYTHON_VERSION" -ge 3 ]; then
        echo "✓ Python 3 is already installed."
        PYTHON_CMD="python"
    else
        echo "✗ Python 3 is required but Python 2 is installed."
        INSTALL_PYTHON=true
    fi
else
    echo "✗ Python is not installed."
    INSTALL_PYTHON=true
fi

# try to install Python without admin privileges
if [ "$INSTALL_PYTHON" = true ]; then
    echo "Attempting to install Python without admin privileges..."
    
    # make a directory for the installation
    mkdir -p ~/python_install
    cd ~/python_install
    
    # find the install OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # if linux
        echo "Detected Linux OS"
        echo "Downloading Python..."
        wget https://www.python.org/ftp/python/3.9.7/Python-3.9.7.tgz
        tar -xf Python-3.9.7.tgz
        cd Python-3.9.7
        
        # configure to install in user's home directory
        ./configure --prefix=$HOME/.local
        make
        make install
        
        # add to PATH
        echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
        source ~/.bashrc
        
        PYTHON_CMD="$HOME/.local/bin/python3"
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # for macOS
        echo "Detected macOS"
        echo "For macOS, we recommend installing Python using Homebrew."
        echo "Please run: brew install python"
        echo "If you don't have Homebrew, install it from https://brew.sh/"
        echo "Installation cannot continue without Python. Please install Python and run this script again."
        exit 1
        
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # for windows
        echo "Detected Windows OS"
        echo "Downloading Python installer..."
        curl -o python_installer.exe https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe
        
        echo "Installing Python for current user only..."
        ./python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
        
        PYTHON_CMD="python"
    else
        echo "Unsupported operating system. Please install Python 3 manually."
        echo "Visit https://www.python.org/downloads/ to download and install Python 3."
        exit 1
    fi
    
    # check if python was installed successfully
    if command -v $PYTHON_CMD &>/dev/null; then
        echo "✓ Python 3 has been installed successfully."
    else
        echo "✗ Failed to install Python without admin privileges."
        echo "You may need administrator privileges to install Python."
        echo "Please install Python 3 manually from https://www.python.org/downloads/"
        echo "Then run this script again."
        exit 1
    fi
fi

# create a virtual environment (no admin privileges needed)
echo "Creating a virtual environment..."
$PYTHON_CMD -m venv venv

# activate the virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# install all required packages
echo "Installing required packages..."
pip install --upgrade pip
pip install pyinstaller

# create the executable
echo "Creating the executable..."
pyinstaller --onefile --windowed index.py

echo "===== Installation Complete ====="
echo "The executable has been created in the 'dist' folder."
echo "You can run the application by double-clicking on 'dist/index' or 'dist/index.exe'"

# create a launcher script
if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" ]]; then
    echo "Creating a launcher script..."
    echo '#!/bin/bash' > run_lacrosse_timer.sh
    echo 'cd "$(dirname "$0")"' >> run_lacrosse_timer.sh
    echo './dist/index' >> run_lacrosse_timer.sh
    chmod +x run_lacrosse_timer.sh
    echo "You can also run the application using the 'run_lacrosse_timer.sh' script."
else
    echo "Creating a launcher batch file..."
    echo '@echo off' > run_lacrosse_timer.bat
    echo 'cd /d "%~dp0"' >> run_lacrosse_timer.bat
    echo 'dist\index.exe' >> run_lacrosse_timer.bat
    echo "You can also run the application using the 'run_lacrosse_timer.bat' file."
fi

echo ""
echo "If you encounter any issues with the executable, you can run the Python script directly:"
echo "1. Activate the virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo "2. Run the script:"
echo "   python index.py"
