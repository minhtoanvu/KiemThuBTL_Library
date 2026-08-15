from app.models.book import Book
from app.models.category import Category


def get_book_by_id(book_id):
    return Book.query.get(book_id)


def load_books(kw=None, author=None, category=None, page=1):
    query = Book.query
    if kw:
        query = query.filter(Book.title.contains(kw))  # Tìm gần đúng (TC1.2)
    if author:
        query = query.filter(Book.author.contains(author))  # Tìm theo tác giả (TC2.1)
    if category:
        query = query.join(Category).filter(Category.name == category)  # Theo thể loại (TC3.1)

    page_size = 50
    return query.paginate(page=page, per_page=page_size, error_out=False)


def get_all_categories():
    """Lấy danh sách thể loại từ bảng Category"""
    results = Category.query.order_by(Category.name).all()
    return [c.name for c in results]