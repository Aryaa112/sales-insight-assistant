import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path


# =========================================================
# DIRECTORIES
# =========================================================

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "application.jsonl"

TRACE_DIR = LOG_DIR / "traces"
TRACE_DIR.mkdir(exist_ok=True)


# =========================================================
# TRACE ID
# =========================================================

def generate_trace_id() -> str:
    """Generate a unique ID for one request."""
    return str(uuid.uuid4())


# =========================================================
# JSON FORMATTER
# =========================================================

class JSONFormatter(logging.Formatter):

    def format(self, record):

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": getattr(record, "trace_id", None),
            "component": getattr(record, "component", "unknown"),
            "event": getattr(record, "event", "unknown"),
            "payload": getattr(record, "payload", {}),
            "level": record.levelname,
        }

        return json.dumps(
            log_entry,
            default=str
        )


# =========================================================
# LOGGER SETUP
# =========================================================

logger = logging.getLogger("sales_insights")

logger.setLevel(logging.INFO)

# Prevent duplicate handlers
if not logger.handlers:

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )

    file_handler.setFormatter(
        JSONFormatter()
    )

    logger.addHandler(file_handler)


# =========================================================
# STRUCTURED LOG FUNCTION
# =========================================================

def log_event(
    trace_id: str,
    component: str,
    event: str,
    payload: dict | None = None,
    level: str = "info",
):
    """
    Write one structured JSON log entry.

    Do not place raw PII inside payload.
    """

    payload = payload or {}

    extra = {
        "trace_id": trace_id,
        "component": component,
        "event": event,
        "payload": payload,
    }

    if level == "warning":

        logger.warning(
            event,
            extra=extra
        )

    elif level == "error":

        logger.error(
            event,
            extra=extra
        )

    elif level == "critical":

        logger.critical(
            event,
            extra=extra
        )

    else:

        logger.info(
            event,
            extra=extra
        )


# =========================================================
# TRACE CREATION
# =========================================================

def create_trace(
    trace_id: str,
    question: str,
):
    """
    Create a complete trace object for one request.
    """

    trace = {

        "trace_id": trace_id,

        "created_at": (
            datetime.now(timezone.utc).isoformat()
        ),

        "original_question": question,

        "context": {
            "schema": None,
            "relationships": None,
            "lov": None,
        },

        "llm": {
            "prompt": None,
            "generated_sql": None,
        },

        "guardrails": [],

        "database": {
            "raw_result": None,
        },

        "response": {
            "shown_to_user": None,
        },
    }

    save_trace(trace)

    return trace



# SAVE TRACE
def save_trace(trace: dict):
    """
    Save the complete trace as a JSON file.
    """

    trace_id = trace["trace_id"]

    trace_file = TRACE_DIR / f"{trace_id}.json"

    with open(
        trace_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            trace,
            file,
            indent=2,
            default=str
        )



# UPDATE TRACE
def update_trace(
    trace: dict,
    section: str,
    data,
):
    """
    Update one section of the trace and save it.
    """

    if section == "guardrails":

        trace["guardrails"].append(data)

    elif section == "context":

        trace["context"].update(data)

    elif section == "llm":

        trace["llm"].update(data)

    elif section == "database":

        trace["database"].update(data)

    elif section == "response":

        trace["response"].update(data)

    save_trace(trace)