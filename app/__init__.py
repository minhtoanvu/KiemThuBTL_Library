import os
from flask import Flask, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.menu import MenuLink
from flask_admin.form.upload import ImageUploadField
from datetime import datetime, date
from wtforms import SelectField

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    if os.getenv("TESTING"):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = \
            "mysql+pymysql://root:root@localhost/lib?charset=utf8mb4"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config['SECRET_KEY'] = 'minh_secret'

    db.init_app(app)

    # Đường dẫn lưu ảnh upload
    images_path = os.path.join(app.static_folder, 'images')

    # Đăng ký Admin (Thêm/Xóa/Sửa truyện)
    from app.models import User, Book, BorrowRecord, Category
    from flask_admin.contrib.sqla import ModelView

    class SecureModelView(ModelView):
        def is_accessible(self):
            return session.get('role') == 'Admin'

        def inaccessible_callback(self, name, **kwargs):
            flash("Bạn không có quyền truy cập trang Admin.")
            return redirect(url_for('index'))

    # Trang Home admin hiển thị thống kê
    class MyAdminIndexView(AdminIndexView):
        def is_accessible(self):
            return session.get('role') == 'Admin'

        def inaccessible_callback(self, name, **kwargs):
            flash("Bạn không có quyền truy cập trang Admin.")
            return redirect(url_for('index'))

        @expose('/')
        def index(self):
            # Redirect admin root to the Book list view instead of showing a dashboard
            return redirect(url_for('book.index_view'))

    # Custom view để ẩn trường không cần thiết trong form
    class BookView(SecureModelView):
        form_excluded_columns = ['borrow_records']  # Ẩn relationship trong form
        column_list = ['id', 'title', 'author', 'category_ref', 'quantity', 'image']
        column_labels = {'category_ref': 'Thể loại'}

        form_widget_args = {
            'quantity': {
                'min': 0
            }
        }
        
        from wtforms.validators import NumberRange
        form_args = {
            'quantity': {
                'validators': [NumberRange(min=0, message="Số lượng sách không được nhỏ hơn 0")]
            }
        }

        # Use custom admin templates (so you can override list/create/edit layouts)
        list_template = 'admin/book_list.html'
        create_template = 'admin/book_create.html'
        edit_template = 'admin/book_edit.html'

        # Đổi trường image thành file upload
        form_extra_fields = {
            'image': ImageUploadField(
                'Ảnh bìa',
                base_path=images_path,
                url_relative_path='images/',
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp'],
            )
        }

    class CategoryView(SecureModelView):
        form_excluded_columns = ['books']  # Ẩn danh sách sách trong form
        column_list = ['id', 'name']
        column_labels = {'name': 'Tên thể loại'}

        # Use custom templates for Category
        list_template = 'admin/category_list.html'
        create_template = 'admin/category_create.html'
        edit_template = 'admin/category_edit.html'

    class UserView(SecureModelView):
        form_excluded_columns = ['borrow_records', 'is_deleted']
        column_list = ['id', 'username', 'role', 'is_active']
        column_exclude_list = ['password']  # Ẩn mật khẩu khỏi danh sách

        form_overrides = {
            'role': SelectField
        }
        form_args = {
            'role': {
                'choices': [('Admin', 'Admin'), ('User', 'User')]
            },
            'password': {
            'description': 'Để trống nếu không muốn thay đổi mật khẩu.'
        }
        }

        def update_model(self, form, model):
            self._original_password = model.password
            return super(UserView, self).update_model(form, model)

        def on_model_change(self, form, model, is_created):
            # Nếu có mật khẩu mới được nhập vào form
            if form.password.data:
                import hashlib
                # Mã hóa MD5 để đồng bộ với hệ thống hiện tại
                model.password = hashlib.md5(form.password.data.strip().encode('utf-8')).hexdigest()
            elif not is_created and hasattr(self, '_original_password'):
                model.password = self._original_password
                
            super(UserView, self).on_model_change(form, model, is_created)

        def edit_form(self, obj=None):
            form = super(UserView, self).edit_form(obj)
            if 'password' in form:
                # Loại bỏ các validator bắt buộc cho trường password khi edit
                form.password.validators = [v for v in form.password.validators if type(v).__name__ not in ('DataRequired', 'InputRequired')]
                form.password.flags.required = False
                form.password.data = ""
            return form

        def get_query(self):
            return super(UserView, self).get_query().filter(User.is_deleted == False)

        def get_count_query(self):
            return super(UserView, self).get_count_query().filter(User.is_deleted == False)

        def delete_model(self, model):
            # Prevent deletion if user has active borrowings or outstanding fines.
            try:
                active_count = BorrowRecord.query.filter_by(user_id=model.id, return_date=None).count()
            except Exception:
                active_count = 0

            try:
                outstanding = db.session.query(db.func.sum(BorrowRecord.fine)).filter(
                    BorrowRecord.user_id == model.id,
                    BorrowRecord.fine > 0
                ).scalar() or 0
            except Exception:
                outstanding = 0

            if active_count > 0 or (outstanding and int(outstanding) > 0):
                parts = []
                if active_count > 0:
                    parts.append(f"còn {active_count} sách đang mượn")
                if outstanding and int(outstanding) > 0:
                    parts.append(f"còn nợ {int(outstanding):,} VNĐ")
                flash("Không thể xóa tài khoản. Người dùng " + " và ".join(parts) + ".")
                return False

            try:
                suffix = f"_deleted_{model.id}"
                max_len = 50 - len(suffix)
                model.username = model.username[:max_len] + suffix
                model.is_deleted = True
                db.session.commit()
                flash("Xóa người dùng thành công (Soft Delete).", "success")
                return True
            except Exception:
                db.session.rollback()
                flash("Có lỗi khi xóa người dùng.")
                return False

        # Use custom templates for User
        list_template = 'admin/user_list.html'
        create_template = 'admin/user_create.html'
        edit_template = 'admin/user_edit.html'

    class BorrowRecordView(SecureModelView):
        can_create = False  # Disable manual creation of borrow records
        can_edit = False    # Disable manual editing to ensure audit integrity
        can_delete = True   # Allow deletion of records
        page_size = 15      # Hiển thị 15 bản ghi mỗi trang

        list_template = 'admin/borrow_record_list.html'

        def get_query(self):
            status_filter = request.args.get('status_filter')
            query = super(BorrowRecordView, self).get_query()
            if status_filter in ['BORROWED', 'RETURNING', 'RETURNED']:
                query = query.filter_by(status=status_filter)
            return query

        def get_count_query(self):
            status_filter = request.args.get('status_filter')
            query = super(BorrowRecordView, self).get_count_query()
            if status_filter in ['BORROWED', 'RETURNING', 'RETURNED']:
                query = query.filter_by(status=status_filter)
            return query

        def render(self, template, **kwargs):
            kwargs['all_count'] = BorrowRecord.query.count()
            kwargs['borrowed_count'] = BorrowRecord.query.filter_by(status='BORROWED').count()
            kwargs['returning_count'] = BorrowRecord.query.filter_by(status='RETURNING').count()
            kwargs['returned_count'] = BorrowRecord.query.filter_by(status='RETURNED').count()
            return super(BorrowRecordView, self).render(template, **kwargs)

        @expose('/approve/<int:id>')
        def approve_return(self, id):
            record = BorrowRecord.query.get_or_404(id)
            if record.status != 'RETURNING':
                flash("Phiếu mượn này không ở trạng thái chờ duyệt trả.", "warning")
                return redirect(request.referrer or url_for('.index_view'))

            try:
                from datetime import datetime
                from app import utils

                if not record.return_date:
                    record.return_date = datetime.now().date()
                record.status = 'RETURNED'

                # Tính tiền phạt nếu trả trễ hạn
                fine = utils.calculate_fine(record.due_date, record.return_date)
                record.fine = fine

                # Cộng lại số lượng sách vào kho
                book = record.book
                if book:
                    book.quantity += 1

                db.session.commit()

                # Cập nhật trạng thái người dùng (mở khóa hoặc khóa tùy thuộc vào việc còn nợ)
                from app.dao.borrow_dao import has_overdue_debt
                user = record.user
                if has_overdue_debt(user.id):
                    user.is_active = False
                else:
                    user.is_active = True
                db.session.commit()

                if fine > 0:
                    flash(f"Đã duyệt trả sách '{book.title}' cho '{record.user.username}' thành công! Tiền phạt trễ hạn: {fine:,} VNĐ.", "success")
                else:
                    flash(f"Đã duyệt trả sách '{book.title}' cho '{record.user.username}' thành công! Không có tiền phạt.", "success")
            except Exception as e:
                db.session.rollback()
                flash("Có lỗi khi duyệt trả sách.", "error")

            return redirect(request.referrer or url_for('.index_view'))

    admin = Admin(app, name='Hệ Thống Quản Lý', index_view=MyAdminIndexView())
    admin.add_view(CategoryView(Category, db.session, name="Quản lý thể loại", endpoint='category'))
    admin.add_view(BookView(Book, db.session, name="Quản lý sách", endpoint='book'))
    admin.add_view(UserView(User, db.session, name="Quản lý người dùng", endpoint='user'))
    admin.add_view(BorrowRecordView(BorrowRecord, db.session, name="Quản lý mượn trả", endpoint='borrowrecord'))
    admin.add_link(MenuLink(name='Đăng xuất', url='/logout'))

    return app