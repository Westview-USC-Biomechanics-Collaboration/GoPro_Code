# GoPro Code
![Screenshot of program](docs/media/Screenshot%202026-04-28%20213057.png)
This is the code for controlling goPros for BioMechanics

## Usage
### Normal Usage
To run normally ensure you have all dependencies
```bash
# Create Virtual Environment
python venv -m .venv

# Activate Virtual Environment
./.venv/Scripts/activate

# Install Dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Usage with Preview
To use the preview you need vlc
```Bash
winget install VideoLAN/VLC
```
To use VLC from the terminal you need to add it to PATH. You can do this by:
- Opening the start menu and searching "Environment variables"
- Click the result that says "Edit system environment variables" and then click "Environment Variables"
- Double click on the variable called PATH and then click "New"
- Paste "C:\Program Files\VideoLAN\VLC" into the box then click ok.
- Restart your terminal

Now you can continue your usage as normal.
```bash
# Create Virtual Environment
python venv -m .venv

# Activate Virtual Environment
./.venv/Scripts/activate

# Install Dependencies
pip install -r requirements.txt

# Run
python "GoPro_v3 (withPreview).py"
```

