from check_input import (
    validate_non_empty_text,
    validate_sort_direction,
    validate_sort_field,
    validate_year,
)


class Book:
    """Represents a single book object in the library system."""

    def __init__(self, book_id, title, author, genre, year, available=True):
        """Initializes a Book object with its main details."""
        self.book_id = book_id
        self.title = title
        self.author = author
        self.genre = genre
        self.year = year
        self.available = available

    def __str__(self):
        """Returns a readable string version of the book."""
        availability_label = "Available" if self.available else "Borrowed"
        return f"[{self.book_id}] {self.title} by {self.author} | Genre: {self.genre} | Year: {self.year} | {availability_label}"


class BookManager:
    """Handles all book-related database operations."""

    def __init__(self, database_connection):
        """Stores the database connection object for reuse."""
        self.database_connection = database_connection

    def create_book(self, title, author, genre, year):
        """Validates and inserts a new book into the database."""
        book_title = validate_non_empty_text(title, "Title")
        book_author = validate_non_empty_text(author, "Author")
        book_genre = validate_non_empty_text(genre, "Genre")
        published_year = validate_year(year)

        connection = self.database_connection.connect()
        if not connection:
            return None

        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO books (title, author, genre, year, available) VALUES (%s, %s, %s, %s, %s)",
                (book_title, book_author, book_genre, published_year, True),
            )
            connection.commit()
            new_book_id = cursor.lastrowid
            print("✅ Book created successfully.")
            return new_book_id
        finally:
            cursor.close()
            connection.close()

    def add_book(self, title, author, year, genre="General"):
        """Calls create_book for compatibility with older code."""
        return self.create_book(title, author, genre, year)

    def get_all_books(self):
        """Fetches and returns all book records from the database."""
        connection = self.database_connection.connect()
        if not connection:
            return []

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM books")
            return cursor.fetchall()
        finally:
            cursor.close()
            connection.close()

    def get_book_by_id(self, book_id):
        """Returns one book record that matches the given ID."""
        connection = self.database_connection.connect()
        if not connection:
            return None

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            connection.close()

    def view_books(self):
        """Returns Book objects (unchanged for compatibility)."""
        rows = self.get_all_books()
        return [
            Book(
                row["book_id"],
                row["title"],
                row["author"],
                row.get("genre", "General"),
                row["year"],
                row["available"],
            )
            for row in rows
        ]

    def view_books_formatted(self):
        """Displays the book list in a clean formatted table."""
        books = self.view_books()

        print("\n" + "═" * 90)
        print("📚" + " " * 38 + "LIBRARY CATALOG" + " " * 38 + "📚")
        print("═" * 90)

        available_count = sum(1 for b in books if b.available)
        total_count = len(books)

        print(
            f"📊 Total: {total_count:2d} books | ✅ Available: {available_count:2d} | 🔴 Borrowed: {total_count - available_count:2d}")
        print("─" * 90)

        for i, book in enumerate(books, 1):
            status = "✅ AVAILABLE" if book.available else "🔴 BORROWED"
            status_color = "🟢" if book.available else "🔴"
            print(
                f"{i:2d}. {status_color} {status:<10} │ {book.title:<38} │ {book.author:<18} │ {book.genre:<12} │ {book.year:4d}")

        print("─" * 90)
        print("═" * 90)
        print()

    def search_books_by_keywords(self, keyword_text):
        """Searches books by up to three keywords in title, author, or genre."""
        keyword_text = validate_non_empty_text(keyword_text, "Search text")
        keywords = keyword_text.split()[:3]

        connection = self.database_connection.connect()
        if not connection:
            return []

        cursor = connection.cursor(dictionary=True)
        try:
            where_parts = []
            parameters = []
            for keyword in keywords:
                where_parts.append("(title LIKE %s OR author LIKE %s OR genre LIKE %s)")
                parameters.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

            query = "SELECT * FROM books WHERE " + " OR ".join(where_parts)
            cursor.execute(query, parameters)
            return cursor.fetchall()
        finally:
            cursor.close()
            connection.close()

    def search_books(self, keywords):
        """Calls keyword search method for compatibility with other code."""
        return self.search_books_by_keywords(keywords)

    def update_book_details(self, book_id, title, author, genre, year):
        """Validates and updates a book record by its ID."""
        updated_title = validate_non_empty_text(title, "Title")
        updated_author = validate_non_empty_text(author, "Author")
        updated_genre = validate_non_empty_text(genre, "Genre")
        updated_year = validate_year(year)

        connection = self.database_connection.connect()
        if not connection:
            return False

        cursor = connection.cursor()
        try:
            cursor.execute("SELECT book_id FROM books WHERE book_id = %s", (book_id,))
            if not cursor.fetchone():
                raise ValueError("Book not found.")

            cursor.execute(
                "UPDATE books SET title=%s, author=%s, genre=%s, year=%s WHERE book_id=%s",
                (updated_title, updated_author, updated_genre, updated_year, book_id),
            )
            connection.commit()
            print("✅ Book updated successfully.")
            return True
        finally:
            cursor.close()
            connection.close()

    def update_book(self, book_id, title, author, year, genre="General"):
        """Calls update_book_details to keep older method name working."""
        return self.update_book_details(book_id, title, author, genre, year)

    def remove_book(self, book_id):
        """Deletes a book if it has no active borrowing records."""
        connection = self.database_connection.connect()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "SELECT record_id FROM borrowings WHERE book_id = %s AND return_date IS NULL",
                (book_id,)
            )
            if cursor.fetchone():
                raise ValueError("Cannot delete this book because borrowing records already exist.")

            cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
            connection.commit()
            print("✅ Book deleted successfully.")
            return True
        finally:
            cursor.close()
            connection.close()

    def delete_book(self, book_id):
        """Calls remove_book for compatibility with older code."""
        return self.remove_book(book_id)

    def sort_books_python(self, sort_field, direction):
        """Sorts selected books in Python using field and direction."""
        validated_field = validate_sort_field(sort_field)
        validated_direction = validate_sort_direction(direction)
        reverse_order = validated_direction == "desc"

        books = self.get_all_books()

        if len(books) >= 2:
            books = books[-2:]

        return sorted(books, key=lambda current_book: current_book[validated_field], reverse=reverse_order)

    def display_books(self):
        """Displays all books in a formatted table for the user."""
        rows = self.get_all_books()
        if not rows:
            print("\n❌ No books found.")
            return

        print("\n" + "=" * 92)
        print("📚 LIBRARY BOOKS".center(92))
        print("=" * 92)
        print(f"{'No.':<4} {'Status':<10} {'Title':<30} {'Author':<20} {'Genre':<12} {'Year':<6}")
        print("-" * 92)

        for i, book in enumerate(rows, start=1):
            status = "✅ AVAILABLE" if book["available"] else "🔴 BORROWED"
            print(
                f"{i:<4} "
                f"{status:<10} "
                f"{book['title']:<30} "
                f"{book['author']:<20} "
                f"{book['genre']:<12} "
                f"{book['year']:<6}"
            )

        print("=" * 92)

    def sort_books_sql(self, sort_field, direction):
        """Retrieves books and sorts them using SQL-related settings."""
        validated_field = validate_sort_field(sort_field)
        validated_direction = validate_sort_direction(direction).upper()

        connection = self.database_connection.connect()
        if not connection:
            return []

        cursor = connection.cursor(dictionary=True)
        try:
            query = f"SELECT * FROM books ORDER BY book_id DESC LIMIT 2"
            cursor.execute(query)
            rows = cursor.fetchall()
            rows.reverse()
            sorted_rows = sorted(
                rows,
                key=lambda current_book: current_book[validated_field],
                reverse=(validated_direction == "DESC"),
            )
            return sorted_rows
        finally:
            cursor.close()
            connection.close()