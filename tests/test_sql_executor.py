from unittest.mock import patch, MagicMock

from app.llm.sql_executor import execute_sql_with_retry


def test_successful_execution():

    mock_chain = MagicMock()

    first_response = MagicMock()
    first_response.content = """
    SELECT company_name
    FROM customers
    LIMIT 5;
    """

    mock_chain.invoke.return_value = first_response

    mock_connection = MagicMock()

    mock_result = MagicMock()
    mock_result.keys.return_value = ["company_name"]
    mock_result.fetchall.return_value = [
        ("Alfreds Futterkiste",),
        ("Ana Trujillo Emparedados y helados",),
    ]

    mock_connection.exec_driver_sql.return_value = mock_result

    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection

    with patch(
        "app.llm.sql_executor.get_sql_chain",
        return_value=mock_chain,
    ), patch(
        "app.llm.sql_executor.get_engine",
        return_value=mock_engine,
    ):

        result = execute_sql_with_retry(
            question="List 5 customers",
            schema="customers(customer_id, company_name)",
            relationships="",
            lov="",
        )

    assert result["success"] is True
    assert result["attempts"] == 1
    assert len(result["rows"]) == 2