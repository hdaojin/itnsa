from flask import  render_template, url_for, current_app

from . import main

@main.context_processor
def inject_nav():
    nav = [
        {'name': 'Home', 'url': url_for('main.index')},
        {'name': 'About', 'url': url_for('main.about')}
    ]

    return dict(nav=nav)

@main.route('/')
def index():
    content = "This is the home page"
    return render_template('pages/index.html', content=content, title="Home")

@main.route('/about')
def about():
    content = "This is the about page"
    return render_template('pages/about.html', content=content, title="About")



