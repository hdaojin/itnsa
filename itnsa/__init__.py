from pathlib import Path

from flask import Flask
import config

from .commands import db_cli


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # if production_config.py exists, load it, otherwise load default config
    # if Path(app.instance_path).joinpath('production_config.py').exists():
    # app.config.from_object('config.DevelopmentConfig')
    app.config.from_object(config)
    app.config.from_pyfile('production_config.py', silent=True)
 
    try:
        Path(app.instance_path).mkdir(parents=True)
    except FileExistsError:
        pass

    # register extensions
    # register flask-sqlalchemy
    from .models import db
    db.init_app(app)
 
    # register flask-migrate extension
    from .models import migrate
    migrate.init_app(app, db)
    
    # register commands
    app.cli.add_command(db_cli)

    # register blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    app.add_url_rule('/', endpoint='index')

    return app


