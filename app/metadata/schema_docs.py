from pathlib import Path


def generate_schema_documentation(metadata: dict) -> str:
    """
    Convert extracted database metadata into
    human-readable Markdown documentation.
    """

    lines = []

    
    # TITLE
    lines.append("# Northwind Database Schema")
    lines.append("")
    lines.append(
        "This document was generated automatically from "
        "the Northwind PostgreSQL database."
    )
    lines.append("")

    
    # TABLES
    lines.append("## Tables")
    lines.append("")

    for table in metadata["tables"]:
        row_count = metadata["row_counts"].get(table, 0)

        lines.append(f"### {table}")
        lines.append("")
        lines.append(f"**Row count:** {row_count}")
        lines.append("")
        lines.append("| Column | Data Type | Nullable |")
        lines.append("|---|---|---|")

        for column in metadata["columns"].get(table, []):
            lines.append(
                f"| {column['name']} "
                f"| {column['data_type']} "
                f"| {column['nullable']} |"
            )

        lines.append("")

    
    # FOREIGN KEY RELATIONSHIPS
    lines.append("## Foreign Key Relationships")
    lines.append("")

    if metadata["foreign_keys"]:

        lines.append(
            "| Table | Column | Referenced Table | Referenced Column |"
        )
        lines.append(
            "|---|---|---|---|"
        )

        for fk in metadata["foreign_keys"]:
            lines.append(
                f"| {fk['table']} "
                f"| {fk['column']} "
                f"| {fk['referenced_table']} "
                f"| {fk['referenced_column']} |"
            )

    else:
        lines.append("No foreign key relationships found.")

    lines.append("")

   
    # LIST OF VALUES
    lines.append("## List of Values (LOV)")
    lines.append("")

    for table, columns in metadata["lov"].items():

        lines.append(f"### {table}")
        lines.append("")

        for column, values in columns.items():

            lines.append(f"**{column}:**")

            if values:
                formatted_values = ", ".join(
                    str(value) for value in values
                )

                lines.append(formatted_values)

            else:
                lines.append("No values found.")

            lines.append("")

    return "\n".join(lines)


def save_schema_documentation(
    metadata: dict,
    output_path: str = "docs/schema.md"
):
    """
    Generate schema documentation and save it to a Markdown file.
    """

    documentation = generate_schema_documentation(metadata)

    path = Path(output_path)

    # Create parent directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        documentation,
        encoding="utf-8"
    )

    return path