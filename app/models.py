from datetime import datetime
from app import db

class DataAudit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_name = db.Column(db.String(255), nullable=False)
    time_taken = db.Column(db.Float, nullable=False)
    records_created = db.Column(db.Integer, nullable=False)
    records_altered = db.Column(db.Integer, nullable=False)
    records_deleted = db.Column(db.Integer, nullable=False)
    errors = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Ledger(db.Model):
    name = db.Column(db.String(255), nullable=False, primary_key=True)
    opening_balance = db.Column(db.Float, nullable=False, default=0.0)
    group = db.Column(db.String(255), nullable=False, default="Unknown")

    def __init__(self, name, opening_balance, group):
        self.name = name
        self.opening_balance = opening_balance
        self.group = group

    def to_dict(self):
        """Convert the Ledger object into a JSON serializable dictionary."""
        return {
            "name": self.name,
            "opening_balance": self.opening_balance,
            "group": self.group
        }