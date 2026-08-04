"""
AI Failure Triage helper module.
"""


def triage_failure(exception_info: str) -> str:
    """Analyze test failure stack trace."""
    if "TimeoutError" in exception_info:
        return "Element timeout - check element visibility or locator strategy."
    if "AssertionError" in exception_info:
        return "Assertion mismatch - verify expected test data vs actual DOM."
    return "General test error: inspect logs and screenshots."
