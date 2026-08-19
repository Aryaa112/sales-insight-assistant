import sqlglot
from sqlglot import exp


# Northwind tables allowed by our application
ALLOWED_TABLES = {
    "categories",
    "customer_demographics",
    "customer_customer_demo",
    "customers",
    "employees",
    "employee_territories",
    "orders",
    "order_details",
    "products",
    "shippers",
    "suppliers",
    "territories",
    "us_states",
    "region",
}


FORBIDDEN_STATEMENTS = (
    exp.Drop,
    exp.Delete,
    exp.Update,
    exp.Insert,
    exp.Create,
    exp.Alter,
)


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validate generated SQL before it is allowed
    to reach the database.

    Returns:
        (True, "SQL is valid") if safe.
        (False, reason) if rejected.
    """

    if not sql or not sql.strip():
        return False, "SQL query is empty."

    # Remove markdown code fences if the LLM returned them
    cleaned_sql = sql.strip()

    if cleaned_sql.startswith("```"):
        cleaned_sql = cleaned_sql.replace("```sql", "", 1)
        cleaned_sql = cleaned_sql.replace("```", "")
        cleaned_sql = cleaned_sql.strip()

    # Parse SQL
    try:
        statements = sqlglot.parse(
            cleaned_sql,
            read="postgres",
        )
    except Exception as exc:
        return False, f"Invalid SQL syntax: {exc}"

    if not statements:
        return False, "No SQL statement found."

    # Only one statement should be accepted
    if len(statements) != 1:
        return False, "Multiple SQL statements are not allowed."

    statement = statements[0]

    # Reject dangerous statement types
    if isinstance(statement, FORBIDDEN_STATEMENTS):
        return False, (
            f"Forbidden SQL operation: "
            f"{statement.key.upper()}"
        )

    # Only SELECT statements are allowed
    if not isinstance(statement, exp.Select):
        return False, "Only SELECT queries are allowed."

    # Check referenced tables
    referenced_tables = {
        table.name.lower()
        for table in statement.find_all(exp.Table)
    }

    unauthorized_tables = (
        referenced_tables - ALLOWED_TABLES
    )

    if unauthorized_tables:
        return False, (
            "Unauthorized table(s): "
            + ", ".join(sorted(unauthorized_tables))
        )

    return True, "SQL is valid and safe."