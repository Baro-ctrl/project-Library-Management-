from database import connect_db
from models.book import Book

def search(keyword):

    conn=connect_db()

    cur=conn.cursor()

    sql="""
    SELECT
    id,
    title,
    author,
    category,
    publisher,
    quantity,
    available

    FROM books

    WHERE

    title LIKE %s
    OR author LIKE %s
    OR category LIKE %s
    OR publisher LIKE %s
    """

    key="%"+keyword+"%"

    cur.execute(sql,(key,key,key,key))

    books=[]

    for row in cur.fetchall():

        books.append(Book(*row))

    cur.close()
    conn.close()

    return books