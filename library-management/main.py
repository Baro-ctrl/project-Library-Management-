from services.search_service import search
from services.borrow_service import borrow_book
from services.return_service import return_book

while True:

    print("""
==========================
LIBRARY MANAGEMENT
==========================
1. Tìm sách
2. Mượn sách
3. Trả sách
0. Thoát
==========================
""")

    choice=input("Chọn: ")

    if choice=="1":

        keyword=input("Nhập từ khóa: ")

        books=search(keyword)

        if len(books)==0:

            print("Không tìm thấy sách")

        else:

            for book in books:

                print(book)

    elif choice=="2":

        user_id=int(input("User ID: "))
        book_id=int(input("Book ID: "))

        borrow_book(user_id,book_id)

    elif choice=="3":

        record_id=int(input("Borrow Record ID: "))

        return_book(record_id)

    elif choice=="0":

        break

    else:

        print("Lựa chọn không hợp lệ")