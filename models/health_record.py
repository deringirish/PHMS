"""
Health Record model and database operations
"""
from datetime import datetime
from bson import ObjectId

class HealthRecordModel:
    """Health Record model for MongoDB operations"""
    
    # Whitelist of allowed health metrics
    ALLOWED_FIELDS = {
        # Vitals
        'bpSystolic', 'bpDiastolic', 'heartRate', 'temperature', 'spo2',
        'weight', 'height', 'bmi',
        
        # Diabetes/Glucose
        'sugarFasting', 'sugarPostMeal', 'randomBloodSugar', 'hbA1c',
        
        # Lipid Profile
        'cholesterolTotal', 'cholesterolHDL', 'cholesterolLDL', 
        'triglycerides', 'vldl',
        
        # Renal/Kidney
        'serumCreatinine', 'bloodUrea', 'bun', 'eGFR',
        
        # Liver Function
        'sgptAlt', 'sgotAst', 'alkalinePhosphatase', 'totalBilirubin',
        'directBilirubin', 'indirectBilirubin',
        
        # Electrolytes
        'sodium', 'potassium', 'chloride',
        
        # Hematology (CBC)
        'hemoglobin', 'totalLeukocyteCount', 'plateletCount', 
        'rbcCount', 'pcv', 'mcv',
        
        # Thyroid
        'tsh', 't3', 't4',
        
        # Vitamins
        'vitaminD', 'vitaminB12',
        
        # Meta
        'notes'
    }
    
    def __init__(self, db):
        self.collection = db.healthRecords
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create indexes for health records collection"""
        self.collection.create_index('patientId')
        self.collection.create_index('timestamp')
        self.collection.create_index([('patientId', 1), ('timestamp', -1)])
    
    @staticmethod
    def calculate_bmi(weight, height):
        """
        Calculate BMI from weight (kg) and height (cm)
        
        Returns:
            BMI value rounded to 2 decimal places or None
        """
        if weight and height and height > 0:
            height_m = height / 100  # Convert cm to meters
            bmi = weight / (height_m ** 2)
            return round(bmi, 2)
        return None
    
    def filter_whitelisted_fields(self, data):
        """
        Filter data to include only whitelisted fields
        
        Args:
            data: Dictionary with health metrics
            
        Returns:
            Filtered dictionary with only allowed fields
        """
        return {k: v for k, v in data.items() if k in self.ALLOWED_FIELDS}
    
    def create_record(self, patient_id, data, source_type='MANUAL'):
        """
        Create a new health record
        
        Args:
            patient_id: Patient ID this record belongs to
            data: Dictionary with health metrics
            source_type: 'MANUAL' or 'REPORT_AI'
            
        Returns:
            The inserted record ID
        """
        # Validate at least one metric is provided
        has_metric = any(k in self.ALLOWED_FIELDS for k in data.keys())
        if not has_metric:
            raise ValueError('At least one health metric is required')
        
        # Filter to whitelisted fields only
        filtered_data = self.filter_whitelisted_fields(data)
        
        # Calculate BMI if weight and height available
        if 'weight' in filtered_data and 'height' in filtered_data:
            bmi = self.calculate_bmi(filtered_data['weight'], filtered_data['height'])
            if bmi:
                filtered_data['bmi'] = bmi
        
        # Build record
        record = {
            'patientId': ObjectId(patient_id),
            'timestamp': data.get('timestamp', datetime.utcnow()),
            'sourceType': source_type,
            'createdAt': datetime.utcnow(),
            **filtered_data
        }
        
        result = self.collection.insert_one(record)
        return result.inserted_id
    
    def get_records_by_patient(self, patient_id, start_date=None, end_date=None):
        """
        Get all health records for a patient
        
        Args:
            patient_id: Patient ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of health records sorted by timestamp (newest first)
        """
        query = {'patientId': ObjectId(patient_id)}
        
        # Add date range filter if provided
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter['$gte'] = start_date
            if end_date:
                date_filter['$lte'] = end_date
            query['timestamp'] = date_filter
        
        return list(self.collection.find(query).sort('timestamp', -1))
    
    def get_latest_record(self, patient_id):
        """Get the most recent health record for a patient"""
        return self.collection.find_one(
            {'patientId': ObjectId(patient_id)},
            sort=[('timestamp', -1)]
        )
    
    def get_record_by_id(self, record_id):
        """Get a specific health record"""
        try:
            return self.collection.find_one({'_id': ObjectId(record_id)})
        except:
            return None
    
    def delete_record(self, record_id):
        """Delete a health record"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(record_id)})
            return result.deleted_count > 0
        except:
            return False
