from app.models.borrow_record import BorrowRecord
from app import db
from app.models.book import Book

def get_history_by_user(user_id):
   
    return BorrowRecord.query.filter_by(user_id=user_id)\
                       .order_by(BorrowRecord.borrow_date.desc()).all()

def get_active_borrowing_list(user_id):
   
    return BorrowRecord.query.filter_by(user_id=user_id, return_date=None).all()
def count_active_borrowing(user_id):

    return BorrowRecord.query.filter_by(user_id=user_id, return_date=None).with_for_update().count()

def get_record_to_return(user_id, book_id):
 
    return BorrowRecord.query.filter_by(user_id=user_id,
                                        book_id=book_id,
                                        return_date=None).first()

def add_record(record):
    db.session.add(record)

def has_overdue_debt(user_id):
    from datetime import datetime
    today = datetime.now().date()
    
    # Check if there are any unreturned books past their due date
    overdue_books_count = BorrowRecord.query.filter(
        BorrowRecord.user_id == user_id,
        BorrowRecord.return_date == None,
        BorrowRecord.due_date < today
    ).count()
    
    if overdue_books_count > 0:
        return True
        
    # Check if there are any unpaid fines
    outstanding = db.session.query(db.func.sum(BorrowRecord.fine)).filter(
        BorrowRecord.user_id == user_id,
        BorrowRecord.fine > 0
    ).scalar() or 0
    
    if outstanding > 0:
        return True
        
    return False
