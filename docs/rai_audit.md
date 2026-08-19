# Responsible AI Audit

## 1. System Overview

The Sales Insights Assistant is an AI-powered application that allows sales
managers to ask natural-language questions about the Northwind sales database.
The system uses an LLM to generate read-only PostgreSQL queries, validates the
generated SQL, applies output guardrails, executes approved queries, sanitizes
the results, and displays the results through a Streamlit interface.

The system includes input guardrails, SQL validation, output guardrails, result
sanitization, structured logging, end-to-end tracing, bounded retry handling,
anomaly detection, and an evaluation harness.

This audit evaluates the system from four Responsible AI perspectives:
fairness, transparency, accountability, and data minimisation.

---

# 2. Fairness

## Question

Could the system produce different quality answers depending on how a question
is phrased, such as British versus American English or formal versus informal
language?

## Assessment

Yes, there is a possibility that different phrasings of the same question could
produce different SQL queries or results because SQL generation is performed by
an LLM.

For example, the following questions should represent the same business intent:

- "List the top 5 customers by number of orders."
- "Show me the five customers who placed the most orders."
- "Which 5 customers have the highest number of orders?"
- "Can you give me the top five customers based on order count?"

The system is designed to produce equivalent SQL for these variations, but the
LLM may occasionally interpret wording differently or select a different valid
query structure.

The system does not intentionally use user identity, gender, nationality,
race, or other personal characteristics when generating SQL. The primary input
to the SQL-generation process is the business question together with database
metadata.

## Fairness Testing

Fairness was considered by testing equivalent questions with different wording,
including formal and informal language and different expressions of the same
business intent.

The expected behaviour is that semantically equivalent questions should return
the same or equivalent business results even if the generated SQL syntax differs.

The evaluation harness also provides a fixed set of questions that can be
rerun after system changes. This allows changes in answer quality to be
identified.

## Known Limitation

The system does not currently use a dedicated semantic-equivalence evaluator
to automatically compare answers from differently phrased questions.

An LLM can therefore occasionally generate different queries for questions that
have similar meanings.

## Proposed Mitigation

Future versions should include a larger paraphrase-based evaluation dataset and
automatically compare the results of semantically equivalent questions.
A semantic evaluator could also be introduced to identify meaningful differences
between answers.

---

# 3. Transparency

## Question

Does the user know that they are talking to an AI?

## Assessment

Yes. The Streamlit interface identifies the application as the "Sales Insights
Assistant" and explains that it converts natural-language questions into
read-only SQL queries against the Northwind PostgreSQL database.

The interface also provides transparency about the AI-generated SQL.

## Question

Does the user know what SQL was run on their behalf?

## Assessment

Yes. The generated SQL is displayed in the Streamlit interface for successful
requests.

The UI explicitly informs the user that the generated SQL is shown so they can
see what query was executed on their behalf.

A unique trace ID is also displayed for each request.

## Why This Matters

Showing the generated SQL allows users to inspect the query rather than treating
the AI response as an unexplained result.

The trace ID provides an additional transparency and support mechanism because
the corresponding request can be located in the application's trace and log
files.

## Known Limitation

Displaying SQL does not guarantee that a non-technical user will understand
whether the query correctly represents their business question.

## Proposed Mitigation

The interface could provide a short natural-language explanation of the generated
query, such as:

"The system counted orders for each customer and returned the five customers
with the highest order counts."

The SQL should continue to remain available for users who want technical
transparency.

---

# 4. Accountability

## Question

If the system returns a wrong answer that a manager uses to make a bad business
decision, what is the failure chain?

## Possible Failure Chain

A possible failure chain is:

1. The user asks an ambiguous or incorrectly phrased business question.
2. The input guardrail allows the question because it is not considered unsafe.
3. The LLM interprets the question incorrectly.
4. The LLM generates SQL that is syntactically valid and read-only.
5. The SQL validator approves the query because it does not violate safety
   rules.
6. The output guardrail also approves the query.
7. The database executes the query successfully.
8. The returned result is technically valid but does not represent the user's
   intended business meaning.
9. The manager relies on the result and makes an incorrect business decision.

This is an important limitation because safety validation does not guarantee
business correctness.

## Detection

The system provides several mechanisms for investigating such failures.

Each request receives a unique trace ID. The trace can contain:

- The original user question.
- The retrieved database context.
- The prompt sent to the LLM.
- The generated SQL.
- SQL validation results.
- Output guardrail decisions.
- Database execution information.
- Raw database results.
- Sanitized results shown to the user.

Structured logs also record important events such as SQL generation,
guardrail triggers, query execution, retries, and response generation.

The evaluation harness provides another mechanism for detecting regressions in
SQL generation and system behaviour.

## Accountability Measures

The system does not claim that every generated answer is guaranteed to be
correct. The generated SQL is exposed to the user and trace information is
stored for investigation.

When an error occurs, technical details are retained in logs while the user
receives a safer and more understandable error message.

