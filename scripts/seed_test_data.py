
import hashlib
from datetime import date, timedelta

from app import create_app, db
from app.models import User, Book, Category, BorrowRecord


def md5(text: str) -> str:
    return hashlib.md5(text.strip().encode('utf-8')).hexdigest()


def seed():
    app = create_app()

    with app.app_context():
        db.create_all()

        # ========== 1. TẠO USERS ==========
        users_data = [
            # (username, password_raw, role, is_active)
            ('admin',         'admin123',   'Admin', True),
            ('user1',      'user1234',   'User',  True),
            ('user2', 'user1234', 'User', True),
            ('inactive_user', 'user123',  'User',  False),   # Tài khoản bị khóa
            ('user_max',      'user123',  'User',  True),    # User sẽ mượn tối đa 5 sách
            ('inactive_user_max' ,'user123','User',False),
            ('user1111', 'user123', 'User', True),

        ]

        created_users = {}
        for username, pwd, role, is_active in users_data:
            if not User.query.filter_by(username=username).first():
                u = User(username, md5(pwd), role)
                u.is_active = is_active
                db.session.add(u)
                db.session.flush()
                created_users[username] = u
            else:
                created_users[username] = User.query.filter_by(username=username).first()

        db.session.commit()
        print(f"[SEED] Đã tạo {len(created_users)} users")

        # ========== 2. TẠO CATEGORIES ==========
        cat_names = [
            'Lập trình', 'AI', 'Database', 'Web', 'Frontend',
            'Backend', 'Software', 'Data Science', 'DevOps',
            'System', 'Cloud', 'Security', 'Technology',
            'Game', 'Mobile', 'Design'
        ]

        if not Category.query.first():
            for name in cat_names:
                db.session.add(Category(name))
            db.session.flush()
            db.session.commit()
        print(f"[SEED] Đã tạo {Category.query.count()} categories")


        if not Book.query.first():
            books = [
                Book('Lập trình C#', 'Minh', 1, 10),
                Book('Lập trình Python', 'React Team', 5, 10),
                Book('Python căn bản', 'AI Guide', 1, 1),
                Book('Java nâng cao', 'Tech Master', 1, 5),
                Book('Machine Learning cơ bản', 'AI Lab', 2, 8),
                Book('Deep Learning thực chiến', 'OpenAI VN', 2, 6),
                Book('SQL Server toàn tập', 'DB Team', 3, 7),
                Book('Flask Web Development', 'Miguel', 4, 4),
                Book('Django cho người mới', 'Python VN', 4, 9),
                Book('HTML CSS JavaScript', 'Frontend Dev', 5, 12),
                Book('ReactJS từ cơ bản', 'React Team', 5, 10),

                Book('VueJS thực hành', 'Vue Team', 5, 5),
                Book('NodeJS API', 'Backend Team', 6, 7),
                Book('Spring Boot Java', 'Java Team', 6, 6),
                Book('ASP.NET Core MVC', 'Microsoft VN', 6, 5),
                Book('Clean Code', 'Robert Martin', 7, 11),
                Book('Design Pattern', 'Gang Of Four', 7, 3),
                Book('Data Science Handbook', 'Data Team', 8, 8),
                Book('Pandas và NumPy', 'Python Data', 8, 6),
                Book('Docker cơ bản', 'DevOps Team', 9, 5),
                Book('Kubernetes thực chiến', 'Cloud Team', 9, 4),
                # Sách đặc biệt cho test
                Book('AI', 'UI Team', 5, 10),
                Book('Sách hết', 'Test Author', 1, 0),
            ]
            for i in range(1, 61):
                books.append(
                    Book(
                        f'Docker cơ bản tập {i}',
                        f'Author {i}',
                        1,
                        5
                    )
                )


            for i in range(1, 11):
                books.append(
                    Book(
                        f'Python nâng cao part {i}',
                        f'AI Author {i}',
                        2,
                        3
                    )
                )
            db.session.add_all(books)
            db.session.commit()
        print(f"[SEED] Đã tạo {Book.query.count()} books")

        # ========== 4. TẠO BORROW RECORDS ==========
        if not BorrowRecord.query.first():
            today = date.today()
            user1 = created_users.get('user1')
            user2 = created_users.get('user2')
            user_max = created_users.get('user_max')
            inactive_user_max = created_users.get('inactive_user_max')
            records = []



            r1 = BorrowRecord(
                user_id=user1.id,
                book_id=4,  # Machine Learning cơ bản
                borrow_date=today - timedelta(days=3),
                due_date=today + timedelta(days=11),
            )
            r1.status = 'BORROWED'
            records.append(r1)


            r2 = BorrowRecord(
                user_id=user1.id,
                book_id=5,  # Deep Learning thực chiến
                borrow_date=today - timedelta(days=12),
                due_date=today + timedelta(days=2),
            )
            r2.status = 'BORROWED'
            records.append(r2)


            r3 = BorrowRecord(
                user_id=user1.id,
                book_id=6,  # SQL Server toàn tập
                borrow_date=today - timedelta(days=20),
                due_date=today - timedelta(days=6),
            )
            r3.status = 'BORROWED'
            records.append(r3)

            # --- user1234: 1 sách đang chờ duyệt trả (RETURNING) ---
            r4 = BorrowRecord(
                user_id=user1.id,
                book_id=7,  # Flask Web Development
                borrow_date=today - timedelta(days=10),
                due_date=today - timedelta(days=3),
                return_date=today,
            )
            r4.status = 'RETURNING'
            r4.fine = 3 * 5000  # 3 ngày trễ × 5000 VNĐ
            records.append(r4)

            # --- user1234: 1 sách đã trả (RETURNED) ---
            r5 = BorrowRecord(
                user_id=user1.id,
                book_id=1,  # Lập trình C#
                borrow_date=today - timedelta(days=30),
                due_date=today - timedelta(days=16),
                return_date=today - timedelta(days=18),
            )
            r5.status = 'RETURNED'
            r5.fine = 0  # Trả đúng hạn
            records.append(r5)


            r6 = BorrowRecord(
                user_id=user1.id,
                book_id=2,  # Python căn bản
                borrow_date=today - timedelta(days=25),
                due_date=today - timedelta(days=20),
                return_date=today - timedelta(days=15),
            )
            r6.status = 'RETURNED'
            r6.fine = 5 * 5000  # 5 ngày trễ × 5000 VNĐ
            records.append(r6)

            # --- user2: 1 sách đang mượn ---
            r7 = BorrowRecord(
                user_id=user2.id,
                book_id=10,  # ReactJS từ cơ bản
                borrow_date=today - timedelta(days=5),
                due_date=today + timedelta(days=9),
            )
            r7.status = 'BORROWED'
            records.append(r7)

            # --- user_max: 5 sách đang mượn (đạt giới hạn tối đa) ---
            for i, bid in enumerate([15, 16, 17, 18, 19], start=1):
                rm1 = BorrowRecord(
                    user_id=user_max.id,
                    book_id=bid,
                    borrow_date=today - timedelta(days=i),
                    due_date=today + timedelta(days=14 - i),
                )
                rm2 = BorrowRecord(
                    user_id=inactive_user_max.id,
                    book_id=bid,
                    borrow_date=today - timedelta(days=i),
                    due_date=today + timedelta(days=14 - i),
                )
                rm1.status = 'BORROWED'
                rm2.status = 'BORROWED'

                records.append(rm1)
                records.append(rm2)


            db.session.add_all(records)

            # Cập nhật quantity sách (trừ đi số lượng đang mượn)
            borrowed_counts = {}
            for r in records:
                if r.status in ('BORROWED', 'RETURNING'):
                    borrowed_counts[r.book_id] = borrowed_counts.get(r.book_id, 0) + 1

            for book_id, count in borrowed_counts.items():
                book = Book.query.get(book_id)
                if book:
                    book.quantity = max(0, book.quantity - count)

            db.session.commit()
        username = 'overdue'
        desired_book_id = 1

        u = User.query.filter_by(username=username).first()
        if u is None:
            password = 'user123'
            passwordHash = hashlib.md5(password.strip().encode('utf-8')).hexdigest()
            print(f"User '{username}' not found. Creating test user with password 'user123'.")
            u = User(username=username, password=passwordHash)
            db.session.add(u)
            db.session.commit()

        b = Book.query.get(desired_book_id)
        if b is None:
            print(f"Book id={desired_book_id} not found. Creating sample book.")
            b = Book(title='Sample Book', author='Sample Author', quantity=5)
            db.session.add(b)
            db.session.commit()
            desired_book_id = b.id

        # Ensure there's at least one copy to borrow (so decrement won't go negative)
        if b.quantity <= 0:
            print(f"Book (id={b.id}) has quantity={b.quantity}. Setting to 1 before creating borrow record.")
            b.quantity = 1

        # Decrement quantity to simulate a borrow
        b.quantity -= 1

        r = BorrowRecord(user_id=u.id,
                         book_id=b.id,
                         borrow_date=date.today() - timedelta(days=10),
                         due_date=date.today() - timedelta(days=5))
        db.session.add(r)
        db.session.commit()
        print('Created borrow id:', r.id)
        print(f"User '{u.username}' borrowed '{b.title}' with due date {r.due_date}. ,password {u.password}")
        print(f"[SEED] Đã tạo {BorrowRecord.query.count()} borrow records")

        # ========== THỐNG KÊ ==========
        print("\n" + "=" * 50)
        print("THỐNG KÊ DỮ LIỆU TEST")
        print("=" * 50)
        print(f"  Users:          {User.query.count()}")
        print(f"  Categories:     {Category.query.count()}")
        print(f"  Books:          {Book.query.count()}")
        print(f"  BorrowRecords:  {BorrowRecord.query.count()}")
        print(f"    - BORROWED:   {BorrowRecord.query.filter_by(status='BORROWED').count()}")
        print(f"    - RETURNING:  {BorrowRecord.query.filter_by(status='RETURNING').count()}")
        print(f"    - RETURNED:   {BorrowRecord.query.filter_by(status='RETURNED').count()}")
        print("=" * 50)

        # In thông tin đăng nhập
        print("\nTÀI KHOẢN TEST:")
        print("  Admin:  admin / admin123")
        print("  User:   user1/ user1234")
        print("  User2:  user2 / user@1234")
        print("  Locked: inactive_user / user1234 (bị khóa)")
        print("  Max:    user_max / user1234 (đã mượn 5 sách)")
        print("  inactivite_Max:    inactive_user_max / user1234 (đã mượn 5 sách + khoa)")




if __name__ == '__main__':
    seed()
