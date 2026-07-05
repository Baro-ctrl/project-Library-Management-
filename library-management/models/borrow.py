class BorrowRecord:

    def __init__(self,id,user_id,book_id,borrow_date,due_date,return_date,fine,status):

        self.id=id
        self.user_id=user_id
        self.book_id=book_id
        self.borrow_date=borrow_date
        self.due_date=due_date
        self.return_date=return_date
        self.fine=fine
        self.status=status

    def __str__(self):

        return f"""
Borrow ID : {self.id}
User      : {self.user_id}
Book      : {self.book_id}
Borrow    : {self.borrow_date}
Due       : {self.due_date}
Return    : {self.return_date}
Fine      : {self.fine}
Status    : {self.status}
"""