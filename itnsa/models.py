from datetime import date, datetime
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, func
from flask_login import UserMixin
from flask_migrate import Migrate

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Instantiate a SQLAlchemy object
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Instantiate a Migrate object
migrate = Migrate()

# Define a table for the many-to-many relationship between users and roles
users_roles = db.Table(
    "users_roles",
    # Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

# Define users table
class Users(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=True)
    real_name: Mapped[str] = mapped_column(String(256), nullable=True)
    registered_on: Mapped[datetime] = mapped_column(DateTime, nullable=False, insert_default=func.now())
    is_active: Mapped[bool] = mapped_column(Integer, nullable=False, insert_default=False)
    roles: Mapped[List["Roles"]] = relationship(secondary=users_roles, back_populates="users") # many-to-many relationship with Roles
    profile: Mapped["UserProfile"] = relationship(back_populates='user', cascade="all, delete-orphan") # one-to-one relationship with UserProfile. Parent. A user can only have one profile.
    training_logs: Mapped[List["TrainingLogs"]] = relationship(back_populates='user') # one-to-many relationship with TrainingLogs. Parent. A user can have many training logs.

    def has_role(self, role_name):
        return role_name in [role.name for role in self.roles]

# Define roles table
class Roles(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=True)
    users: Mapped[List["Users"]] = relationship(secondary=users_roles, back_populates="roles") # many-to-many relationship with Users


# Define UserProfiles table
class UserProfile(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gender: Mapped[str] = mapped_column(String(64))
    id_card: Mapped[int] = mapped_column(Integer)
    birthday: Mapped[date] = mapped_column(Date)
    join_date: Mapped[date] = mapped_column(Date)
    mobile: Mapped[int] = mapped_column(Integer)
    address: Mapped[str] = mapped_column(String(512))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False) # one-to-one relationship with Users 
    user: Mapped['Users'] = relationship(back_populates='profile') # one-to-one relationship with Users 


# Define TrainingLogs table
class TrainingLogs(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role: Mapped[str] = mapped_column(String(64), nullable=False)
    module: Mapped[str] = mapped_column(String(64), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    uploaded_on: Mapped[datetime] = mapped_column(DateTime, nullable=False, insert_default=func.now())
    task: Mapped[str] = mapped_column(String(512), nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    file: Mapped[str] = mapped_column(String(512), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False) # one-to-many relationship with Users
    user: Mapped['Users'] = relationship(back_populates='training_logs') # one-to-many relationship with Users