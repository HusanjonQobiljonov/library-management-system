import re


def validate_positive_integer(raw_value, field_name):
    """Validates that the input is a positive integer and returns it."""
    raw_value = str(raw_value).strip()
    if not raw_value.isdigit() or int(raw_value) <= 0:
        raise ValueError(f"{field_name} must be a positive integer.")
    return int(raw_value)


def validate_year(raw_value):
    """Validates that the year is a positive integer between 1000 and 2100."""
    year_value = validate_positive_integer(raw_value, "Year")
    if year_value < 1000 or year_value > 2100:
        raise ValueError("Year must be between 1000 and 2100.")
    return year_value


def validate_non_empty_text(raw_value, field_name):
    """Validates that the input text is not empty after stripping spaces."""
    cleaned_value = str(raw_value).strip()
    if not cleaned_value:
        raise ValueError(f"{field_name} cannot be empty.")
    return cleaned_value


def validate_email_address(raw_value):
    """Validates that the input matches a standard email address format."""
    email_value = str(raw_value).strip().lower()
    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    if not re.match(email_pattern, email_value):
        raise ValueError("Please enter a valid email address.")
    return email_value


def validate_user_role(raw_value):
    """Validates that the role is student, staff, or faculty."""
    role_value = str(raw_value).strip().lower()
    allowed_roles = {"student", "staff", "faculty"}
    if role_value not in allowed_roles:
        raise ValueError("Role must be student, staff, or faculty.")
    return role_value


def validate_sort_field(raw_value):
    """Validates that the sort field is one of the allowed book fields."""
    sort_field = str(raw_value).strip().lower()
    allowed_fields = {"book_id", "title", "author", "genre", "year", "available"}
    if sort_field not in allowed_fields:
        raise ValueError("Sort field must be one of: book_id, title, author, genre, year, available.")
    return sort_field


def validate_sort_direction(raw_value):
    """Validates that the sort direction is either ASC or DESC."""
    direction = str(raw_value).strip().lower()
    if direction not in {"asc", "desc"}:
        raise ValueError("Sort direction must be ASC or DESC.")
    return direction