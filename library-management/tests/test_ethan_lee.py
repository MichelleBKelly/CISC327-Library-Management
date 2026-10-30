def _create_book(client, title="Dune", author="Frank Herbert", isbn="978-0441172719", total_copies=2):
    response = client.post("/books", json={
        "title": title,
        "author": author,
        "isbn": isbn,
        "total_copies": total_copies,
    })
    assert response.status_code == 201
    return response.get_json()


def test_create_book_persists_for_later_get(client):
    created = _create_book(client)

    fetched = client.get(f"/books/{created['id']}")

    assert fetched.status_code == 200
    book = fetched.get_json()
    assert book["id"] == created["id"]
    assert book["title"] == "Dune"
    assert book["author"] == "Frank Herbert"
    assert book["isbn"] == "978-0441172719"
    assert book["total_copies"] == 2
    assert book["available_copies"] == 2


def test_update_book_changes_title_seen_by_later_get(client):
    created = _create_book(client)

    updated = client.put(f"/books/{created['id']}", json={"title": "Dune Messiah"})

    assert updated.status_code == 200
    body = updated.get_json()
    assert body["title"] == "Dune Messiah"
    assert body["author"] == "Frank Herbert"
    assert body["isbn"] == "978-0441172719"
    assert body["total_copies"] == 2
    fetched = client.get(f"/books/{created['id']}")
    assert fetched.get_json()["title"] == "Dune Messiah"


def test_get_missing_book_returns_404(client):
    response = client.get("/books/999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Book not found"


def test_search_books_matches_title_or_author_ignoring_case(client):
    _create_book(client, title="Dune", author="Frank Herbert", isbn="1")
    _create_book(client, title="Neuromancer", author="William Gibson", isbn="2")

    by_title = client.get("/books?search=dune")
    by_author = client.get("/books?search=GIBSON")

    assert by_title.status_code == 200
    assert [book["title"] for book in by_title.get_json()] == ["Dune"]
    assert by_author.status_code == 200
    assert [book["title"] for book in by_author.get_json()] == ["Neuromancer"]


def test_search_with_no_match_returns_empty_list(client):
    _create_book(client)

    response = client.get("/books?search=no-such-book")

    assert response.status_code == 200
    assert response.get_json() == []


def test_delete_book_removes_it_from_later_reads(client):
    created = _create_book(client)

    deleted = client.delete(f"/books/{created['id']}")

    assert deleted.status_code == 204
    assert client.get(f"/books/{created['id']}").status_code == 404
    assert client.get("/books").get_json() == []


def test_delete_missing_book_returns_404(client):
    response = client.delete("/books/404")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Book not found"


def _create_member(client, name="Ada Lovelace", email="ada@example.com"):
    response = client.post("/members", json={"name": name, "email": email})
    assert response.status_code == 201
    return response.get_json()


def test_create_member_persists_for_later_get(client):
    created = _create_member(client)

    fetched = client.get(f"/members/{created['id']}")

    assert fetched.status_code == 200
    member = fetched.get_json()
    assert member["id"] == created["id"]
    assert member["name"] == "Ada Lovelace"
    assert member["email"] == "ada@example.com"
    assert "membership_date" in member


def test_update_member_name_is_visible_on_later_get(client):
    created = _create_member(client)

    updated = client.put(f"/members/{created['id']}", json={"name": "Ada King"})

    assert updated.status_code == 200
    body = updated.get_json()
    assert body["name"] == "Ada King"
    assert body["email"] == "ada@example.com"
    fetched = client.get(f"/members/{created['id']}")
    assert fetched.get_json()["name"] == "Ada King"


def test_list_members_returns_each_created_member(client):
    _create_member(client, name="Ada Lovelace", email="ada@example.com")
    _create_member(client, name="Grace Hopper", email="grace@example.com")

    response = client.get("/members")

    assert response.status_code == 200
    assert [member["name"] for member in response.get_json()] == ["Ada Lovelace", "Grace Hopper"]


def test_get_and_delete_missing_member(client):
    missing = client.get("/members/999")
    assert missing.status_code == 404
    assert missing.get_json()["error"] == "Member not found"

    created = _create_member(client)
    deleted = client.delete(f"/members/{created['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/members/{created['id']}").status_code == 404
    assert client.get("/members").get_json() == []


def test_members_can_be_searched_by_name(client):
    _create_member(client, name="Ada Lovelace", email="ada@example.com")
    _create_member(client, name="Grace Hopper", email="grace@example.com")

    response = client.get("/members?search=grace")

    assert response.status_code == 200
    body = response.get_json()
    assert [member["name"] for member in body] == ["Grace Hopper"]


def test_member_can_be_found_by_library_card_number(client):
    created = client.post("/members", json={
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "card_number": "CARD-1001",
    })
    assert created.status_code == 201
    assert created.get_json()["card_number"] == "CARD-1001"

    found = client.get("/members?card_number=CARD-1001")
    assert found.status_code == 200
    assert [member["id"] for member in found.get_json()] == [created.get_json()["id"]]

    missing = client.get("/members?card_number=CARD-9999")
    assert missing.status_code == 200
    assert missing.get_json() == []

    fetched = client.get(f"/members/{created.get_json()['id']}")
    assert fetched.get_json()["card_number"] == "CARD-1001"


def test_duplicate_library_card_number_is_rejected(client):
    first = {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "card_number": "CARD-1001",
    }
    second = {
        "name": "Grace Hopper",
        "email": "grace@example.com",
        "card_number": "CARD-1001",
    }
    assert client.post("/members", json=first).status_code == 201

    rejected = client.post("/members", json=second)

    assert rejected.status_code == 409
    assert rejected.get_json()["error"] == "Card number already in use"
    assert len(client.get("/members").get_json()) == 1
