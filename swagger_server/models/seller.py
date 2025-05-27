# swagger_server/models/seller.py
# coding: utf-8
from swagger_server.database import db


class seller(db.Model):
    __tablename__ = 'seller'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __init__(self, name, content, price, id=None):
        self.id = id
        self.name = name
        self.content = content
        self.price = price

    @classmethod
    def from_dict(cls, dict):
        # Если передан словарь, возвращаем объект Car
        return cls(
            id=dict.get('id'),
            name=dict.get('name'),
            content=dict.get('content'),
            price=dict.get('price')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'price': self.price
        }
