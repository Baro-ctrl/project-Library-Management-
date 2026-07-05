-- LibraryManagement.sql (đã chuyển sang cú pháp MySQL, dùng cho MySQL Workbench)

DROP DATABASE IF EXISTS LibraryManagement;
CREATE DATABASE LibraryManagement CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE LibraryManagement;

CREATE TABLE `User`(
 userId VARCHAR(50) PRIMARY KEY,
 username VARCHAR(50) NOT NULL UNIQUE,
 password VARCHAR(100) NOT NULL,
 fullName VARCHAR(100) NOT NULL,
 email VARCHAR(100) UNIQUE,
 phone VARCHAR(20),
 role VARCHAR(20) NOT NULL CHECK(role IN ('Admin','Reader','Librarian'))
);


CREATE TABLE Category(
 categoryId VARCHAR(50) PRIMARY KEY,
 name VARCHAR(100) NOT NULL,
 description TEXT
);

CREATE TABLE Author (
    authorId VARCHAR(50) PRIMARY KEY,
    authorName VARCHAR(100) NOT NULL,
    imageUrl VARCHAR(500),
    biography TEXT
);


CREATE TABLE Books(
    isbn VARCHAR(20) PRIMARY KEY,
    categoryId VARCHAR(50) NOT NULL,
    authorId VARCHAR(50) NOT NULL,
    title VARCHAR(150) NOT NULL,
    publisher VARCHAR(200),
    publishYear INT NOT NULL CHECK (publishYear >= 1800),
    imageUrl VARCHAR(500),      -- ảnh bìa sách
    description TEXT,

    FOREIGN KEY (categoryId) REFERENCES Category(categoryId),
    FOREIGN KEY (authorId) REFERENCES Author(authorId)
);


CREATE TABLE BookCopy(
 barcode VARCHAR(50) PRIMARY KEY,
 isbn VARCHAR(20) NOT NULL,
 status VARCHAR(20) NOT NULL DEFAULT 'Available'
   CHECK(status IN ('Available','Borrowed','Lost','Damaged')),
 `condition` VARCHAR(50),
 FOREIGN KEY(isbn) REFERENCES Books(isbn)
);

CREATE TABLE Reader(
 readerId VARCHAR(50) PRIMARY KEY,
 userId VARCHAR(50) UNIQUE,
 cardExpiryDate DATE,
 totalBorrowed INT DEFAULT 0 CHECK(totalBorrowed>=0),
 FOREIGN KEY(userId) REFERENCES `User`(userId)
);


CREATE TABLE Librarian(
 librarianId VARCHAR(50) PRIMARY KEY,
 userId VARCHAR(50) UNIQUE,
 shift VARCHAR(20) CHECK(shift IN ('Morning','Afternoon','Evening')),
 FOREIGN KEY(userId) REFERENCES `User`(userId)
);


CREATE TABLE BookSlip(
 slipId VARCHAR(50) PRIMARY KEY,
 readerId VARCHAR(50) NOT NULL,
 librarianId VARCHAR(50) NOT NULL,
 borrowDate DATE NOT NULL,
 dueDate DATE NOT NULL,
 status VARCHAR(20) CHECK(status IN ('Borrowing','Returned','Late')),
 CHECK(dueDate>=borrowDate),
 FOREIGN KEY(readerId) REFERENCES Reader(readerId),
 FOREIGN KEY(librarianId) REFERENCES Librarian(librarianId)
);



CREATE TABLE BorrowDetail(
 detailId INT AUTO_INCREMENT PRIMARY KEY,
 slipId VARCHAR(50) NOT NULL,
 barcode VARCHAR(50) NOT NULL,
 returnDate DATE,
 fineAmount DECIMAL(10,2) DEFAULT 0 CHECK(fineAmount>=0),
 note TEXT,
 renewalCount INT DEFAULT 0 CHECK(renewalCount>=0),
 FOREIGN KEY(slipId) REFERENCES BookSlip(slipId),
 FOREIGN KEY(barcode) REFERENCES BookCopy(barcode)
);


INSERT INTO `User` ( userId,username,password,fullName,email,phone,role)
VALUES
('U001', 'admin01', 'admin123', 'Nguyễn Quản Trị', 'admin@library.com', '0901000001', 'Admin'),

('U002', 'reader01', 'reader123', 'Trần Minh Anh', 'reader01@gmail.com', '0901000002', 'Reader'),

('U003', 'reader02', 'reader123', 'Lê Hoàng Nam', 'reader02@gmail.com', '0901000003', 'Reader'),

('U004', 'reader03', 'reader123', 'Phạm Thu Trang', 'reader03@gmail.com', '0901000004', 'Reader'),

('U005', 'librarian01', 'lib123', 'Nguyễn Thủ Thư', 'librarian01@library.com', '0901000005', 'Librarian'),

('U006', 'librarian02', 'lib123', 'Hoàng Minh Đức', 'librarian02@library.com', '0901000006', 'Librarian');

INSERT INTO Category(categoryId,name,description)
VALUES
('C001','Tiểu Thuyết','...'),
('C002','Văn Học','...'),
('C003','Truyện Tranh','...'),
('C004','Kinh Dị','...');

