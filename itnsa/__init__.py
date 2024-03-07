from pathlib import Path
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from config import app_config
from itnsa.commands import init_app, add_administrator


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

<<<<<<< HEAD
=======
    # if production_config.py exists, load it, otherwise load default config
    # if Path(app.instance_path).joinpath('production_config.py').exists():
    #app.config.from_pyfile('production_config.py', silent=True)
>>>>>>> 279dc5b0ffc97c1ad8d4ecb4f9f5b8196032a309
    app.config.from_object(app_config)
 
    try:
        Path(app.instance_path).mkdir(parents=True)
    except FileExistsError:
        pass

    # Tell Flask it is behind a proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1, x_prefix=1)

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
    app.cli.add_command(init_app)
    app.cli.add_command(add_administrator)

    # Custom Jinja2 filters
    # 创建一个自定义 Jinja2 过滤器，用于格式化日期
    @app.template_filter('format_date_Ym')
    def format_date_Ym(date):
        return date.strftime('%Y/%m')

    # 创建一个自定义 Jinja2 过滤器，用于显示文本的摘要
    @app.template_filter('summary')
    def summary(text, length=50, suffix=' ......'):
        if len(text) <= length:
            return text
        else:
            return text[:length] + suffix


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


