"""
Prescription Routes
Handles prescription creation and management
"""
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from bson import ObjectId
from datetime import datetime
from utils.decorators import login_required

def init_prescription_routes(db):
    """Initialize prescription routes blueprint"""
    from models.prescription import PrescriptionModel
    from models.medication import MedicationModel
    from models.patient import PatientModel
    from models.admin import AdminModel
    from models.visit import VisitModel
    
    prescription_bp = Blueprint('prescriptions', __name__, url_prefix='/prescriptions')
    prescription_model = PrescriptionModel(db)
    medication_model = MedicationModel(db)
    patient_model = PatientModel(db)
    admin_model = AdminModel(db)
    visit_model = VisitModel(db)
    
    @prescription_bp.route('/create/<patient_id>', methods=['GET', 'POST'])
    @login_required
    def create_prescription(patient_id):
        """Create a new prescription"""
        patient = patient_model.get_patient_by_id(patient_id)
        if not patient:
            flash('Patient not found.', 'error')
            return redirect(url_for('patients.dashboard'))
        
        if request.method == 'GET':
            # Get recent visits for linking
            visits = visit_model.get_visits_by_patient(patient_id)[:5]
            return render_template('prescription_form.html', patient=patient, visits=visits, prescription=None)
        
        # POST - Create prescription
        try:
            # Parse medications from form
            medications = []
            med_count = int(request.form.get('medication_count', 0))
            
            for i in range(med_count):
                med_name = request.form.get(f'medication_name_{i}')
                if med_name:
                    medications.append({
                        'medicationName': med_name,
                        'dosage': request.form.get(f'dosage_{i}', ''),
                        'frequency': request.form.get(f'frequency_{i}', ''),
                        'duration': request.form.get(f'duration_{i}', ''),
                        'instructions': request.form.get(f'instructions_{i}', ''),
                        'quantity': request.form.get(f'quantity_{i}', '')
                    })
            
            if not medications:
                flash('Please add at least one medication.', 'error')
                return redirect(url_for('prescriptions.create_prescription', patient_id=patient_id))
            
            data = {
                'patientId': patient_id,
                'visitId': request.form.get('visit_id'),
                'doctorId': session.get('admin_id'),
                'medications': medications,
                'notes': request.form.get('notes', '')
            }
            
            prescription_id = prescription_model.create_prescription(data)
            
            # Link to visit if specified
            if data.get('visitId'):
                visit_model.link_prescription(data['visitId'], str(prescription_id))
            
            flash('Prescription created successfully!', 'success')
            return redirect(url_for('prescriptions.view_prescription', prescription_id=str(prescription_id)))
        except Exception as e:
            flash(f'Error creating prescription: {str(e)}', 'error')
            return redirect(url_for('prescriptions.create_prescription', patient_id=patient_id))
    
    @prescription_bp.route('/<prescription_id>')
    @login_required
    def view_prescription(prescription_id):
        """View prescription details"""
        prescription = prescription_model.get_prescription_by_id(prescription_id)
        if not prescription:
            flash('Prescription not found.', 'error')
            return redirect(url_for('patients.dashboard'))
        
        # Enrich with related data
        prescription['patient'] = patient_model.get_patient_by_id(str(prescription['patientId']))
        if prescription.get('doctorId'):
            prescription['doctor'] = admin_model.find_by_id(str(prescription['doctorId']))
        if prescription.get('visitId'):
            prescription['visit'] = visit_model.get_visit_by_id(str(prescription['visitId']))
        
        return render_template('prescription_view.html', prescription=prescription)
    
    @prescription_bp.route('/patient/<patient_id>')
    @login_required
    def patient_prescriptions(patient_id):
        """Get all prescriptions for a patient"""
        prescriptions = prescription_model.get_prescriptions_by_patient(patient_id)
        patient = patient_model.get_patient_by_id(patient_id)
        
        # Enrich with doctor data
        for prescription in prescriptions:
            if prescription.get('doctorId'):
                prescription['doctor'] = admin_model.find_by_id(str(prescription['doctorId']))
        
        return render_template('patient_prescriptions.html', prescriptions=prescriptions, patient=patient)
    
    @prescription_bp.route('/api/search-medications')
    @login_required
    def search_medications():
        """API endpoint to search medications"""
        query = request.args.get('q', '')
        medications = medication_model.search_medications(query)
        
        return jsonify([{
            'id': str(med['_id']),
            'name': med['name'],
            'genericName': med.get('genericName', ''),
            'category': med.get('category', ''),
            'commonDosages': med.get('commonDosages', [])
        } for med in medications])
    
    return prescription_bp
