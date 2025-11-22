"""
Chart data formatting service
"""
from datetime import datetime

class ChartDataService:
    """Service for formatting health records for Chart.js"""
    
    @staticmethod
    def format_for_charts(records):
        """
        Format health records for Chart.js visualization
        
        Args:
            records: List of health record documents from MongoDB
            
        Returns:
            Dictionary with formatted datasets for different chart types
        """
        if not records:
            return {
                'labels': [],
                'sugar': {},
                'bloodPressure': {},
                'lipids': {},
                'weight': {},
                'kidney': {},
                'thyroid': {},
                'liver': {},
                'cbc': {}
            }
        
        # Sort records by timestamp (oldest first for charts)
        sorted_records = sorted(records, key=lambda x: x.get('timestamp', datetime.min))
        
        # Extract labels (dates)
        labels = []
        for record in sorted_records:
            timestamp = record.get('timestamp')
            if timestamp:
                labels.append(timestamp.strftime('%Y-%m-%d'))
            else:
                labels.append('N/A')
        
        # Helper to extract metric values
        def extract_metric(metric_name):
            return [record.get(metric_name) for record in sorted_records]
        
        # Build datasets
        chart_data = {
            'labels': labels,
            
            # Sugar/Diabetes
            'sugar': {
                'fasting': extract_metric('sugarFasting'),
                'postMeal': extract_metric('sugarPostMeal'),
                'random': extract_metric('randomBloodSugar'),
                'hbA1c': extract_metric('hbA1c')
            },
            
            # Blood Pressure
            'bloodPressure': {
                'systolic': extract_metric('bpSystolic'),
                'diastolic': extract_metric('bpDiastolic'),
                'heartRate': extract_metric('heartRate')
            },
            
            # Lipid Profile
            'lipids': {
                'total': extract_metric('cholesterolTotal'),
                'hdl': extract_metric('cholesterolHDL'),
                'ldl': extract_metric('cholesterolLDL'),
                'triglycerides': extract_metric('triglycerides'),
                'vldl': extract_metric('vldl')
            },
            
            # Weight & BMI
            'weight': {
                'weight': extract_metric('weight'),
                'height': extract_metric('height'),
                'bmi': extract_metric('bmi')
            },
            
            # Kidney Function
            'kidney': {
                'creatinine': extract_metric('serumCreatinine'),
                'urea': extract_metric('bloodUrea'),
                'bun': extract_metric('bun'),
                'egfr': extract_metric('eGFR')
            },
            
            # Thyroid
            'thyroid': {
                'tsh': extract_metric('tsh'),
                't3': extract_metric('t3'),
                't4': extract_metric('t4')
            },
            
            # Liver Function
            'liver': {
                'sgpt': extract_metric('sgptAlt'),
                'sgot': extract_metric('sgotAst'),
                'alp': extract_metric('alkalinePhosphatase'),
                'bilirubin': extract_metric('totalBilirubin')
            },
            
            # CBC
            'cbc': {
                'hemoglobin': extract_metric('hemoglobin'),
                'wbc': extract_metric('totalLeukocyteCount'),
                'platelets': extract_metric('plateletCount'),
                'rbc': extract_metric('rbcCount')
            }
        }
        
        return chart_data
    
    @staticmethod
    def has_data(chart_data_category):
        """
        Check if a chart category has any actual data
        
        Args:
            chart_data_category: Dictionary of metric arrays
            
        Returns:
            True if any metric has at least one non-null value
        """
        for metric_values in chart_data_category.values():
            if any(v is not None for v in metric_values):
                return True
        return False
