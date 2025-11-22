"""
Analytics Service
Provides statistical analysis and insights for the dashboard
"""
from datetime import datetime, timedelta
from bson import ObjectId

class AnalyticsService:
    """Analytics and statistics service"""
    
    def __init__(self, db):
        self.db = db
    
    def get_overview_stats(self):
        """Get overall system statistics"""
        stats = {
            'total_patients': self.db.patients.count_documents({}),
            'total_appointments': self.db.appointments.count_documents({}),
            'total_visits': self.db.visits.count_documents({}),
            'total_prescriptions': self.db.prescriptions.count_documents({}),
            'total_health_records': self.db.healthRecords.count_documents({})
        }
        
        # Today's appointments
        from datetime import date
        today = datetime.combine(date.today(), datetime.min.time())
        stats['todays_appointments'] = self.db.appointments.count_documents({
            'appointmentDate': today,
            'status': {'$ne': 'CANCELLED'}
        })
        
        # This week's visits
        week_ago = datetime.now() - timedelta(days=7)
        stats['weekly_visits'] = self.db.visits.count_documents({
            'visitDate': {'$gte': week_ago}
        })
        
        return stats
    
    def get_patient_demographics(self):
        """Get patient demographic statistics"""
        demographics = {}
        
        # By gender
        gender_pipeline = [
            {'$group': {'_id': '$gender', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        demographics['by_gender'] = list(self.db.patients.aggregate(gender_pipeline))
        
        # By age group
        age_pipeline = [
            {
                '$addFields': {
                    'ageGroup': {
                        '$switch': {
                            'branches': [
                                {'case': {'$lt': [{'$toInt': '$age'}, 18]}, 'then': '0-17'},
                                {'case': {'$lt': [{'$toInt': '$age'}, 30]}, 'then': '18-29'},
                                {'case': {'$lt': [{'$toInt': '$age'}, 45]}, 'then': '30-44'},
                                {'case': {'$lt': [{'$toInt': '$age'}, 60]}, 'then': '45-59'},
                            ],
                            'default': '60+'
                        }
                    }
                }
            },
            {'$group': {'_id': '$ageGroup', 'count': {'$sum': 1}}},
            {'$sort': {'_id': 1}}
        ]
        try:
            demographics['by_age_group'] = list(self.db.patients.aggregate(age_pipeline))
        except:
            demographics['by_age_group'] = []
        
        # By medical condition
        condition_pipeline = [
            {'$unwind': '$medicalConditions'},
            {'$group': {'_id': '$medicalConditions', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        demographics['by_condition'] = list(self.db.patients.aggregate(condition_pipeline))
        
        return demographics
    
    def get_appointment_metrics(self, days=30):
        """Get appointment statistics"""
        start_date = datetime.now() - timedelta(days=days)
        
        metrics = {}
        
        # Total appointments in period
        metrics['total'] = self.db.appointments.count_documents({
            'appointmentDate': {'$gte': start_date}
        })
        
        # By status
        status_pipeline = [
            {'$match': {'appointmentDate': {'$gte': start_date}}},
            {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
        ]
        metrics['by_status'] = list(self.db.appointments.aggregate(status_pipeline))
        
        # Completion rate
        completed = self.db.appointments.count_documents({
            'appointmentDate': {'$gte': start_date},
            'status': 'COMPLETED'
        })
        metrics['completion_rate'] = (completed / metrics['total'] * 100) if metrics['total'] > 0 else 0
        
        # No-show rate
        no_shows = self.db.appointments.count_documents({
            'appointmentDate': {'$gte': start_date},
            'status': 'NO_SHOW'
        })
        metrics['no_show_rate'] = (no_shows / metrics['total'] * 100) if metrics['total'] > 0 else 0
        
        # Appointments over time (daily)
        daily_pipeline = [
            {'$match': {'appointmentDate': {'$gte': start_date}}},
            {'$group': {
                '_id': {
                    '$dateToString': {'format': '%Y-%m-%d', 'date': '$appointmentDate'}
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        metrics['daily_counts'] = list(self.db.appointments.aggregate(daily_pipeline))
        
        return metrics
    
    def get_visit_statistics(self, days=30):
        """Get visit statistics"""
        start_date = datetime.now() - timedelta(days=days)
        
        stats = {}
        
        # Total visits
        stats['total'] = self.db.visits.count_documents({
            'visitDate': {'$gte': start_date}
        })
        
        # Most common diagnoses
        diagnosis_pipeline = [
            {'$match': {'visitDate': {'$gte': start_date}}},
            {'$unwind': '$diagnosis'},
            {'$group': {'_id': '$diagnosis', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        stats['common_diagnoses'] = list(self.db.visits.aggregate(diagnosis_pipeline))
        
        # Visits per month
        monthly_pipeline = [
            {'$match': {'visitDate': {'$gte': start_date}}},
            {'$group': {
                '_id': {
                    '$dateToString': {'format': '%Y-%m', 'date': '$visitDate'}
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        stats['monthly_counts'] = list(self.db.visits.aggregate(monthly_pipeline))
        
        return stats
    
    def get_prescription_analytics(self):
        """Get prescription statistics"""
        stats = {}
        
        # Total prescriptions
        stats['total'] = self.db.prescriptions.count_documents({})
        
        # Most prescribed medications
        med_pipeline = [
            {'$unwind': '$medications'},
            {'$group': {
                '_id': '$medications.medicationName',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 15}
        ]
        stats['top_medications'] = list(self.db.prescriptions.aggregate(med_pipeline))
        
        # Recent prescriptions (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        stats['recent_count'] = self.db.prescriptions.count_documents({
            'prescriptionDate': {'$gte': thirty_days_ago}
        })
        
        return stats
    
    def get_health_trends(self, metric='sugarFasting', days=90):
        """Get health trend data for a specific metric"""
        start_date = datetime.now() - timedelta(days=days)
        
        # Get average values over time
        pipeline = [
            {'$match': {
                'timestamp': {'$gte': start_date},
                metric: {'$exists': True, '$ne': None}
            }},
            {'$group': {
                '_id': {
                    '$dateToString': {'format': '%Y-%m-%d', 'date': '$timestamp'}
                },
                'average': {'$avg': f'${metric}'},
                'min': {'$min': f'${metric}'},
                'max': {'$max': f'${metric}'},
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        return list(self.db.healthRecords.aggregate(pipeline))
    
    def get_critical_alerts(self):
        """Identify patients with critical health values"""
        alerts = []
        
        # High blood pressure (>140/90)
        high_bp_records = self.db.healthRecords.find({
            '$or': [
                {'bpSystolic': {'$gte': 140}},
                {'bpDiastolic': {'$gte': 90}}
            ]
        }).sort('timestamp', -1)
        
        # Group by patient (get latest only)
        seen_patients = set()
        for record in high_bp_records:
            patient_id = str(record['patientId'])
            if patient_id not in seen_patients:
                from models.patient import PatientModel
                patient_model = PatientModel(self.db)
                patient = patient_model.get_patient_by_id(patient_id)
                if patient:
                    alerts.append({
                        'patient': patient,
                        'type': 'High Blood Pressure',
                        'value': f"{record.get('bpSystolic')}/{record.get('bpDiastolic')} mmHg",
                        'date': record.get('timestamp')
                    })
                    seen_patients.add(patient_id)
                    if len(alerts) >= 10:
                        break
        
        # High blood sugar (fasting >125)
        high_sugar_records = self.db.healthRecords.find({
            'sugarFasting': {'$gte': 125}
        }).sort('timestamp', -1)
        
        seen_patients_sugar = set()
        for record in high_sugar_records:
            patient_id = str(record['patientId'])
            if patient_id not in seen_patients_sugar and len(alerts) < 20:
                from models.patient import PatientModel
                patient_model = PatientModel(self.db)
                patient = patient_model.get_patient_by_id(patient_id)
                if patient:
                    alerts.append({
                        'patient': patient,
                        'type': 'High Fasting Sugar',
                        'value': f"{record.get('sugarFasting')} mg/dL",
                        'date': record.get('timestamp')
                    })
                    seen_patients_sugar.add(patient_id)
        
        return alerts
