"""Assignment 3 tests — Ethan Lee (Member A).

Covers hold-available notification success (stub + mock) and uncovered UI /
member-update behavior from the baseline coverage report.
"""

from unittest.mock import patch

from app import store


def _book(client, title="Dune", isbn="1", total_copies=1):
    response = client.post("/books", json={
        "title": title,
        "author": "Frank Herbert",
        "isbn": isbn,
        "total_copies": total_copies,
    })
    assert response.status_code == 201
    return response.get_json()


def _member(client, name="Ada Lovelace", email="ada@example.com", card_number=None):
    payload = {"name": name, "email": email}
    if card_number is not None:
        payload["card_number"] = card_number
    response = client.post("/members", json=payload)
    assert response.status_code == 201
    return response.get_json()


def _loan_with_waiting_hold(client):
    book = _book(client, total_copies=1)
    borrower = _member(client, name="Grace Hopper", email="grace@example.com")
    waiting = _member(client, name="Ada Lovelace", email="ada@example.com")
    loan = client.post(
        "/loans",
        json={"book_id": book["id"], "member_id": borrower["id"]},
    ).get_json()
    reserved = client.post(
        "/reservations",
        json={"book_id": book["id"], "member_id": waiting["id"]},
    )
    assert reserved.status_code == 201
    return book, waiting, loan


def test_return_with_hold_reports_successful_notification(client, monkeypatch):
    """Stub: notification succeeds; return still completes and reports notified."""
    book, waiting, loan = _loan_with_waiting_hold(client)
    monkeypatch.setattr(
        "app.routes.loans.send_notification",
        lambda recipient, subject, message: True,
    )

    response = client.put(f"/loans/{loan['id']}/return")

    assert response.status_code == 200
    body = response.get_json()
    assert body["return_date"] is not None
    assert body["hold_notification_attempted"] is True
    assert body["hold_notified"] is True
    assert client.get(f"/books/{book['id']}").get_json()["available_copies"] == 1
    assert waiting["email"] == "ada@example.com"


def test_return_with_hold_sends_expected_notification_details(client):
    """Mock: verify recipient, subject, message, and call count on success."""
    book, waiting, loan = _loan_with_waiting_hold(client)
    expected_message = (
        f"Hello {waiting['name']}, your hold on \"{book['title']}\" is available "
        f"for pickup at Queen's City Library."
    )

    with patch("app.routes.loans.send_notification", return_value=True) as mock_send:
        response = client.put(f"/loans/{loan['id']}/return")

    assert response.status_code == 200
    body = response.get_json()
    assert body["hold_notified"] is True
    assert body["hold_notification_attempted"] is True
    mock_send.assert_called_once_with(
        waiting["email"],
        "Hold available",
        expected_message,
    )
    assert client.get(f"/books/{book['id']}").get_json()["available_copies"] == 1


def test_home_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Library" in response.data or b"library" in response.data.lower()


def test_books_ui_create_and_delete(client):
    create = client.post("/ui/books", data={
        "title": "Neuromancer",
        "author": "William Gibson",
        "isbn": "978-0441569595",
        "total_copies": "2",
    }, follow_redirects=True)
    assert create.status_code == 200
    assert b"Neuromancer" in create.data
    assert len(store.books) == 1
    book_id = next(iter(store.books))

    deleted = client.post(f"/ui/books/{book_id}/delete", follow_redirects=True)
    assert deleted.status_code == 200
    assert store.books == {}


def test_members_ui_create_delete_and_duplicate_card(client):
    first = client.post("/ui/members", data={
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "card_number": "CARD-42",
    }, follow_redirects=True)
    assert first.status_code == 200
    assert b"Ada Lovelace" in first.data
    assert len(store.members) == 1

    duplicate = client.post("/ui/members", data={
        "name": "Grace Hopper",
        "email": "grace@example.com",
        "card_number": "CARD-42",
    }, follow_redirects=True)
    assert duplicate.status_code == 200
    assert b"Card number already in use" in duplicate.data
    assert len(store.members) == 1

    member_id = next(iter(store.members))
    deleted = client.post(f"/ui/members/{member_id}/delete", follow_redirects=True)
    assert deleted.status_code == 200
    assert store.members == {}


def test_loans_ui_checkout_success_and_error(client):
    book = _book(client, total_copies=1)
    member = _member(client)

    success = client.post("/ui/loans", data={
        "book_id": str(book["id"]),
        "member_id": str(member["id"]),
    }, follow_redirects=True)
    assert success.status_code == 200
    assert len(store.loans) == 1

    blocked = client.post("/ui/loans", data={
        "book_id": str(book["id"]),
        "member_id": str(member["id"]),
    }, follow_redirects=True)
    assert blocked.status_code == 200
    assert b"No copies available" in blocked.data
    assert len(store.loans) == 1


def test_loans_ui_return_restores_copy(client):
    book = _book(client, total_copies=1)
    member = _member(client)
    loan = client.post(
        "/loans",
        json={"book_id": book["id"], "member_id": member["id"]},
    ).get_json()

    returned = client.post(f"/ui/loans/{loan['id']}/return", follow_redirects=True)
    assert returned.status_code == 200
    assert store.loans[loan["id"]].return_date is not None
    assert store.books[book["id"]].available_copies == 1


def test_update_member_card_number_and_reject_duplicate(client):
    first = _member(client, name="Ada Lovelace", email="ada@example.com", card_number="CARD-1")
    second = _member(client, name="Grace Hopper", email="grace@example.com", card_number="CARD-2")

    updated = client.put(f"/members/{second['id']}", json={"card_number": "CARD-1"})
    assert updated.status_code == 409
    assert updated.get_json()["error"] == "Card number already in use"

    cleared = client.put(f"/members/{first['id']}", json={"card_number": ""})
    assert cleared.status_code == 200
    assert cleared.get_json()["card_number"] is None
    assert client.get(f"/members/{first['id']}").get_json()["card_number"] is None
