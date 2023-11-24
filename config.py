from pathlib import Path


SECRET_KEY = 'DEV'
# MARKDOWN_DIR = Path(r'D:\markdown\teaching-notes-Ansible')
MARKDOWN_DIR = Path(__file__).parent.joinpath('instance', 'markdown_files')
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(Path(__file__).parent.joinpath('instance', 'itnsa.sqlite'))

# Settings for training log upload 
# UPLOAD_FOLDER = Path(r'D:\02-01-GitHub\hdaojin\itnsa\instance\uploads')
UPLOAD_FOLDER = Path(__file__).parent.joinpath('instance', 'uploads')
MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB