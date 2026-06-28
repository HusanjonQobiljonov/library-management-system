# 📚 Library Management System

A command-line Library Management System developed in **Python** with **MySQL** as the backend database. This project was created as part of the **Software & Databases (UDEZ04IT)** module to demonstrate object-oriented programming, relational database design, CRUD operations, and software engineering best practices.

## ✨ Features

* 📖 Manage books (Create, Read, Update, Delete)
* 👤 Manage library users
* 🔄 Borrow and return books
* 🔍 Search books using up to three keywords
* 📊 Sort books using both Python (`sorted()`) and SQL (`ORDER BY`)
* ✅ Input validation and error handling
* 🔒 Prevent borrowing unavailable books
* 💾 Persistent data storage with MySQL
* 🧪 Manual and unit testing

## 🛠️ Technologies

* Python 3
* MySQL
* SQL
* Object-Oriented Programming (OOP)

## 📂 Project Structure

```text
books.py             Book management
borrow.py            Borrowing operations
user.py              User management
connect_dp.py        Database connection
check_input.py       Input validation
main.py              Application entry point
setup.sql            Database schema
requirements.txt     Project dependencies
```

## 🚀 Getting Started

### Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/library-management-system.git
cd library-management-system
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Create the database

Run the SQL script:

```sql
setup.sql
```

Configure your MySQL credentials inside `connect_dp.py`.

### Run the application

```bash
python main.py
```

## 🏗️ System Design

The application follows a modular object-oriented architecture. Separate components handle database connectivity, book management, user management, and borrowing operations. A relational MySQL database stores books, users, and borrowing records using foreign-key relationships to maintain data integrity.

## 🧪 Testing

The project includes both manual and automated testing to verify:

* CRUD operations
* Borrowing and returning books
* Search functionality
* Sorting
* Input validation
* Edge cases
* Database integrity

## 📈 Future Improvements

* Graphical User Interface (GUI)
* User authentication
* Role-based access control
* Barcode/ISBN scanning
* Overdue notifications
* Cloud database support
* REST API integration

## 📜 License

This project is licensed under the MIT License.

---

Developed as a university software engineering project to demonstrate practical skills in Python programming, database design, software testing, and object-oriented development.