INSERT INTO Author (authorId, authorName, imageUrl, biography)
VALUES
('A001', 'Antoine de Saint-Exupéry', 'D:\\CNPM\\Actor\\Antoine de Saint-Exupéry.jpg', 'Nhà văn và phi công phiêu lưu người Pháp. Ông nổi tiếng với văn phong giàu tính triết lý, chất thơ và sự trinh nguyên, được đúc kết từ chính những trải nghiệm đơn độc bay lượn trên bầu trời. Hoàng tử bé là kiệt tác để đời của ông, cuốn sách mang hình thức truyện thiếu nhi nhưng chứa đựng những bài học sâu sắc làm say mê cả người lớn trên toàn thế giới.'),

('A002', 'J.K. Rowling', 'D:\\CNPM\\Actor\\J.K. Rowling.jpg', 'Nữ nhà văn người Anh, "mẹ đẻ" của thế giới phù thủy Harry Potter. Bà được mệnh danh là người đã làm sống lại văn hóa đọc của trẻ em toàn cầu nhờ lối kể chuyện cuốn hút, cách xây dựng thế giới phép thuật đồ sộ và hệ thống nhân vật có chiều sâu.'),

('A003', 'J.R.R. Tolkien', 'D:\\CNPM\\Actor\\J.R.R. Tolkien.jpg', 'Nhà ngôn ngữ học và giáo sư văn học người Anh, được tôn vinh là cha đẻ của dòng văn học kỳ ảo hiện đại. Ông là tác giả bộ sử thi The Lord of the Rings với thế giới Trung Địa nổi tiếng.'),

('A004', 'Margaret Mitchell', 'D:\\CNPM\\Actor\\Margaret Mitchell.jpg', 'Nữ nhà văn và nhà báo người Mỹ. Tiểu thuyết Gone with the Wind đã mang về cho bà giải Pulitzer và trở thành một trong những tác phẩm kinh điển của văn học thế giới.'),

('A005', 'Nam Cao', 'D:\\CNPM\\Actor\\Nam Cao.jpg', 'Đại biểu xuất sắc của dòng văn học hiện thực phê phán Việt Nam trước năm 1945. Ông nổi tiếng với các tác phẩm Chí Phèo, Lão Hạc, phản ánh sâu sắc số phận người nông dân và tầng lớp trí thức nghèo.'),

('A006', 'Ngô Tất Tố', 'D:\\CNPM\\Actor\\Ngô Tất Tố.jpg', 'Nhà văn, nhà báo và nhà nho học Việt Nam. Ông nổi tiếng với tác phẩm Tắt đèn phản ánh hiện thực xã hội thực dân nửa phong kiến.'),

('A007', 'Vũ Trọng Phụng', 'D:\\CNPM\\Actor\\Vũ Trọng Phụng.jpg', 'Nhà văn hiện thực phê phán nổi tiếng của Việt Nam, được mệnh danh là "Vôn-te của Việt Nam". Các tác phẩm tiêu biểu gồm Số đỏ và Trúng số độc đắc.'),

('A008', 'Thạch Lam', 'D:\\CNPM\\Actor\\Thạch Lam.jpg', 'Thành viên của Tự Lực Văn Đoàn, nổi tiếng với phong cách truyện ngắn giàu chất trữ tình và miêu tả nội tâm tinh tế. Tác phẩm tiêu biểu: Hà Nội băm sáu phố phường.'),

('A009', 'Tô Hoài', 'D:\\CNPM\\Actor\\Tô Hoài.jpg', 'Cây bút lớn của văn học Việt Nam hiện đại, nổi tiếng với Dế Mèn phiêu lưu ký và nhiều tác phẩm viết về văn hóa các vùng miền.'),

('A010', 'Kim Lân', 'D:\\CNPM\\Actor\\Kim Lân.jpg', 'Nhà văn chuyên viết truyện ngắn về nông thôn Việt Nam. Tác phẩm tiêu biểu: Làng và Vợ nhặt.'),

('A011', 'Fujiko F. Fujio', 'D:\\CNPM\\Actor\\Fujiko F. Fujio.jpg', 'Họa sĩ manga huyền thoại người Nhật Bản, cha đẻ của Doraemon, biểu tượng tuổi thơ của nhiều thế hệ trên thế giới.'),

('A012', 'Lê Linh', 'D:\\CNPM\\Actor\\Lê Linh.jpg', 'Họa sĩ truyện tranh Việt Nam, người sáng tạo bộ truyện Thần đồng Đất Việt với các nhân vật Tý, Sửu, Dần, Mẹo.'),

('A013', 'Aoyama Gosho', 'D:\\CNPM\\Actor\\Aoyama Gosho.jpg', 'Họa sĩ manga người Nhật, tác giả bộ truyện Thám tử lừng danh Conan, nổi tiếng với các vụ án trinh thám và cốt truyện kéo dài.'),

('A014', 'Toriyama Akira', 'D:\\CNPM\\Actor\\Toriyama Akira.jpg', 'Huyền thoại manga Nhật Bản, tác giả Dragon Ball, có ảnh hưởng to lớn đến nền công nghiệp manga và anime thế giới.'),

