# controllers.py
from flask import request
from flask_restful import Resource
from models import db, MachineReport

class ReportReceiver(Resource):
    def post(self):
        data = request.get_json()
        machine_id = data.get("machine_id")

        if not machine_id:
            return {"error": "machine_id is required"}, 400

        existing = MachineReport.query.filter_by(machine_id=machine_id).first()

        if not existing:
            # New machine — insert
            new_report = MachineReport(**data)
            db.session.add(new_report)
            db.session.commit()
            return {"msg": "New report saved"}, 200

        EXCLUDED_FIELDS = {"id", "last_updated"}
        has_changed = False

        for key, value in data.items():
            if key in EXCLUDED_FIELDS:
                continue
            if hasattr(existing, key):
                current_value = getattr(existing, key)

                # Optional: normalize boolean/string mismatch
                if isinstance(current_value, bool):
                    value = bool(value)
                elif isinstance(current_value, int):
                    try:
                        value = int(value)
                    except:
                        pass

                if current_value != value:
                    setattr(existing, key, value)
                    has_changed = True

        if has_changed:
            db.session.commit()
            print(f"Updated report for machine_id: {machine_id}")
            return {"msg": "Existing report updated"}, 200
        else:
            print(f"No changes detected for machine_id: {machine_id}")
            return {"msg": "No changes detected"}, 200
        

