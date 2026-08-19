# Decision Journal

## D1 — Database Choice

### Decision
Use PostgreSQL for the Sales Insights Assistant.

### Why
- Production-grade relational database
- Strong SQL and foreign-key support
- Realistic for a production application
- Supports database permissions and concurrent access

### Tradeoff
More setup than SQLite.

---

## D2 — Metadata Extraction

### Decision
Extract database metadata programmatically using SQLAlchemy and
PostgreSQL `information_schema`.

### Why
- Keeps schema information synchronized with the database
- Avoids hardcoding schema details
- Can be reused by the prompt builder

### Extracted Information
- Tables and row counts
- Columns and data types
- Foreign keys
- List of Values (LOVs)

### Tradeoff
Requires additional database queries and code.

---

## D2 — Structured Metadata

### Decision
Return metadata as a structured Python dictionary.

### Why
The metadata will be consumed by other components such as the prompt
builder.

### Tradeoff
The structure must be maintained if the schema changes.

---

## D2 — Schema Documentation

### Decision
Generate human-readable Markdown documentation from the extracted
metadata.

### Why
- Keeps documentation synchronized with the database
- Provides reusable schema context for the LLM

### Tradeoff
The complete schema may contain more information than required for
individual queries.

---

## D3 — Custom SQL Prompt

### Decision
Use a custom schema-aware prompt instead of LangChain's default SQL prompt.

### Why
The LLM needs:
- Exact table names
- Column names and data types
- Relationships
- Relevant LOVs
- SQL safety instructions

### Tradeoff
More schema context increases prompt size but improves SQL accuracy.

---

## D3 — SQL Validator

### Decision
Use a deterministic SQLGlot-based validator.

### Why
Security validation should not depend on another LLM.

The validator:
- Allows only SELECT
- Blocks DROP, DELETE, UPDATE, INSERT, CREATE and ALTER
- Rejects multiple statements
- Rejects invalid SQL
- Rejects tables outside the Northwind schema

### Tradeoff
Some unusual but valid SQL may be rejected, but deterministic
validation provides stronger safety.

---

## D3 — SQL Execution Boundary

### Decision
Never execute LLM-generated SQL directly.

### Flow
User → LLM → Generated SQL → Validator → Database

### Why
The validator acts as a security boundary between the LLM and database.

---

## D3 — Retry Strategy

### Decision
Use a maximum of 2 retries when SQL execution fails.

### Why
The LLM can correct errors such as:
- Incorrect column names
- Incorrect joins
- SQL execution errors

### Tradeoff
Some queries may still fail after two attempts, but bounded retries
prevent infinite loops and excessive API usage.

---

## D3 — Systematic Testing

### Decision
Test the system using different types of questions.

### Tested
- Simple lookup
- Aggregation
- Multi-table join
- Ambiguous question
- Unanswerable question
- Injection attempt
- Out-of-scope question

### Findings
- Simple lookup: PASS
- Multi-table join: PASS
- Aggregation: blocked due to incorrect table name
- Ambiguous query: blocked
- Unanswerable query: needs semantic guardrail
- Injection attempt: dangerous SQL was removed by the LLM
- Out-of-scope query: rejected

### Conclusion
The validator works as a security layer, but input and output guardrails
are required to handle semantic, injection, and out-of-scope risks.

---

## D3 — Overall Decision

### Decision
Separate SQL generation, validation, and database execution into different
layers.

### Why
This provides:
- Better security
- Easier debugging
- Clear responsibilities
- Defense in depth

### Tradeoff
More components make the system slightly more complex, but improve
reliability and safety.

---

## D4 — Input Guardrail

### Decision
Use deterministic rule-based checks for prompt injection, jailbreaks,
off-topic requests, and PII detection.

### Why
These checks should be predictable and should not depend on another LLM.

### PII Handling
Detect email addresses and redact them before downstream processing
or logging.

### Tradeoff
Rule-based detection may miss sophisticated attacks, but it provides
fast and deterministic protection.

---

## D4 — Output Guardrail

### Decision
Re-validate generated SQL immediately before database execution.

### Why
This provides defense in depth in addition to the D3 SQL validator.

### Checks
- SELECT only
- Allowed Northwind tables
- No dangerous SQL operations
- Maximum 100 result rows

### Tradeoff
Some legitimate large queries may be limited, but this prevents
uncontrolled result retrieval.

---

## D4 — Result Sanitization

### Decision
Sanitize database results before returning them to the user.

### Why
The database may contain columns that should not be exposed directly.

### Checks
- Remove sensitive columns
- Format numeric values
- Handle empty results explicitly

