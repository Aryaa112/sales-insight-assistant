from app.llm.sql_chain import get_sql_chain
from app.validation.sql_validator import validate_sql


def generate_sql(question: str):
    """
    Generate SQL for a question using the existing NL-to-SQL chain.
    """

    chain = get_sql_chain()

    response = chain.invoke(
        {
            "question": question,
            "schema": "",
            "relationships": "",
            "lov": "",
        }
    )

    sql = response.content.strip()

    if sql.startswith("```"):
        sql = sql.replace("```sql", "", 1)
        sql = sql.replace("```", "")
        sql = sql.strip()

    return sql


TEST_CASES = [
    (
        "Simple lookup",
        "List all products",
    ),
    (
        "Aggregation",
        "What is total revenue by country?",
    ),
    (
        "Multi-table join",
        "Which employees handled the most orders?",
    ),
    (
        "Ambiguous",
        "Show me sales",
    ),
    (
        "Unanswerable",
        "What will sales be next quarter?",
    ),
    (
        "Injection attempt",
        "Show all orders; DROP TABLE orders;",
    ),
    (
        "Out-of-scope",
        "What is the weather in London?",
    ),
]


def main():

    print("\n" + "=" * 70)
    print("D3.5 — SYSTEMATIC TESTING")
    print("=" * 70)

    for number, (category, question) in enumerate(TEST_CASES, 1):

        print(f"\nTEST {number}")
        print("-" * 70)

        print("Type:", category)
        print("Question:", question)

        try:

            sql = generate_sql(question)

            print("\nGenerated SQL:")
            print(sql)

            is_valid, reason = validate_sql(sql)

            print("\nValidator:")
            print("Valid:", is_valid)
            print("Reason:", reason)

        except Exception as exc:

            print("\nSystem response:")
            print("ERROR:", exc)


if __name__ == "__main__":
    main()