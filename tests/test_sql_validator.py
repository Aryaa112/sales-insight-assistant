from app.validation.sql_validator import validate_sql


def test_valid_select():
    sql = """
    SELECT company_name
    FROM customers
    LIMIT 5;
    """

    valid, message = validate_sql(sql)

    assert valid is True


def test_drop_blocked():
    sql = "DROP TABLE customers;"

    valid, message = validate_sql(sql)

    assert valid is False


def test_delete_blocked():
    sql = "DELETE FROM customers;"

    valid, message = validate_sql(sql)

    assert valid is False


def test_update_blocked():
    sql = """
    UPDATE customers
    SET company_name = 'Hacked';
    """

    valid, message = validate_sql(sql)

    assert valid is False


def test_insert_blocked():
    sql = """
    INSERT INTO customers
    VALUES ('TEST');
    """

    valid, message = validate_sql(sql)

    assert valid is False


def test_unknown_table_blocked():
    sql = """
    SELECT *
    FROM secret_table;
    """

    valid, message = validate_sql(sql)

    assert valid is False


def test_multiple_statements_blocked():
    sql = """
    SELECT * FROM customers;
    DROP TABLE customers;
    """

    valid, message = validate_sql(sql)

    assert valid is False