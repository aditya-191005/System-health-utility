# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class MachineReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.String(100), unique=True, nullable=False)
    os_name = db.Column(db.String(50))
    disk_encrypted = db.Column(db.Boolean)
    os_up_to_date = db.Column(db.Boolean)
    antivirus_present = db.Column(db.Boolean)
    sleep_timeout = db.Column(db.Integer)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
