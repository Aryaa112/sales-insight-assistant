from app.database.connection import get_engine
from app.metadata.extractor import MetadataExtractor
from app.metadata.schema_docs import save_schema_documentation


def main():

    print("Connecting to Northwind database...")

    engine = get_engine()

    with engine.connect():
        print("Connected Successfully!")

    print("\nExtracting metadata...")

    extractor = MetadataExtractor(engine)

    metadata = extractor.extract_metadata()

    print("Metadata extracted successfully!")

    print("\nGenerating schema documentation...")

    output_path = save_schema_documentation(metadata)

    print(f"Schema documentation created: {output_path}")


if __name__ == "__main__":
    main()