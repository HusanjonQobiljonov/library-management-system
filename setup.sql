DROP DATABASE IF EXISTS library_db;
CREATE DATABASE library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE library_db;

CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    available BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_year CHECK (year >= 1000 AND year <= 2100)
);

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role ENUM('student','staff','faculty') NOT NULL DEFAULT 'student'
);

CREATE TABLE borrowings (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    borrow_date DATE NOT NULL,
    return_date DATE DEFAULT NULL,
    CONSTRAINT fk_borrowing_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_borrowing_book FOREIGN KEY (book_id)
        REFERENCES books(book_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_return_date CHECK (return_date IS NULL OR return_date >= borrow_date)
);

INSERT INTO books (title, author, genre, year, available) VALUES
('Animal Farm', 'George Orwell', 'Political Satire', 1945, TRUE),
('1984', 'George Orwell', 'Dystopian', 1949, TRUE),
('Harry Potter and the Philosopher''s Stone', 'J. K. Rowling', 'Fantasy', 1997, TRUE),
('Harry Potter and the Chamber of Secrets', 'J. K. Rowling', 'Fantasy', 1998, TRUE),
('Harry Potter and the Prisoner of Azkaban', 'J. K. Rowling', 'Fantasy', 1999, TRUE),
('Harry Potter and the Goblet of Fire', 'J. K. Rowling', 'Fantasy', 2000, TRUE),
('Moby-Dick', 'Herman Melville', 'Adventure', 1851, TRUE),
('Brave New World', 'Aldous Huxley', 'Dystopian', 1932, TRUE),
('The Hobbit', 'J.R.R. Tolkien', 'Fantasy', 1937, TRUE),
('Crime and Punishment', 'Fyodor Dostoevsky', 'Classic', 1866, TRUE),
('White Nights', 'Fyodor Dostoevsky', 'Novel', 1848, TRUE);

INSERT INTO users (name, email, role) VALUES
('John Smith', 'john.smith@example.com', 'student'),
('Emma Johnson', 'emma.johnson@example.com', 'student'),
('Michael Brown', 'michael.brown@example.com', 'staff'),
('Sophia Davis', 'sophia.davis@example.com', 'faculty'),
('Daniel Wilson', 'daniel.wilson@example.com', 'student');