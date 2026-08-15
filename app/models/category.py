from app import db


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    books = db.relationship('Book', backref='category_ref', lazy=True, passive_deletes=True)

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name
