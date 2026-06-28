from books import BookManager
from borrow import BorrowingManager
from user import UserManager
from connect_dp import DatabaseConnection
from check_input import (
    validate_email_address,
    validate_non_empty_text,
    validate_positive_integer,
    validate_sort_direction,
    validate_sort_field,
    validate_user_role,
    validate_year,
)


def prompt_database_configuration():
    print("\n--- Database Configuration ---")
    host_name = input("Enter host (default localhost): ").strip() or "localhost"
    port_number = input("Enter port (default 3306): ").strip() or "3306"
    username = input("Enter user (default root): ").strip() or "root"
    password = input("Enter password (default root): ").strip() or "root"
    database_name = input("Enter database name (default library_db): ").strip() or "library_db"

    return DatabaseConnection(
        host=host_name,
        port=int(port_number),
        user=username,
        password=password,
        database=database_name,
    )


def print_books(book_list):
    if not book_list:
        print("No books found.")
        return
    for book in book_list:
        print(book)


def print_users(user_list):
    if not user_list:
        print("No users found.")
        return
    for user in user_list:
        print(user)


def print_borrowings(record_list):
    if not record_list:
        print("No borrowing records found.")
        return
    for record in record_list:
        print(record)


def run_library_menu():
    database_connection = prompt_database_configuration()
    database_connection.initialize_database()

    book_manager = BookManager(database_connection)
    user_manager = UserManager(database_connection)
    borrowing_manager = BorrowingManager(database_connection)

    while True:
        print("\n=== Library Management System ===")
        print("1. Add book")
        print("2. View books")
        print("3. Search books (up to 3 keywords)")
        print("4. Add user")
        print("5. View users")
        print("6. Borrow book")
        print("7. Return book")
        print("8. Update book")
        print("9. Delete book")
        print("10. Update user")
        print("11. Delete user")
        print("12. Show borrowing records")
        print("13. Sort books with Python")
        print("14. Sort books with SQL")
        print("15. Reset database to default data")
        print("16. Exit")

        menu_choice = input("Choose an option: ").strip()

        try:
            if menu_choice == "1":
                title = validate_non_empty_text(input("Title: "), "Title")
                author = validate_non_empty_text(input("Author: "), "Author")
                genre = validate_non_empty_text(input("Genre: "), "Genre")
                year = validate_year(input("Year: "))
                book_manager.create_book(title, author, genre, year)

            elif menu_choice == "2":

                book_manager.view_books_formatted()


            elif menu_choice == "3":
                keyword = input("Enter a keyword: ").strip()
                results = book_manager.search_books(keyword)
                print("═" * 90)
                print(" SEARCH RESULTS ".center(90))
                print("═" * 90)

                if not results:
                    print("❌ No matching books found.")

                else:
                    print(f'{"ID":<4} | {"STATUS":<10} | {"TITLE":<35} | {"AUTHOR":<20} | {"YEAR":<6}')
                    print("─" * 90)

                    for r in results:
                        status = "AVAILABLE" if r["available"] else "BORROWED"
                        print(
                            f'{r["book_id"]:<4} | {status:<10} | {r["title"]:<35.35} | {r["author"]:<20.20} | {r["year"]:<6}')
                print("═" * 90)

            elif menu_choice == "4":  # 4. Add user: validates name, email, role then saves to users table.
                name = validate_non_empty_text(input("Name: "), "Name")
                email = validate_email_address(input("Email: "))
                role = validate_user_role(input("Role (student/staff/faculty): "))
                user_manager.create_user(name, email, role)

            elif menu_choice == "5":
                user_manager.display_users()



            elif menu_choice == "6":

                print("=" * 60)

                print("📚 LIBRARY BOOKS".center(60))

                print("=" * 60)

                book_manager.display_books()

                print("=" * 60)

                email = validate_email_address(input("User email: "))

                book_id = validate_positive_integer(

                    input("Enter the Book ID to borrow: "),

                    "Book ID"

                )

                borrowing_manager.borrow_book(email, book_id)

            elif menu_choice == "7":
                email = validate_email_address(input("User email: "))
                active_records = borrowing_manager.get_active_borrowings_for_user(email)

                if not active_records:
                    print("No active borrowings found for this user.")
                else:
                    print("Active borrowings:")
                    for record in active_records:
                        print(
                            f"Record {record['record_id']} | "
                            f"Book ID {record['book_id']} | "
                            f"{record['title']} | "
                            f"Borrowed on {record['borrow_date']}"
                        )

                    record_id = validate_positive_integer(
                        input("Enter record ID to return: "),
                        "Record ID"
                    )
                    borrowing_manager.return_book_by_record(email, record_id)

            elif menu_choice == "8":
                book_id = validate_positive_integer(input("Book ID to update: "), "Book ID")
                title = validate_non_empty_text(input("New title: "), "Title")
                author = validate_non_empty_text(input("New author: "), "Author")
                genre = validate_non_empty_text(input("New genre: "), "Genre")
                year = validate_year(input("New year: "))
                book_manager.update_book_details(book_id, title, author, genre, year)

            elif menu_choice == "9":
                book_id = validate_positive_integer(input("Book ID to delete: "), "Book ID")
                book_manager.remove_book(book_id)

            elif menu_choice == "10":
                user_id = validate_positive_integer(input("User ID to update: "), "User ID")
                name = validate_non_empty_text(input("New name: "), "Name")
                email = validate_email_address(input("New email: "))
                role = validate_user_role(input("New role (student/staff/faculty): "))
                user_manager.update_user_details(user_id, name, email, role)

            elif menu_choice == "11":
                user_id = validate_positive_integer(input("User ID to delete: "), "User ID")
                user_manager.remove_user(user_id)



            elif menu_choice == "12":
                borrowing_manager.display_borrowings()



            elif menu_choice == "13":

                field = input("Sort by (book_id/title/author/year): ").strip().lower()
                order = input("Order (asc/desc): ").strip().lower()

                if field not in ("book_id", "title", "author", "year"):
                    print("❌ Invalid field. Choose: book_id, title, author, year.")

                elif order not in ("asc", "desc"):
                    print("❌ Invalid order. Choose: asc or desc.")

                else:
                    print("═" * 70)
                    print(f" BOOKS SORTED WITH PYTHON BY {field.upper()} ({order.upper()}) ".center(70))
                    print("═" * 70)
                    books_list = book_manager.view_books()

                    if field in ("title", "author"):
                        sorted_books = sorted(
                            books_list,
                            key=lambda b: getattr(b, field).lower(),
                            reverse=(order == "desc")
                        )

                    else:
                        sorted_books = sorted(
                            books_list,
                            key=lambda b: getattr(b, field),
                            reverse=(order == "desc")
                        )

                    for b in sorted_books:
                        print(b)

                    print("═" * 70)


            elif menu_choice == "14":
                field = input("Sort by (book_id/title/author/year): ").strip().lower()
                order = input("Order (asc/desc): ").strip().lower()

                if field not in ("book_id", "title", "author", "year"):
                    print("❌ Invalid field. Choose: book_id, title, author, year.")

                elif order not in ("asc", "desc"):
                    print("❌ Invalid order. Choose: asc or desc.")

                else:
                    print("═" * 70)
                    print(f" BOOKS SORTED WITH SQL BY {field.upper()} ({order.upper()}) ".center(70))
                    print("═" * 70)
                    conn = database_connection.connect()

                    if conn:
                        cursor = conn.cursor(dictionary=True)
                        sql_order = "ASC" if order == "asc" else "DESC"
                        cursor.execute(f"SELECT * FROM books ORDER BY {field} {sql_order}")
                        results = cursor.fetchall()
                        conn.close()

                        for r in results:
                            status = "Available" if r["available"] else "Borrowed"
                            print(f'[{r["book_id"]}] {r["title"]} by {r["author"]} ({r["year"]}) - {status}')

                    print("═" * 70)


            elif menu_choice == "15":
                confirm = input(
                    "Type YES to reset all books, users, and borrowing records: "
                ).strip()
                if confirm == "YES":
                    database_connection.initialize_database(reset=True)
                    print("✅ Database has been reset to default sample data.")
                else:
                    print("Reset cancelled.")

            elif menu_choice == "16":
                print("Goodbye!")
                break

            else:
                print("❌ Invalid menu option. Please try again.")

        except ValueError as error:
            print(f"❌ {error}")
        except Exception as error:
            print(f"❌ Unexpected error: {error}")


if __name__ == "__main__":
    run_library_menu()