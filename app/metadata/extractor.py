from sqlalchemy import text


class MetadataExtractor:
    """
    Extracts database metadata from the Northwind PostgreSQL database.

    The extracted metadata will later be used as context
    for the NL-to-SQL LLM.
    """

    def __init__(self, engine):
        self.engine = engine

    
    # 1. GET TABLES
    def get_tables(self):
        """Return all tables in the public schema."""

        query = text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)

        with self.engine.connect() as conn:
            result = conn.execute(query)

            return [row[0] for row in result]

   
    # 2. GET COLUMNS AND DATA TYPES
    def get_columns(self):
        """
        Return column names and data types for every table.
        """

        query = text("""
            SELECT
                table_name,
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """)

        columns = {}

        with self.engine.connect() as conn:
            result = conn.execute(query)

            for row in result:
                table_name = row[0]

                if table_name not in columns:
                    columns[table_name] = []

                columns[table_name].append({
                    "name": row[1],
                    "data_type": row[2],
                    "nullable": row[3]
                })

        return columns

    
    # 3. GET ROW COUNTS
    def get_row_counts(self):
        """
        Return the number of rows in every table.
        """

        tables = self.get_tables()
        row_counts = {}

        with self.engine.connect() as conn:

            for table in tables:

                # Table names come from our own database metadata,
                # not from user input.
                query = text(
                    f'SELECT COUNT(*) FROM "{table}"'
                )

                result = conn.execute(query)

                row_counts[table] = result.scalar()

        return row_counts

    
    # 4. GET FOREIGN KEYS
    def get_foreign_keys(self):
        """
        Return all foreign-key relationships.
        """

        query = text("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS referenced_table,
                ccu.column_name AS referenced_column
            FROM information_schema.table_constraints AS tc

            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema

            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema

            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public'

            ORDER BY tc.table_name, kcu.column_name;
        """)

        foreign_keys = []

        with self.engine.connect() as conn:
            result = conn.execute(query)

            for row in result:
                foreign_keys.append({
                    "table": row[0],
                    "column": row[1],
                    "referenced_table": row[2],
                    "referenced_column": row[3]
                })

        return foreign_keys

    
    # 5. GET LIST OF VALUES (LOV)
    def get_lov(self, max_values=5):
        """
        Extract a small number of distinct values from
        useful categorical columns.

        This helps the LLM understand what values actually
        exist in the database.
        """

        # These are useful categorical columns in Northwind.
        categorical_columns = {
            "customers": ["country", "city"],
            "employees": ["title", "country"],
            "products": ["category_id", "supplier_id"],
            "categories": ["category_name"],
            "suppliers": ["country", "city"],
            "shippers": ["company_name"],
            "orders": ["ship_country", "ship_city"],
            "territories": ["region_id"],
        }

        lov = {}

        with self.engine.connect() as conn:

            for table, columns in categorical_columns.items():

                lov[table] = {}

                for column in columns:

                    query = text(
                        f'''
                        SELECT DISTINCT "{column}"
                        FROM "{table}"
                        WHERE "{column}" IS NOT NULL
                        ORDER BY "{column}"
                        LIMIT :limit
                        '''
                    )

                    result = conn.execute(
                        query,
                        {"limit": max_values}
                    )

                    values = [row[0] for row in result]

                    lov[table][column] = values

        return lov

    
    # 6. EXTRACT EVERYTHING

    def extract_metadata(self):
        """
        Extract all required metadata and return
        it as one structured Python dictionary.
        """

        metadata = {
            "tables": self.get_tables(),
            "columns": self.get_columns(),
            "row_counts": self.get_row_counts(),
            "foreign_keys": self.get_foreign_keys(),
            "lov": self.get_lov()
        }

        return metadata