-- Database minicloud (giữ nguyên)
CREATE DATABASE IF NOT EXISTS minicloud;
USE minicloud;
CREATE TABLE IF NOT EXISTS notes(
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO notes(title) VALUES ('Hello from MariaDB!');

-- Tạo database studentdb (yêu cầu mới)
CREATE DATABASE IF NOT EXISTS studentdb;
USE studentdb;

-- Tạo bảng students với đầy đủ các trường theo yêu cầu
CREATE TABLE IF NOT EXISTS students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(10) UNIQUE NOT NULL,
    fullname VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    major VARCHAR(50) NOT NULL
);

-- Chèn ít nhất 3 bản ghi mẫu
INSERT INTO students (student_id, fullname, dob, major) VALUES
('SV001', 'Nguyễn Văn A', '2000-05-15', 'Computer Science'),
('SV002', 'Trần Thị B', '2001-08-22', 'Electrical Engineering'),
('SV003', 'Lê Văn C', '1999-12-30', 'Business Administration');
