import mysql.connector


class User:
    def __init__(self, user_id, name, email, role="student"):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role

    def __str__(self):
        return f"[{self.user_id}] {self.name} <{self.email}> ({self.role})"


class UserManager:
    def __init__(self, db):
        self.db = db
        self.allowed_roles = {"student", "staff", "faculty"}

    def create_user(self, name, email, role="student"):
        cleaned_name = str(name).strip()
        cleaned_email = str(email).strip().lower()
        cleaned_role = str(role).strip().lower()

        if not cleaned_name:
            raise ValueError("Name cannot be empty.")
        if not cleaned_email:
            raise ValueError("Email cannot be empty.")
        if "@" not in cleaned_email or "." not in cleaned_email:
            raise ValueError("Invalid email format.")
        if cleaned_role not in self.allowed_roles:
            raise ValueError("Invalid role.")

        connection = self.db.connect()
        if not connection:
            return None

        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s",
                (cleaned_email,)
            )
            if cursor.fetchone():
                raise ValueError("Duplicate email.")

            cursor.execute(
                "INSERT INTO users (name, email, role) VALUES (%s, %s, %s)",
                (cleaned_name, cleaned_email, cleaned_role)
            )
            connection.commit()
            print("✅ User created successfully.")
            return cursor.lastrowid

        except mysql.connector.errors.IntegrityError as error:
            raise ValueError(f"Could not create user: {error}")

        finally:
            cursor.close()
            connection.close()

    def add_user(self, name, email, role="student"):
        return self.create_user(name, email, role)

    def get_all_users(self):
        connection = self.db.connect()
        if not connection:
            return []

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users ORDER BY user_id ASC")
            return cursor.fetchall()
        finally:
            cursor.close()
            connection.close()

    def display_users(self):
        rows = self.get_all_users()

        if not rows:
            print("\n❌ No users found.")
            return

        print("\n" + "=" * 92)
        print("👥 LIBRARY USERS".center(92))
        print("=" * 92)
        print(f"{'No.':<5} {'Name':<22} {'Email':<35} {'Role':<15}")
        print("-" * 92)

        for i, user in enumerate(rows, start=1):
            role = user["role"].upper()

            if user["role"] == "student":
                icon = "🎓"
            elif user["role"] == "staff":
                icon = "👔"
            else:
                icon = "🧑‍🏫"

            print(
                f"{i:<5} "
                f"{icon} {user['name']:<20} "
                f"{user['email']:<35} "
                f"{role:<15}"
            )

        print("=" * 92)

    def view_users(self):
        rows = self.get_all_users()
        return [
            User(row["user_id"], row["name"], row["email"], row.get("role", "student"))
            for row in rows
        ]

    def get_user_by_email(self, email):
        connection = self.db.connect()
        if not connection:
            return None

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email.strip().lower(),)
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            connection.close()

    def update_user_details(self, user_id, name, email, role="student"):
        cleaned_name = str(name).strip()
        cleaned_email = str(email).strip().lower()
        cleaned_role = str(role).strip().lower()

        if not cleaned_name:
            raise ValueError("Name cannot be empty.")
        if not cleaned_email:
            raise ValueError("Email cannot be empty.")
        if "@" not in cleaned_email or "." not in cleaned_email:
            raise ValueError("Invalid email format.")
        if cleaned_role not in self.allowed_roles:
            raise ValueError("Invalid role.")

        connection = self.db.connect()
        if not connection:
            return False

        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT user_id FROM users WHERE user_id = %s",
                (user_id,)
            )
            if not cursor.fetchone():
                raise ValueError("User not found.")

            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s AND user_id != %s",
                (cleaned_email, user_id)
            )
            if cursor.fetchone():
                raise ValueError("Duplicate email.")

            cursor.execute(
                "UPDATE users SET name = %s, email = %s, role = %s WHERE user_id = %s",
                (cleaned_name, cleaned_email, cleaned_role, user_id)
            )
            connection.commit()
            print("✅ User updated successfully.")
            return True

        finally:
            cursor.close()
            connection.close()

    def update_user(self, user_id, name, email, role="student"):
        return self.update_user_details(user_id, name, email, role)

    def remove_user(self, user_id):
        connection = self.db.connect()
        if not connection:
            return False

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT user_id, name, email FROM users WHERE user_id = %s",
                (user_id,)
            )
            existing_user = cursor.fetchone()
            if not existing_user:
                raise ValueError("User not found.")

            cursor.execute(
                "SELECT record_id FROM borrowings WHERE user_id = %s AND return_date IS NULL",
                (user_id,)
            )
            if cursor.fetchone():
                raise ValueError("Cannot delete: user has active borrowings.")

            cursor.execute(
                "DELETE FROM users WHERE user_id = %s",
                (user_id,)
            )
            connection.commit()

            if cursor.rowcount == 0:
                raise ValueError("User was not deleted.")

            print(f"✅ User '{existing_user['name']}' deleted successfully.")
            return True

        except mysql.connector.Error as error:
            raise ValueError(f"Could not delete user: {error}")

        finally:
            cursor.close()
            connection.close()

    def delete_user(self, user_id):
        return self.remove_user(user_id)


User_Manager = UserManager