### Tradeoff
Some raw database information may be hidden from the user, but this
reduces unnecessary data exposure.

---

## D4 — Responsible AI

### Decision
Apply fairness, transparency, accountability, and data-minimisation
principles throughout the system.

### Why
The assistant supports business decisions, so incorrect or biased
answers could have real consequences.

### Approach
- Tell users they are interacting with an AI system
- Make generated SQL inspectable
- Keep sufficient execution information for debugging
- Minimise retrieved data
- Maintain human oversight for important decisions

---

## D5 — Observability, Evaluation and Anomaly Detection

### Decision
Use structured JSON logging, unique trace IDs, trace storage,
a fixed evaluation harness, and threshold-based anomaly detection.

### Evaluation
The system was tested with 15 fixed questions. 11 passed and 4 failed,
giving a pass rate of 73.33%. Results are stored in
logs/evaluation_results.json.

### Anomaly Detection
Three rules were implemented:
- SQL longer than 500 characters → WARNING
- Validation failure rate above 30% over 10 minutes → CRITICAL
- More than 20 queries from one user within 5 minutes → WARNING

### Tradeoff
The prototype uses in-memory counters for anomaly detection.
A production system would use persistent metrics and centralized
monitoring.


## Day 6 — UI Development, Integration & Final Polish

### Decision 1 — Use Streamlit for the user interface

**Decision:**  
We chose Streamlit to build the user interface for the Sales Insights Assistant.

**Reason:**  
Streamlit allows us to quickly create an interactive interface for natural-language
questions without introducing unnecessary frontend complexity. It also integrates
well with the existing Python-based backend.

**Impact:**  
Users can enter natural-language sales questions, view generated SQL, inspect
results, see the trace ID, and maintain conversation history within the session.

---

### Decision 2 — Show generated SQL to the user

**Decision:**  
The generated SQL query is displayed in the UI for every successful response.

**Reason:**  
The Responsible AI audit identified transparency as an important requirement.
Users should know what query the AI generated and what was executed on their behalf.

**Impact:**  
The system provides greater transparency and allows users to identify potentially
incorrect SQL before relying on the returned business information.

---

### Decision 3 — Display a unique trace ID for every request

**Decision:**  
Every user request receives a unique trace ID that is displayed in the Streamlit UI.

**Reason:**  
The system already uses trace IDs for structured logging and end-to-end tracing.
Showing the same ID to the user makes it possible to connect a reported problem
with the corresponding logs and trace data.

**Impact:**  
Failures and unexpected results can be investigated by searching the logs using
the trace ID.

---

### Decision 4 — Handle errors using user-friendly messages

**Decision:**  
Technical exceptions and Python stack traces are not displayed directly to users.

**Reason:**  
Exposing internal exceptions could confuse users and may reveal implementation
details. The UI should provide a clear explanation while keeping technical
details in the logs.

**Impact:**  
The application remains easier and safer to use while developers can still
investigate failures through structured logs and trace files.

---

### Decision 5 — Maintain conversation history within the Streamlit session

**Decision:**  
Conversation history is maintained using Streamlit session state.

**Reason:**  
A sales manager may need to compare multiple questions and results during the
same session. Maintaining history provides continuity without requiring a
separate conversation database.

**Impact:**  
Users can review previous questions and responses during their current session.

---

### Decision 6 — Perform integration testing across the complete pipeline

**Decision:**  
The final system is tested through the complete flow rather than testing only
individual modules.

**Reason:**  
Individual components may work correctly while integration between components
can still fail. The final test therefore checks the complete path from user
input through guardrails, SQL generation, validation, database execution,
sanitization, and UI output.

**Impact:**  
Integration testing provides stronger evidence that the complete architecture
works as intended.

---

### Decision 7 — Include adversarial testing before finalizing the system

**Decision:**  
The system is tested with malicious and unexpected inputs before final submission.

**Reason:**  
A sales assistant powered by an LLM can be vulnerable to prompt injection,
jailbreak attempts, unauthorized data requests, malformed questions, and
incorrect SQL generation. Testing these cases helps identify weaknesses that
normal functional tests may not reveal.

**Impact:**  
Identified vulnerabilities are either fixed or documented as known limitations
with proposed mitigations.

---

### Decision 8 — Keep known limitations documented instead of hiding failures

**Decision:**  
Known weaknesses discovered during testing will be explicitly documented rather
than claiming that the system is completely secure or accurate.

**Reason:**  
LLM-generated SQL can occasionally be incorrect even when it is syntactically
valid and passes safety validation. Responsible AI requires acknowledging such
limitations.

**Impact:**  
The final documentation provides a realistic description of system capabilities,
risks, and future improvements.