"""
Seed realistic patient data into the PHMS database
Generates 53 patients with comprehensive health records
"""

import os
import sys
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'phms')

# Realistic Indian patient data
INDIAN_NAMES = [
    # Male names
    ("Rajesh Kumar", "Male"), ("Amit Sharma", "Male"), ("Vijay Singh", "Male"),
    ("Suresh Patel", "Male"), ("Anil Gupta", "Male"), ("Ramesh Rao", "Male"),
    ("Manoj Verma", "Male"), ("Sanjay Reddy", "Male"), ("Prakash Joshi", "Male"),
    ("Ashok Mehta", "Male"), ("Deepak Nair", "Male"), ("Ravi Kumar", "Male"),
    ("Ajay Desai", "Male"), ("Kiran Shah", "Male"), ("Mohan Iyer", "Male"),
    ("Naveen Chopra", "Male"), ("Akash Pillai", "Male"), ("Rohit Agarwal", "Male"),
    ("Vikram Pandey", "Male"), ("Arjun Malhotra", "Male"),
    
    # Female names
    ("Priya Sharma", "Female"), ("Anjali Patel", "Female"), ("Neha Gupta", "Female"),
    ("Kavita Singh", "Female"), ("Pooja Reddy", "Female"), ("Sunita Rao", "Female"),
    ("Rekha Verma", "Female"), ("Meena Joshi", "Female"), ("Shweta Mehta", "Female"),
    ("Divya Nair", "Female"), ("Anita Kumar", "Female"), ("Sneha Desai", "Female"),
    ("Radhika Shah", "Female"), ("Lakshmi Iyer", "Female"), ("Swati Chopra", "Female"),
    ("Nidhi Pillai", "Female"), ("Kriti Agarwal", "Female"), ("Ishita Pandey", "Female"),
    ("Simran Malhotra", "Female"), ("Ritu Kapoor", "Female"),
    
    # More diverse names
    ("Aryan Bansal", "Male"), ("Tanvi Saxena", "Female"), ("Karan Bhatia", "Male"),
    ("Isha Khanna", "Female"), ("Aditya Sinha", "Male"), ("Shreya Mishra", "Female"),
    ("Rohan Tiwari", "Male"), ("Aditi Jain", "Female"), ("Nikhil Awasthi", "Male"),
    ("Priyanka Mathur", "Female"), ("Gaurav Dubey", "Male"), ("Nikita Kulkarni", "Female"),
    ("Vishal Yadav", "Male")
]

# Medical conditions pool
MEDICAL_CONDITIONS_POOL = [
    "Type 2 Diabetes", "Hypertension", "Hyperlipidemia", "Hypothyroidism",
    "Chronic Kidney Disease", "Asthma", "COPD", "Coronary Artery Disease",
    "Obesity", "Vitamin D Deficiency", "Anemia", "Fatty Liver Disease",
    "Osteoarthritis", "Gastritis", "Migraine"
]

# Indian cities
INDIAN_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata",
    "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Chandigarh", "Kochi",
    "Indore", "Nagpur", "Bhopal", "Visakhapatnam", "Surat", "Vadodara"
]

def generate_phone_number():
    """Generate a realistic Indian phone number"""
    return f"+91 {random.randint(70000, 99999)}{random.randint(10000, 99999)}"

def generate_email(name):
    """Generate email from name"""
    first_name = name.split()[0].lower()
    last_name = name.split()[-1].lower()
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    return f"{first_name}.{last_name}{random.randint(1, 99)}@{random.choice(domains)}"

def generate_address(city):
    """Generate a realistic Indian address"""
    sectors = ["Sector", "Block", "Area", "Colony", "Nagar", "Road"]
    return f"{random.randint(1, 500)}, {random.choice(sectors)} {random.randint(1, 50)}, {city}"

def get_medical_conditions(age):
    """Assign realistic medical conditions based on age"""
    conditions = []
    
    # Older patients more likely to have chronic conditions
    if age > 60:
        num_conditions = random.randint(2, 4)
    elif age > 45:
        num_conditions = random.randint(1, 3)
    elif age > 30:
        num_conditions = random.randint(0, 2)
    else:
        num_conditions = random.randint(0, 1)
    
    if num_conditions > 0:
        conditions = random.sample(MEDICAL_CONDITIONS_POOL, num_conditions)
    
    return conditions

