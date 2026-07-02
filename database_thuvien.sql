-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: library_management
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `book`
--

DROP TABLE IF EXISTS `book`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `book` (
  `ISBN` varchar(20) NOT NULL,
  `title` varchar(200) NOT NULL,
  `author` varchar(100) DEFAULT NULL,
  `publisher` varchar(100) DEFAULT NULL,
  `publishYear` int DEFAULT NULL,
  `categoryId` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`ISBN`),
  KEY `categoryId` (`categoryId`),
  CONSTRAINT `book_ibfk_1` FOREIGN KEY (`categoryId`) REFERENCES `category` (`categoryId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `book`
--

LOCK TABLES `book` WRITE;
/*!40000 ALTER TABLE `book` DISABLE KEYS */;
INSERT INTO `book` VALUES ('ISBN-123','Tắt đèn','Ngô Tất Tố','NXB Trẻ',2020,'CAT01');
/*!40000 ALTER TABLE `book` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bookcopy`
--

DROP TABLE IF EXISTS `bookcopy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookcopy` (
  `barcode` varchar(50) NOT NULL,
  `status` varchar(50) DEFAULT NULL,
  `book_condition` varchar(100) DEFAULT NULL,
  `ISBN` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`barcode`),
  KEY `ISBN` (`ISBN`),
  CONSTRAINT `bookcopy_ibfk_1` FOREIGN KEY (`ISBN`) REFERENCES `book` (`ISBN`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookcopy`
--

LOCK TABLES `bookcopy` WRITE;
/*!40000 ALTER TABLE `bookcopy` DISABLE KEYS */;
INSERT INTO `bookcopy` VALUES ('BC-001','Borrowed','Mới','ISBN-123'),('BC-002','Available','Rách bìa nhẹ','ISBN-123');
/*!40000 ALTER TABLE `bookcopy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `borrowdetail`
--

DROP TABLE IF EXISTS `borrowdetail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `borrowdetail` (
  `slipId` varchar(20) NOT NULL,
  `barcode` varchar(50) NOT NULL,
  `returnDate` date DEFAULT NULL,
  `fineAmount` double DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  `renewalCount` int DEFAULT NULL,
  PRIMARY KEY (`slipId`,`barcode`),
  KEY `barcode` (`barcode`),
  CONSTRAINT `borrowdetail_ibfk_1` FOREIGN KEY (`slipId`) REFERENCES `borrowslip` (`slipId`) ON DELETE CASCADE,
  CONSTRAINT `borrowdetail_ibfk_2` FOREIGN KEY (`barcode`) REFERENCES `bookcopy` (`barcode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `borrowdetail`
--

LOCK TABLES `borrowdetail` WRITE;
/*!40000 ALTER TABLE `borrowdetail` DISABLE KEYS */;
INSERT INTO `borrowdetail` VALUES ('PM-001','BC-001',NULL,0,'',0),('PM-002','BC-001',NULL,0,'',0);
/*!40000 ALTER TABLE `borrowdetail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `borrowslip`
--

DROP TABLE IF EXISTS `borrowslip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `borrowslip` (
  `slipId` varchar(20) NOT NULL,
  `borrowDate` date DEFAULT NULL,
  `dueDate` date DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `readerId` varchar(20) DEFAULT NULL,
  `employeeId` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`slipId`),
  KEY `readerId` (`readerId`),
  KEY `employeeId` (`employeeId`),
  CONSTRAINT `borrowslip_ibfk_1` FOREIGN KEY (`readerId`) REFERENCES `reader` (`readerId`),
  CONSTRAINT `borrowslip_ibfk_2` FOREIGN KEY (`employeeId`) REFERENCES `librarian` (`employeeId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `borrowslip`
--

LOCK TABLES `borrowslip` WRITE;
/*!40000 ALTER TABLE `borrowslip` DISABLE KEYS */;
INSERT INTO `borrowslip` VALUES ('PM-001','2026-07-02','2026-07-16','Active','R001',NULL),('PM-002','2026-07-03','2026-07-17','Active','R001',NULL);
/*!40000 ALTER TABLE `borrowslip` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `category` (
  `categoryId` varchar(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text,
  PRIMARY KEY (`categoryId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category`
--

LOCK TABLES `category` WRITE;
/*!40000 ALTER TABLE `category` DISABLE KEYS */;
INSERT INTO `category` VALUES ('CAT01','Văn học','Sách văn học Việt Nam');
/*!40000 ALTER TABLE `category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `librarian`
--

DROP TABLE IF EXISTS `librarian`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `librarian` (
  `employeeId` varchar(20) NOT NULL,
  `shift` varchar(50) DEFAULT NULL,
  `username` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`employeeId`),
  KEY `username` (`username`),
  CONSTRAINT `librarian_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `librarian`
--

LOCK TABLES `librarian` WRITE;
/*!40000 ALTER TABLE `librarian` DISABLE KEYS */;
/*!40000 ALTER TABLE `librarian` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reader`
--

DROP TABLE IF EXISTS `reader`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reader` (
  `readerId` varchar(20) NOT NULL,
  `cardExpiryDate` date DEFAULT NULL,
  `totalBorrowed` int DEFAULT NULL,
  `username` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`readerId`),
  KEY `username` (`username`),
  CONSTRAINT `reader_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reader`
--

LOCK TABLES `reader` WRITE;
/*!40000 ALTER TABLE `reader` DISABLE KEYS */;
INSERT INTO `reader` VALUES ('R001','2026-12-31',0,'student01');
/*!40000 ALTER TABLE `reader` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `fullName` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES ('student01','123456','John Doe','john@gmail.com');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-03  0:05:13
