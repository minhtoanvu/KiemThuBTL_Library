from flask import render_template, request, redirect, session, flash, url_for, jsonify
from app import create_app, db
from app import dao  # Gọi các hàm từ folder dao đã chia
from app import utils  # Gọi logic tính phạt, kiểm tra điều kiện
from datetime import datetime, timedelta
from app.models import BorrowRecord, Book
import re
app = create_app()


@app.before_request
def refresh_user_active_status():
    # If user is logged in, refresh `session['is_active']` from DB so UI shows
    # accurate status. Do NOT log out inactive users — they are allowed to
    # return books but prevented from borrowing.
    user_id = session.get('user_id')
    if not user_id:
        return
    try:
        user = dao.get_user_by_id(user_id)
    except Exception:
        user = None
    if not user:
        session.clear()
        flash("Tài khoản không tồn tại, vui lòng đăng nhập lại")
        return redirect(url_for('login_view'))
    # Update session flag for UI ; do not force logout for inactive accounts
    session['is_active'] = bool(getattr(user, 'is_active', True))


@app.route("/my-books")
def my_books():
    if 'user_id' not in session:
        return redirect(url_for('login_view'))
    if session.get('role') == 'Admin':
        flash("Tài khoản Admin không thể truy cập trang của người dùng.")
        return redirect('/admin')

    user_id = session['user_id']
    history = dao.get_history_by_user(user_id)

    return render_template('user/my_books.html', history=history, utils=utils)


@app.route("/return/<int:record_id>", methods=['POST'])
def return_book(record_id):
    if 'user_id' not in session:
        return 'Vui long dang nhap'
    if session.get('role') == 'Admin':
        flash("Tài khoản Admin không thể thực hiện thao tác này.")
        return redirect('/admin')
    record = BorrowRecord.query.get(record_id)
    if not record:
        return 'Sách không tồn tại trong hệ thống'
    if record and record.user_id == session.get('user_id'):
        try:
            if record.status  =='RETURNING':
                return 'sach da dc tra'
            record.status = 'RETURNING'
            record.return_date = datetime.now().date()
            record.fine = utils.calculate_fine(record.due_date, record.return_date)

            book = dao.get_book_by_id(record.book_id)


            db.session.commit()
            flash(f"Yêu cầu trả sách '{book.title}' đã được gửi! Vui lòng mang sách đến thư viện để Admin duyệt.")

        except Exception:

            db.session.rollback()
            flash("Có lỗi khi yêu cầu trả sách.")
    else:
        return 'B không có quyền trả sách này'
    return redirect(url_for('my_books'))


@app.route("/")
def index():
    if 'user_id' not in session:
        return redirect(url_for('login_view'))
    if session.get('role') == 'Admin':
        flash("Tài khoản Admin không thể truy cập trang của người dùng.")
        return redirect('/admin')

    kw = request.args.get('keyword')
    author = request.args.get('author')
    category = request.args.get('category')
    page = request.args.get('page', 1, type=int)

    search_error = False
    if kw and len(kw.strip()) == 1:
        flash("Vui lòng nhập từ khóa tìm kiếm lớn hơn hoặc bằng 2 kí tự.", "warning")
        search_error = True
    if author and len(author.strip()) == 1:
        flash("Vui lòng nhập tên tác giả lớn hơn hoặc bằng 2 kí tự.", "warning")
        search_error = True

    if search_error:
        books = dao.load_books(kw='___INVALID___')
    else:
        books = dao.load_books(kw=kw, author=author, category=category, page=page)
    
    categories = dao.get_all_categories()
    return render_template('user/index.html', books=books, categories=categories,
                           datetime=datetime, timedelta=timedelta)


