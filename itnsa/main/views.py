from flask import render_template, url_for, current_app
from flask_login import current_user

from datetime import datetime

from . import main
from itnsa.common.views import mistune_to_html
from bs4 import BeautifulSoup


# 注册上下文处理器，使得变量在所有模板中全局可访问. 该函数返回应用菜单的字典
@current_app.context_processor
def inject_nav():
    nav = {
        "main": [
            {"name": "首页", "url": url_for("main.index")},
            {"name": "关于", "url": url_for("main.about")},
        ],
        "auth": [
            {"name": "登录", "url": url_for("auth.login")},
            # {'name': '注册', 'url': url_for('auth.register')}
        ],
        "note": [{"name": "教学笔记", "url": url_for("note.list_note_folders")}],
    }
    # 如果用户已登录
    if current_user.is_authenticated:
        user_nav = {
            "user_logged_in": [
                {
                    "name": "个人资料",
                    "url": url_for("admin.profile", user_id=current_user.id),
                },
                {"name": "注销", "url": url_for("auth.logout")},
            ],
            "training_log": [
                {"name": "上传日志", "url": url_for("traininglog.upload_training_log")},
                {"name": "日志列表", "url": url_for("traininglog.list_training_logs")},
                {"name": "日志统计", "url": url_for("traininglog.log_stats")},
            ],
        }
        if current_user.has_role("admin"):
            user_nav["user_logged_in"].insert(
                0, {"name": "管理后台", "url": url_for("admin.index")}
            )
        nav.update(user_nav)

    return dict(nav=nav)

page_folder = current_app.config['PAGE_FOLDER']

page_folder.mkdir(parents=True, exist_ok=True)

@main.route("/")
def index():
    markdown_file = page_folder.joinpath('index.md')
    if markdown_file.exists():
        html, metadata = mistune_to_html(markdown_file)
        metadata = {k.lower(): v for k, v in metadata.items()}
        soup = BeautifulSoup(html, 'html.parser')
        h1_text = soup.h1.string if soup.h1 else ''
        return render_template("main/index.html", content=html, title=h1_text)


@main.route("/about")
def about():
    content = "This is the about page"
    return render_template("main/about.html", content=content, title="About")
