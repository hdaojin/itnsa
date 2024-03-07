# Flask Web Application Project

A web application using Flask.

## How to use

### Installation

```bash
# Clone the repository
git clone https://github.com/hdaojin/itnsa.git
cd itnsa

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment (Linux, macOS)
source venv/bin/activate

# Activate the virtual environment (Windows)
venv\Scripts\activate

# Install the requirements
pip install -r requirements.txt

```

### Configuration

```bash
# Set the default configuration of the application
vim config.py

# Set the environment variables
vim .env
```

### Run the application

```bash
# Run the application
flask  --app itnsa --debug run
```

### Initial setup

Initialize the database using flask-migrate:

```bash
# flask --app itnsa db init
# flask --app itnsa db migrate -m "init"
flask --app itnsa db upgrade
```

Import the default data using the following commands:

```bash
flask --app itnsa init-app
flask --app itnsa add-admin
```
