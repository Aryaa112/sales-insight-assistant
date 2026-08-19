import re

import sqlglot
from sqlglot import exp


# Tables that the application permits
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


MAX_ROWS = 100


def apply_output_guardrail(sql: str) -> tuple[bool, str, str]:
    """
    Final safety check before SQL reaches PostgreSQL.

    Returns:
        (allowed, reason, safe_sql)
    """

    if not sql or not sql.strip():
        return False, "SQL is empty.", ""

    cleaned_sql = sql.strip()

    # Remove markdown fences
    if cleaned_sql.startswith("```"):
        cleaned_sql = cleaned_sql.replace("```sql", "", 1)
        cleaned_sql = cleaned_sql.replace("```", "")
        cleaned_sql = cleaned_sql.strip()

    
    # 1. Parse SQL
    try:
        statements = sqlglot.parse(
            cleaned_sql,
            read="postgres",
        )

    except Exception as exc:
        return False, f"Invalid SQL syntax: {exc}", ""

    
    # 2. Only one statement
    if len(statements) != 1:
        return False, "Multiple SQL statements are not allowed.", ""

    statement = statements[0]

    
    # 3. Defense in depth: SELECT only
    if not isinstance(statement, exp.Select):
        return False, "Only SELECT queries are allowed.", ""

    
    # 4. Check referenced tables
    referenced_tables = {
        table.name.lower()
        for table in statement.find_all(exp.Table)
    }

    unauthorized_tables = (
        referenced_tables - ALLOWED_TABLES
    )

    if unauthorized_tables:
        return (
            False,
            "Unauthorized table(s): "
            + ", ".join(sorted(unauthorized_tables)),
            "",
        )

   
    # 5. Prevent dangerous SQL keywords
    dangerous_keywords = [
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "CREATE",
        "ALTER",
        "TRUNCATE",
        "GRANT",
        "REVOKE",
    ]

    upper_sql = cleaned_sql.upper()

    for keyword in dangerous_keywords:

        if re.search(
            rf"\b{keyword}\b",
            upper_sql,
        ):
            return (
                False,
                f"Dangerous SQL operation detected: {keyword}",
                "",
            )

    
    # 6. Add LIMIT if missing
    if statement.args.get("limit") is None:

        cleaned_sql = cleaned_sql.rstrip(";")

        cleaned_sql = (
            f"{cleaned_sql}\nLIMIT {MAX_ROWS};"
        )

    return (
        True,
        "Output SQL passed all safety checks.",
        cleaned_sql,
    )