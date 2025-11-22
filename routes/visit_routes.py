"""
Visit Routes
Handles visit/consultation records
"""
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from bson import ObjectId
from datetime import datetime
from utils.decorators import login_required

def init_visit_routes(db):
    """Initialize visit routes blueprint"""
    from models.visit import VisitModel
    from models.patient import PatientModel
    from models.admin import AdminModel
    from models.prescription import PrescriptionModel
    from models.health_record import HealthRecordModel
    
    visit_bp = Blueprint('visits', __name__, url_prefix='/visits')
    visit_model = VisitModel(db)
    patient_model = PatientModel(db)
    admin_model = AdminModel(db)
    prescription_model = PrescriptionModel(db)
    record_model = HealthRecordModel(db)
    
    @visit_bp.route('/create/<patient_id>', methods=['GET', 'POST'])
    @login_required
    def create_visit(patient_id):
        """Create a new visit record"""
        patient = patient_model.get_patient_by_id(patient_id)
        if not patient:
            flash('Patient not found.', 'error')
            return redirect(url_for('patients.dashboard'))
        
        if request.method == 'GET':
            doctors = admin_model.get_all_admins()
            return render_template('visit_form.html', patient=patient, doctors=doctors, visit=None)
        
        # POST - Create visit
        try:
            data = {
                'patientId': patient_id,
                'doctorId': request.form.get('doctor_id') or session.get('admin_id'),
                'visitDate': datetime.strptime(request.form.get('visit_date'), '%Y-%m-%d'),
                'chiefComplaint': request.form.get('chief_complaint', ''),
                'diagnosis': [d.strip() for d in request.form.get('diagnosis', '').split(',') if d.strip()],
                'treatmentPlan': request.form.get('treatment_plan', ''),
                'followUpDate': datetime.strptime(request.form.get('follow_up_date'), '%Y-%m-%d') if request.form.get('follow_up_date') else None,
                'notes': request.form.get('notes', ''),
                'vitalSigns': {}
            }
            
            # Add vital signs if provided
            if request.form.get('bp_systolic'):
                data['vitalSigns']['bpSystolic'] = int(request.form.get('bp_systolic'))
                data['vitalSigns']['bpDiastolic'] = int(request.form.get('bp_diastolic'))
            if request.form.get('heart_rate'):
                data['vitalSigns']['heartRate'] = int(request.form.get('heart_rate'))
            if request.form.get('temperature'):
                data['vitalSigns']['temperature'] = float(request.form.get('temperature'))
            
            visit_id = visit_model.create_visit(data)
            
            flash('Visit record created successfully!', 'success')
            return redirect(url_for('patients.patient_detail', patient_id=patient_id))
        except Exception as e:
            flash(f'Error creating visit: {str(e)}', 'error')
            return redirect(url_for('visits.create_visit', patient_id=patient_id))
    
    @visit_bp.route('/<visit_id>')
    @login_required
    def view_visit(visit_id):
        """View visit details"""
        visit = visit_model.get_visit_by_id(visit_id)
        if not visit:
            flash('Visit not found.', 'error')
            return redirect(url_for('patients.dashboard'))
        
        # Enrich with related data
        visit['patient'] = patient_model.get_patient_by_id(str(visit['patientId']))
        if visit.get('doctorId'):
            visit['doctor'] = admin_model.find_by_id(str(visit['doctorId']))
        
        # Get linked prescriptions
        if visit.get('prescriptionIds'):
            visit['prescriptions'] = [prescription_model.get_prescription_by_id(str(pid)) 
                                     for pid in visit['prescriptionIds']]
        
        # Get linked health records
        if visit.get('healthRecordIds'):
            visit['healthRecords'] = [record_model.get_record_by_id(str(hid)) 
                                     for hid in visit['healthRecordIds']]
        
        return render_template('visit_detail.html', visit=visit)
    
    @visit_bp.route('/<visit_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_visit(visit_id):
        """Edit visit record"""
        visit = visit_model.get_visit_by_id(visit_id)
        if not visit:
            flash('Visit not found.', 'error')
            return redirect(url_for('patients.dashboard'))
        
        if request.method == 'GET':
            visit['patient'] = patient_model.get_patient_by_id(str(visit['patientId']))
            doctors = admin_model.get_all_admins()
            return render_template('visit_form.html', patient=visit['patient'], doctors=doctors, visit=visit)
        
        # POST - Update visit
        try:
            data = {
                'chiefComplaint': request.form.get('chief_complaint', ''),
                'diagnosis': [d.strip() for d in request.form.get('diagnosis', '').split(',') if d.strip()],
                'treatmentPlan': request.form.get('treatment_plan', ''),
                'followUpDate': datetime.strptime(request.form.get('follow_up_date'), '%Y-%m-%d') if request.form.get('follow_up_date') else None,
                'notes': request.form.get('notes', '')
            }
            
            visit_model.update_visit(visit_id, data)
            flash('Visit updated successfully!', 'success')
            return redirect(url_for('visits.view_visit', visit_id=visit_id))
        except Exception as e:
            flash(f'Error updating visit: {str(e)}', 'error')
            return redirect(url_for('visits.edit_visit', visit_id=visit_id))
    
    @visit_bp.route('/patient/<patient_id>')
    @login_required
    def patient_visits(patient_id):
        """Get all visits for a patient"""
        visits = visit_model.get_visits_by_patient(patient_id)
        patient = patient_model.get_patient_by_id(patient_id)
        
        # Enrich with doctor data
        for visit in visits:
            if visit.get('doctorId'):
                visit['doctor'] = admin_model.find_by_id(str(visit['doctorId']))
        
        return render_template('patient_visits.html', visits=visits, patient=patient)
    
    return visit_bp
