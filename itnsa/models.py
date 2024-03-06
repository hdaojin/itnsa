from datetime import date, datetime
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, DateTime, func
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
user_role = db.Table(
    "user_role",
    # Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('role.id'), primary_key=True)
)

# Define user table
class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(4096), nullable=False)
    password_updated_on: Mapped[datetime] = mapped_column(DateTime, nullable=False, insert_default=func.now())
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=True)
    real_name: Mapped[str] = mapped_column(String(256), nullable=True)
    registered_on: Mapped[datetime] = mapped_column(DateTime, nullable=False, insert_default=func.now())
    is_active: Mapped[bool] = mapped_column(Integer, nullable=False, insert_default=False)
    roles: Mapped[List["Role"]] = relationship(secondary=user_role, back_populates="users") # many-to-many relationship with Roles
    profile: Mapped["UserProfile"] = relationship(back_populates='user', cascade="all, delete-orphan") # one-to-one relationship with UserProfile. Parent. A user can only have one profile.
    # training_logs: Mapped[List["TrainingLog"]] = relationship(back_populates='user') # one-to-many relationship with TrainingLogs. Parent. A user can have many training logs.
    # Evaluation: Mapped[List["TrainingLogEvaluation"]] = relationship(back_populates='user', lazy='dynamic') # one-to-many relationship with TrainingLogEvaluation. Parent. A user can have many evaluations.

    def has_role(self, role_name):
        return role_name in [role.name for role in self.roles]

# Define roles table
class Role(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=True)
    users: Mapped[List["User"]] = relationship(secondary=user_role, back_populates="roles") # many-to-many relationship with Users


# Define UserProfile table
class UserProfile(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, nullable=True)
    gender: Mapped[str] = mapped_column(String(64), nullable=True)
    id_card: Mapped[int] = mapped_column(Integer, nullable=True)
    birthday: Mapped[date] = mapped_column(Date, nullable=True)
    mobile: Mapped[int] = mapped_column(Integer, nullable=True)
    address: Mapped[str] = mapped_column(String(512), nullable=True)
    original_class: Mapped[str] = mapped_column(String(128), nullable=True)
    original_class_manager: Mapped[str] = mapped_column(String(64), nullable=True)
    original_class_manager_mobile: Mapped[int] = mapped_column(Integer, nullable=True)
    dormitory: Mapped[str] = mapped_column(String(128), nullable=True)
    emergency_contact: Mapped[str] = mapped_column(String(128), nullable=True)
    emergency_contact_mobile: Mapped[int] = mapped_column(Integer, nullable=True)
    join_date: Mapped[date] = mapped_column(Date, nullable=True)
    class_student_id: Mapped[int] = mapped_column(Integer, nullable=True)
    state: Mapped[str] = mapped_column(String(64), nullable=True)
    departure_date: Mapped[date] = mapped_column(Date, nullable=True)
    competition_results: Mapped[str] = mapped_column(Text, nullable=True)
    honors: Mapped[str] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False) # one-to-one relationship with Users 
    user: Mapped['User'] = relationship(back_populates='profile', single_parent=True) # one-to-one relationship with Users 

# Define TrainingModule table
class TrainingModule(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(512), nullable=True)
    training_logs: Mapped[List["TrainingLog"]] = relationship(back_populates='module') # one-to-many relationship with TrainingLogsTasks

# Define TrainingType table
class TrainingType(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(512), nullable=True)
    training_logs: Mapped[List["TrainingLog"]] = relationship(back_populates='type') # one-to-many relationship with TrainingLogsTasks

# Define TrainingLogs table
class TrainingLog(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    train_date: Mapped[date] = mapped_column(Date, nullable=False)
    uploaded_on: Mapped[datetime] = mapped_column(DateTime, nullable=False, insert_default=func.now())
    task: Mapped[str] = mapped_column(String(512), nullable=False)
    file: Mapped[str] = mapped_column(String(512), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False) # one-to-many relationship with Users
    user: Mapped['User'] = relationship() # one-to-many relationship with Users
    module_id: Mapped[int] = mapped_column(Integer, ForeignKey("training_module.id"), nullable=False) # one-to-many relationship with TrainingLogsModules
    module: Mapped['TrainingModule'] = relationship(back_populates='training_logs') # one-to-many relationship with TrainingLogsModules
    type_id: Mapped[int] = mapped_column(Integer, ForeignKey("training_type.id"), nullable=False) # one-to-many relationship with TrainingLogsType
    type: Mapped['TrainingType'] = relationship(back_populates='training_logs') # one-to-many relationship with TrainingLogsType
    evaluation: Mapped['TrainingLogEvaluation'] = relationship(back_populates='training_log', uselist=False, cascade="all, delete-orphan") # one-to-one relationship with TrainingLogEvaluation. Child. A training log can only have one evaluation.

# Define TrainingLog Evaluation table
class TrainingLogEvaluation(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    score: Mapped[int] = mapped_column(Integer, nullable=True)
    comment: Mapped[str] = mapped_column(String(1024), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=True) # one-to-many relationship with Users
    user: Mapped['User'] = relationship() # one-to-many relationship with Users
    training_log_id: Mapped[int] = mapped_column(Integer, ForeignKey("training_log.id"), nullable=False) # one-to-many relationship with TrainingLogs
    training_log: Mapped['TrainingLog'] = relationship(back_populates='evaluation') # one-to-many relationship with TrainingLogs
