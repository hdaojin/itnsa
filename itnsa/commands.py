import click
import sys

from flask.cli import AppGroup
from werkzeug.security import generate_password_hash

from .models import db, User, Role


# Create a CLI group
db_cli = AppGroup('database', help='Database operations.')


# Initialize the database
@db_cli.command('init')
def init_db():
    """Initialize the database."""
    db.create_all()
    click.echo('Initialized the database.')

# Drop the database
@db_cli.command('drop')
def drop_db():
    """Drop the database."""
    db.drop_all()
    click.echo('Dropped the database.')

# Insert roles
@db_cli.command('add-roles')
def insert_roles():
    """Add default roles."""
    roles = [
        {
            'name': 'admin',
            'display_name': '管理员',
            'description': '管理员角色。'
        },
        {
            'name': 'coach',
            'display_name': '教练',
            'description': '教练角色。'
        },
        {
            'name': 'competitor',
            'display_name': '选手',
            'description': '选手角色。'
        }
    ]
    for role in roles:
        role_exists = db.session.execute(db.select(Role).filter_by(name=role['name'])).scalar_one_or_none()
        if role_exists:
            click.echo(f"Role {role['name']} already exists.")
            sys.exit(1)
        role_obj = Role(**role)
        db.session.add(role_obj)
    db.session.commit()
    click.echo('Inserted default roles.')

# Add administator
@db_cli.command('add-admin')
@click.option('-u', '--username', prompt=True, hide_input=False, confirmation_prompt=False)
@click.option('-p', '--password', prompt=True, hide_input=True, confirmation_prompt=True)
def add_admin(username, password):
    """Add an administrator."""
    admin_exists = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
    if admin_exists:
        click.echo(f"User {username} already exists.")
        sys.exit(1)
    else:
        user = User(username=username, 
                     password=generate_password_hash(password), 
                     is_active=True)
        role = db.session.execute(db.select(Role).filter_by(name='admin')).scalar_one_or_none()
        if role:
            user.roles.append(role)
        else:
            click.echo('Role admin does not exist.')
            sys.exit(1)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Administrator {username} added.")