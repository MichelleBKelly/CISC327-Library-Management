"""Simulated external notification service for the library project.

This module stands in for a real email/SMS provider. It makes no network
calls and never sends real messages. Customize lightly for the project, but
keep send_notification(recipient, subject, message) -> bool unchanged.
"""

SENDER_NAME = "Queen's City Library"
SUBJECT_PREFIX = "[City Library]"


def send_notification(recipient, subject, message):
    """Pretend to send a notification.

    Returns True on simulated success and False on simulated failure.
    An empty or clearly invalid recipient fails without raising.
    """
    if not recipient or "@" not in str(recipient):
        return False

    # Simulated delivery log for local debugging; tests replace this function.
    print(
        f"{SENDER_NAME} -> {recipient}\n"
        f"Subject: {SUBJECT_PREFIX} {subject}\n"
        f"{message}"
    )
    return True