## Proposed Mitigation

Future versions should introduce stronger semantic validation between the
user's question and the generated SQL. A human review mechanism could also be
used for high-impact business decisions.

---

# 5. Data Minimisation

## Question

Is the system retrieving more data than it needs to answer the question?

## Assessment

The system is designed to retrieve only the data required by the generated
SQL query.

The LLM receives database metadata, including tables, columns, relationships,
and selected list-of-value information, so that it can generate a query against
the relevant parts of the database.

The query validator restricts generated SQL to safe read-only operations.

The result sanitization layer processes database results before they are
returned to the user.

The system does not intentionally expose the entire database to the user for
every question.

## PII Protection

The input guardrail detects email addresses in user input and replaces them
with `[REDACTED_EMAIL]` before the sanitized input is passed downstream.

Result sanitization is also applied before database results are returned to the
user.

Structured logs avoid storing raw user questions and raw sensitive payloads.
Instead, logs record metadata such as question length, SQL length, row counts,
and event types.

## Known Limitation

The system relies on the generated SQL to determine the minimum required data.
An LLM could potentially generate a query that retrieves more rows or columns
than are strictly necessary while still passing basic SQL safety checks.

For example, a query could use a broad SELECT statement when a smaller set of
columns would have been sufficient.

## Proposed Mitigation

Future versions should enforce column-level and row-level access policies and
introduce stricter query constraints.

The system could also automatically reject unnecessarily broad queries and
require explicit justification for large result sets.

---

# 6. Guardrail Assessment

The system uses multiple layers of protection rather than relying on the LLM
alone.

## Input Guardrail

The input guardrail checks for:

- Prompt injection attempts.
- Jailbreak attempts.
- Email addresses and other detectable PII.
- Questions outside the sales-data scope.
- Empty inputs.

Unsafe requests are blocked before reaching the SQL-generation process.

## SQL Validation

Generated SQL is validated before database execution.

The validator is intended to prevent unsafe database operations and ensure that
only permitted read-only SQL is executed.

Unsafe SQL is not retried.

## Output Guardrail

The output guardrail performs an additional safety check on generated SQL before
execution.

Only SQL that passes the required safety checks is allowed to reach the
database.

## Result Sanitization

Database results are passed through the result sanitization layer before being
shown to the user.

This provides an additional protection layer against exposing information that
should not be directly returned.

---

# 7. Evaluation

The system includes an evaluation harness containing 15 predefined questions.

The questions include easy, medium, hard, and adversarial cases.

The final evaluation produced:

    Total questions : 15
    Passed          : 11
    Failed          : 4
    Pass rate       : 73.33%

The evaluation records the generated SQL, execution status, and result for each
question.

The evaluation harness can be rerun after system changes to identify
regressions.

The 73.33% pass rate also demonstrates that the system is not considered
perfectly reliable and that further improvements are required.

---

# 8. Traceability and Auditability

Every request receives a unique trace ID.

The trace contains information required to reconstruct the processing chain,
including:

- Original question.
- Retrieved context.
- LLM prompt.
- Generated SQL.
- Guardrail decisions.
- Database result.
- Sanitized response shown to the user.

Structured logs are stored in JSON format and contain timestamps, trace IDs,
components, event types, log levels, and sanitized payload information.

This allows developers to investigate failures without relying only on the
information displayed in the UI.

---

# 9. Overall RAI Assessment

The Sales Insights Assistant incorporates Responsible AI principles through
layered guardrails, transparency, traceability, data minimisation, evaluation,
and explicit documentation of limitations.

The strongest protections are the input guardrail, SQL validation, output
guardrail, result sanitization, structured logging, trace IDs, and evaluation
harness.

However, the system cannot guarantee that every generated query is
business-correct. A query can be safe and syntactically valid while still
misinterpreting the user's intended question.

Therefore, the system should be treated as a decision-support tool rather than
an autonomous decision-maker. Users should review important results and
consider the displayed SQL and context before making high-impact business
decisions.

Future improvements should focus on semantic validation, broader fairness
testing, stronger data-access controls, improved confidence estimation, and
human review for high-impact decisions.

---

# 10. RAI Commitments

The project commits to the following principles:

1. **Safety:** Unsafe SQL and malicious inputs should be blocked before reaching
   the database.

2. **Transparency:** Users should be able to see the generated SQL and receive
   a trace ID for each request.

3. **Privacy:** Sensitive information should be minimized, sanitized, and not
   unnecessarily written to logs.

4. **Accountability:** System failures should be traceable through structured
   logs and stored traces.

5. **Fairness:** Equivalent business questions should be evaluated across
   different phrasings to identify differences in answer quality.

6. **Honesty about limitations:** The system will not claim that LLM-generated
   answers are guaranteed to be correct.

7. **Continuous evaluation:** The evaluation harness will be rerun whenever
   significant changes are made to the system.

8. **Human oversight:** Important business decisions should not rely solely on
   an AI-generated answer without appropriate human review.