def generate_realistic_vitals(age, gender, has_diabetes, has_hypertension, has_obesity):
    """Generate realistic vital signs based on patient profile"""
    vitals = {}
    
    # Blood Pressure (more variable if hypertension)
    if has_hypertension:
        vitals['bpSystolic'] = random.randint(130, 160)
        vitals['bpDiastolic'] = random.randint(85, 100)
    else:
        vitals['bpSystolic'] = random.randint(110, 135)
        vitals['bpDiastolic'] = random.randint(70, 85)
    
    # Heart Rate
    vitals['heartRate'] = random.randint(65, 90)
    
    # Temperature
    vitals['temperature'] = round(random.uniform(36.5, 37.2), 1)
    
    # SpO2
    vitals['spo2'] = random.randint(95, 99)
    
    # Weight and BMI
    if gender == "Male":
        base_weight = 70
        base_height = 172
    else:
        base_weight = 58
        base_height = 160
    
    if has_obesity:
        vitals['weight'] = round(base_weight + random.uniform(15, 30), 1)
    else:
        vitals['weight'] = round(base_weight + random.uniform(-10, 15), 1)
    
    vitals['height'] = base_height + random.randint(-8, 8)
    
    # Calculate BMI
    height_m = vitals['height'] / 100
    vitals['bmi'] = round(vitals['weight'] / (height_m ** 2), 2)
    
    return vitals

def generate_realistic_labs(age, has_diabetes, has_hypertension, has_kidney_disease, has_thyroid):
    """Generate realistic lab values based on conditions"""
    labs = {}
    
    # Diabetes markers
    if has_diabetes:
        labs['sugarFasting'] = random.randint(130, 200)
        labs['sugarPostMeal'] = random.randint(180, 280)
        labs['hbA1c'] = round(random.uniform(7.0, 10.5), 1)
    else:
        # Sometimes include normal values
        if random.random() > 0.3:
            labs['sugarFasting'] = random.randint(80, 110)
            labs['sugarPostMeal'] = random.randint(100, 140)
            if random.random() > 0.5:
                labs['hbA1c'] = round(random.uniform(4.5, 6.0), 1)
    
    # Lipid Profile (more often abnormal in older patients)
    if random.random() > 0.2:
        if age > 50 or has_diabetes:
            labs['cholesterolTotal'] = random.randint(200, 280)
            labs['cholesterolLDL'] = random.randint(130, 180)
            labs['cholesterolHDL'] = random.randint(35, 50)
            labs['triglycerides'] = random.randint(150, 300)
        else:
            labs['cholesterolTotal'] = random.randint(150, 220)
            labs['cholesterolLDL'] = random.randint(80, 130)
            labs['cholesterolHDL'] = random.randint(40, 65)
            labs['triglycerides'] = random.randint(80, 180)
    
    # Kidney Function
    if has_kidney_disease:
        labs['serumCreatinine'] = round(random.uniform(1.5, 3.5), 2)
        labs['bloodUrea'] = random.randint(50, 100)
        labs['eGFR'] = random.randint(30, 60)
    elif random.random() > 0.4:
        labs['serumCreatinine'] = round(random.uniform(0.7, 1.3), 2)
        labs['bloodUrea'] = random.randint(15, 45)
        if random.random() > 0.6:
            labs['eGFR'] = random.randint(60, 120)
    
    # Liver Function (occasionally)
    if random.random() > 0.6:
        labs['sgptAlt'] = random.randint(15, 60)
        labs['sgotAst'] = random.randint(15, 55)
        if random.random() > 0.7:
            labs['alkalinePhosphatase'] = random.randint(40, 130)
    
    # Hemoglobin (often checked)
    if random.random() > 0.3:
        labs['hemoglobin'] = round(random.uniform(11.5, 16.0), 1)
    
    # Thyroid (if condition exists)
    if has_thyroid:
        labs['tsh'] = round(random.uniform(5.5, 15.0), 2)
        if random.random() > 0.5:
            labs['t3'] = round(random.uniform(60, 180), 1)
            labs['t4'] = round(random.uniform(4.5, 12.0), 1)
    elif random.random() > 0.7:
        # Sometimes check even without condition
        labs['tsh'] = round(random.uniform(0.5, 4.5), 2)
    
    # Vitamins (commonly deficient in India)
    if random.random() > 0.5:
        labs['vitaminD'] = round(random.uniform(10, 45), 1)
    if random.random() > 0.6:
        labs['vitaminB12'] = random.randint(150, 600)
    
    return labs

