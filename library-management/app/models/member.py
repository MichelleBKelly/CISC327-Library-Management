from datetime import date


class Member:
    def __init__(self, id, name, email, membership_date=None, card_number=None):
        self.id = id
        self.name = name
        self.email = email
        self.membership_date = membership_date or date.today()
        self.card_number = card_number

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "membership_date": self.membership_date.isoformat(),
            "card_number": self.card_number,
        }
