# Problem Analysis

## Problem Statement

Sales managers often need information from business databases to answer questions
about customers, orders, products, employees, and sales performance. However,
retrieving this information traditionally requires knowledge of SQL and the
underlying database schema.

The Sales Insights Assistant addresses this problem by allowing users to ask
questions about the Northwind sales database using natural language. The system
converts the user's question into a read-only SQL query, validates the generated
SQL, executes it against PostgreSQL, sanitizes the results, and presents the
answer through a Streamlit interface.

## Key Challenges

The system must solve several challenges:

1. Natural-language questions must be converted into valid SQL.
2. The generated SQL must use the correct database tables and columns.
3. Unsafe SQL operations such as DELETE, UPDATE, DROP, or INSERT must be blocked.
4. Prompt injection and jailbreak attempts must be detected.
5. Sensitive information should not be unnecessarily exposed.
6. Database errors should be handled without exposing technical stack traces.
7. LLM-generated answers can be incorrect, so the generated SQL must be visible
   to the user for transparency.
8. The system must provide traceability so that a response can be investigated
   later.
9. The system must be evaluated using a fixed set of test questions.
10. The system should remain usable when unexpected or adversarial inputs are
    provided.

## Proposed Solution

The system uses a layered architecture consisting of input guardrails,
metadata retrieval, an LLM-based SQL generation chain, SQL validation, output
guardrails, database execution, result sanitization, and a Streamlit interface.

Structured logging and trace IDs are used to reconstruct the complete processing
chain for each request. An evaluation harness measures system performance using
15 predefined questions, including adversarial cases.

## Expected Outcome

The final system allows a sales manager to query the Northwind database using
natural language while maintaining safety, transparency, traceability, and
controlled access to database information.