"""
Input validation utilities
"""
import re

def validate_patient_data(data):
    """
    Validate patient data
    
    Args:
        data: Dictionary with patient information
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data.get('fullName') or not data.get('fullName').strip():
        return False, 'Full name is required'
    
    # Validate email format if provided
    if data.get('email'):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return False, 'Invalid email format'
    
    # Validate age if provided
    if data.get('age'):
        try:
            age = int(data['age'])
            if age < 0 or age > 150:
                return False, 'Age must be between 0 and 150'
        except ValueError:
            return False, 'Age must be a number'
    
    return True, None

def validate_health_record(data):
    """
    Validate health record data
    
    Args:
        data: Dictionary with health metrics
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # List of all possible health metric fields
    metric_fields = {
        'bpSystolic', 'bpDiastolic', 'heartRate', 'temperature', 'spo2',
        'weight', 'height', 'bmi', 'sugarFasting', 'sugarPostMeal',
        'randomBloodSugar', 'hbA1c', 'cholesterolTotal', 'cholesterolHDL',
        'cholesterolLDL', 'triglycerides', 'vldl', 'serumCreatinine',
        'bloodUrea', 'bun', 'eGFR', 'sgptAlt', 'sgotAst', 'alkalinePhosphatase',
        'totalBilirubin', 'directBilirubin', 'indirectBilirubin', 'sodium',
        'potassium', 'chloride', 'hemoglobin', 'totalLeukocyteCount',
        'plateletCount', 'rbcCount', 'pcv', 'mcv', 'tsh', 't3', 't4',
        'vitaminD', 'vitaminB12'
    }
    
    # Check if at least one metric is provided
    has_metric = any(key in data and data[key] for key in metric_fields)
    if not has_metric:
        return False, 'At least one health metric is required'
    
    return True, None

def sanitize_numeric_input(value):
    """
    Convert input to float safely
    
    Args:
        value: Input value (string, int, float, or None)
        
    Returns:
        Float value or None if invalid
    """
    if value is None or value == '':
        return None
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def validate_file_extension(filename, allowed_extensions):
    """
    Check if file has allowed extension
    
    Args:
        filename: Name of file
        allowed_extensions: Set of allowed extensions
        
    Returns:
        True if extension is allowed, False otherwise
    """
    if not filename:
        return False
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_admin_data(data):
    """
    Validate admin creation data
    
    Args:
        data: Dictionary with admin information
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data.get('userId') or not data.get('userId').strip():
        return False, 'User ID is required'
    
    if not data.get('name') or not data.get('name').strip():
        return False, 'Name is required'
    
    # Enhanced password validation
    password = data.get('password', '')
    if not password:
        return False, 'Password is required'
    
    if len(password) < 8:
        return False, 'Password must be at least 8 characters'
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter'
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter'
    
    # Check for at least one number
    if not re.search(r'\d', password):
        return False, 'Password must contain at least one number'
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/`~;]', password):
        return False, 'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>_-+=[]\\\/`~;)'
    
    if not data.get('secretPassword') or not data.get('secretPassword').strip():
        return False, 'Secret password is required'
    
    return True, None
