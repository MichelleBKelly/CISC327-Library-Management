"""Assignment 3 tests for Michelle Kelly (Member B)."""

from datetime import date
from unittest.mock import patch


def _book(client):
    response = client.post("/books", json={
        "title": "Dune",
        "author": "Frank Herbert",
        "isbn": "978-0441172719",
        "total_copies": 1,
    })
    assert response.status_code == 201
    return response.get_json()


def _member(client, name="Ada Lovelace", email="ada@example.com"):
    response = client.post("/members", json={"name": name, "email": email})
    assert response.status_code == 201
    return response.get_json()


def _checked_out_book(client):
    book = _book(client)
    borrower = _member(client)
    response = client.post("/loans", json={
        "book_id": book["id"], "member_id": borrower["id"],
    })
    assert response.status_code == 201
    assert client.get(f"/books/{book['id']}").get_json()["available_copies"] == 0
    return book, response.get_json()


def test_return_with_hold_reports_failed_notification(client, monkeypatch):
    """A False notification result must not prevent the book's return."""
    book, loan = _checked_out_book(client)
    waiting = _member(client, name="Grace Hopper", email="grace@example.com")
    reserved = client.post("/reservations", json={
        "book_id": book["id"], "member_id": waiting["id"],
    })
    assert reserved.status_code == 201
    # Patch the imported dependency in the route that calls it.
    monkeypatch.setattr(
        "app.routes.loans.send_notification",
        lambda recipient, subject, message: False,
    )

    response = client.put(f"/loans/{loan['id']}/return")

    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == loan["id"]
    assert body["return_date"] == date.today().isoformat()
    assert body["hold_notification_attempted"] is True
    assert body["hold_notified"] is False
    assert client.get(f"/books/{book['id']}").get_json()["available_copies"] == 1
    assert client.get("/loans").get_json()[0]["return_date"] == body["return_date"]
    holds = client.get(f"/reservations?book_id={book['id']}").get_json()
    assert holds[0]["fulfilled"] is False


def test_return_without_hold_sends_no_notification(client):
    """Returning without a waiting member must not contact the notifier."""
    book, loan = _checked_out_book(client)

    with patch("app.routes.loans.send_notification") as mock_send:
        response = client.put(f"/loans/{loan['id']}/return")

    mock_send.assert_not_called()
    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == loan["id"]
    assert body["return_date"] == date.today().isoformat()
    assert body["hold_notification_attempted"] is False
    assert body["hold_notified"] is False
    assert client.get(f"/books/{book['id']}").get_json()["available_copies"] == 1
    assert client.get("/loans").get_json()[0]["return_date"] == body["return_date"]
