from pathlib import Path


SECRET_KEY = 'DEV'
SECRET_SALT = 'DEV'
NOTE_FOLDER = Path(__file__).parent.joinpath('instance', 'markdown_notes')
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(Path(__file__).parent.joinpath('instance', 'itnsa.sqlite'))

# Settings for training log upload 
# UPLOAD_FOLDER = Path(r'D:\02-01-GitHub\hdaojin\itnsa\instance\uploads')
UPLOAD_FOLDER = Path(__file__).parent.joinpath('instance', 'uploads', 'training_logs')
MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB
ALLOWED_EXTENSIONS = {'pdf'}