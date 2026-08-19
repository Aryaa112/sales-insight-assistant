from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta

from app.observability.logger import log_event



# CONFIGURATION
MAX_SQL_LENGTH = 500

VALIDATION_FAILURE_THRESHOLD = 0.30

MAX_QUERIES_PER_USER = 20

WINDOW_MINUTES = 5



# IN-MEMORY TRACKING
validation_events = deque()

user_queries = defaultdict(deque)



# RULE 1 — SQL LENGTH
def check_sql_length(
    trace_id: str,
    sql: str,
):

    if len(sql) > MAX_SQL_LENGTH:

        log_event(
            trace_id=trace_id,
            component="anomaly_detector",
            event="sql_length_anomaly",
            payload={
                "sql_length": len(sql),
                "threshold": MAX_SQL_LENGTH,
            },
            level="warning",
        )

        return True

    return False



# RULE 2 — VALIDATION FAILURE RATE
def record_validation_event(
    trace_id: str,
    failed: bool,
):

    now = datetime.now(timezone.utc)

    validation_events.append(
        (now, failed)
    )

    cutoff = now - timedelta(
        minutes=10
    )

    # Remove old events
    while (
        validation_events
        and validation_events[0][0] < cutoff
    ):
        validation_events.popleft()

    total = len(validation_events)

    failures = sum(
        1
        for _, was_failed in validation_events
        if was_failed
    )

    if total == 0:
        return False

    failure_rate = failures / total

    if (
        total >= 5
        and failure_rate > VALIDATION_FAILURE_THRESHOLD
    ):

        log_event(
            trace_id=trace_id,
            component="anomaly_detector",
            event="high_validation_failure_rate",
            payload={
                "failure_rate": round(
                    failure_rate,
                    2,
                ),
                "total_queries": total,
                "failed_queries": failures,
                "threshold": VALIDATION_FAILURE_THRESHOLD,
            },
            level="critical",
        )

        return True

    return False



# RULE 3 — TOO MANY QUERIES
def record_user_query(
    trace_id: str,
    user_id: str = "default_user",
):

    now = datetime.now(timezone.utc)

    user_queries[user_id].append(now)

    cutoff = now - timedelta(
        minutes=WINDOW_MINUTES
    )

    # Remove old queries
    while (
        user_queries[user_id]
        and user_queries[user_id][0] < cutoff
    ):
        user_queries[user_id].popleft()

    query_count = len(
        user_queries[user_id]
    )

    if query_count > MAX_QUERIES_PER_USER:

        log_event(
            trace_id=trace_id,
            component="anomaly_detector",
            event="query_rate_anomaly",
            payload={
                "user_id": user_id,
                "query_count": query_count,
                "window_minutes": WINDOW_MINUTES,
                "threshold": MAX_QUERIES_PER_USER,
            },
            level="warning",
        )

        return True

    return False