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
