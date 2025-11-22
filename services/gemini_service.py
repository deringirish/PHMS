"""
Gemini API integration for lab report extraction
"""
import google.generativeai as genai
import json
import os
from config import Config

class GeminiService:
    """Service for extracting health data from lab reports using Gemini API"""
    
    def __init__(self):
        """Initialize Gemini API"""
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None
    
    def _build_extraction_prompt(self):
        """Build the prompt for controlled extraction"""
        return """
You are a medical lab report data extractor. Extract ONLY the following health metrics from the provided lab report.
Return the data as a JSON object. Use null for any values that are not found in the report.

**IMPORTANT**: Extract ONLY these fields and ignore all other values:

VITALS:
- bpSystolic (systolic blood pressure in mmHg)
- bpDiastolic (diastolic blood pressure in mmHg)
- heartRate (beats per minute)
- temperature (in Celsius)
- spo2 (oxygen saturation %)
- weight (in kg)
- height (in cm)

DIABETES/GLUCOSE:
- sugarFasting (fasting blood sugar in mg/dL)
- sugarPostMeal (post-meal blood sugar in mg/dL)
- randomBloodSugar (random blood sugar in mg/dL)
- hbA1c (HbA1c percentage)

LIPID PROFILE:
- cholesterolTotal (total cholesterol in mg/dL)
- cholesterolHDL (HDL cholesterol in mg/dL)
- cholesterolLDL (LDL cholesterol in mg/dL)
- triglycerides (in mg/dL)
- vldl (VLDL in mg/dL)

KIDNEY FUNCTION:
- serumCreatinine (in mg/dL)
- bloodUrea (in mg/dL)
- bun (blood urea nitrogen in mg/dL)
- eGFR (estimated GFR in mL/min/1.73m²)

LIVER FUNCTION:
- sgptAlt (SGPT/ALT in U/L)
- sgotAst (SGOT/AST in U/L)
- alkalinePhosphatase (ALP in U/L)
- totalBilirubin (in mg/dL)
- directBilirubin (in mg/dL)
- indirectBilirubin (in mg/dL)

ELECTROLYTES:
- sodium (in mEq/L)
- potassium (in mEq/L)
- chloride (in mEq/L)

HEMATOLOGY (CBC):
- hemoglobin (in g/dL)
- totalLeukocyteCount (WBC in cells/μL)
- plateletCount (in lakhs or x10^3/μL)
- rbcCount (RBC in million/μL)
- pcv (packed cell volume %)
- mcv (mean corpuscular volume in fL)

THYROID:
- tsh (TSH in μIU/mL)
- t3 (T3 in ng/dL)
- t4 (T4 in μg/dL)

VITAMINS:
- vitaminD (in ng/mL)
- vitaminB12 (in pg/mL)

Return ONLY valid JSON in this exact format:
{
  "bpSystolic": null,
  "bpDiastolic": null,
  "heartRate": null,
  ...
}

Extract numeric values only. Include the report date as "timestamp" in ISO format if available.
Do not include any other fields, tests, or markers not listed above.
"""
    
    def extract_from_report(self, file_path):
        """
        Extract health data from lab report
        
        Args:
            file_path: Path to the uploaded file
            
        Returns:
            Dictionary with extracted health metrics or None if extraction fails
        """
        if not self.model:
            raise ValueError('Gemini API key not configured')
        
        try:
            # Upload file to Gemini
            uploaded_file = genai.upload_file(file_path)
            
            # Generate extraction prompt
            prompt = self._build_extraction_prompt()
            
            # Call Gemini API
            response = self.model.generate_content([uploaded_file, prompt])
            
            # Parse response
            response_text = response.text.strip()
            
            # Try to extract JSON from response
            # Look for JSON block in response
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            
            # Parse JSON
            extracted_data = json.loads(response_text)
            
            # Filter out null values and non-numeric values
            filtered_data = {}
            for key, value in extracted_data.items():
                if value is not None and value != '':
                    # Try to convert to float for numeric fields
                    if key != 'timestamp':
                        try:
                            filtered_data[key] = float(value)
                        except (ValueError, TypeError):
                            # Keep as is if not numeric
                            filtered_data[key] = value
                    else:
                        filtered_data[key] = value
            
            return filtered_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f'Failed to parse Gemini response as JSON: {str(e)}')
        except Exception as e:
            raise ValueError(f'Failed to extract data from report: {str(e)}')
