"""
Patient model and database operations
"""
from datetime import datetime
from bson import ObjectId

class PatientModel:
    """Patient model for MongoDB operations"""
    
    def __init__(self, db):
        self.collection = db.patients
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create indexes for patient collection"""
        self.collection.create_index('fullName')
        self.collection.create_index([('fullName', 'text')])
    
    def create_patient(self, data):
        """
        Create a new patient
        
        Args:
            data: Dictionary with patient information
                Required: fullName
                Optional: age, gender, contactNumber, email, address, 
                         medicalConditions, emergencyContact
                         
        Returns:
            The inserted patient ID
        """
        # Validate required fields
        if not data.get('fullName'):
            raise ValueError('fullName is required')
        
        patient = {
            'fullName': data['fullName'],
            'age': data.get('age'),
            'gender': data.get('gender'),
            'contactNumber': data.get('contactNumber'),
            'email': data.get('email'),
            'address': data.get('address'),
            'medicalConditions': data.get('medicalConditions', []),
            'emergencyContact': data.get('emergencyContact'),
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow()
        }
        
        result = self.collection.insert_one(patient)
        return result.inserted_id
    
    def get_all_patients(self):
        """Get all patients sorted by name"""
        return list(self.collection.find().sort('fullName', 1))
    
    def get_patient_by_id(self, patient_id):
        """Find patient by ID"""
        try:
            return self.collection.find_one({'_id': ObjectId(patient_id)})
        except:
            return None
    
    def update_patient(self, patient_id, data):
        """
        Update patient information
        
        Args:
            patient_id: Patient ID to update
            data: Dictionary with fields to update
            
        Returns:
            True if updated, False otherwise
        """
        try:
            data['updatedAt'] = datetime.utcnow()
            result = self.collection.update_one(
                {'_id': ObjectId(patient_id)},
                {'$set': data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def search_patients(self, query):
        """
        Search patients by name (text search)
        
        Args:
            query: Search query string
            
        Returns:
            List of matching patients
        """
        if not query:
            return self.get_all_patients()
        
        # Try text search
        results = list(self.collection.find(
            {'$text': {'$search': query}}
        ).sort('fullName', 1))
        
        # If no results, try regex search
        if not results:
            results = list(self.collection.find(
                {'fullName': {'$regex': query, '$options': 'i'}}
            ).sort('fullName', 1))
        
        return results
    
    def delete_patient(self, patient_id):
        """Delete a patient"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(patient_id)})
            return result.deleted_count > 0
        except:
            return False
