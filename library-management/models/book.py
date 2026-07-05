class Book:

    def __init__(self,id,title,author,category,publisher,quantity,available):

        self.id=id
        self.title=title
        self.author=author
        self.category=category
        self.publisher=publisher
        self.quantity=quantity
        self.available=available

    def __str__(self):

        return f"""
ID        : {self.id}
Tên sách  : {self.title}
Tác giả   : {self.author}
Thể loại  : {self.category}
NXB       : {self.publisher}
Còn lại   : {self.available}
"""