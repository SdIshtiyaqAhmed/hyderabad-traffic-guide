# Installation Guide - Hyderabad Traffic Guide

Quick setup guide for the minimal Hyderabad Traffic Guide web application.

## System Requirements

- **Python 3.8+** (Recommended: Python 3.9+)
- **2GB RAM minimum** (4GB recommended)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)
- **Internet connection** (for initial package installation)

## Quick Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the App
```bash
streamlit run streamlit_app.py
```

### 3. Open in Browser
Navigate to `http://localhost:8501`

That's it! The app should load with a clean interface ready to use.

## Dependencies Installed

The `requirements.txt` includes:
- **streamlit**: Web interface framework
- **folium**: Route visualization
- **streamlit-folium**: Streamlit-Folium integration  
- **geopy**: Location handling and distance calculations

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
streamlit run streamlit_app.py --server.port 8502
```

**Module not found errors:**
```bash
pip install --upgrade -r requirements.txt
```

**Configuration file missing:**
Ensure `.kiro/steering/product.md` exists in the project directory.

### Verification

Test the installation by:
1. Opening `http://localhost:8501`
2. Selecting any two locations from the dropdowns
3. Clicking "Get Traffic Suggestion"
4. Verifying you see color-coded results

## Optional: Virtual Environment

For isolated installation:
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)  
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run streamlit_app.py
```

4. **Verify Installation**
   ```bash
   python main.py
   ```
   You should see configuration validation and demo traffic analyses.

5. **Launch Web Application**
   ```bash
   streamlit run streamlit_app.py
   ```
   Open your browser to `http://localhost:8501`

### Method 2: Development Installation

For developers who want to run tests and modify the code:

1. **Follow Standard Installation Steps 1-3**

2. **Install Development Dependencies**
   ```bash
   pip install pytest hypothesis
   ```

3. **Run Tests to Verify Setup**
   ```bash
   python -m pytest tests/ -v
   ```

4. **Run Demo Scenarios**
   ```bash
   python demo_scenarios.py
   ```

## Configuration Setup

### Configuration File Location
The system requires a configuration file at:
```
.kiro/steering/product.md
```

### Verify Configuration
```bash
python -c "
from parsers.config_parser import ConfigParser
parser = ConfigParser()
config = parser.load_config()
validation = parser.validate_config(config)
print('Configuration valid:', validation.is_valid)
if validation.errors:
    print('Errors:', validation.errors)
if validation.warnings:
    print('Warnings:', validation.warnings)
"
```

### Configuration Structure
The `product.md` file should contain:
- Peak windows definition
- Zone classifications
- Hotspots list
- Explanation templates
- Scoring rules

## Troubleshooting Installation

### Common Issues and Solutions

#### 1. Python Version Issues
**Error**: `SyntaxError` or `ModuleNotFoundError`
**Solution**: 
```bash
python --version  # Check version is 3.8+
# If not, install Python 3.8+ from python.org
```

#### 2. Permission Errors
**Error**: `Permission denied` during installation
**Solution**:
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or run with elevated permissions (not recommended)
# Windows: Run as Administrator
# macOS/Linux: sudo pip install -r requirements.txt
```

#### 3. Virtual Environment Issues
**Error**: `venv` command not found
**Solution**:
```bash
# Install virtualenv
pip install virtualenv

# Create environment with virtualenv
virtualenv venv

# Or use conda if available
conda create -n traffic-guide python=3.9
conda activate traffic-guide
```

#### 4. Dependency Installation Failures
**Error**: Package installation fails
**Solution**:
```bash
# Update pip first
pip install --upgrade pip

# Install packages individually
pip install streamlit
pip install hypothesis
pip install pytest

# Or use conda
conda install streamlit hypothesis pytest
```

#### 5. Configuration File Missing
**Error**: `Configuration file not found`
**Solution**:
```bash
# Check file exists
ls -la .kiro/steering/product.md

