CREATE DATABASE library;
USE library;

CREATE TABLE users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(100),
    email VARCHAR(100),
    password VARCHAR(255)
);

CREATE TABLE books(
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    author VARCHAR(100),
    category VARCHAR(100),
    publisher VARCHAR(100),
    quantity INT,
    available INT
);

CREATE TABLE borrow_records(
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    book_id INT,
    borrow_date DATE,
    due_date DATE,
    return_date DATE,
    fine DECIMAL(10,2) DEFAULT 0,
    status ENUM('Borrowing','Returned'),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(book_id) REFERENCES books(id)
);

INSERT INTO users(fullname,email,password)
VALUES
('Nguyen Van A','a@gmail.com','123'),
('Tran Van B','b@gmail.com','123');

INSERT INTO books(title,author,category,publisher,quantity,available)
VALUES
('Clean Code','Robert C. Martin','Programming','Prentice Hall',5,5),
('Python Crash Course','Eric Matthes','Programming','No Starch Press',3,3),
('Harry Potter','J.K. Rowling','Fantasy','Bloomsbury',4,4);