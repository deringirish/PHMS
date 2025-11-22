"""
Patient management routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.patient import PatientModel
from models.health_record import HealthRecordModel
from utils.decorators import login_required
from utils.validators import validate_patient_data
from services.chart_data_service import ChartDataService

patients_bp = Blueprint('patients', __name__)

def init_patient_routes(db):
    """Initialize patient routes with database"""
    patient_model = PatientModel(db)
    health_record_model = HealthRecordModel(db)
    chart_service = ChartDataService()
    
    @patients_bp.route('/dashboard')
    @login_required
    def dashboard():
        """Patient dashboard with search"""
        search_query = request.args.get('search', '').strip()
        
        if search_query:
            patients = patient_model.search_patients(search_query)
        else:
            patients = patient_model.get_all_patients()
        
        return render_template('dashboard.html', patients=patients, search_query=search_query)
    
    @patients_bp.route('/patients/add')
    @login_required
    def add_patient_page():
        """Show add patient form"""
        return render_template('add_patient.html')
    
    @patients_bp.route('/patients/create', methods=['POST'])
    @login_required
    def create_patient():
        """Create new patient"""
        # Extract medical conditions as a list
        medical_conditions = request.form.getlist('medicalConditions')
        
        data = {
            'fullName': request.form.get('fullName', '').strip(),
            'age': request.form.get('age'),
            'gender': request.form.get('gender'),
            'contactNumber': request.form.get('contactNumber', '').strip(),
            'email': request.form.get('email', '').strip(),
            'address': request.form.get('address', '').strip(),
            'medicalConditions': medical_conditions,
            'emergencyContact': request.form.get('emergencyContact', '').strip()
        }
        
        # Validate input
        is_valid, error_msg = validate_patient_data(data)
        if not is_valid:
            flash(error_msg, 'error')
            return redirect(url_for('patients.add_patient_page'))
        
        # Create patient
        patient_id = patient_model.create_patient(data)
        flash(f'Patient "{data["fullName"]}" added successfully!', 'success')
        return redirect(url_for('patients.patient_detail', patient_id=str(patient_id)))
    
    @patients_bp.route('/patients/<patient_id>')
    @login_required
    def patient_detail(patient_id):
        """Patient detail page with records and charts"""
        patient = patient_model.get_patient_by_id(patient_id)
        
        if not patient:
            flash('Patient not found', 'error')
            return redirect(url_for('patients.dashboard'))
        
        # Get health records
        records = health_record_model.get_records_by_patient(patient_id)
        latest_record = health_record_model.get_latest_record(patient_id)
        
        # Format data for charts
        chart_data = chart_service.format_for_charts(records)
        
        return render_template(
            'patient_detail.html',
            patient=patient,
            records=records,
            latest_record=latest_record,
            chart_data=chart_data
        )
    
    @patients_bp.route('/patients/<patient_id>/update', methods=['POST'])
    @login_required
    def update_patient(patient_id):
        """Update patient information"""
        medical_conditions = request.form.getlist('medicalConditions')
        
        data = {
            'fullName': request.form.get('fullName', '').strip(),
            'age': request.form.get('age'),
            'gender': request.form.get('gender'),
            'contactNumber': request.form.get('contactNumber', '').strip(),
            'email': request.form.get('email', '').strip(),
            'address': request.form.get('address', '').strip(),
            'medicalConditions': medical_conditions,
            'emergencyContact': request.form.get('emergencyContact', '').strip()
        }
        
        # Validate input
        is_valid, error_msg = validate_patient_data(data)
        if not is_valid:
            flash(error_msg, 'error')
            return redirect(url_for('patients.patient_detail', patient_id=patient_id))
        
        # Update patient
        if patient_model.update_patient(patient_id, data):
            flash('Patient information updated successfully!', 'success')
        else:
            flash('Failed to update patient', 'error')
        
        return redirect(url_for('patients.patient_detail', patient_id=patient_id))
    
    @patients_bp.route('/patients/<patient_id>/delete', methods=['POST'])
    @login_required
    def delete_patient(patient_id):
        """Delete patient and all their health records"""
        patient = patient_model.get_patient_by_id(patient_id)
        
        if not patient:
            flash('Patient not found', 'error')
            return redirect(url_for('patients.dashboard'))
        
        patient_name = patient.get('fullName', 'Unknown')
        
        # Delete all health records for this patient first
        try:
            health_record_model.collection.delete_many({'patientId': patient['_id']})
        except Exception as e:
            flash(f'Error deleting health records: {str(e)}', 'error')
            return redirect(url_for('patients.patient_detail', patient_id=patient_id))
        
        # Delete the patient
        if patient_model.delete_patient(patient_id):
            flash(f'Patient "{patient_name}" and all their health records have been deleted.', 'success')
            return redirect(url_for('patients.dashboard'))
        else:
            flash('Failed to delete patient', 'error')
            return redirect(url_for('patients.patient_detail', patient_id=patient_id))
    
    return patients_bp
