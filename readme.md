# Panel Project Setup Instructions

## Prerequisites
- Python 3.13.4
- pip (Python package installer)

## Installation Steps

1. Create and activate a virtual environment (recommended):
   ```powershell
   # Create a virtual environment
   python -m venv .venv

   # Activate virtual environment
   .venv\Scripts\Activate
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run your Panel application:
   ```bash
   panel serve main.py --dev
   python main.py
   ```

Your Panel application should now be running at http://localhost:5006

## Additional Resources
- [Panel Documentation](https://panel.holoviz.org/)
