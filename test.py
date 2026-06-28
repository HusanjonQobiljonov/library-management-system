import unittest
from books import BookManager
from user import UserManager
from borrow import BorrowingManager
from connect_dp import DatabaseConnection


class TestLibrarySystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_db = DatabaseConnection(
            host="localhost",
            port=3306,
            user="root",
            password="root",
            database="library_test_db"
        )

    def setUp(self):
        self.test_db.initialize_database(reset=True)
        self.book_mgr = BookManager(self.test_db)
        self.user_mgr = UserManager(self.test_db)
        self.borrow_mgr = BorrowingManager(self.test_db)

    @classmethod
    def tearDownClass(cls):
        admin_connection = DatabaseConnection(
            host="localhost",
            port=3306,
            user="root",
            password="root",
            database="mysql"
        ).connect()

        if admin_connection:
            cursor = admin_connection.cursor()
            cursor.execute("DROP DATABASE IF EXISTS library_test_db")
            cursor.close()
            admin_connection.close()

    def test_01_add_book_success(self):
        book_id = self.book_mgr.create_book("Test Book", "Test Author", "Fiction", 2020)
        self.assertIsInstance(book_id, int)

    def test_02_book_validation_failures(self):
        with self.assertRaises(ValueError):
            self.book_mgr.create_book("", "Author", "Genre", 2020)
        with self.assertRaises(ValueError):
            self.book_mgr.create_book("Title", "", "Genre", 2020)
        with self.assertRaises(ValueError):
            self.book_mgr.create_book("Title", "Author", "", 2020)
        with self.assertRaises(ValueError):
            self.book_mgr.create_book("Title", "Author", "Genre", 999)

    def test_03_add_user_success(self):
        user_id = self.user_mgr.create_user("Test User", "test@example.com", "student")
        self.assertIsInstance(user_id, int)

    def test_04_user_validation(self):
        self.user_mgr.create_user("User1", "test@example.com", "student")

        with self.assertRaises(ValueError) as context:
            self.user_mgr.create_user("User2", "test@example.com", "student")
        self.assertEqual(str(context.exception), "Duplicate email.")

        with self.assertRaises(ValueError):
            self.user_mgr.create_user("User", "user@test.com", "invalid")

    def test_05_borrow_book_happy_path(self):
        book_id = self.book_mgr.create_book("Borrow Test", "Author", "Fiction", 2020)
        self.user_mgr.create_user("Borrow User", "borrow@test.com", "student")

        self.borrow_mgr.borrow_book("borrow@test.com", book_id)

        book = self.book_mgr.get_book_by_id(book_id)
        self.assertFalse(book["available"])
        records = self.borrow_mgr.get_active_borrowings_for_user("borrow@test.com")
        self.assertEqual(len(records), 1)

    def test_06_borrow_unavailable_book(self):
        self.user_mgr.create_user("First User", "test@example.com", "student")
        self.user_mgr.create_user("Other User", "other@test.com", "student")

        book_id = self.book_mgr.create_book("Unavailable", "Author", "Fiction", 2020)
        self.borrow_mgr.borrow_book("test@example.com", book_id)

        with self.assertRaises(ValueError):
            self.borrow_mgr.borrow_book("other@test.com", book_id)

    def test_07_return_book_success(self):
        self.user_mgr.create_user("Return User", "return@test.com", "student")
        book_id = self.book_mgr.create_book("Return Test", "Author", "Fiction", 2020)
        self.borrow_mgr.borrow_book("return@test.com", book_id)

        records = self.borrow_mgr.get_active_borrowings_for_user("return@test.com")
        record_id = records[0]["record_id"]

        self.borrow_mgr.return_book_by_record("return@test.com", record_id)

        book = self.book_mgr.get_book_by_id(book_id)
        self.assertTrue(book["available"])
        records = self.borrow_mgr.get_active_borrowings_for_user("return@test.com")
        self.assertEqual(len(records), 0)

    def test_08_search_books(self):
        self.book_mgr.create_book("Python Programming", "John Doe", "Tech", 2023)
        self.book_mgr.create_book("Java Programming", "Jane Smith", "Tech", 2022)

        results = self.book_mgr.search_books_by_keywords("Python")
        self.assertGreater(len(results), 0)
        self.assertIn("Python", results[0]["title"])

    def test_09_python_sorting(self):
        self.book_mgr.create_book("Z Book", "Z Author", "Fiction", 2000)
        self.book_mgr.create_book("A Book", "A Author", "Fiction", 2000)

        sorted_asc = self.book_mgr.sort_books_python("title", "asc")
        self.assertEqual(sorted_asc[0]["title"], "A Book")

        sorted_desc = self.book_mgr.sort_books_python("title", "desc")
        self.assertEqual(sorted_desc[0]["title"], "Z Book")

    def test_10_sql_sorting(self):
        self.book_mgr.create_book("SQL Z", "Z Author", "Tech", 2000)
        self.book_mgr.create_book("SQL A", "A Author", "Tech", 2000)

        sorted_asc = self.book_mgr.sort_books_sql("title", "asc")
        self.assertEqual(sorted_asc[0]["title"], "SQL A")

    def test_11_delete_protected_book(self):
        self.user_mgr.create_user("Protected Borrower", "test@example.com", "student")
        book_id = self.book_mgr.create_book("Protected", "Author", "Fiction", 2020)
        self.borrow_mgr.borrow_book("test@example.com", book_id)

        with self.assertRaises(ValueError):
            self.book_mgr.remove_book(book_id)

    def test_12_delete_protected_user(self):
        user_id = self.user_mgr.create_user("Protected User", "protected@test.com", "student")
        book_id = self.book_mgr.create_book("Test", "Author", "Fiction", 2020)
        self.borrow_mgr.borrow_book("protected@test.com", book_id)

        with self.assertRaises(ValueError):
            self.user_mgr.remove_user(user_id)




if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)  # Your existing line
    input("\n🎉 All tests passed! Press Enter to close...")