from decimal import Decimal


# Columns that should not normally be exposed
HIDDEN_COLUMNS = {
    "password",
    "password_hash",
    "secret",
    "api_key",
}


def sanitize_results(
    columns: list[str],
    rows: list,
) -> dict:
    """
    Sanitize database results before displaying them.
    """

    if not rows:

        return {
            "success": True,
            "message": (
                "No matching records were found. "
                "The query executed successfully but returned no rows."
            ),
            "columns": [],
            "rows": [],
        }

    
    # Remove sensitive columns

    visible_indexes = [
        index
        for index, column in enumerate(columns)
        if column.lower() not in HIDDEN_COLUMNS
    ]

    visible_columns = [
        columns[index]
        for index in visible_indexes
    ]

    sanitized_rows = []

    for row in rows:

        sanitized_row = []

        for index in visible_indexes:

            value = row[index]

            # Format Decimal values
            if isinstance(value, Decimal):

                value = float(value)

            sanitized_row.append(value)

        sanitized_rows.append(
            sanitized_row
        )

    return {
        "success": True,
        "message": f"{len(sanitized_rows)} result(s) found.",
        "columns": visible_columns,
        "rows": sanitized_rows,
    }