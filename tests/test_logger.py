from app.observability.logger import (
    generate_trace_id,
    log_event,
)


def test_generate_trace_id():

    trace_id = generate_trace_id()

    assert trace_id
    assert len(trace_id) > 10


def test_log_event():

    trace_id = generate_trace_id()

    log_event(
        trace_id=trace_id,
        component="test",
        event="test_event",
        payload={
            "status": "success"
        },
    )