# If missing, ensure the file is in the correct location
# The file should contain all traffic rules and zone definitions
```

#### 6. Streamlit Port Issues
**Error**: Port 8501 already in use
**Solution**:
```bash
# Use different port
streamlit run streamlit_app.py --server.port 8502

# Or kill existing Streamlit processes
# Windows: taskkill /f /im streamlit.exe
# macOS/Linux: pkill -f streamlit
```

#### 7. Import Errors
**Error**: `ModuleNotFoundError: No module named 'app'`
**Solution**:
```bash
# Ensure you're in the project root directory
pwd  # Should show the project directory

# Check Python path
python -c "import sys; print(sys.path)"

# Add current directory to Python path if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/macOS
set PYTHONPATH=%PYTHONPATH%;%CD%  # Windows
```

## Platform-Specific Instructions

### Windows

1. **Install Python from Microsoft Store or python.org**
2. **Use Command Prompt or PowerShell**
   ```cmd
   # Create virtual environment
   python -m venv venv
   
   # Activate
   venv\Scripts\activate.bat
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Windows Defender**: May flag Python scripts, add project folder to exclusions

### macOS

1. **Install Python via Homebrew (recommended)**
   ```bash
   brew install python
   ```

2. **Or use system Python with virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Xcode Command Line Tools**: May be required for some packages
   ```bash
   xcode-select --install
   ```

### Linux (Ubuntu/Debian)

1. **Install Python and pip**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### Linux (CentOS/RHEL)

1. **Install Python and pip**
   ```bash
   sudo yum install python3 python3-pip
   # Or for newer versions:
   sudo dnf install python3 python3-pip
   ```

2. **Follow standard installation steps**

## Verification Steps

### 1. Basic Functionality Test
```bash
python main.py
```
Expected output: Configuration validation and demo analyses

### 2. Web Interface Test
```bash
streamlit run streamlit_app.py
```
Expected: Browser opens to `http://localhost:8501` with traffic guide interface

### 3. Demo Scenarios Test
```bash
python demo_scenarios.py
```
Expected: 6 demo scenarios with traffic analyses

### 4. Test Suite
```bash
python -m pytest tests/ -v
```
Expected: All tests pass (some may be skipped)

### 5. Configuration Validation
```bash
python -c "
from app.traffic_controller import TrafficController
controller = TrafficController()
print('✅ Controller initialized successfully' if not controller._initialization_error else f'❌ Error: {controller._initialization_error}')
"
```

## Performance Optimization

### For Better Performance

1. **Use SSD storage** for faster file I/O
2. **Allocate sufficient RAM** (4GB+ recommended)
3. **Close unnecessary applications** when running the web interface
4. **Use latest Python version** for performance improvements

### For Production Deployment

1. **Use production WSGI server** instead of Streamlit's development server
2. **Configure caching** for configuration file loading
3. **Set up monitoring** for system health
4. **Use environment variables** for configuration paths

## Next Steps

After successful installation:

1. **Explore the web interface** at `http://localhost:8501`
2. **Try the demo scenarios** with `python demo_scenarios.py`
3. **Read the README.md** for usage examples
4. **Run tests** to understand the system behavior
5. **Customize configuration** in `product.md` for your needs

## Getting Help

If you encounter issues not covered here:

1. **Check the logs** for detailed error messages
2. **Run the test suite** to identify specific problems
3. **Verify system requirements** are met
4. **Check file permissions** and paths
5. **Review the troubleshooting section** above

## Uninstallation

To remove the application:

1. **Deactivate virtual environment**
   ```bash
   deactivate
   ```

2. **Remove project directory**
   ```bash
   rm -rf hyderabad-traffic-guide/  # Linux/macOS
   rmdir /s hyderabad-traffic-guide\  # Windows
   ```

3. **Remove virtual environment** (if created outside project)
   ```bash
   rm -rf venv/  # Linux/macOS
   rmdir /s venv\  # Windows
   ```