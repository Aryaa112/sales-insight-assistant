from app.llm.sql_chain import get_sql_chain


def main():
    chain = get_sql_chain()

    response = chain.invoke(
        {
            "schema": """
customers(
    customer_id,
    company_name,
    country
)

orders(
    order_id,
    customer_id,
    order_date
)

order_details(
    order_id,
    product_id,
    unit_price,
    quantity,
    discount
)
""",
            "relationships": """
orders.customer_id → customers.customer_id
order_details.order_id → orders.order_id
""",
            "lov": """
customers.country:
Argentina, Austria, Belgium, Brazil, Canada, Germany, UK
""",
            "question": "List the top 5 customers by number of orders."
        }
    )

    print("\nGenerated SQL:")
    print(response.content)


if __name__ == "__main__":
    main()