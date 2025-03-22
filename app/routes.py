from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Patient, AccessPermission
from flask import current_app

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role'].lower()  # Ensure role is lowercase

        user = User.query.filter_by(username=username, role=role).first()
        
        if user and user.check_password(password):
            login_user(user)

            # Log the login transaction
            current_app.blockchain.new_transaction(
                action="login",
                user_id=user.id
            )
            current_app.blockchain.new_block(proof=12345)  # Mine a new block

            if user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            elif user.role == 'doctor':
                return redirect(url_for('main.doctor_dashboard'))
            elif user.role == 'patient':
                return redirect(url_for('main.patient_dashboard'))
        
        return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@bp.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return "Unauthorized", 403

    try:
        # Fetch blockchain data
        chain = current_app.blockchain.chain
        
        # Debug: Print blockchain data
        print("Blockchain Data:", chain)
        
        # Render the template
        return render_template('admin.html', chain=chain)
    except Exception as e:
        print(f"Error in admin_dashboard: {str(e)}")  # Log the error
        return "An error occurred while loading the admin dashboard.", 500

@bp.route('/doctor')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        return "Unauthorized", 403

    try:
        # Fetch patients assigned to this doctor from AccessPermission
        access_permissions = AccessPermission.query.filter_by(
            doctor_id=current_user.id,
            granted=True
        ).all()

        # Extract patient IDs from access permissions
        patient_ids = [ap.patient_id for ap in access_permissions]

        # Fetch patients using the extracted IDs
        patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()

        # Fetch all patients for the "Request Access" feature
        all_patients = Patient.query.all()

        return render_template('doctor.html', patients=patients, all_patients=all_patients)
    except Exception as e:
        # Log the error
        print(f"Error in doctor_dashboard: {str(e)}")
        return "An error occurred while loading the doctor dashboard.", 500

@bp.route('/doctor/<int:doctor_id>')
@login_required
def doctor_profile(doctor_id):
    if current_user.id != doctor_id and current_user.role != 'admin':
        return "Unauthorized", 403

    try:
        # Fetch patients assigned to this doctor from AccessPermission
        access_permissions = AccessPermission.query.filter_by(
            doctor_id=doctor_id,
            granted=True
        ).all()

        # Debug: Print access permissions
        print("Access Permissions:", access_permissions)

        # Extract patient IDs from access permissions
        patient_ids = [ap.patient_id for ap in access_permissions]

        # Debug: Print patient IDs
        print("Patient IDs:", patient_ids)

        # Fetch patients using the extracted IDs
        patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()

        # Debug: Print patients
        print("Patients:", patients)

        # Fetch all patients for the "Request Access" feature
        all_patients = Patient.query.all()

        return render_template(
            'doctor_profile.html',
            doctor=current_user,
            patients=patients,
            all_patients=all_patients
        )
    except Exception as e:
        # Log the error
        print(f"Error in doctor_profile: {str(e)}")
        return "An error occurred while loading the doctor profile.", 500

@bp.route('/patient')
@login_required
def patient_dashboard():
    if current_user.role != 'patient':
        return "Unauthorized", 403

    # Fetch the patient's details
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        print("Patient not found for user:", current_user.id)
        return "Patient not found", 404

    # Debug: Print patient details
    print(f"Patient: {patient.name}, ID: {patient.id}")

    # Fetch access requests and granted access
    access_requests = AccessPermission.query.filter_by(patient_id=patient.id, granted=False).all()
    granted_access = AccessPermission.query.filter_by(patient_id=patient.id, granted=True).all()

    # Debug: Print access requests and granted access
    print(f"Access Requests: {access_requests}")
    print(f"Granted Access: {granted_access}")

    # Fetch access logs from the blockchain
    access_logs = []
    if current_app.blockchain and current_app.blockchain.chain:
        for block in current_app.blockchain.chain:
            if 'transactions' in block:  # Check if 'transactions' key exists
                for transaction in block['transactions']:  # Access 'transactions' as a dictionary key
                    if transaction.get('patient_id') == patient.id and transaction.get('action') == "file_accessed":
                        doctor = User.query.get(transaction.get('doctor_id'))
                        if doctor:
                            access_logs.append({
                                "doctor_username": doctor.username,
                                "timestamp": transaction.get('timestamp')
                            })
                        else:
                            print(f"Doctor not found for ID: {transaction.get('doctor_id')}")

    # Debug: Print access logs
    print(f"Access Logs: {access_logs}")

    return render_template(
        'patient.html',
        patient=patient,
        access_requests=access_requests,
        granted_access=granted_access,
        access_logs=access_logs
    )


