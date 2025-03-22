from app import create_app, db
from app.models import User, Patient, AccessPermission
from werkzeug.security import generate_password_hash

app = create_app()

def seed_database():
    with app.app_context():
        try:
            # Create tables
            db.create_all()

            # Create admin user
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', role='admin')
                admin.set_password('admin123')
                db.session.add(admin)

            # Create doctors
            doctors = [
                ('dr_smith', 'doctor123', 'doctor'),
                ('dr_jones', 'doctor123', 'doctor'),
            ]
            for username, password, role in doctors:
                if not User.query.filter_by(username=username).first():
                    user = User(username=username, role=role)
                    user.set_password(password)
                    db.session.add(user)

            # Commit the doctors to ensure their IDs are available
            db.session.commit()

            # Create patients
            patients_data = [
                {'username': 'patient1', 'password': 'patient123', 'name': 'John Doe', 'age': 35, 'disease': 'Diabetes', 'doctor_id': 2},
                {'username': 'patient2', 'password': 'patient123', 'name': 'Jane Smith', 'age': 28, 'disease': 'Hypertension', 'doctor_id': 3},
            ]
            for data in patients_data:
                if not User.query.filter_by(username=data['username']).first():
                    user = User(username=data['username'], role='patient')
                    user.set_password(data['password'])
                    db.session.add(user)
                    db.session.flush()  # Ensure user ID is available

                    patient = Patient(
                        name=data['name'],
                        age=data['age'],
                        disease=data['disease'],
                        doctor_id=data['doctor_id'],  # Add doctor_id
                        user_id=user.id
                    )
                    db.session.add(patient)

            # Commit the patients to ensure their IDs are available
            db.session.commit()

            # Insert data into the access_permissions table
            access_permissions_data = [
                {'doctor_id': 2, 'patient_id': 1, 'granted': True},
                {'doctor_id': 3, 'patient_id': 2, 'granted': True},
            ]
            for data in access_permissions_data:
                access_permission = AccessPermission(
                    doctor_id=data['doctor_id'],
                    patient_id=data['patient_id'],
                    granted=data['granted']
                )
                db.session.add(access_permission)

            db.session.commit()
            print("Database seeded successfully!")
        except Exception as e:
            print(f"Error seeding database: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    seed_database()