('A015', 'Oda Eiichiro', 'D:\\CNPM\\Actor\\Oda Eiichiro.jpg', 'Tác giả One Piece, bộ manga bán chạy nhất mọi thời đại, nổi tiếng với khả năng xây dựng thế giới và cốt truyện đồ sộ.'),

('A016', 'Nguyễn Hùng Lân', 'D:\\CNPM\\Actor\\Nguyễn Hùng Lân.jpg', 'Họa sĩ truyện tranh Việt Nam, tác giả bộ truyện Dũng sĩ Hesman, gắn liền với tuổi thơ của nhiều thế hệ độc giả Việt.'),

('A017', 'Đào Hải', 'D:\\CNPM\\Actor\\Đào Hải.jpg', 'Cố họa sĩ truyện tranh Việt Nam, tác giả bộ truyện Tý Quậy với phong cách hài hước, gần gũi đời sống học đường.'),

('A018', 'Kishimoto Masashi', 'D:\\CNPM\\Actor\\Kishimoto Masashi.jpg', 'Họa sĩ manga Nhật Bản, tác giả Naruto. Tác phẩm nổi bật với chủ đề tình bạn, ý chí và sự trưởng thành.'),

('A019', 'Gotouge Koyoharu', 'D:\\CNPM\\Actor\\Gotouge Koyoharu.jpg', 'Tác giả Demon Slayer (Thanh gươm diệt quỷ), nổi tiếng với cốt truyện cảm động và những trận chiến hấp dẫn.'),

('A020', 'Sakura Momoko', 'D:\\CNPM\\Actor\\Sakura Momoko.jpg', 'Nữ họa sĩ manga Nhật Bản, tác giả Chibi Maruko-chan (Nhóc Maruko), tái hiện cuộc sống gia đình Nhật Bản đầy ấm áp.'),

('A021', 'Bram Stoker', 'D:\\CNPM\\Actor\\Bram Stoker.jpg', 'Nhà văn người Ireland, tác giả Dracula, người đặt nền móng cho hình tượng ma cà rồng hiện đại.'),

('A022', 'Mary Shelley', 'D:\\CNPM\\Actor\\Mary Shelley.jpg', 'Nữ nhà văn người Anh, tác giả Frankenstein, được xem là người đặt nền móng cho văn học khoa học viễn tưởng và kinh dị hiện đại.'),

('A023', 'Stephen King', 'D:\\CNPM\\Actor\\Stephen King.jpg', '"Ông hoàng kinh dị" người Mỹ với hàng chục tiểu thuyết nổi tiếng như The Shining và It.'),

('A024', 'Koji Suzuki', 'D:\\CNPM\\Actor\\Koji Suzuki.jpg', 'Nhà văn Nhật Bản, tác giả Ring (Vòng tròn ác nghiệt), người khởi xướng làn sóng kinh dị J-Horror.'),

('A025', 'William Peter Blatty', 'D:\\CNPM\\Actor\\William Peter Blatty.jpg', 'Nhà văn và biên kịch người Mỹ, tác giả The Exorcist (Quỷ ám), một trong những tác phẩm kinh dị nổi tiếng nhất mọi thời đại.'),

('A026', 'Shirley Jackson', 'D:\\CNPM\\Actor\\Shirley Jackson.jpg', 'Nữ nhà văn Mỹ nổi tiếng với phong cách kinh dị tâm lý. Tác phẩm tiêu biểu: The Haunting of Hill House.'),

('A027', 'Yukito Ayatsuji', 'D:\\CNPM\\Actor\\Yukito Ayatsuji.jpg', 'Nhà văn Nhật Bản, tác giả Another, nổi tiếng với phong cách kết hợp kinh dị và trinh thám.'),

('A028', 'H.P. Lovecraft', 'D:\\CNPM\\Actor\\H.P. Lovecraft.jpg', 'Nhà văn người Mỹ, cha đẻ của dòng kinh dị vũ trụ (Cosmic Horror) và thần thoại Cthulhu.'),

('A029', 'Thảo Trang', 'D:\\CNPM\\Actor\\Thảo Trang.jpg', 'Cây bút kinh dị Việt Nam hiện đại, nổi tiếng với các tác phẩm mang màu sắc tín ngư.');


INSERT INTO Books (isbn, categoryId, authorId, title, publisher, publishYear, imageUrl, description)
VALUES
('ISBN001', 'C001', 'A001', 'Hoàng tử bé', 'Gallimard', 1943, 'Hoàng tử bé.jpg', 
'Một câu chuyện ngụ ngôn triết học sâu sắc về cuộc gặp gỡ giữa người phi công và cậu bé đến từ tinh cầu B-612. Qua lăng kính ngây thơ, tác phẩm phơi bày những thói hư tật xấu của người lớn và gửi gắm bài học thức tỉnh về tình yêu, trách nhiệm cùng những giá trị vô hình chỉ có thể nhìn thấu bằng trái tim.'),

('ISBN002', 'C001', 'A002', 'Harry Potter và Hòn đá Phù thủy', 'Bloomsbury', 1997, 'Harry Potter và Hòn đá Phù thủy.jpg', 
'Mở đầu chuỗi sử thi phù thủy huyền thoại. Cậu bé mồ côi Harry Potter phát hiện mình là phù thủy và nhập học tại Hogwarts. Tại đây, cậu tìm thấy những người bạn thân thiết, khám phá bí mật về cái chết của cha mẹ và bước vào cuộc đối đầu nghẹt thở bảo vệ Hòn đá Phù thủy khỏi tay kẻ đại ác Voldemort.'),