@bp.route('/patient/<int:patient_id>')
@login_required
def patient_profile(patient_id):
    if current_user.role != 'patient' or current_user.patient.id != patient_id:
        return "Unauthorized", 403

    # Fetch the patient's details
    patient = Patient.query.get_or_404(patient_id)

    # Fetch access requests and granted access
    access_requests = AccessPermission.query.filter_by(patient_id=patient_id, granted=False).all()
    granted_access = AccessPermission.query.filter_by(patient_id=patient_id, granted=True).all()

    # Fetch access logs from the blockchain
    access_logs = []
    if current_app.blockchain and current_app.blockchain.chain:
        for block in current_app.blockchain.chain:
            if 'transactions' in block:  # Check if 'transactions' key exists
                for transaction in block['transactions']:  # Access 'transactions' as a dictionary key
                    if transaction.get('patient_id') == patient.id and transaction.get('action') == "file_accessed":
                        doctor = User.query.get(transaction.get('doctor_id'))
                        if doctor:
                            access_logs.append({
                                "doctor_username": doctor.username,
                                "timestamp": transaction.get('timestamp')
                            })

    return render_template(
        'patient_profile.html',
        patient=patient,
        access_requests=access_requests,
        granted_access=granted_access,
        access_logs=access_logs
    )

@bp.route('/request_access/<int:patient_id>')
@login_required
def request_access(patient_id):
    if current_user.role != 'doctor':
        return "Unauthorized", 403

    # Debug: Print all access permissions before creating a new one
    print("Access Permissions Before Request:", AccessPermission.query.all())

    # Check if the request already exists
    existing_request = AccessPermission.query.filter_by(
        doctor_id=current_user.id,
        patient_id=patient_id
    ).first()

    if not existing_request:
        # Debug: Print the doctor and patient IDs
        print(f"Creating new access request for Doctor ID: {current_user.id}, Patient ID: {patient_id}")

        # Create a new access request
        access_request = AccessPermission(
            doctor_id=current_user.id,
            patient_id=patient_id,
            granted=False  # Set to False for pending requests
        )
        db.session.add(access_request)
        db.session.commit()

        # Debug: Print all access permissions after creating a new one
        print("Access Permissions After Request:", AccessPermission.query.all())

        # Add the request to the blockchain
        current_app.blockchain.new_transaction(
            action="access_requested",
            doctor_id=current_user.id,
            patient_id=patient_id
        )
        current_app.blockchain.new_block(proof=12345)  # Mine a new block

        flash("Access request sent successfully.", "success")  # Use flash here
    else:
        flash("Access request already exists.", "info")  # Use flash here

    return redirect(url_for('main.doctor_profile', doctor_id=current_user.id))

@bp.route('/grant_access/<int:doctor_id>')
@login_required
def grant_access(doctor_id):
    if current_user.role != 'patient':
        return "Unauthorized", 403

    # Debug: Print all access permissions before granting access
    print("Access Permissions Before Grant:", AccessPermission.query.all())

    # Grant access to the doctor
    access = AccessPermission.query.filter_by(
        doctor_id=doctor_id,
        patient_id=current_user.patient.id
    ).first()

    if access:
        # Debug: Print the access permission being updated
        print(f"Updating access permission: Doctor ID: {doctor_id}, Patient ID: {current_user.patient.id}")

        access.granted = True
        db.session.commit()

        # Debug: Print all access permissions after granting access
        print("Access Permissions After Grant:", AccessPermission.query.all())

        # Add the grant to the blockchain
        current_app.blockchain.new_transaction(
            action="access_granted",
            doctor_id=doctor_id,
            patient_id=current_user.patient.id
        )
        current_app.blockchain.new_block(proof=12345)  # Mine a new block

        # Flash a success message
        flash(f"Access granted to Dr. {access.doctor.username}", "success")
    else:
        # Debug: Print why the access request was not found
        print(f"Access request not found for Doctor ID: {doctor_id}, Patient ID: {current_user.patient.id}")
        flash("Access request not found.", "error")

    return redirect(url_for('main.patient_profile', patient_id=current_user.patient.id))

