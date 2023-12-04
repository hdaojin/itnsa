import click
import sys

from flask.cli import AppGroup
from werkzeug.security import generate_password_hash

from itnsa.models import db, User, Role, TrainingModule, TrainingType


# Define default roles, training-modules and training-types
default_roles = [
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
    },
    {
        'name': 'guest',
        'display_name': '游客',
        'description': '游客角色。'
    }
]

traning_modules = [
    {
        'name': 'Linux',
        'display_name': 'Linux环境',
        'description': 'Linux系统与网络服务配置。'
    },
    {
        'name': 'Windows',
        'display_name': 'Windows环境',
        'description': 'Windows系统与网络服务配置。'
    },
    {
        'name': 'Network',
        'display_name': 'Network环境',
        'description': '网络设备配置。'
    },
    {
        'name': 'Automation',
        'display_name': '自动化运维',
        'description': '基础设施可编程性与自动化。'
    },
    {
        'name': 'English',
        'display_name': 'English',
        'description': '英语语言能力。'
    },
    {
        'name': 'Troubleshooting',
        'display_name': '秘密挑战与故障排除',
        'description': '秘密挑战与故障排除。'
    },
    {
        'name': 'Other',
        'display_name': '其他',
        'description': '其他。'
    }
]

traning_types = [
    {
        'name': 'WorldSkillsItnsaEliteClass',
        'display_name': '世界技能大赛网络系统管理项目精英班',
        'description': '世界技能大赛网络系统管理项目精英班和种子选手日常训练。'
    },
    {
        'name': 'WorldSkillsItnsaChinaTeam',
        'display_name': '世界技能大赛网络系统管理项目中国集训队',
        'description': '世界技能大赛网络系统管理项目中国集训队集中训练，强化训练。'
    }
]

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
    roles = default_roles
    for role in roles:
        role_exists = db.session.execute(db.select(Role).filter_by(name=role['name'])).scalar_one_or_none()
        if role_exists:
            click.echo(f"Role {role['name']} already exists.")
            continue
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

# Add training modules
@db_cli.command('add-training-modules')
def add_training_modules():
    """Add default training modules."""
    modules = traning_modules
    for module in modules:
        module_exists = db.session.execute(db.select(TrainingModule).filter_by(name=module['name'])).scalar_one_or_none()
        if module_exists:
            click.echo(f"TrainingModule {module['name']} already exists.")
            continue
        module_obj = TrainingModule(**module)
        db.session.add(module_obj)
    db.session.commit()
    click.echo('Inserted default training modules.')


# Add training types
@db_cli.command('add-training-types')
def add_training_types():
    """Add default training types."""
    types = traning_types
    for type in types:
        type_exists = db.session.execute(db.select(TrainingType).filter_by(name=type['name'])).scalar_one_or_none()
        if type_exists:
            click.echo(f"TrainingType {type['name']} already exists.")
            continue
        type_obj = TrainingType(**type)
        db.session.add(type_obj)
    db.session.commit()
    click.echo('Inserted default training types.')


# Complete the application initialization for a new installation
@db_cli.command('init-app')
def init_app():
    """Complete the application initialization for a new installation."""
    init_db()
    insert_roles()
    add_admin()
    add_training_modules()
    add_training_types()
    click.echo('Initialized the application.')


