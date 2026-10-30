# Library Management System (LMS)

A small Flask REST API for tracking books, members, and loans. Data is stored
**in memory** (plain Python objects, no database) and is reset every time the
app restarts — this project is meant to run before you've covered databases.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

The API runs at `http://127.0.0.1:5000`.

## Web UI

Open `http://127.0.0.1:5000/` in a browser for a basic HTML front end (plain
forms and tables, no JavaScript) to add/delete books and members, and check
books in/out:

| Page | Path |
|---|---|
| Home | `/` |
| Books | `/ui/books` |
| Members | `/ui/members` |
| Loans | `/ui/loans` |

This UI is separate from the JSON API below — it's there so you can see the
app working without a REST client, and calls the same in-memory store.

## Entities

- **Book**: `id, title, author, isbn, total_copies, available_copies`
- **Member**: `id, name, email, membership_date, card_number`
- **Loan**: `id, book_id, member_id, loan_date, due_date, return_date`

## JSON API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/books` | List all books |
| POST | `/books` | Create a book |
| GET | `/books/<id>` | Get one book |
| PUT | `/books/<id>` | Update a book |
| DELETE | `/books/<id>` | Delete a book |
| GET | `/members` | List members. Optional `search` matches the name, and optional `card_number` matches the library card. |
| POST | `/members` | Create a member. Optional `card_number` is the library card number. A repeated card number returns 409. |
| GET | `/members/<id>` | Get one member |
| PUT | `/members/<id>` | Update a member |
| DELETE | `/members/<id>` | Delete a member |
| POST | `/loans` | Check out a book (`book_id`, `member_id`). Fails with 404 if the book or member does not exist, and with 409 if no copies remain or another member is first in the hold queue. Checking out fulfills that member's hold. |
| PUT | `/loans/<id>/return` | Return a loaned book |
| PUT | `/loans/<id>/renew` | Extend the due date by 14 days. Fails with 409 when another member is waiting for the book. |
| GET | `/loans/<id>/fine` | Report the overdue fine at $0.25 per day. A returned loan still calculates through today; that defect is documented in the group report. |
| GET | `/loans?member_id=&book_id=` | Look up loans by member id, book id, or both |
| GET | `/reservations` | List holds. Optional `book_id` and `member_id` filters. |
| POST | `/reservations` | Place a hold (`book_id`, `member_id`) |

## Tests

```bash
pytest
```