def generate_patient_records(patient_id, age, gender, conditions, num_records=5):
    """Generate multiple health records for a patient over time"""
    records = []
    
    # Determine conditions
    has_diabetes = "Type 2 Diabetes" in conditions
    has_hypertension = "Hypertension" in conditions
    has_obesity = "Obesity" in conditions
    has_kidney = "Chronic Kidney Disease" in conditions
    has_thyroid = "Hypothyroidism" in conditions
    
    # Generate records spanning last 1-2 years
    days_back = random.randint(30, 730)
    
    for i in range(num_records):
        # Create timestamp (going backwards in time)
        record_date = datetime.utcnow() - timedelta(days=days_back - (i * (days_back // num_records)))
        
        # Generate vitals and labs
        vitals = generate_realistic_vitals(age, gender, has_diabetes, has_hypertension, has_obesity)
        labs = generate_realistic_labs(age, has_diabetes, has_hypertension, has_kidney, has_thyroid)
        
        # Combine data
        record_data = {
            **vitals,
            **labs,
            'timestamp': record_date,
            'notes': f"Routine checkup on {record_date.strftime('%B %d, %Y')}"
        }
        
        # Randomly decide source (mostly manual, some AI)
        source_type = 'REPORT_AI' if random.random() > 0.7 else 'MANUAL'
        
        records.append({
            'data': record_data,
            'source_type': source_type
        })
    
    return records

def seed_database():
    """Main function to seed the database"""
    print("🌱 Starting database seeding...")
    print(f"📊 Connecting to MongoDB: {MONGODB_URI}")
    
    # Connect to MongoDB
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        print(f"✅ Connected to database: {DATABASE_NAME}")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)
    
    # Get collections
    patients_collection = db.patients
    records_collection = db.healthRecords
    
    # Ask for confirmation
    print(f"\n⚠️  This will create 53 new patients with health records")
    print(f"📍 Database: {DATABASE_NAME}")
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("❌ Seeding cancelled")
        return
    
    print("\n🚀 Generating patient data...")
    
    total_patients = 0
    total_records = 0
    
    # Generate 53 patients
    for i, (name, gender) in enumerate(INDIAN_NAMES[:53], 1):
        try:
            # Generate patient demographics
            age = random.randint(18, 85)
            city = random.choice(INDIAN_CITIES)
            conditions = get_medical_conditions(age)
            
            patient_data = {
                'fullName': name,
                'age': age,
                'gender': gender,
                'contactNumber': generate_phone_number(),
                'email': generate_email(name),
                'address': generate_address(city),
                'medicalConditions': conditions,
                'emergencyContact': generate_phone_number(),
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            
            # Insert patient
            result = patients_collection.insert_one(patient_data)
            patient_id = result.inserted_id
            total_patients += 1
            
            print(f"✅ [{i}/53] Created patient: {name} (Age: {age}, Conditions: {len(conditions)})")
            
            # Generate 3-7 health records per patient
            num_records = random.randint(3, 7)
            patient_records = generate_patient_records(
                patient_id, age, gender, conditions, num_records
            )
            
            # Insert health records
            for record_info in patient_records:
                record = {
                    'patientId': patient_id,
                    'sourceType': record_info['source_type'],
                    'createdAt': datetime.utcnow(),
                    **record_info['data']
                }
                records_collection.insert_one(record)
                total_records += 1
            
            print(f"   📋 Added {num_records} health records")
            
        except Exception as e:
            print(f"❌ Error creating patient {name}: {e}")
            continue
    
    print("\n" + "="*60)
    print(f"✨ Seeding completed successfully!")
    print(f"👥 Total patients created: {total_patients}")
    print(f"📊 Total health records created: {total_records}")
    print(f"📈 Average records per patient: {total_records/total_patients:.1f}")
    print("="*60)
    
    client.close()

if __name__ == "__main__":
    seed_database()
