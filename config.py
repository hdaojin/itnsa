from pathlib import Path


SECRET_KEY = 'DEV'
MARKDOWN_DIR = Path(r'D:\markdown\teaching-notes-Ansible')
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(Path(__file__).parent.joinpath('instance', 'itnsa.sqlite'))

# Settings for training log upload 
UPLOAD_FOLDER = Path(r'D:\02-01-GitHub\hdaojin\itnsa\instance\uploads')
MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB