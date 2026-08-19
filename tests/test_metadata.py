from app.database.connection import get_engine
from app.metadata.extractor import MetadataExtractor
from app.metadata.schema_docs import generate_schema_documentation


def get_metadata():
    engine = get_engine()
    extractor = MetadataExtractor(engine)

    return extractor.extract_metadata()


def test_tables_exist():
    metadata = get_metadata()

    assert "tables" in metadata
    assert len(metadata["tables"]) > 0

    assert "customers" in metadata["tables"]
    assert "orders" in metadata["tables"]
    assert "products" in metadata["tables"]


def test_columns_exist():
    metadata = get_metadata()

    assert "columns" in metadata

    assert "customers" in metadata["columns"]
    assert "orders" in metadata["columns"]

    customer_columns = [
        column["name"]
        for column in metadata["columns"]["customers"]
    ]

    assert "customer_id" in customer_columns
    assert "company_name" in customer_columns


def test_row_counts_exist():
    metadata = get_metadata()

    assert "row_counts" in metadata

    assert metadata["row_counts"]["customers"] > 0
    assert metadata["row_counts"]["orders"] > 0
    assert metadata["row_counts"]["products"] > 0


def test_foreign_keys_exist():
    metadata = get_metadata()

    assert "foreign_keys" in metadata
    assert len(metadata["foreign_keys"]) > 0

    relationships = [
        (
            fk["table"],
            fk["column"],
            fk["referenced_table"],
            fk["referenced_column"]
        )
        for fk in metadata["foreign_keys"]
    ]

    assert (
        "orders",
        "customer_id",
        "customers",
        "customer_id"
    ) in relationships


def test_lov_exists():
    metadata = get_metadata()

    assert "lov" in metadata

    assert "customers" in metadata["lov"]
    assert "country" in metadata["lov"]["customers"]

    countries = metadata["lov"]["customers"]["country"]

    assert len(countries) <= 5


def test_schema_documentation():
    metadata = get_metadata()

    documentation = generate_schema_documentation(metadata)

    assert "# Northwind Database Schema" in documentation
    assert "## Tables" in documentation
    assert "## Foreign Key Relationships" in documentation
    assert "## List of Values" in documentation

    assert "customers" in documentation
    assert "orders" in documentation
    assert "products" in documentation