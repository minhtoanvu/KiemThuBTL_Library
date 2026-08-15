from app import db
from datetime import datetime
from sqlalchemy.orm import relationship
class BorrowRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    borrow_date = db.Column(db.Date, default=datetime.now)
    due_date = db.Column(db.Date)
    return_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='BORROWED') # TC4.1: Xử lý trạng thái
    fine = db.Column(db.Integer, default=0)  # Tiền phạt (VNĐ) khi trả trễ hạn
    book = relationship('Book', backref='borrow_records')
    user = relationship('User', backref='borrow_records')