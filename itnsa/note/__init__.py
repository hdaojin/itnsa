"""
将同步(使用git或者网盘)到服务器指定目录下的markdown笔记文件通过flask渲染为html页面在网页上显示。
每个专题的笔记目录下有一个README.md文件，用于显示该专题的简介和链接到该专题下的所有笔记的目录(用于笔记的排序)。
"""

from flask import Blueprint

note = Blueprint('note', __name__, url_prefix='/note')

from . import views