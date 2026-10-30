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