('ISBN003', 'C001', 'A002', 'Harry Potter và Phòng chứa Bí mật', 'Bloomsbury', 1998, 'Harry Potter và Phòng chứa Bí mật.jpg', 
'Năm học thứ hai của Harry nhuốm màu sợ hãi khi Phòng chứa Bí mật bị mở ra, giải phóng quái thú chuyên hóa đá các học sinh gốc Muggle. Bằng lòng dũng cảm và khả năng nói xà ngữ, Harry đã dấn thân vào lòng đất để tiêu diệt con tử xà Basilisk và phá hủy cuốn nhật ký ký ức của Tom Riddle.'),

('ISBN004', 'C001', 'A002', 'Harry Potter và Tù nhân ngục Azkaban', 'Bloomsbury', 1999, 'Harry Potter và Tù nhân ngục Azkaban.jpg', 
'Năm học thứ ba đầy đen tối khi tên sát nhân khét tiếng Sirius Black trốn khỏi ngục Azkaban và được cho là đang săn lùng Harry. Tập truyện không xoay quanh Voldemort mà tập trung vào bí mật quá khứ, nơi Harry tìm ra sự thật về lòng trung thành, phản bội và có được một người cha đỡ đầu đúng nghĩa.'),

('ISBN005', 'C001', 'A002', 'Harry Potter và Chiếc cốc lửa', 'Bloomsbury', 2000, 'Harry Potter và Chiếc cốc lửa.jpg', 
'Bước ngoặt lớn khi Harry bị cuốn vào Giải đấu Tam Pháp thuật đầy nguy hiểm dù chưa đủ tuổi. Trải qua ba bài thi khắc nghiệt, vinh quang bỗng chốc biến thành bi kịch ở chặng cuối khi chiếc cúp biến thành Khóa cảng, đưa Harry đến nghĩa địa hoang vu – nơi máu của cậu bị dùng để hồi sinh Chúa tể Voldemort.'),

('ISBN006', 'C001', 'A002', 'Harry Potter và Hội Phượng Hoàng', 'Bloomsbury', 2003, 'Harry Potter và Hội Phượng Hoàng.jpg', 
'Thế giới phù thủy phủ nhận sự trở lại của Voldemort, biến Harry thành kẻ nói dối. Tại Hogwarts, sự độc tài của giáo sư Umbridge buộc các học sinh phải âm thầm thành lập Quân đoàn Dumbledore để tự vệ, dẫn đến trận chiến khốc liệt tại Bộ Pháp thuật và nỗi đau mất mát to lớn của Harry.'),

('ISBN007', 'C001', 'A003', 'The Lord of the Rings', 'Allen & Unwin', 1954, 'The Lord of the Rings.jpg', 
'Kiệt tác vĩ đại của dòng văn học kỳ ảo lấy bối cảnh vùng đất Middle-earth. Sứ mệnh thế giới phụ thuộc vào Frodo Baggins – một người Hobbit nhỏ bé gánh vác trọng trách đem Nhẫn Chúa đi tiêu hủy tại núi Diệt Vong. Một bản anh hùng ca hoành tráng về tình bạn, lòng quả cảm và cuộc chiến thiện ác.'),

('ISBN008', 'C001', 'A004', 'Gone with the Wind', 'Macmillan', 1936, 'Gone with the Wind.jpg', 
'Thiên tiểu thuyết sử thi lấy bối cảnh cuộc Nội chiến Mỹ khốc liệt, xoay quanh Scarlett O’Hara – tiểu thư miền Nam bướng bỉnh có sức sống mãnh liệt. Bản lĩnh của cô được thử thách qua bom đạn, nghèo đói để bảo vệ đồn điền Tara bên cạnh Rhett Butler, vẽ nên bức tranh chân thực về một thời đại đã mất.'),

('ISBN009', 'C001', 'A002', 'Harry Potter và Hòn đá Phù thủy (US Edition)', 'Scholastic', 1997, 'Harry Potter và Hòn đá Phù thủy (US Edition).jpg', 
'Phiên bản phát hành tại Mỹ với tên "Sorcerer’s Stone". Câu chuyện kể về cậu bé mồ côi Harry Potter khám phá ra thế giới phù thủy, nhập học trường Hogwarts và cùng những người bạn thân thiết bảo vệ Hòn đá Phù thủy khỏi bàn tay của kẻ đại ác Voldemort.'),

('ISBN010', 'C001', 'A002', 'Harry Potter và Phòng chứa Bí mật (US Edition)', 'Scholastic', 1998, 'Harry Potter và Phòng chứa Bí mật (US Edition).jpg', 
'Phiên bản phát hành tại Mỹ. Tiếp tục hành trình năm thứ hai đầy hiểm nguy của Harry tại Hogwarts khi Phòng chứa Bí mật bị mở ra, buộc cậu phải dùng lòng dũng cảm để tiêu diệt con tử xà Basilisk và phá hủy cuốn nhật ký ký ức của Tom Riddle.'),

