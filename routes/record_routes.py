"""
Health record routes (manual entry and AI upload)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from models.patient import PatientModel
from models.health_record import HealthRecordModel
from services.gemini_service import GeminiService
from services.chart_data_service import ChartDataService
from utils.decorators import login_required
from utils.validators import validate_health_record, sanitize_numeric_input
from config import Config

records_bp = Blueprint('records', __name__)

def init_record_routes(db):
    """Initialize health record routes with database"""
    patient_model = PatientModel(db)
    health_record_model = HealthRecordModel(db)
    gemini_service = GeminiService()
    chart_service = ChartDataService()
    
    # Ensure upload folder exists
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    @records_bp.route('/patients/<patient_id>/add-record')
    @login_required
    def add_record_page(patient_id):
        """Show manual health record entry form"""
        patient = patient_model.get_patient_by_id(patient_id)
        
        if not patient:
            flash('Patient not found', 'error')
            return redirect(url_for('patients.dashboard'))
        
        return render_template('add_record.html', patient=patient, now=datetime.now())
    
    @records_bp.route('/patients/<patient_id>/records/create', methods=['POST'])
    @login_required
    def create_record(patient_id):
        """Create manual health record"""
        patient = patient_model.get_patient_by_id(patient_id)
        
        if not patient:
            flash('Patient not found', 'error')
            return redirect(url_for('patients.dashboard'))
        
        # Extract and sanitize all health metrics
        data = {}
        
        # Timestamp
        timestamp_str = request.form.get('timestamp')
        if timestamp_str:
            try:
                data['timestamp'] = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                data['timestamp'] = datetime.utcnow()
        else:
            data['timestamp'] = datetime.utcnow()
        
        # All health metrics
        metric_fields = [
            'bpSystolic', 'bpDiastolic', 'heartRate', 'temperature', 'spo2',
            'weight', 'height', 'sugarFasting', 'sugarPostMeal', 'randomBloodSugar',
            'hbA1c', 'cholesterolTotal', 'cholesterolHDL', 'cholesterolLDL',
            'triglycerides', 'vldl', 'serumCreatinine', 'bloodUrea', 'bun',
            'eGFR', 'sgptAlt', 'sgotAst', 'alkalinePhosphatase', 'totalBilirubin',
            'directBilirubin', 'indirectBilirubin', 'sodium', 'potassium',
            'chloride', 'hemoglobin', 'totalLeukocyteCount', 'plateletCount',
            'rbcCount', 'pcv', 'mcv', 'tsh', 't3', 't4', 'vitaminD', 'vitaminB12'
        ]
        
        for field in metric_fields:
            value = sanitize_numeric_input(request.form.get(field))
            if value is not None:
                data[field] = value
        
        # Notes
        notes = request.form.get('notes', '').strip()
        if notes:
            data['notes'] = notes
        
        # Validate
        is_valid, error_msg = validate_health_record(data)
        if not is_valid:
            flash(error_msg, 'error')
            return redirect(url_for('records.add_record_page', patient_id=patient_id))
        
        # Create record
        try:
            record_id = health_record_model.create_record(patient_id, data, 'MANUAL')
            flash('Health record added successfully!', 'success')
            return redirect(url_for('patients.patient_detail', patient_id=patient_id))
        except Exception as e:
            flash(f'Error creating record: {str(e)}', 'error')
            return redirect(url_for('records.add_record_page', patient_id=patient_id))
    
    @records_bp.route('/patients/<patient_id>/upload-report', methods=['POST'])
    @login_required
    def upload_report(patient_id):
        """Upload lab report and extract data using AI"""
        patient = patient_model.get_patient_by_id(patient_id)
        
        if not patient:
            flash('Patient not found', 'error')
            return redirect(url_for('patients.dashboard'))
        
        # Check if file was uploaded
        if 'reportFile' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('patients.patient_detail', patient_id=patient_id))
        
        file = request.files['reportFile']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('patients.patient_detail', patient_id=patient_id))
        
        # Validate file extension
        if not Config.allowed_file(file.filename):
            flash('Invalid file type. Please upload PDF, PNG, JPG, or JPEG files.', 'error')
            return redirect(url_for('patients.patient_detail', patient_id=patient_id))
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Extract data using Gemini
        try:
            extracted_data = gemini_service.extract_from_report(file_path)
            
            # Store extracted data in session for confirmation
            session['ai_extracted_data'] = extracted_data
            session['ai_upload_patient_id'] = patient_id
            session['ai_upload_filename'] = filename
            
            flash('Lab report processed successfully! Please review and confirm the extracted data.', 'success')
            return redirect(url_for('records.confirm_ai_record', patient_id=patient_id))
            
        except Exception as e:
            flash(f'Error extracting data from report: {str(e)}', 'error')
            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
            return redirect(url_for('patients.patient_detail', patient_id=patient_id))
    
    @records_bp.route('/patients/<patient_id>/confirm-ai')
    @login_required
    def confirm_ai_record(patient_id):
        """Show confirmation page for AI-extracted data"""
        patient = patient_model.get_patient_by_id(patient_id)
        
        if not patient:
            flash('Patient not found', 'error')
            return redirect(url_for('patients.dashboard'))
        
        # Get extracted data from session
        extracted_data = session.get('ai_extracted_data')
        if not extracted_data:
            flash('No extracted data found. Please upload a report first.', 'error')
            return redirect(url_for('patients.patient_detail', patient_id=patient_id))
        
        return render_template('confirm_ai_record.html', patient=patient, data=extracted_data, now=datetime.now())
    
    @records_bp.route('/patients/<patient_id>/records/confirm-ai', methods=['POST'])
    @login_required
    def save_ai_record(patient_id):
        """Save confirmed AI-extracted record"""
        patient = patient_model.get_patient_by_id(patient_id)
        
        if not patient:
            flash('Patient not found', 'error')
            return redirect(url_for('patients.dashboard'))
        
        # Extract and sanitize all health metrics (same as manual entry)
        data = {}
        
        # Timestamp
        timestamp_str = request.form.get('timestamp')
        if timestamp_str:
            try:
                data['timestamp'] = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                data['timestamp'] = datetime.utcnow()
        else:
            data['timestamp'] = datetime.utcnow()
        
        # All health metrics
        metric_fields = [
            'bpSystolic', 'bpDiastolic', 'heartRate', 'temperature', 'spo2',
            'weight', 'height', 'sugarFasting', 'sugarPostMeal', 'randomBloodSugar',
            'hbA1c', 'cholesterolTotal', 'cholesterolHDL', 'cholesterolLDL',
            'triglycerides', 'vldl', 'serumCreatinine', 'bloodUrea', 'bun',
            'eGFR', 'sgptAlt', 'sgotAst', 'alkalinePhosphatase', 'totalBilirubin',
            'directBilirubin', 'indirectBilirubin', 'sodium', 'potassium',
            'chloride', 'hemoglobin', 'totalLeukocyteCount', 'plateletCount',
            'rbcCount', 'pcv', 'mcv', 'tsh', 't3', 't4', 'vitaminD', 'vitaminB12'
        ]
        
        for field in metric_fields:
            value = sanitize_numeric_input(request.form.get(field))
            if value is not None:
                data[field] = value
        
        # Notes
        notes = request.form.get('notes', '').strip()
        if notes:
            data['notes'] = notes
        
        # Validate
        is_valid, error_msg = validate_health_record(data)
        if not is_valid:
            flash(error_msg, 'error')
            return redirect(url_for('records.confirm_ai_record', patient_id=patient_id))
        
        # Create record with AI source type
        try:
            record_id = health_record_model.create_record(patient_id, data, 'REPORT_AI')
            
            # Clear session data
            session.pop('ai_extracted_data', None)
            session.pop('ai_upload_patient_id', None)
            
            # Clean up uploaded file
            filename = session.pop('ai_upload_filename', None)
            if filename:
                file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            flash('Health record from AI report saved successfully!', 'success')
            return redirect(url_for('patients.patient_detail', patient_id=patient_id))
        except Exception as e:
            flash(f'Error saving record: {str(e)}', 'error')
            return redirect(url_for('records.confirm_ai_record', patient_id=patient_id))
    
    @records_bp.route('/api/records/<record_id>')
    @login_required
    def get_record_details(record_id):
        """Get single health record details as JSON"""
        from bson import ObjectId
        try:
            record = health_record_model.collection.find_one({'_id': ObjectId(record_id)})
            if not record:
                return jsonify({'error': 'Record not found'}), 404
            
            # Convert ObjectId and datetime to strings
            record['_id'] = str(record['_id'])
            record['patientId'] = str(record['patientId'])
            if record.get('timestamp'):
                record['timestamp'] = record['timestamp'].strftime('%Y-%m-%d %H:%M')
            
            # Remove None values for cleaner JSON
            cleaned_record = {k: v for k, v in record.items() if v is not None}
            
            return jsonify(cleaned_record)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @records_bp.route('/patients/<patient_id>/records/json')
    @login_required
    def records_json(patient_id):
        """Get health records as JSON for charts"""
        records = health_record_model.get_records_by_patient(patient_id)
        chart_data = chart_service.format_for_charts(records)
        return jsonify(chart_data)
    
    @records_bp.route('/api/records/<record_id>/delete', methods=['POST'])
    @login_required
    def delete_health_record(record_id):
        """Delete a single health record"""
        from bson import ObjectId
        try:
            # Get the record to verify it exists and get patient_id
            record = health_record_model.get_record_by_id(record_id)
            if not record:
                return jsonify({'success': False, 'error': 'Record not found'}), 404
            
            patient_id = str(record['patientId'])
            
            # Delete the record
            if health_record_model.delete_record(record_id):
                return jsonify({'success': True, 'patient_id': patient_id})
            else:
                return jsonify({'success': False, 'error': 'Failed to delete record'}), 500
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return records_bp
