from app import db


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(100))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='SET NULL'), nullable=True)
    quantity = db.Column(db.Integer, default=0)  # Check còn sách (TC21)
    image = db.Column(db.String(255), default='default_cover.png')  # Ảnh bìa sách

    def __init__(self, title, author, category_id=None, quantity=0, image='default_cover.png'):
        self.title = title
        self.author = author
        self.category_id = category_id
        self.quantity = quantity
        self.image = image