('ISBN011', 'C002', 'A005', 'Chí Phèo', 'NXB Văn Học', 1946, 'Chí Phèo.jpg', 
'Kiệt tác hiện thực phê phán về tấn bi kịch đau đớn của người nông dân hiền lành bị xã hội lưu manh hóa, cướp đi cả nhân hình lẫn nhân tính. Cuộc gặp gỡ với Thị Nở đã đánh thức thiên lương trong Chí, nhưng bi kịch đẩy lên đỉnh điểm khi anh bị cự tuyệt quyền làm người.'),

('ISBN012', 'C002', 'A006', 'Lều Chõng', 'NXB Văn Học', 1941, 'Lều Chõng.jpg', 
'Tiểu thuyết phóng sự xuất sắc tái hiện bức tranh chân thực về chế độ khoa cử phong kiến buổi xế tà. Qua hành trình của Đào Vân Hạc, tác phẩm phơi bày những góc khuất khắc nghiệt nơi trường thi và là lời tiễn biệt đầy xót xa cho một thế hệ trí thức cũ lạc lõng giữa buổi giao thời.'),

('ISBN013', 'C002', 'A007', 'Trúng Số Độc Đắc', 'NXB Văn Học', 1938, 'Trúng Số Độc Đắc.jpg', 
'Bức tranh châm biếm sâu cay về sức mạnh tha hóa của đồng tiền trong xã hội thành thị thuộc địa. Câu chuyện xoay quanh một thư ký nghèo bỗng chốc đổi đời nhờ vé số, từ đó bóc trần sự giả dối, tham lam của lòng người khi đứng trước ma lực của vật chất.'),

('ISBN014', 'C002', 'A008', 'Hà Nội Băm Sáu Phố Phường', 'NXB Văn Học', 1943, 'Hà Nội Băm Sáu Phố Phường.jpg', 
'Tập bút ký tràn đầy chất thơ, kết tinh tình yêu sâu sắc dành cho mảnh đất Kinh Kỳ. Đi sâu vào văn hóa, phong tục, nếp sống thanh lịch cùng những món quà đặc sản, tác phẩm hiện thực hóa một Hà Nội cổ kính, trầm mặc nhưng đượm một nỗi buồn man mác.'),

('ISBN015', 'C002', 'A009', 'Dế Mèn Phiêu Lưu Ký', 'NXB Kim Đồng', 1941, 'Dế Mèn Phiêu Lưu Ký.jpg', 
'Kiệt tác văn học thiếu nhi kinh điển kể về cuộc hành trình dấn thân đầy sóng gió của chàng Dế Mèn bồng bột. Trải qua những vấp ngã đau đớn, Mèn trưởng thành, biết gắn bó với cộng đồng và cùng bạn đường đi khắp thế gian để đấu tranh cho một thế giới hòa bình, đại đồng.'),

('ISBN016', 'C002', 'A005', 'Lão Hạc', 'NXB Văn Học', 1943, 'Lão Hạc.jpg', 
'Truyện ngắn lay động tâm can về tình phụ tử và lòng tự trọng của người nông dân nông thôn trước Cách mạng. Sống cô đơn cùng cậu Vàng, vì muốn giữ lại mảnh vườn cho con và bảo toàn nhân phẩm sạch trong, lão đã chọn kết cục đau đớn bằng bả chó để giải thoát cho mình.'),

('ISBN017', 'C002', 'A006', 'Tắt đèn', 'NXB Văn Học', 1939, 'Tắt đèn.jpg', 
'Bản cáo trạng đanh thép vạch trần chính sách thuế khóa bóc lột tàn nhẫn của chế độ thực dân phong kiến. Trung tâm tác phẩm là chị Dậu, biểu tượng cho người phụ nữ nông thôn kiên cường, giàu tình thương và sức phản kháng mạnh mẽ dù bị đẩy vào bước đường cùng bế tắc.'),

('ISBN018', 'C002', 'A007', 'Số đỏ', 'NXB Văn Học', 1936, 'Số đỏ.jpg', 
'Kiệt tác trào phúng vô tiền khoáng hậu xoay quanh Xuân Tóc Đỏ, một kẻ hạ lưu nhờ sự uế tạp và trào lưu Âu hóa rởm đời mà nhảy vọt lên hàng ngũ vĩ nhân xã hội. Bằng giọng văn sắc sảo, tác phẩm bóc trần bộ mặt giả dối, lố lăng của tầng lớp tư sản thành thị đương thời.'),

('ISBN019', 'C002', 'A010', 'Làng', 'NXB Văn Học', 1948, 'Làng.jpg', 
'Tác phẩm xuất sắc thời kỳ kháng chiến chống Pháp khắc họa nhân vật ông Hai – người nông dân yêu làng Chợ Dầu da diết. Qua diễn biến tâm lý tinh tế khi nghe tin làng theo giặc, tác phẩm ca ngợi sự hòa quyện sâu sắc giữa tình yêu làng quê với lòng yêu nước, tinh thần kháng chiến.'),

