"""
Appointment Routes
Handles appointment scheduling, management, and calendar views
"""
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from bson import ObjectId
from datetime import datetime, timedelta, date
from utils.decorators import login_required

def init_appointment_routes(db):
    """Initialize appointment routes blueprint"""
    from models.appointment import AppointmentModel
    from models.patient import PatientModel
    from models.admin import AdminModel
    
    appointment_bp = Blueprint('appointments', __name__, url_prefix='/appointments')
    appointment_model = AppointmentModel(db)
    patient_model = PatientModel(db)
    admin_model = AdminModel(db)
    
    @appointment_bp.route('/')
    @login_required
    def list_appointments():
        """List all appointments with filters"""
        # Get filter parameters
        status = request.args.get('status')
        doctor_id = request.args.get('doctor_id')
        date_filter = request.args.get('date')
        
        # Build query
        today = datetime.combine(date.today(), datetime.min.time())
        
        if date_filter == 'today':
            appointments = appointment_model.get_todays_appointments(doctor_id)
        elif date_filter == 'week':
            week_end = today + timedelta(days=7)
            appointments = appointment_model.get_appointments_by_date_range(today, week_end, status)
        elif date_filter == 'month':
            month_end = today + timedelta(days=30)
            appointments = appointment_model.get_appointments_by_date_range(today, month_end, status)
        else:
            # Upcoming appointments
            appointments = appointment_model.get_upcoming_appointments(50)
        
        # Enrich with patient and doctor data
        for appointment in appointments:
            appointment['patient'] = patient_model.get_patient_by_id(str(appointment['patientId']))
            if appointment.get('doctorId'):
                appointment['doctor'] = admin_model.find_by_id(str(appointment['doctorId']))
        
        # Get all doctors for filter
        doctors = admin_model.get_all_admins()
        
        return render_template('appointments.html', 
                             appointments=appointments,
                             doctors=doctors,
                             current_filter=date_filter or 'upcoming')
    
    @appointment_bp.route('/create', methods=['GET', 'POST'])
    @login_required
    def create_appointment():
        """Create a new appointment"""
        if request.method == 'GET':
            patients = patient_model.get_all_patients()
            doctors = admin_model.get_all_admins()
            return render_template('appointment_form.html', 
                                 patients=patients, 
                                 doctors=doctors,
                                 appointment=None)
        
        # POST - Create appointment
        try:
            data = {
                'patientId': request.form.get('patient_id'),
                'doctorId': request.form.get('doctor_id') or session.get('admin_id'),
                'appointmentDate': datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%d'),
                'appointmentTime': request.form.get('appointment_time'),
                'duration': int(request.form.get('duration', 30)),
                'type': request.form.get('type', appointment_model.TYPE_CONSULTATION),
                'notes': request.form.get('notes', '')
            }
            
            appointment_id = appointment_model.create_appointment(data)
            
            if appointment_id:
                flash('Appointment scheduled successfully!', 'success')
                return redirect(url_for('appointments.list_appointments'))
            else:
                flash('Time slot conflict! Please choose another time.', 'error')
                patients = patient_model.get_all_patients()
                doctors = admin_model.get_all_admins()
                return render_template('appointment_form.html', 
                                     patients=patients, 
                                     doctors=doctors,
                                     appointment=None,
                                     form_data=request.form)
        except Exception as e:
            flash(f'Error creating appointment: {str(e)}', 'error')
            return redirect(url_for('appointments.create_appointment'))
    
    @appointment_bp.route('/<appointment_id>')
    @login_required
    def view_appointment(appointment_id):
        """View appointment details"""
        appointment = appointment_model.get_appointment_by_id(appointment_id)
        if not appointment:
            flash('Appointment not found.', 'error')
            return redirect(url_for('appointments.list_appointments'))
        
        # Enrich with patient and doctor data
        appointment['patient'] = patient_model.get_patient_by_id(str(appointment['patientId']))
        if appointment.get('doctorId'):
            appointment['doctor'] = admin_model.find_by_id(str(appointment['doctorId']))
        
        return render_template('appointment_detail.html', appointment=appointment)
    
    @appointment_bp.route('/<appointment_id>/reschedule', methods=['POST'])
    @login_required
    def reschedule_appointment(appointment_id):
        """Reschedule an appointment"""
        try:
            new_date = datetime.strptime(request.form.get('new_date'), '%Y-%m-%d')
            new_time = request.form.get('new_time')
            
            success = appointment_model.reschedule_appointment(appointment_id, new_date, new_time)
            
            if success:
                flash('Appointment rescheduled successfully!', 'success')
            else:
                flash('Could not reschedule - time slot conflict or appointment not found.', 'error')
        except Exception as e:
            flash(f'Error rescheduling appointment: {str(e)}', 'error')
        
        return redirect(url_for('appointments.view_appointment', appointment_id=appointment_id))
    
    @appointment_bp.route('/<appointment_id>/cancel', methods=['POST'])
    @login_required
    def cancel_appointment(appointment_id):
        """Cancel an appointment"""
        success = appointment_model.cancel_appointment(appointment_id)
        
        if success:
            flash('Appointment cancelled successfully.', 'success')
        else:
            flash('Error cancelling appointment.', 'error')
        
        return redirect(url_for('appointments.list_appointments'))
    
    @appointment_bp.route('/<appointment_id>/complete', methods=['POST'])
    @login_required
    def complete_appointment(appointment_id):
        """Mark appointment as completed"""
        success = appointment_model.complete_appointment(appointment_id)
        
        if success:
            flash('Appointment marked as completed.', 'success')
        else:
            flash('Error updating appointment.', 'error')
        
        return redirect(url_for('appointments.view_appointment', appointment_id=appointment_id))
    
    @appointment_bp.route('/<appointment_id>/no-show', methods=['POST'])
    @login_required
    def mark_no_show(appointment_id):
        """Mark appointment as no-show"""
        success = appointment_model.mark_no_show(appointment_id)
        
        if success:
            flash('Appointment marked as no-show.', 'success')
        else:
            flash('Error updating appointment.', 'error')
        
        return redirect(url_for('appointments.list_appointments'))
    
    @appointment_bp.route('/patient/<patient_id>')
    @login_required
    def patient_appointments(patient_id):
        """Get all appointments for a patient"""
        appointments = appointment_model.get_appointments_by_patient(patient_id)
        patient = patient_model.get_patient_by_id(patient_id)
        
        # Enrich with doctor data
        for appointment in appointments:
            if appointment.get('doctorId'):
                appointment['doctor'] = admin_model.find_by_id(str(appointment['doctorId']))
        
        return render_template('patient_appointments.html', 
                             appointments=appointments,
                             patient=patient)
    
    @appointment_bp.route('/calendar')
    @login_required
    def calendar_view():
        """Calendar view of appointments"""
        # Get month parameter or default to current month
        month_str = request.args.get('month')
        if month_str:
            view_date = datetime.strptime(month_str, '%Y-%m')
        else:
            view_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get first and last day of month
        first_day = view_date.replace(day=1)
        if first_day.month == 12:
            last_day = first_day.replace(year=first_day.year + 1, month=1) - timedelta(days=1)
        else:
            last_day = first_day.replace(month=first_day.month + 1) - timedelta(days=1)
        
        # Get all appointments for the month
        appointments = appointment_model.get_appointments_by_date_range(first_day, last_day)
        
        # Enrich with patient and doctor data
        for appointment in appointments:
            appointment['patient'] = patient_model.get_patient_by_id(str(appointment['patientId']))
            if appointment.get('doctorId'):
                appointment['doctor'] = admin_model.find_by_id(str(appointment['doctorId']))
        
        return render_template('appointment_calendar.html', 
                             appointments=appointments,
                             view_date=view_date)
    
    @appointment_bp.route('/api/check-conflict', methods=['POST'])
    @login_required
    def check_conflict():
        """API endpoint to check for scheduling conflicts"""
        try:
            data = request.get_json()
            doctor_id = data.get('doctor_id')
            appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d')
            appointment_time = data['appointment_time']
            duration = int(data.get('duration', 30))
            
            has_conflict = appointment_model.has_conflict(doctor_id, appointment_date, appointment_time, duration)
            
            return jsonify({'has_conflict': has_conflict})
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    return appointment_bp
