from database import connect_db
from datetime import date

FINE_PER_DAY=5000

def return_book(record_id):

    conn=connect_db()

    cur=conn.cursor()

    cur.execute("""

        SELECT

        book_id,
        due_date,
        status

        FROM borrow_records

        WHERE id=%s

    """,(record_id,))

    record=cur.fetchone()

    if record is None:

        print("Không tìm thấy phiếu mượn")
        return

    if record[2]=="Returned":

        print("Sách đã trả")
        return

    today=date.today()

    overdue=(today-record[1]).days

    fine=0

    if overdue>0:

        fine=overdue*FINE_PER_DAY

    cur.execute("""

        UPDATE borrow_records

        SET

        return_date=%s,
        fine=%s,
        status='Returned'

        WHERE id=%s

    """,(today,fine,record_id))

    cur.execute("""

        UPDATE books

        SET available=available+1

        WHERE id=%s

    """,(record[0],))

    conn.commit()

    print("Đã trả sách")
    print("Tiền phạt:",fine)

    cur.close()

    conn.close()