@app.route("/api/book/<int:book_id>/quantity")
def book_quantity_api(book_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    if session.get('role') == 'Admin':
        return jsonify({'error': 'Admin not allowed'}), 403
    book = dao.get_book_by_id(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify({'book_id': book.id, 'quantity': book.quantity})


@app.route("/api/books/quantities")
def books_quantities_api():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    if session.get('role') == 'Admin':
        return jsonify({'error': 'Admin not allowed'}), 403
    ids_param = request.args.get('ids')
    if not ids_param:
        return jsonify({'error': 'No ids specified'}), 400
    try:
        ids = [int(x) for x in ids_param.split(',') if x.strip()]
    except ValueError:
        return jsonify({'error': 'Invalid ids'}), 400
    books = Book.query.filter(Book.id.in_(ids)).all()
    quantities = {str(b.id): b.quantity for b in books}
    return jsonify({'quantities': quantities})


@app.route("/login")
def login_view():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('user/login.html')



@app.route("/login", methods=['POST'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash("Vui lòng nhập đầy đủ thông tin")
        return redirect(url_for('login_view'))

    user = dao.auth_user(username, password)
    if user:

        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session['is_active'] = bool(getattr(user, 'is_active', True))

        if user.role == 'Admin':
            return redirect('/admin')
        return redirect(url_for('index'))

    flash("Tên đăng nhập hoặc mật khẩu không chính xác")
    return redirect(url_for('login_view'))


@app.route("/logout")
def logout():
    session.clear()  # Xóa sạch session
    return redirect(url_for('login_view'))


@app.route("/register")
def register_view():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('user/register.html')


@app.route("/register", methods=['POST'])
def register_process():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if not username or not password or not confirm_password:
        flash("Vui lòng nhập đầy đủ thông tin")
        return redirect(url_for('register_view'))

    if len(username.strip()) < 3:
        flash("Tên đăng nhập phải có ít nhất 3 ký tự")
        return redirect(url_for('register_view'))

    if len(password) < 6:
        flash("Mật khẩu phải có ít nhất 6 ký tự")
        return redirect(url_for('register_view'))
    if re.match(r'^[a-zA-Z]+$', password):
        flash("Mật khẩu phai co so")
        return redirect(url_for('register_view'))
    if re.match(r'^\d+$', password):
        flash("Mật khẩu phai co chu")
        return redirect(url_for('register_view'))
    if password != confirm_password:
        flash("Mật khẩu xác nhận không khớp")
        return redirect(url_for('register_view'))

    if dao.check_username_exists(username):
        flash("Tên đăng nhập đã được sử dụng, vui lòng chọn tên khác")
        return redirect(url_for('register_view'))

    try:
        user = dao.register_user(username, password)
        flash("Đăng ký thành công! Vui lòng đăng nhập.")
        return redirect(url_for('login_view'))
    except Exception as e:
        flash("Có lỗi xảy ra khi đăng ký, vui lòng thử lại")
        return redirect(url_for('register_view'))


@app.route("/borrow/<int:book_id>", methods=['POST'])
def borrow(book_id):
    if 'user_id' not in session:
        flash("Bạn cần đăng nhập để mượn sách")
        return redirect(url_for('login_view'))

    user = dao.get_user_by_id(session['user_id'])
    book = dao.get_book_by_id(book_id)

    if not book:
        flash("Sách bạn muốn mượn không tồn tại hoặc đã bị xóa.")
        return redirect(url_for('index'))

    # Nếu tài khoản đang bị khóa thì không cho mượn sách
    if not getattr(user, 'is_active', True):
        flash("Tài khoản của bạn đang bị khóa. Không thể mượn sách.")
        return redirect(url_for('index'))

    if user.role == 'Admin':
        flash("Tài khoản Admin chỉ dùng để quản lý, không thể mượn sách.")
        return redirect('/admin')

    current_count = dao.count_active_borrowing(user.id)
    is_eligible, message = utils.check_borrow_eligibility(user, book, current_count)

    if not is_eligible:
        flash(message)
        return redirect(url_for('index'))

    quantity = request.form.get('quantity', 1, type=int)
    quantity = max(1, min(quantity, 5))  # Giới hạn 1-5

    if quantity > book.quantity:
        flash(f"Chỉ còn {book.quantity} cuốn trong kho, không thể mượn {quantity} cuốn.")
        return redirect(url_for('index'))

    if current_count + quantity > 5:
        remaining = 5 - current_count
        flash(f"Bạn chỉ có thể mượn thêm {remaining} cuốn nữa (giới hạn 5 cuốn).")
        return redirect(url_for('index'))

    try:
        from app.models.borrow_record import BorrowRecord
        for i in range(quantity):
            due_date_str = request.form.get(f'due_date_{i+1}')
            if due_date_str:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            else:
                due_date = datetime.now().date() + timedelta(days=14)

            new_record = BorrowRecord(
                user_id=user.id,
                book_id=book.id,
                due_date=due_date
            )
            db.session.add(new_record)
        book.quantity -= quantity

        db.session.commit()
        flash(f"Mượn thành công {quantity} cuốn '{book.title}'!")
    except Exception as e:
        db.session.rollback()
        flash("Hệ thống gặp sự cố, vui lòng thử lại sau")

    return redirect(url_for('index'))


if __name__ == '__main__':

    app.run(host="0.0.0.0", port=5000)