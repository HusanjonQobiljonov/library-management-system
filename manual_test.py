from connect_dp import DatabaseConnection
from books import BookManager
from user import UserManager
from borrow import BorrowingManager


def run_all_tests():
    test_db = DatabaseConnection(database="library_db")
    test_db.initialize_database(reset=True)

    book_mgr = BookManager(test_db)
    user_mgr = UserManager(test_db)
    borrow_mgr = BorrowingManager(test_db)

    print("🧪 TESTING LIBRARY MANAGEMENT SYSTEM")
    print("=" * 50)

    print("\n1️⃣ TEST: Invalid inputs")
    try:
        book_mgr.create_book("", "Author", "Fiction", 2024)
        print("❌ FAIL: Empty title was accepted.")
    except Exception as e:
        print(f"✅ PASS: {e}")

    print("\n2️⃣ TEST: Borrow unavailable book")
    user_mgr.create_user("Test User", "test@example.com", "student")
    book_id = book_mgr.create_book("Unavailable", "Author", "Fiction", 2024)

    borrow_mgr.borrow_book("test@example.com", book_id)
    try:
        borrow_mgr.borrow_book("test@example.com", book_id)
        print("❌ FAIL: Borrowed unavailable book.")
    except Exception as e:
        print(f"✅ PASS: {e}")

    print("\n3️⃣ TEST: Return borrowed book")
    try:
        borrow_mgr.return_book("test@example.com")
        print("✅ PASS: Book returned successfully.")
    except Exception as e:
        print(f"❌ FAIL: {e}")

    print("\n4️⃣ TEST: Search books")
    try:
        book_mgr.create_book("Harry Potter Test", "J. K. Rowling", "Fantasy", 2020)
        book_mgr.create_book("Python Basics", "Programmer", "Education", 2021)
        results = book_mgr.search_books("Harry")
        if results:
            print("✅ PASS: Search returned results.")
            for book in results[:3]:
                print(f"   - {book['title']} by {book['author']}")
        else:
            print("❌ FAIL: Search returned no results.")
    except Exception as e:
        print(f"❌ FAIL: {e}")

    print("\n5️⃣ TEST: Duplicate user email")
    try:
        user_mgr.create_user("Duplicate User", "dup@example.com", "student")
        try:
            user_mgr.create_user("Duplicate Again", "dup@example.com", "student")
            print("❌ FAIL: Duplicate email was accepted.")
        except Exception as e:
            print(f"✅ PASS: {e}")
    except Exception as e:
        print(f"❌ FAIL: {e}")

    print("\n6️⃣ TEST: View all borrowings")
    try:
        borrowings = borrow_mgr.view_borrowings()
        if borrowings:
            print("✅ PASS: Borrowings found.")
            for b in borrowings[:5]:
                print(f"   - {b}")
        else:
            print("⚠️ No borrowings found.")
    except Exception as e:
        print(f"❌ FAIL: {e}")

    print("\n7️⃣ TEST: Delete protected user")
    try:
        user_mgr.create_user("Protected User", "protected@example.com", "student")
        protected_book_id = book_mgr.create_book("Protected Book", "Author", "Drama", 2024)
        borrow_mgr.borrow_book("protected@example.com", protected_book_id)

        user = user_mgr.get_user_by_email("protected@example.com")
        try:
            user_mgr.delete_user(user["user_id"])
            print("❌ FAIL: Deleted user with active borrowing.")
        except Exception as e:
            print(f"✅ PASS: {e}")
    except Exception as e:
        print(f"❌ FAIL: {e}")

    print("\n8️⃣ TEST: Delete protected book")
    try:
        user_mgr.create_user("Book Protector", "bookprotector@example.com", "student")
        protected_book_id_2 = book_mgr.create_book("Do Not Delete", "Author", "Mystery", 2024)
        borrow_mgr.borrow_book("bookprotector@example.com", protected_book_id_2)

        try:
            book_mgr.delete_book(protected_book_id_2)
            print("❌ FAIL: Deleted borrowed book.")
        except Exception as e:
            print(f"✅ PASS: {e}")
    except Exception as e:
        print(f"❌ FAIL: {e}")

    print("\n🎉 Manual test finished!")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()
    input("\n🔍 Manual tests complete! Press Enter to exit...")