('ISBN020', 'C002', 'A010', 'Người Kép Già', 'NXB Văn Học', 1940, 'Người Kép Già.jpg', 
'Truyện ngắn đậm chất nhân văn đi sâu vào số phận người nghệ sĩ chèo truyền thống bước vào giai đoạn suy tàn trước làn sóng tân thời. Qua hình ảnh người kép già trăn trở nặng lòng với nghề, tác phẩm là tiếng thở dài nuối tiếc cho những giá trị cổ truyền dần bị mai một.'),

('ISBN021', 'C003', 'A011', 'Doraemon', 'Shōgakukan', 1969, 'Doraemon.jpg', 
'Biểu tượng tuổi thơ toàn cầu xoay quanh chú mèo máy thông minh đến từ thế kỷ 22 và chiếc túi bảo bối kỳ diệu. Cùng nhóm bạn Nobita, Shizuka, Suneo và Gian, bộ truyện mở ra những cuộc phiêu lưu giả tưởng lý thú, gửi gắm bài học sâu sắc về tình bạn và lòng nhân ái.'),

('ISBN022', 'C003', 'A012', 'Thần đồng Đất Việt', 'NXB Trẻ', 2002, 'Thần đồng Đất Việt.jpg', 
'Niềm tự hào của truyện tranh Việt Nam, lấy bối cảnh thời Hậu Lê. Bộ truyện theo chân trạng nguyên nhí Lê Tí cùng nhóm bạn Sửu, Dần, Mẹo dùng trí thông minh vượt trội để phá các vụ án hóc búa, giúp đỡ dân làng và đối đầu với sứ thần phương Bắc để bảo vệ bờ cõi.'),

('ISBN023', 'C003', 'A013', 'Thám tử lừng danh Conan', 'Shōnen Sunday', 1994, 'Thám tử lừng danh Conan.jpg', 
'Hành trình trinh thám ly kỳ của thiên tài học đường Kudo Shinichi sau khi bị tổ chức áo đen ép uống thuốc độc teo nhỏ thành đứa trẻ 7 tuổi Edogawa Conan. Bằng óc suy luận sắc bén, cậu âm thầm phá giải hàng loạt vụ án hóc búa để tìm cách vạch trần tổ chức bí ẩn.'),

('ISBN024', 'C003', 'A014', 'Bảy viên ngọc rồng', 'Weekly Shōnen Jump', 1984, 'Bảy viên ngọc rồng.jpg', 
'Tác phẩm định hình dòng truyện tranh hành động shounen, bắt đầu từ chuyến tầm ngọc rồng của cậu bé đuôi khỉ Son Goku và Bulma. Mạch truyện mở rộng thành bản anh hùng ca hoành tráng khi Goku cùng các chiến binh Z tham gia vào những trận chiến bảo vệ vũ trụ, đề cao tinh thần thượng võ.'),

('ISBN025', 'C003', 'A015', 'Đảo hải tặc', 'Weekly Shōnen Jump', 1997, 'Đảo hải tặc.jpg', 
'Bản thiên sử thi vĩ đại về thế giới đại dương và khát vọng tự do. Truyện theo chân Monkey D. Luffy – cậu bé sở hữu cơ thể co giãn như cao su – cùng băng hải tặc Mũ Rơm vượt qua muôn vàn vùng biển nguy hiểm để tìm kiếm kho báu huyền thoại One Piece và trở thành Vua Hải Tặc.'),

('ISBN026', 'C003', 'A016', 'Dũng sĩ Hesman', 'NXB Trẻ', 1992, 'Dũng sĩ Hesman.jpg', 
'Hiện tượng của làng truyện tranh Việt Nam thập niên 90 lấy bối cảnh giả tưởng ngoài vũ trụ. Truyện khắc họa những trận chiến không gian kịch tính của kíp trưởng Gat-cô và các đồng đội khi điều khiển siêu robot khổng lồ Hesman để đấu tranh bảo vệ hòa bình thiên hà.'),

('ISBN027', 'C003', 'A017', 'Tý Quậy', 'NXB Trẻ', 2003, 'Tý Quậy.jpg', 
'Bức tranh sinh động, hóm hỉnh về đời sống học đường của trẻ em Việt Nam thời kỳ đổi mới. Xoay quanh cặp bài trùng Tý và Tèo tinh nghịch, bộ truyện mang lại tiếng cười sảng khoái qua những tình huống dở khóc dở cười về học hành, thi cử và các bài học giáo dục nhẹ nhàng.'),

('ISBN028', 'C003', 'A018', 'Naruto', 'Weekly Shōnen Jump', 1999, 'Naruto.jpg', 
'Hành trình vươn lên lay động lòng người của Uzumaki Naruto, cậu bé mồ côi mang trong mình phong ấn Cửu Vĩ bị cả làng ghẻ lạnh. Bằng nỗ lực không ngừng và trái tim thuần khiết, Naruto từng bước chinh phục đỉnh cao danh hiệu Hokage, xóa bỏ vòng lặp của hận thù thế giới ninja.'),

