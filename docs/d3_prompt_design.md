# D3.1 — NL-to-SQL Prompt Design

## Objective

The purpose of the prompt is to convert a user's natural language
sales question into a valid PostgreSQL SELECT query using the
Northwind database.

## Context Required by the LLM

The LLM requires:

1. The user's natural language question.
2. Relevant database tables.
3. Relevant columns and their data types.
4. Foreign-key relationships between relevant tables.
5. Relevant List of Values (LOV) for categorical columns.
6. PostgreSQL as the SQL dialect.
7. Explicit instructions that SQL must be read-only.
8. Instructions not to invent tables or columns.

## Schema Context Strategy

The complete Northwind schema will not be blindly included in every
prompt.

The metadata extractor from Day 2 provides the complete database
metadata. For each user question, the application will identify the
tables and columns relevant to the question and include only that
context in the prompt.

This reduces unnecessary context and makes SQL generation more
focused.

## LOV Strategy

Only LOV information relevant to the user's question will be included.

For example, if the user asks about customers in Germany, the
customers.country LOV can help the LLM use the correct database value.

Irrelevant LOVs will not be included because they add unnecessary
context and may confuse the model.

## SQL Safety Instructions

The LLM will be instructed to:

- Generate PostgreSQL SQL.
- Generate SELECT statements only.
- Never generate INSERT statements.
- Never generate UPDATE statements.
- Never generate DELETE statements.
- Never generate DROP statements.
- Never generate ALTER statements.
- Never generate CREATE statements.
- Never modify database data or structure.
- Use only tables and columns provided in the schema.
- Never invent database objects.
- Never access system tables.
- Return only the generated SQL.

These instructions reduce the probability of unsafe SQL generation.

However, prompt instructions are not treated as a security boundary.
All generated SQL will be independently validated before execution.

## Output

The LLM should return the generated SQL query without executing it.

The SQL will then be passed to the SQL validator before it can reach
the database.