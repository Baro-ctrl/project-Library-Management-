from database import connect_db
from datetime import date,timedelta

def borrow_book(user_id,book_id):

    conn=connect_db()

    cur=conn.cursor()

    cur.execute(
        "SELECT available FROM books WHERE id=%s",
        (book_id,)
    )

    book=cur.fetchone()

    if book is None:

        print("Không tìm thấy sách")
        return

    if book[0]<=0:

        print("Sách đã được mượn hết")
        return

    borrow_date=date.today()

    due_date=borrow_date+timedelta(days=7)

    cur.execute("""

        INSERT INTO borrow_records

        (user_id,book_id,borrow_date,due_date,status)

        VALUES(%s,%s,%s,%s,'Borrowing')

    """,(user_id,book_id,borrow_date,due_date))

    cur.execute("""

        UPDATE books

        SET available=available-1

        WHERE id=%s

    """,(book_id,))

    conn.commit()

    print("Mượn sách thành công")

    cur.close()

    conn.close()