@bp.route('/revoke_access/<int:doctor_id>')
@login_required
def revoke_access(doctor_id):
    if current_user.role != 'patient':
        return "Unauthorized", 403

    # Revoke access from the doctor
    access = AccessPermission.query.filter_by(
        doctor_id=doctor_id,
        patient_id=current_user.patient.id
    ).first()

    if access:
        # Store the doctor's username before deleting the access
        doctor_username = access.doctor.username

        # Delete the access permission
        db.session.delete(access)
        db.session.commit()

        # Add the revoke to the blockchain
        current_app.blockchain.new_transaction(
            action="access_revoked",
            doctor_id=doctor_id,
            patient_id=current_user.patient.id
        )
        current_app.blockchain.new_block(proof=12345)  # Mine a new block

        # Flash a success message
        flash(f"Access revoked for Dr. {doctor_username}", "success")
    else:
        flash("Access request not found.", "error")

    return redirect(url_for('main.patient_profile', patient_id=current_user.patient.id))

@bp.route('/doctor/patient/<int:patient_id>')
@login_required
def view_patient_record(patient_id):
    if current_user.role != 'doctor':
        return "Unauthorized", 403

    # Fetch the patient's details
    patient = Patient.query.get_or_404(patient_id)

    # Ensure the doctor has access to this patient
    access = AccessPermission.query.filter_by(
        doctor_id=current_user.id,
        patient_id=patient_id,
        granted=True
    ).first()

    if not access:
        flash("You do not have access to this patient's records.", "error")
        return redirect(url_for('main.doctor_dashboard'))

    # Log the access in the blockchain
    current_app.blockchain.new_transaction(
        action="file_accessed",
        doctor_id=current_user.id,
        patient_id=patient_id
    )
    current_app.blockchain.new_block(proof=12345)  # Mine a new block

    # Fetch access logs from the blockchain
    access_logs = []
    if current_app.blockchain and current_app.blockchain.chain:
        for block in current_app.blockchain.chain:
            if 'transactions' in block:
                for transaction in block['transactions']:
                    if transaction.get('patient_id') == patient.id and transaction.get('action') == "file_accessed":
                        doctor = User.query.get(transaction.get('doctor_id'))
                        if doctor:
                            access_logs.append({
                                "doctor_username": doctor.username,
                                "timestamp": transaction.get('timestamp')
                            })

    # Render the patient's details using the patient_profile.html template
    return render_template(
        'patient_profile.html',
        patient=patient,
        access_logs=access_logs
    )
    
@bp.route('/add_doctor', methods=['POST'])
@login_required
def add_doctor():
    if current_user.role != 'admin':
        return "Unauthorized", 403

    username = request.form['username']
    password = "doctor123"  # Default password

    # Generate username in the form of dr_something
    if not username.startswith('dr_'):
        username = f"dr_{username}"

    # Check if the username already exists
    if User.query.filter_by(username=username).first():
        flash("Username already exists.", "error")
        return redirect(url_for('main.admin_dashboard'))

    # Create new doctor
    doctor = User(username=username, role='doctor')
    doctor.set_password(password)
    db.session.add(doctor)
    db.session.commit()

    flash(f"Doctor {username} added successfully. Default password: {password}", "success")
    return redirect(url_for('main.admin_dashboard'))

@bp.route('/add_patient', methods=['POST'])
@login_required
def add_patient():
    if current_user.role != 'admin':
        return "Unauthorized", 403

    name = request.form['name']
    age = request.form['age']
    disease = request.form['disease']
    password = "patient123"  # Default password

    # Generate patient username (e.g., patient20)
    last_patient = User.query.filter_by(role='patient').order_by(User.id.desc()).first()
    if last_patient:
        last_number = int(last_patient.username.replace('patient', ''))
        new_number = last_number + 1
    else:
        new_number = 1
    username = f"patient{new_number}"

    # Create new patient user
    user = User(username=username, role='patient')
    user.set_password(password)
    db.session.add(user)
    db.session.flush()  # Ensure user ID is available

    # Create new patient
    patient = Patient(
        name=name,
        age=age,
        disease=disease,
        user_id=user.id
    )
    db.session.add(patient)
    db.session.commit()

    flash(f"Patient {name} added successfully. Username: {username}, Default password: {password}", "success")
    return redirect(url_for('main.admin_dashboard'))

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))