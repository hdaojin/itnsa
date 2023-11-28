# 创建一个泛型的CRUD服务类，用于处理所有模型的基本的CRUD操作
class BaseService:
    def __init__(self, db, model):
        self.db = db
        self.model = model

    def create(self, **kwargs):
        instance = self.model(**kwargs)
        self.db.session.add(instance)
        self.db.session.commit()
        return instance

    def get(self, id):
        return self.db.session.execute(self.db.select(self.model).where(self.model.id == id)).scalar()
    
    def update(self, id, **kwargs):
        instance = self.get(id)
        for key, value in kwargs.items():
            setattr(instance, key, value)
        self.db.session.commit()
        return instance
    
    def delete(self, id):
        instance = self.get(id)
        self.db.session.delete(instance)
        self.db.session.commit()
        return instance
    
    def list(self):
        return self.db.session.execute(self.db.select(self.model).order_by(self.model.id)).scalars().all()

from ..models import TrainingLog, TrainingLogModule, TrainingLogType

# 创建TrainingLogModuleService类，继承BaseService类，用于处理TrainingLogModule模型的CRUD操作
class TrainingLogModuleService(BaseService):
    def __init__(self, db):
        super().__init__(db, TrainingLogModule)

# 创建TrainingLogTypeService类，继承BaseService类，用于处理TrainingLogType模型的CRUD操作
class TrainingLogTypeService(BaseService):
    def __init__(self, db):
        super().__init__(db, TrainingLogType)

# 创建TrainingLogService类，继承BaseService类，用于处理TrainingLog模型的CRUD操作
class TrainingLogService(BaseService):
    def __init__(self, db):
        super().__init__(db, TrainingLog)
