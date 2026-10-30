from datetime import date, timedelta

from app.models.loan import LOAN_PERIOD_DAYS


def _book(client, title="Dune", isbn="1", total_copies=1):
    response = client.post("/books", json={
        "title": title,
        "author": "Frank Herbert",
        "isbn": isbn,
        "total_copies": total_copies,
    })
    assert response.status_code == 201
    return response.get_json()


def _member(client, name="Ada Lovelace", email="ada@example.com"):
    response = client.post("/members", json={"name": name, "email": email})
    assert response.status_code == 201
    return response.get_json()


def test_checkout_decrements_available_copies_and_sets_due_date(client):
    book = _book(client, total_copies=2)
    member = _member(client)

    response = client.post("/loans", json={"book_id": book["id"], "member_id": member["id"]})

    assert response.status_code == 201
    loan = response.get_json()
    assert loan["book_id"] == book["id"]
    assert loan["member_id"] == member["id"]
    assert loan["return_date"] is None
    assert loan["loan_date"] == date.today().isoformat()
    expected_due = date.today() + timedelta(days=LOAN_PERIOD_DAYS)
    assert loan["due_date"] == expected_due.isoformat()
    fetched = client.get(f"/books/{book['id']}").get_json()
    assert fetched["available_copies"] == 1


def test_checkout_missing_book_returns_404(client):
    member = _member(client)

    response = client.post("/loans", json={"book_id": 999, "member_id": member["id"]})

    assert response.status_code == 404
    assert response.get_json()["error"] == "Book not found"


def test_checkout_missing_member_returns_404(client):
    book = _book(client)

    response = client.post("/loans", json={"book_id": book["id"], "member_id": 999})

    assert response.status_code == 404
    assert response.get_json()["error"] == "Member not found"


def test_checkout_rejected_when_no_copies_remain(client):
    book = _book(client, total_copies=1)
    first = _member(client, name="Ada Lovelace", email="ada@example.com")
    second = _member(client, name="Grace Hopper", email="grace@example.com")
    first_loan = client.post("/loans", json={"book_id": book["id"], "member_id": first["id"]})
    assert first_loan.status_code == 201

    second_loan = client.post("/loans", json={"book_id": book["id"], "member_id": second["id"]})

    assert second_loan.status_code == 409
    assert client.get(f"/books/{book['id']}").get_json()["available_copies"] == 0


def test_return_restores_available_copies_and_records_return_date(client):
    book = _book(client, total_copies=1)
    member = _member(client)
    loan = client.post("/loans", json={"book_id": book["id"], "member_id": member["id"]}).get_json()

    response = client.put(f"/loans/{loan['id']}/return")

    assert response.status_code == 200
    assert response.get_json()["return_date"] == date.today().isoformat()
    assert client.get(f"/books/{book['id']}").get_json()["available_copies"] == 1


def test_return_missing_loan_returns_404(client):
    response = client.put("/loans/999/return")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Loan not found"


def test_returning_a_loan_twice_is_rejected(client):
    book = _book(client)
    member = _member(client)
    loan = client.post("/loans", json={"book_id": book["id"], "member_id": member["id"]}).get_json()
    assert client.put(f"/loans/{loan['id']}/return").status_code == 200

    again = client.put(f"/loans/{loan['id']}/return")

    assert again.status_code == 400
    assert again.get_json()["error"] == "Loan already returned"


def test_loans_can_be_filtered_by_book_id(client):
    first = _book(client, title="Dune", isbn="1", total_copies=1)
    second = _book(client, title="Neuromancer", isbn="2", total_copies=1)
    member = _member(client)
    client.post("/loans", json={"book_id": first["id"], "member_id": member["id"]})
    client.post("/loans", json={"book_id": second["id"], "member_id": member["id"]})

    response = client.get(f"/loans?book_id={second['id']}")

    assert response.status_code == 200
    loans = response.get_json()
    assert len(loans) == 1
    assert loans[0]["book_id"] == second["id"]


def test_loans_can_be_filtered_by_member_id(client):
    _book(client, title="Placeholder", isbn="0")
    book = _book(client, title="Dune", isbn="1")
    member = _member(client)
    assert member["id"] != book["id"]
    client.post("/loans", json={"book_id": book["id"], "member_id": member["id"]})

    response = client.get(f"/loans?member_id={member['id']}")

    assert response.status_code == 200
    loans = response.get_json()
    assert len(loans) == 1
    assert loans[0]["member_id"] == member["id"]
    assert loans[0]["book_id"] == book["id"]
