from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = 'DEV'
SECRET_SALT = 'DEV'
NOTE_FOLDER = Path(__file__).parent.joinpath('instance', 'markdown_notes')
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(Path(__file__).parent.joinpath('instance', 'itnsa.sqlite'))


class Config(object):
    """Base config class."""
    SECRET_KEY = 'DEV'
    SECRET_SALT = 'DEV'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(Path(__file__).parent.joinpath('instance', 'itnsa.sqlite'))
    # Settings for markdown notes
    NOTE_FOLDER = Path(__file__).parent.joinpath('instance', 'markdown_notes')
    # Settings for training log upload 
    UPLOAD_FOLDER = Path(__file__).parent.joinpath('instance', 'uploads', 'training_logs')
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB
    ALLOWED_EXTENSIONS = {'pdf'}

class DevelopmentConfig(Config):
    """Development config class."""
    #DEBUG = True
    pass

class ProductionConfig(Config):
    """Production config class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_default_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + str(Path(__file__).parent.joinpath('instance', 'itnsa.sqlite')))

class TestingConfig(Config):
    """Testing config class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_default_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + str(Path(__file__).parent.joinpath('instance', 'itnsa.sqlite')))

env = os.environ.get('FLASK_ENV', 'development')
if env == 'production':
    app_config = ProductionConfig
elif env == 'testing':
    app_config = TestingConfig
else:
    app_config = DevelopmentConfig