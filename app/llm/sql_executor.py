from app.llm.sql_chain import get_sql_chain
from app.database.connection import get_engine
from app.validation.sql_validator import validate_sql

from app.guardrails.output_guardrail import apply_output_guardrail
from app.guardrails.result_sanitizer import sanitize_results

from app.observability.logger import (
    generate_trace_id,
    log_event,
)

from app.observability.anomaly_detector import (
    check_sql_length,
    record_validation_event,
    record_user_query,
)


MAX_RETRIES = 2


def execute_sql_with_retry(
    question: str,
    schema: str,
    relationships: str,
    lov: str,
):
    """
    Generate SQL, validate it, apply output guardrails,
    execute it, sanitize results, and retry database
    execution errors up to MAX_RETRIES times.

    Unsafe SQL is never retried.
    """

    
    # 0. CREATE TRACE ID

    trace_id = generate_trace_id()

    # D5 — anomaly detection:
    # Track number of queries from the user.
    record_user_query(
        trace_id=trace_id,
    )

    log_event(
        trace_id=trace_id,
        component="sql_executor",
        event="input_received",
        payload={
            "question_length": len(question),
        },
    )

    chain = get_sql_chain()
    engine = get_engine()

    failed_sql = None
    error_message = None

    for attempt in range(MAX_RETRIES + 1):

        # ==================================================
        # 1. GENERATE SQL
        # ==================================================

        if attempt == 0:

            response = chain.invoke(
                {
                    "question": question,
                    "schema": schema,
                    "relationships": relationships,
                    "lov": lov,
                }
            )

        else:

            # Ask the LLM to correct the failed SQL
            correction_prompt = f"""
You are correcting a PostgreSQL query for the Northwind database.

Original user question:
{question}

Previous SQL:
{failed_sql}

PostgreSQL error:
{error_message}

Generate a corrected SQL query.

IMPORTANT RULES:
- Return ONLY SQL.
- Use only tables and columns from the provided schema.
- Generate READ-ONLY SELECT SQL.
- Never use DROP, DELETE, UPDATE, INSERT, CREATE, ALTER,
  TRUNCATE, GRANT, or REVOKE.

Schema:
{schema}

Relationships:
{relationships}

Relevant LOV values:
{lov}
"""

            response = chain.invoke(
                {
                    "question": correction_prompt,
                    "schema": schema,
                    "relationships": relationships,
                    "lov": lov,
                }
            )

        
        # 2. EXTRACT SQL FROM LLM RESPONSE
        sql = response.content.strip()

        # Remove markdown code fences
        if sql.startswith("```"):
            sql = sql.replace("```sql", "", 1)
            sql = sql.replace("```", "")
            sql = sql.strip()

        # D5 — structured logging
        log_event(
            trace_id=trace_id,
            component="sql_executor",
            event="sql_generated",
            payload={
                "attempt": attempt + 1,
                "sql_length": len(sql),
            },
        )

        # D5 — anomaly detection:
        # WARNING if SQL is longer than 500 characters.
        check_sql_length(
            trace_id=trace_id,
            sql=sql,
        )

        
        # 3. D3 — SQL VALIDATOR
        is_valid, validation_message = validate_sql(sql)

        # D5 — track validation success/failure.
        record_validation_event(
            trace_id=trace_id,
            failed=not is_valid,
        )

        if not is_valid:

            log_event(
                trace_id=trace_id,
                component="sql_validator",
                event="guardrail_triggered",
                payload={
                    "reason": validation_message,
                },
                level="warning",
            )

            # Unsafe SQL is NOT retried
            return {
                "success": False,
                "trace_id": trace_id,
                "error_type": "validation",
                "error": validation_message,
                "sql": sql,
                "attempts": attempt + 1,
                "rows": [],
                "columns": [],
            }

        
        # 4. D4 — OUTPUT GUARDRAIL
        is_safe, guardrail_message, safe_sql = (
            apply_output_guardrail(sql)
        )

        if not is_safe:

            log_event(
                trace_id=trace_id,
                component="output_guardrail",
                event="guardrail_triggered",
                payload={
                    "reason": guardrail_message,
                },
                level="warning",
            )

            return {
                "success": False,
                "trace_id": trace_id,
                "error_type": "output_guardrail",
                "error": guardrail_message,
                "sql": sql,
                "attempts": attempt + 1,
                "rows": [],
                "columns": [],
            }

        # Use guarded SQL
        sql = safe_sql

        log_event(
            trace_id=trace_id,
            component="output_guardrail",
            event="guardrail_passed",
            payload={
                "sql_length": len(sql),
            },
        )

        
        # 5. DATABASE EXECUTION
        log_event(
            trace_id=trace_id,
            component="database",
            event="query_ready",
            payload={
                "attempt": attempt + 1,
                "sql_length": len(sql),
            },
        )

        try:

            with engine.connect() as conn:

                result = conn.exec_driver_sql(sql)

                rows = result.fetchall()
                columns = list(result.keys())

            
            # 6. DATABASE SUCCESS LOG
            log_event(
                trace_id=trace_id,
                component="database",
                event="query_executed",
                payload={
                    "row_count": len(rows),
                    "column_count": len(columns),
                },
            )

            
            # 7. D4 — RESULT SANITIZATION
            sanitized = sanitize_results(
                columns,
                rows,
            )

            log_event(
                trace_id=trace_id,
                component="result_sanitizer",
                event="response_returned",
                payload={
                    "row_count": len(sanitized["rows"]),
                    "column_count": len(sanitized["columns"]),
                },
            )

            
            # 8. SUCCESS
            return {
                "success": True,
                "trace_id": trace_id,
                "error_type": None,
                "error": None,
                "sql": sql,
                "columns": sanitized["columns"],
                "rows": sanitized["rows"],
                "message": sanitized["message"],
                "attempts": attempt + 1,
            }

       
        # 9. DATABASE ERROR → RETRY
        except Exception as exc:

            failed_sql = sql
            error_message = str(exc)

            log_event(
                trace_id=trace_id,
                component="database",
                event="query_execution_failed",
                payload={
                    "error_type": type(exc).__name__,
                },
                level="error",
            )

            
            # Final attempt failed
            if attempt == MAX_RETRIES:

                log_event(
                    trace_id=trace_id,
                    component="sql_executor",
                    event="request_failed",
                    payload={
                        "reason": "Maximum retry attempts reached",
                    },
                    level="error",
                )

                return {
                    "success": False,
                    "trace_id": trace_id,
                    "error_type": "database",
                    "error": (
                        "The query could not be executed "
                        "after multiple attempts."
                    ),
                    "sql": failed_sql,
                    "attempts": attempt + 1,
                    "rows": [],
                    "columns": [],
                }

            
            # Retry
            log_event(
                trace_id=trace_id,
                component="sql_executor",
                event="retry_started",
                payload={
                    "attempt": attempt + 2,
                },
                level="warning",
            )


# MANUAL TEST
if __name__ == "__main__":

    result = execute_sql_with_retry(
        question="List the top 5 customers by number of orders.",
        schema="",
        relationships="",
        lov="",
    )

    print("\n================ RESULT ================")
    print(result)