('ISBN029', 'C003', 'A019', 'Thanh gươm diệt quỷ', 'Weekly Shōnen Jump', 2016, 'Thanh gươm diệt quỷ.jpg', 
'Cơn sốt truyện tranh thế hệ mới lấy bối cảnh thời kỳ Taisho tại Nhật Bản. Sau khi gia đình bị quỷ tàn sát, cậu thiếu niên hiền lành Kamado Tanjiro gia nhập Sát Quỷ Đoàn để tìm cách biến em gái Nezuko trở lại thành người, mở ra những trận chiến sinh tử đầy cảm xúc.'),

('ISBN030', 'C003', 'A020', 'Nhóc Maruko', 'Ribon', 1986, 'Nhóc Maruko.jpg', 
'Những lát cắt bình dị, ngọt ngào về cuộc sống đời thường của cô bé lớp 3 Sakura Momoko (Maruko). Sống trong gia đình ba thế hệ thuộc tầng lớp lao động tại Nhật Bản, sự lười biếng đáng yêu và ham chơi của Maruko sưởi ấm trái tim độc giả bằng những mẩu chuyện gia đình ấm áp.'),

('ISBN031', 'C004', 'A021', 'Dracula', 'Archibald Constable & Company', 1897, 'Dracula.jpg', 
'Tác phẩm định hình hình tượng ma cà rồng kinh điển của văn học thế giới. Câu chuyện theo chân một nhóm người quả cảm do Giáo sư Van Helsing dẫn đầu trong cuộc truy đuổi và tiêu diệt vị Bá tước tà ác hòng bảo vệ London khỏi thế lực bóng tối.'),

('ISBN032', 'C004', 'A022', 'Victor Frankenstein', 'Lackington, Hughes, Harding, Mavor & Jones', 1818, 'Victor Frankenstein.jpg', 
'Kiệt tác kinh điển tiên phong cho thể loại khoa học viễn tưởng kết hợp kinh dị Gothic. Truyện theo chân nhà khoa học trẻ Victor, người tìm ra bí mật mang lại sự sống cho vật chất vô tri từ các mảnh xác người, dẫn đến chuỗi bi kịch trả thù tàn khốc đầy cô độc.'),

('ISBN033', 'C004', 'A023', 'The Shining', 'Doubleday', 1977, 'The Shining.jpg', 
'Một kiệt tác kinh dị tâm lý đầy ám ảnh về gia đình Jack Torrance khi nhận việc trông coi khách sạn Overlook biệt lập trên núi tuyết. Nơi đây chứa đựng những linh hồn tà ác âm thầm thao túng tâm trí Jack, đẩy gia đình vào mối đe dọa sinh tử kinh hoàng.'),

('ISBN034', 'C004', 'A024', 'Ring', 'Kadokawa Shoten', 1991, 'Ring.jpg', 
'Tác phẩm mở đầu cho làn sóng kinh dị J-Horror toàn cầu, bắt đầu từ lời nguyền chết chóc trong vòng bảy ngày của một cuốn băng video kỳ lạ. Để tự cứu mình và gia đình, nhà báo Asakawa phải chạy đua với thời gian giải mã oán hận của linh hồn Sadako dưới lòng giếng sâu.'),

('ISBN035', 'C004', 'A025', 'The Exorcist', 'Harper & Row', 1971, 'The Exorcist.jpg', 
'Cuốn tiểu thuyết lấy cảm hứng từ sự kiện có thật, khai thác ranh giới mong manh giữa đức tin và y học. Truyện xoay quanh cô bé 12 tuổi Regan với những biểu hiện tâm thần thể xác kinh hoàng, buộc hai linh mục phải thực hiện nghi lễ trừ tà cổ xưa chống lại thực thể quỷ dữ.'),

('ISBN036', 'C004', 'A026', 'The Haunting of Hill House', 'Viking Press', 1959, 'The Haunting of Hill House.jpg', 
'Tác phẩm mẫu mực của thể loại nhà ma và kinh dị tâm lý. Theo chân một nhóm người đến sống tại dinh thự cổ kính Hill House để tìm kiếm bằng chứng tâm linh, tác phẩm bóp nghẹt tâm trí độc giả khi ngôi nhà dần cô lập và thao túng sự tổn thương tinh thần của nhân vật.'),

('ISBN037', 'C004', 'A027', 'Another', 'Kadokawa Shoten', 2009, 'Another.jpg', 
'Tiểu thuyết kinh dị học đường Nhật Bản đầy lôi cuốn xoay quanh một lớp học vướng phải lời nguyền rùng rợn từ quá khứ: "Luôn có một người chết trộn lẫn vào sĩ số". Những tai nạn thảm khốc liên tiếp xảy ra buộc các học sinh phải tìm ra "người thừa" trước khi quá muộn.'),

('ISBN038', 'C004', 'A028', 'The Call of Cthulhu', 'Weird Tales', 1928, 'The Call of Cthulhu.jpg', 
'Tác phẩm nền tảng định hình nên vũ trụ kinh dị Cosmic Horror của Lovecraft. Khai thác những tài liệu về một giáo phái bí ẩn thờ phụng quái thú cổ xưa Cthulhu dưới thành phố chìm R''lyeh, truyện gieo rắc nỗi sợ tột cùng trước sự nhỏ bé của loài người trước vũ trụ điên rồ.'),

