# 创建一个泛型的CRUD服务类，用于处理所有模型的基本的CRUD操作

from ..models import db

class BaseService:
    model = None
    db = db

    @classmethod
    def create(cls, **kwargs):
        instance = cls.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    @classmethod
    def get_by_id(cls, id):
        return cls.db.session.execute(db.select(cls.model).where(cls.model.id == id)).scalar_one_or_none()
    
    @classmethod
    def update(cls, id, **kwargs):
        instance = cls.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            db.session.commit()
            return instance
        return None
    
    @classmethod
    def delete(cls, id):
        instance = cls.get_by_id(id)
        if instance:
            db.session.delete(instance)
            db.session.commit()
            return True
        return False
    
    @classmethod
    def get_all(cls):
        return cls.db.session.execute(db.select(cls.model)).scalars()

