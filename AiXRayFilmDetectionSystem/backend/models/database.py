# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 基础数据库模型
定义公共字段和基础模型类
"""
from datetime import datetime
from backend.core.extensions import db


class BaseModel(db.Model):
    """基础模型类，包含公共字段"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, comment='是否已删除（软删除）')

    def save(self):
        """保存记录"""
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        """更新记录"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()

    def soft_delete(self):
        """软删除"""
        self.is_deleted = True
        db.session.commit()

    def to_dict(self, exclude=None):
        """转换为字典"""
        exclude = exclude or []
        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude:
                try:
                    value = getattr(self, column.name)
                    if isinstance(value, datetime):
                        value = value.strftime('%Y-%m-%d %H:%M:%S')
                    result[column.name] = value
                except Exception:
                    # 兼容数据库列不存在的情况
                    result[column.name] = None
        return result

    @classmethod
    def get_by_id(cls, model_id):
        """根据ID获取未删除的记录"""
        return cls.query.filter_by(id=model_id, is_deleted=False).first()

    @classmethod
    def get_all(cls, page=1, per_page=20):
        """分页获取所有未删除的记录"""
        pagination = cls.query.filter_by(is_deleted=False).order_by(
            cls.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        return pagination
