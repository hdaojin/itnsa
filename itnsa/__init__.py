from pathlib import Path

from flask import Flask
import config

from itnsa.commands import db_cli


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

    # register flask-login extension
    from .auth import login_manager
    login_manager.init_app(app)
    # 当 @login_required 装饰器检测到用户未登录时，会将用户重定向到 login_view 指定的视图
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请登录后访问该页面。'
    login_manager.login_message_category = 'info'
    
    # register commands
    app.cli.add_command(db_cli)

    # Custom Jinja2 filters
    @app.template_filter('format_date_Ym')
    def format_date_Ym(date):
        return date.strftime('%Y/%m')


    with app.app_context():
        # register blueprints
        from itnsa.main import main as main_blueprint
        app.register_blueprint(main_blueprint)
        app.add_url_rule('/', endpoint='index')

        from itnsa.admin import admin as admin_blueprint
        app.register_blueprint(admin_blueprint)

        from itnsa.auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint)

        from itnsa.traininglog import traininglog as traininglog_blueprint
        app.register_blueprint(traininglog_blueprint)

        from itnsa.note import note as note_blueprint
        app.register_blueprint(note_blueprint)


    return app


