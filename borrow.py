class BorrowingManager:
    """Handles borrowing and returning operations for library books."""

    def __init__(self, db):
        """Stores the database connection object for borrowing operations."""
        self.db = db

    def borrow_book(self, email, book_id):
        """Borrows a book for a user if the user and book are valid."""
        connection = self.db.connect()
        if not connection:
            return False

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s",
                (email,)
            )
            user = cursor.fetchone()
            if not user:
                raise ValueError(f"No user found with email {email}.")

            cursor.execute(
                "SELECT book_id, title, available FROM books WHERE book_id = %s",
                (book_id,)
            )
            book = cursor.fetchone()
            if not book:
                raise ValueError(f"No book found with ID {book_id}.")

            if not bool(book["available"]):
                raise ValueError(f"The book '{book['title']}' is already borrowed.")

            cursor.execute(
                """
                INSERT INTO borrowings (user_id, book_id, borrow_date, return_date)
                VALUES (%s, %s, CURDATE(), NULL)
                """,
                (user["user_id"], book["book_id"])
            )

            cursor.execute(
                "UPDATE books SET available = 0 WHERE book_id = %s",
                (book["book_id"],)
            )

            connection.commit()
            print(f"✅ {email} borrowed '{book['title']}' successfully.")
            return True

        finally:
            cursor.close()
            connection.close()

    def get_active_borrowings_for_user(self, email):
        """Returns all active borrowing records for the given user email."""
        connection = self.db.connect()
        if not connection:
            return []

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s",
                (email,)
            )
            user = cursor.fetchone()
            if not user:
                return []

            cursor.execute(
                """
                SELECT
                    b.record_id,
                    b.book_id,
                    bk.title,
                    b.borrow_date,
                    b.return_date
                FROM borrowings b
                JOIN books bk ON b.book_id = bk.book_id
                WHERE b.user_id = %s AND b.return_date IS NULL
                ORDER BY b.record_id DESC
                """,
                (user["user_id"],)
            )
            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def display_borrowings(self):
        """Displays all borrowing records in a formatted table."""
        connection = self.db.connect()
        if not connection:
            print("\n❌ Could not connect to database.")
            return

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    b.record_id,
                    u.name AS user_name,
                    u.email,
                    bk.title AS book_title,
                    b.borrow_date,
                    b.return_date
                FROM borrowings b
                JOIN users u ON b.user_id = u.user_id
                JOIN books bk ON b.book_id = bk.book_id
                ORDER BY b.record_id ASC
                """
            )
            rows = cursor.fetchall()

            if not rows:
                print("\n❌ No borrowing records found.")
                return

            print("\n" + "=" * 130)
            print("📋 BORROWING RECORDS".center(130))
            print("=" * 130)
            print(
                f"{'No.':<4} {'User':<20} {'Email':<30} {'Book':<30} {'Borrow Date':<12} {'Return Date':<12} {'Status':<15}")
            print("-" * 130)

            for i, row in enumerate(rows, start=1):
                status = "🔴 ACTIVE" if row["return_date"] is None else "✅ RETURNED"
                return_date = str(row["return_date"]) if row["return_date"] else "N/A"

                print(
                    f"{i:<4} "
                    f"{row['user_name']:<20} "
                    f"{row['email']:<30} "
                    f"{row['book_title']:<30} "
                    f"{str(row['borrow_date']):<12} "
                    f"{return_date:<12} "
                    f"{status:<15}"
                )

            print("=" * 130)

        finally:
            cursor.close()
            connection.close()

    def return_book(self, email):
        """Returns all active borrowed books for the given user."""
        active_records = self.get_active_borrowings_for_user(email)
        if not active_records:
            raise ValueError("No active borrowings found.")

        for record in active_records:
            self.return_book_by_record(email, record["record_id"])

        return True

    def return_book_by_record(self, email, record_id):
        """Returns a specific borrowed book record for the user."""
        connection = self.db.connect()
        if not connection:
            return False

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s",
                (email,)
            )
            user = cursor.fetchone()
            if not user:
                raise ValueError(f"No user found with email {email}.")

            cursor.execute(
                """
                SELECT
                    b.record_id,
                    b.book_id,
                    bk.title
                FROM borrowings b
                JOIN books bk ON b.book_id = bk.book_id
                WHERE b.record_id = %s
                  AND b.user_id = %s
                  AND b.return_date IS NULL
                """,
                (record_id, user["user_id"])
            )
            record = cursor.fetchone()

            if not record:
                raise ValueError("Active borrowing record not found.")

            cursor.execute(
                "UPDATE borrowings SET return_date = CURDATE() WHERE record_id = %s",
                (record["record_id"],)
            )

            cursor.execute(
                "UPDATE books SET available = 1 WHERE book_id = %s",
                (record["book_id"],)
            )

            connection.commit()
            print(f"✅ '{record['title']}' returned successfully.")
            return True

        finally:
            cursor.close()
            connection.close()

    def view_borrowings(self):
        """Returns borrowing records as formatted text lines."""
        connection = self.db.connect()
        if not connection:
            return []

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    b.record_id,
                    u.name AS user_name,
                    u.email,
                    bk.title AS book_title,
                    b.borrow_date,
                    b.return_date
                FROM borrowings b
                JOIN users u ON b.user_id = u.user_id
                JOIN books bk ON b.book_id = bk.book_id
                ORDER BY b.record_id ASC
                """
            )
            results = cursor.fetchall()

            borrowing_records = []
            for row in results:
                status = (
                    f"Returned on {row['return_date']}"
                    if row["return_date"]
                    else "Currently borrowed"
                )
                borrowing_records.append(
                    f"[{row['record_id']}] {row['user_name']} ({row['email']}) "
                    f"borrowed '{row['book_title']}' on {row['borrow_date']} - {status}"
                )
            return borrowing_records

        finally:
            cursor.close()
            connection.close()

    def get_all_borrowing_records(self):
        """Calls view_borrowings for compatibility with other code."""
        return self.view_borrowings()


Borrowing_Manager = BorrowingManager