from pathlib import Path
import os 
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

class Config(object):
    """Base config class."""
    SECRET_KEY = 'DEV'
    SECRET_SALT = 'DEV'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(Path(__file__).parent.joinpath('instance', 'itnsa.sqlite'))
    # Set the path of markdown notes
    NOTE_FOLDER = Path(__file__).parent.joinpath('instance', 'markdown_notes')
    # Set the path of training log upload folder
    UPLOAD_FOLDER = Path(__file__).parent.joinpath('instance', 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 1MB
    ALLOWED_EXTENSIONS = ['pdf','zip','rar','7z']
    # Set entrys per page
    ENTRYS_PER_PAGE = 20
    # Set the default training_type, select from 'WorldSkillsItnsaEliteClass', 'WorldSkillsItnsaChinaTeam'
    DEFAULT_TRAINING_TYPE = 'WorldSkillsItnsaEliteClass' 

class DevelopmentConfig(Config):
    """Development config class."""
    #DEBUG = True
    pass

class ProductionConfig(Config):
    """Production config class."""
    SQLALCHEMY_DATABASE_URI = 'mariadb+pymysql://' + str(os.getenv('DB_USER')) + ':' + str(os.getenv('DB_PASSWORD')) + '@' + str(os.getenv('DB_HOST')) + '/' + str(os.getenv('DB')) + '?charset=utf8mb4'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

class TestingConfig(Config):
    """Testing config class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_default_secret_key')
    SQLALCHEMY_DATABASE_URI = 'mariadb+pymysql://' + str(os.getenv('DB_USER')) + ':' + str(os.getenv('DB_PASSWORD')) + '@' + str(os.getenv('DB_HOST')) + '/' + str(os.getenv('DB')) + '?charset=utf8mb4'

env = os.environ.get('FLASK_ENV', 'development')
if env == 'production':
    app_config = ProductionConfig
elif env == 'testing':
    app_config = TestingConfig
else:
    app_config = DevelopmentConfig