('ISBN039', 'C004', 'A029', 'Tết ở làng Địa Ngục', 'NXB Trẻ', 2022, 'Tết ở làng Địa Ngục.jpg', 
'Làn gió mới của văn học kinh dị tâm linh Việt Nam, lấy bối cảnh một ngôi làng hẻo lánh của hậu duệ băng cướp khét tiếng xưa. Vào dịp Tết, những cái chết rùng rợn liên tiếp xảy ra như sự báo oán, lồng ghép khéo léo phong tục và thuật phù thủy dân gian độc đáo.');

SELECT * FROM Books;



INSERT INTO BookCopy (barcode, isbn, status, `condition`)
VALUES
('BC001', 'ISBN001', 'Available', 'Mới'),
('BC002', 'ISBN002', 'Borrowed', 'Tốt'),
('BC003', 'ISBN003', 'Available', 'Mới'),
('BC004', 'ISBN004', 'Lost', 'Cũ'),
('BC005', 'ISBN005', 'Damaged', 'Rách nhẹ'),
('BC006', 'ISBN006', 'Available', 'Tốt'),
('BC007', 'ISBN007', 'Borrowed', 'Tốt'),
('BC008', 'ISBN008', 'Available', 'Mới'),
('BC009', 'ISBN009', 'Available', 'Tốt'),
('BC010', 'ISBN010', 'Borrowed', 'Cũ'),

('BC011', 'ISBN011', 'Available', 'Mới'),
('BC012', 'ISBN012', 'Available', 'Tốt'),
('BC013', 'ISBN013', 'Borrowed', 'Tốt'),
('BC014', 'ISBN014', 'Available', 'Mới'),
('BC015', 'ISBN015', 'Lost', 'Cũ'),
('BC016', 'ISBN016', 'Available', 'Tốt'),
('BC017', 'ISBN017', 'Damaged', 'Rách nhẹ'),
('BC018', 'ISBN018', 'Borrowed', 'Tốt'),
('BC019', 'ISBN019', 'Available', 'Mới'),
('BC020', 'ISBN020', 'Available', 'Tốt'),

('BC021', 'ISBN021', 'Borrowed', 'Tốt'),
('BC022', 'ISBN022', 'Available', 'Mới'),
('BC023', 'ISBN023', 'Available', 'Tốt'),
('BC024', 'ISBN024', 'Lost', 'Cũ'),
('BC025', 'ISBN025', 'Available', 'Mới'),
('BC026', 'ISBN026', 'Borrowed', 'Tốt'),
('BC027', 'ISBN027', 'Damaged', 'Rách nhẹ'),
('BC028', 'ISBN028', 'Available', 'Tốt'),
('BC029', 'ISBN029', 'Borrowed', 'Cũ'),
('BC030', 'ISBN030', 'Available', 'Mới'),

('BC031', 'ISBN031', 'Available', 'Tốt'),
('BC032', 'ISBN032', 'Borrowed', 'Tốt'),
('BC033', 'ISBN033', 'Available', 'Mới'),
('BC034', 'ISBN034', 'Lost', 'Cũ'),
('BC035', 'ISBN035', 'Available', 'Tốt'),
('BC036', 'ISBN036', 'Damaged', 'Rách nhẹ'),
('BC037', 'ISBN037', 'Borrowed', 'Tốt'),
('BC038', 'ISBN038', 'Available', 'Mới'),
('BC039', 'ISBN039', 'Available', 'Tốt');



INSERT INTO Librarian ( librarianId, userId, shift)
VALUES
('L001', 'U005', 'Morning'),
('L002', 'U006', 'Afternoon');

INSERT INTO Reader (readerId, userId, cardExpiryDate, totalBorrowed)
VALUES 
('R001', 'U001', '2026-12-31', 0),
('R002', 'U002', '2026-12-31', 2),
('R003', 'U003', '2026-12-31', 1),
('R004', 'U004', '2026-12-31', 0),
('R005', 'U005', '2026-12-31', 3);

INSERT INTO BookSlip (slipId, readerId, librarianId, borrowDate,dueDate, status)
VALUES
('BS001', 'R001', 'L001', '2026-07-01', '2026-07-10', 'Borrowing'),

('BS002', 'R002', 'L002', '2026-06-20', '2026-06-30', 'Returned'),

('BS003', 'R001', 'L001', '2026-06-01', '2026-06-10', 'Late');



INSERT INTO BorrowDetail (
    slipId,
    barcode,
    returnDate,
    fineAmount,
    note,
    renewalCount
)
VALUES
('BS001', 'BC002', NULL, 0, 'Chưa trả sách', 1),

('BS002', 'BC004', '2026-06-28', 0, 'Trả đúng hạn', 0),

('BS003', 'BC009', NULL, 50000, 'Trễ hạn trả sách', 2);

SELECT * FROM Books LIMIT 1;


SELECT
    b.isbn,
    b.title,
    a.authorName,
    c.categoryId,
    b.publishYear,
    b.imageUrl,
    b.description
FROM Books b
JOIN Author a
    ON b.authorId = a.authorId
JOIN Category c
    ON b.categoryId = c.categoryId
ORDER BY c.categoryId, b.title;


SELECT * FROM Books LIMIT 5;
SELECT * FROM Author LIMIT 5;
SELECT * FROM Category LIMIT 5;