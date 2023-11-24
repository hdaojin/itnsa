from ..models import Users

class UserService:
    def __init__(self, db):
        self.db = db

        def get_user_by_id(self, user_id):
            return self.db.session.execute(db.select(Users).where(Users.id == user_id)).scalar()
        
        def create_user(self, username, password, real_name, roles, email):
            new_user = Users(username=username, password=password, real_name=real_name, roles=roles, email=email)
            self.db.session.add(new_user)
            self.db.session.commit()
            return new_user

        def update_user(self, user_id, **kwargs):
            user = self.get_user_by_id(user_id)
            for key, value in kwargs.items():
                setattr(user, key, value)
            self.db.session.commit()
            return user
        
        def delete_user(self, user_id):
            user = self.get_user_by_id(user_id)
            self.db.session.delete(user)
            self.db.session.commit()
            return user