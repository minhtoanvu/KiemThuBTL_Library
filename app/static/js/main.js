// Chặn double click cho tất cả các form gửi dữ liệu lên server
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
        const btn = this.querySelector('button[type="submit"]');
        if (btn && !btn.disabled) {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Đang xử lý...';
        }
    });
});

// Tính ngày mặc định (hôm nay + 14 ngày)
function getDefaultDueDate() {
    const d = new Date();
    d.setDate(d.getDate() + 14);
    return d.toISOString().split('T')[0];
}

// Tính ngày tối thiểu (ngày mai)
function getMinDate() {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    return d.toISOString().split('T')[0];
}

// Tạo danh sách ô chọn hạn trả theo số lượng
function updateDueDateFields(qty) {
    const container = document.getElementById('due-dates-container');
    if (!container) return;

    const defaultDate = getDefaultDueDate();
    const minDate = getMinDate();

    container.innerHTML = '';
    for (let i = 1; i <= qty; i++) {
        const row = document.createElement('div');
        row.className = 'due-date-row';
        row.style.cssText = 'display:flex; align-items:center; gap:0.8rem; margin-bottom:0.6rem;';
        row.innerHTML =
            '<label style="white-space:nowrap; font-size:0.88rem; color:var(--text-secondary); min-width:70px;">Cuốn ' + i + '</label>' +
            '<input type="date" name="due_date_' + i + '" class="form-control" required ' +
            'value="' + defaultDate + '" min="' + minDate + '" ' +
            'style="border:1px solid var(--border); border-radius:6px; padding:0.4rem 0.6rem; font-size:0.88rem;">';
        container.appendChild(row);
    }
}

// Modal mượn sách
const borrowModal = document.getElementById('borrowModal');
if (borrowModal) {
    borrowModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;

        const bookId = button.getAttribute('data-id');
        const bookTitle = button.getAttribute('data-title');
        const bookCategory = button.getAttribute('data-category');
        const bookQty = button.getAttribute('data-qty');

        document.getElementById('modal-book-title').textContent = bookTitle;
        document.getElementById('modal-book-category').textContent = bookCategory;
        document.getElementById('modal-book-qty').textContent = bookQty + ' cuốn';

        // Cập nhật max số lượng mượn theo số sách còn lại
        const qtyInput = document.getElementById('modal-borrow-qty');
        const maxQty = Math.min(parseInt(bookQty), 5);
        qtyInput.max = maxQty;
        qtyInput.value = 1;

        document.getElementById('borrowForm').action = '/borrow/' + bookId;

        // Hiện 1 ô hạn trả mặc định
        updateDueDateFields(1);
        // Ghi nhớ sách đang hiển thị trong modal để cập nhật động khi polling
        window.currentBorrowModalBookId = bookId;
    });

    // Khi modal đóng, bỏ id đang mở
    borrowModal.addEventListener('hidden.bs.modal', function () {
        window.currentBorrowModalBookId = null;
    });

    // Khi thay đổi số lượng, cập nhật số ô hạn trả
    const qtyInput = document.getElementById('modal-borrow-qty');
    if (qtyInput) {
        qtyInput.addEventListener('input', function() {
            const qty = Math.max(1, Math.min(parseInt(this.value) || 1, parseInt(this.max)));
            this.value = qty;
            updateDueDateFields(qty);
        });
    }
}

// Auto-dismiss flash messages after 5 seconds
document.querySelectorAll('.flash-msg').forEach(msg => {
    setTimeout(() => {
        msg.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        msg.style.opacity = '0';
        msg.style.transform = 'translateY(-10px)';
        setTimeout(() => msg.remove(), 500);
    }, 5000);
});

// --- Polling: cập nhật số lượng sách định kỳ ---
function updateBookQty(bookId, quantity) {
    const span = document.getElementById('book-qty-' + bookId);
    if (!span) return;
    if (quantity > 0) {
        span.classList.remove('out-of-stock');
        span.textContent = 'Còn ' + quantity;
    } else {
        span.classList.add('out-of-stock');
        span.textContent = 'Hết sách';
    }
    // Cập nhật attribute trên các nút mượn
    document.querySelectorAll('button[data-id]')
        .forEach(btn => { if (btn.getAttribute('data-id') === String(bookId)) btn.setAttribute('data-qty', quantity); });

    // Nếu modal đang mở cho cuốn này, cập nhật luôn
    if (window.currentBorrowModalBookId && String(window.currentBorrowModalBookId) === String(bookId)) {
        const modalQtyElem = document.getElementById('modal-book-qty');
        if (modalQtyElem) modalQtyElem.textContent = quantity + ' cuốn';
        const qtyInput = document.getElementById('modal-borrow-qty');
        if (qtyInput) {
            qtyInput.max = Math.min(quantity, 5);
            if (parseInt(qtyInput.value) > qtyInput.max) qtyInput.value = qtyInput.max;
        }
    }
}

async function pollBookQuantitiesOnce() {
    const btns = document.querySelectorAll('button[data-id]');
    const ids = Array.from(new Set(Array.from(btns).map(b => b.getAttribute('data-id')))).filter(Boolean);
    if (ids.length === 0) return;
    try {
        const res = await fetch('/api/books/quantities?ids=' + ids.join(','));
        if (!res.ok) return;
        const data = await res.json();
        if (data && data.quantities) {
            ids.forEach(id => {
                const qty = data.quantities[String(id)];
                if (typeof qty !== 'undefined') updateBookQty(id, qty);
            });
        }
    } catch (e) {
        // ignore network errors silently
    }
}

(function startPolling() {
    // Gọi ngay lần đầu rồi set interval
    pollBookQuantitiesOnce();
    setInterval(pollBookQuantitiesOnce, 10000); // every 10s
})();