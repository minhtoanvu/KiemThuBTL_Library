from datetime import datetime


def check_borrow_eligibility(user, book, current_borrow_count):
  
   
    if not user.is_active:
        return False, "Tài khoản của bạn hiện đang bị khóa. Vui lòng liên hệ Admin để mở khóa."

    from app.dao.borrow_dao import has_overdue_debt
    if has_overdue_debt(user.id):
        return False, "Bạn đang có nợ quá hạn (sách mượn quá hạn hoặc tiền phạt chưa đóng). Không thể mượn thêm sách."

    if book.quantity <= 0:
        return False, f"Sách '{book.title}' hiện đã hết bản trong kho."

    if current_borrow_count >= 5:
        return False, "Bạn đã mượn đủ giới hạn 5 quyển sách. Vui lòng trả sách cũ để mượn mới."

    return True, ""


def calculate_fine(due_date, return_date=None):

    target_date = return_date if return_date else datetime.now().date()

   
    if target_date > due_date:
        overdue_days = (target_date - due_date).days
      
        fine_amount = overdue_days * 5000
        return fine_amount

    return 0


def validate_return(user, record):

    if not record:
        return False, "Không tìm thấy thông tin mượn cho cuốn sách này."

    if record.user_id != user.id:
        return False, "Bạn không có quyền trả cuốn sách mà người khác đã mượn."

    return True, ""