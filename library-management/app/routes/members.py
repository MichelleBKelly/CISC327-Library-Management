from flask import Blueprint, jsonify, request

from app import store
from app.models.member import Member

members_bp = Blueprint("members", __name__, url_prefix="/members")


def _card_in_use(card_number, ignore_member_id=None):
    if not card_number:
        return False
    for member in store.members.values():
        if member.id == ignore_member_id:
            continue
        if member.card_number == card_number:
            return True
    return False


@members_bp.route("", methods=["GET"])
def list_members():
    results = list(store.members.values())
    search = request.args.get("search", "").strip().lower()
    card_number = request.args.get("card_number", "").strip()
    if search:
        results = [member for member in results if search in member.name.lower()]
    if card_number:
        results = [member for member in results if member.card_number == card_number]
    return jsonify([member.to_dict() for member in results])


@members_bp.route("", methods=["POST"])
def create_member():
    data = request.get_json()
    card_number = data.get("card_number") or None
    if _card_in_use(card_number):
        return jsonify({"error": "Card number already in use"}), 409
    member_id = store.next_id("member")
    member = Member(
        id=member_id,
        name=data["name"],
        email=data["email"],
        card_number=card_number,
    )
    store.members[member_id] = member
    return jsonify(member.to_dict()), 201


@members_bp.route("/<int:member_id>", methods=["GET"])
def get_member(member_id):
    member = store.members.get(member_id)
    if member is None:
        return jsonify({"error": "Member not found"}), 404
    return jsonify(member.to_dict())


@members_bp.route("/<int:member_id>", methods=["PUT"])
def update_member(member_id):
    member = store.members.get(member_id)
    if member is None:
        return jsonify({"error": "Member not found"}), 404
    data = request.get_json()
    if "card_number" in data:
        card_number = data.get("card_number") or None
        if _card_in_use(card_number, ignore_member_id=member.id):
            return jsonify({"error": "Card number already in use"}), 409
        member.card_number = card_number
    member.name = data.get("name", member.name)
    member.email = data.get("email", member.email)
    return jsonify(member.to_dict())


@members_bp.route("/<int:member_id>", methods=["DELETE"])
def delete_member(member_id):
    member = store.members.pop(member_id, None)
    if member is None:
        return jsonify({"error": "Member not found"}), 404
    return "", 204
