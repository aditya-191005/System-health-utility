# app.py
from flask import Flask,render_template,Response,request,make_response
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
import csv
from models import db,MachineReport
from controllers import ReportReceiver

def create_app():
    app = Flask(__name__,template_folder="../frontend/templates")
    ADMIN_USERNAME = "adi"
    ADMIN_PASSWORD = "aditya123"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthchecker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    api = Api(app)

    # Register resources
    api.add_resource(ReportReceiver, '/report')
   
    def check_auth(username, password):
        return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

    def authenticate():
        return Response(
            'Could not verify your access level.\n'
            'You have to login with proper credentials', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'})

    @app.route('/')
    def admin_dashboard():
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()

        # authorized: load your dashboard
        os_filter = request.args.get('os', None)
        issue_filter = request.args.get('issue', None)

        query = MachineReport.query

        if os_filter:
            query = query.filter(MachineReport.os_name.ilike(f"%{os_filter}%"))  # Case-insensitive match

        if issue_filter:
            if issue_filter == 'disk_encryption':
                query = query.filter(MachineReport.disk_encrypted == False)
            elif issue_filter == 'os_update':
                query = query.filter(MachineReport.os_up_to_date == False)
            elif issue_filter == 'antivirus':
                query = query.filter(MachineReport.antivirus_present == False)
            elif issue_filter == 'sleep_timeout':
                query = query.filter(MachineReport.sleep_timeout > 10)
        machines = query.all()
        return render_template('admin_dashboard.html', machines=machines)
    
    @app.route('/export/csv')
    def export_csv():
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()

        machines = MachineReport.query.all()

        # Create CSV in memory
        def generate_csv():
            output = []
            # Header row
            header = ['Machine ID', 'OS', 'Disk Encrypted', 'OS Up-to-date', 'Antivirus', 'Sleep Timeout (min)', 'Last Check-in']
            output.append(header)

            for m in machines:
                row = [
                    m.machine_id,
                    m.os_name,
                    "Yes" if m.disk_encrypted else "No",
                    "Yes" if m.os_up_to_date else "No",
                    "Yes" if m.antivirus_present else "No",
                    str(m.sleep_timeout),
                    m.last_updated.strftime('%Y-%m-%d %H:%M:%S')
                ]
                output.append(row)
            
            # Use csv module to convert list of lists into CSV string
            import io
            csv_file = io.StringIO()
            writer = csv.writer(csv_file)
            writer.writerows(output)
            return csv_file.getvalue()

        csv_data = generate_csv()
        response = make_response(csv_data)
        response.headers['Content-Disposition'] = 'attachment; filename=machines_report.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response
    
    with app.app_context():
        db.create_all()
    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
