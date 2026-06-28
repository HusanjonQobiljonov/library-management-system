import sys
import mysql.connector
from mysql.connector import Error


class DatabaseConnection:
    def __init__(self, host="localhost", port=3306, user="root", password="root", database="library_db"):
        self.database_name = database
        self.connection_settings = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }

    def connect(self):
        try:
            return mysql.connector.connect(**self.connection_settings)
        except Error as error:
            print(f"❌ Database connection error: {error}")
            return None

    def initialize_database(self, reset=False):
        try:
            bootstrap_connection = mysql.connector.connect(
                host=self.connection_settings["host"],
                port=self.connection_settings["port"],
                user=self.connection_settings["user"],
                password=self.connection_settings["password"],
            )
            bootstrap_cursor = bootstrap_connection.cursor()
            bootstrap_cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {self.database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            bootstrap_connection.close()

            connection = self.connect()
            if not connection:
                return

            cursor = connection.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS books (
                    book_id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    genre VARCHAR(100) NOT NULL,
                    year INT NOT NULL,
                    available BOOLEAN NOT NULL DEFAULT TRUE,
                    CONSTRAINT chk_year CHECK (year >= 1000 AND year <= 2100)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    role ENUM('student','staff','faculty') NOT NULL DEFAULT 'student'
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS borrowings (
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
                )
                """
            )

            if reset:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                cursor.execute("TRUNCATE TABLE borrowings")
                cursor.execute("TRUNCATE TABLE users")
                cursor.execute("TRUNCATE TABLE books")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                print("✅ Tables reset successfully.")

            cursor.execute("SELECT COUNT(*) FROM books")
            if cursor.fetchone()[0] == 0:
                sample_books = [
                    ("Animal Farm", "George Orwell", "Political Satire", 1945, True),
                    ("1984", "George Orwell", "Dystopian", 1949, True),
                    ("Harry Potter and the Philosopher's Stone", "J. K. Rowling", "Fantasy", 1997, True),
                    ("Harry Potter and the Chamber of Secrets", "J. K. Rowling", "Fantasy", 1998, True),
                    ("Harry Potter and the Prisoner of Azkaban", "J. K. Rowling", "Fantasy", 1999, True),
                    ("Harry Potter and the Goblet of Fire", "J. K. Rowling", "Fantasy", 2000, True),
                    ("Moby-Dick", "Herman Melville", "Adventure", 1851, True),
                    ("Brave New World", "Aldous Huxley", "Dystopian", 1932, True),
                    ("The Hobbit", "J.R.R. Tolkien", "Fantasy", 1937, True),
                    ("Crime and Punishment", "Fyodor Dostoevsky", "Classic", 1866, True),
                    ('White Nights','Fyodor Dostoevsky',"Novel",1848,True)
                ]
                cursor.executemany(
                    "INSERT INTO books (title, author, genre, year, available) VALUES (%s, %s, %s, %s, %s)",
                    sample_books,
                )

            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                sample_users = [
                    ("John Smith", "john.smith@example.com", "student"),
                    ("Emma Johnson", "emma.johnson@example.com", "student"),
                    ("Michael Brown", "michael.brown@example.com", "staff"),
                    ("Sophia Davis", "sophia.davis@example.com", "faculty"),
                    ("Daniel Wilson", "daniel.wilson@example.com", "student"),
                ]
                cursor.executemany(
                    "INSERT INTO users (name, email, role) VALUES (%s, %s, %s)",
                    sample_users,
                )

            connection.commit()
            connection.close()
            print("✅ Database, tables, and sample data initialized successfully!")

        except Error as error:
            print(f"❌ Initialization error: {error}")
            sys.exit(1)
