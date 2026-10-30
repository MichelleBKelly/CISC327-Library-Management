from datetime import date

from flask import Blueprint, jsonify, request

from app import store
from app.models.reservation import Reservation

reservations_bp = Blueprint("reservations", __name__, url_prefix="/reservations")


@reservations_bp.route("", methods=["GET"])
def list_reservations():
    results = list(store.reservations.values())
    book_id = request.args.get("book_id", type=int)
    member_id = request.args.get("member_id", type=int)
    if book_id is not None:
        results = [r for r in results if r.book_id == book_id]
    if member_id is not None:
        results = [r for r in results if r.member_id == member_id]
    return jsonify([r.to_dict() for r in results])


@reservations_bp.route("", methods=["POST"])
def create_reservation():
    data = request.get_json()
    book = store.books.get(data["book_id"])
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    member = store.members.get(data["member_id"])
    if member is None:
        return jsonify({"error": "Member not found"}), 404

    reservation_id = store.next_id("reservation")
    reservation = Reservation(
        id=reservation_id,
        book_id=data["book_id"],
        member_id=data["member_id"],
        reservation_date=date.today(),
        fulfilled=False,
    )
    store.reservations[reservation_id] = reservation
    return jsonify(reservation.to_dict()), 201
