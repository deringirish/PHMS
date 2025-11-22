"""
PDF Report Generation Service
Uses ReportLab to generate various PDF reports
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
from bson import ObjectId

class PDFService:
    """PDF Generation Service for health reports"""
    
    def __init__(self, db):
        self.db = db
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#374151'),
            spaceBefore=15,
            spaceAfter=10
        ))
    
    def _add_header(self, elements, title):
        """Add header to PDF"""
        # Title
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Generated date
        date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        date_para = Paragraph(f"Generated on: {date_str}", self.styles['Normal'])
        elements.append(date_para)
        elements.append(Spacer(1, 0.3 * inch))
    
    def _add_patient_info(self, elements, patient):
        """Add patient information section"""
        elements.append(Paragraph("Patient Information", self.styles['SectionHeader']))
        
        # Patient info table
        patient_data = [
            ['Name:', patient.get('fullName', 'N/A')],
            ['Age:', str(patient.get('age', 'N/A'))],
            ['Gender:', patient.get('gender', 'N/A')],
            ['Contact:', patient.get('contactNumber', 'N/A')],
            ['Email:', patient.get('email', 'N/A')]
        ]
        
        if patient.get('medicalConditions'):
            conditions = ', '.join(patient['medicalConditions'])
            patient_data.append(['Medical Conditions:', conditions])
        
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(patient_table)
        elements.append(Spacer(1, 0.3 * inch))
    
    def generate_health_summary(self, patient_id, date_range=None):
        """
        Generate comprehensive health summary PDF
        
        Args:
            patient_id: Patient ID
            date_range: Optional tuple of (start_date, end_date)
            
        Returns:
            PDF file as BytesIO object
        """
        # Get patient data
        from models.patient import PatientModel
        from models.health_record import HealthRecordModel
        
        patient_model = PatientModel(self.db)
        record_model = HealthRecordModel(self.db)
        
        patient = patient_model.get_patient_by_id(patient_id)
        if not patient:
            return None
        
        # Get health records
        if date_range:
            records = record_model.get_records_by_patient(patient_id, date_range[0], date_range[1])
        else:
            records = record_model.get_records_by_patient(patient_id)
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)
        elements = []
        
        # Add header
        self._add_header(elements, "Health Summary Report")
        
        # Add patient info
        self._add_patient_info(elements, patient)
        
        # Add health records
        if records:
            elements.append(Paragraph("Health Records History", self.styles['SectionHeader']))
            elements.append(Spacer(1, 0.1 * inch))
            
            for record in records[:10]:  # Limit to 10 most recent
                # Record date
                record_date = record.get('timestamp', record.get('createdAt'))
                date_str = record_date.strftime("%b %d, %Y") if record_date else "N/A"
                elements.append(Paragraph(f"<b>Date:</b> {date_str}", self.styles['Normal']))
                
                # Key metrics
                metrics = []
                if record.get('bpSystolic') and record.get('bpDiastolic'):
                    metrics.append(f"BP: {record['bpSystolic']}/{record['bpDiastolic']} mmHg")
                if record.get('sugarFasting'):
                    metrics.append(f"Fasting Sugar: {record['sugarFasting']} mg/dL")
                if record.get('weight'):
                    metrics.append(f"Weight: {record['weight']} kg")
                if record.get('hbA1c'):
                    metrics.append(f"HbA1c: {record['hbA1c']}%")
                
                if metrics:
                    metrics_text = " | ".join(metrics)
                    elements.append(Paragraph(metrics_text, self.styles['Normal']))
                
                elements.append(Spacer(1, 0.15 * inch))
        else:
            elements.append(Paragraph("No health records found.", self.styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_prescription_pdf(self, prescription_id):
        """
        Generate prescription PDF
        
        Args:
            prescription_id: Prescription ID
            
        Returns:
            PDF file as BytesIO object
        """
        from models.prescription import PrescriptionModel
        from models.patient import PatientModel
        from models.admin import AdminModel
        
        prescription_model = PrescriptionModel(self.db)
        patient_model = PatientModel(self.db)
        admin_model = AdminModel(self.db)
        
        prescription = prescription_model.get_prescription_by_id(prescription_id)
        if not prescription:
            return None
        
        patient = patient_model.get_patient_by_id(str(prescription['patientId']))
        doctor = admin_model.find_by_id(str(prescription['doctorId'])) if prescription.get('doctorId') else None
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)
        elements = []
        
        # Add header
        self._add_header(elements, "Medical Prescription")
        
        # Patient info
        if patient:
            self._add_patient_info(elements, patient)
        
        # Prescription date
        prescription_date = prescription.get('prescriptionDate', prescription.get('createdAt'))
        date_str = prescription_date.strftime("%B %d, %Y") if prescription_date else "N/A"
        elements.append(Paragraph(f"<b>Prescription Date:</b> {date_str}", self.styles['Normal']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Medications
        elements.append(Paragraph("Prescribed Medications", self.styles['SectionHeader']))
        
        # Medication table
        med_data = [['Medication', 'Dosage', 'Frequency', 'Duration', 'Instructions']]
        
        for med in prescription.get('medications', []):
            med_data.append([
                med.get('medicationName', ''),
                med.get('dosage', ''),
                med.get('frequency', ''),
                med.get('duration', ''),
                med.get('instructions', '')
            ])
        
        med_table = Table(med_data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1*inch, 1.8*inch])
        med_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(med_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Notes
        if prescription.get('notes'):
            elements.append(Paragraph("Additional Notes", self.styles['SectionHeader']))
            elements.append(Paragraph(prescription['notes'], self.styles['Normal']))
            elements.append(Spacer(1, 0.3 * inch))
        
        # Doctor signature
        if doctor:
            elements.append(Spacer(1, 0.5 * inch))
            elements.append(Paragraph(f"<b>Dr. {doctor.get('name', 'N/A')}</b>", self.styles['Normal']))
            elements.append(Paragraph("Signature: _____________________", self.styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_visit_summary_pdf(self, visit_id):
        """
        Generate visit summary PDF
        
        Args:
            visit_id: Visit ID
            
        Returns:
            PDF file as BytesIO object
        """
        from models.visit import VisitModel
        from models.patient import PatientModel
        from models.admin import AdminModel
        
        visit_model = VisitModel(self.db)
        patient_model = PatientModel(self.db)
        admin_model = AdminModel(self.db)
        
        visit = visit_model.get_visit_by_id(visit_id)
        if not visit:
            return None
        
        patient = patient_model.get_patient_by_id(str(visit['patientId']))
        doctor = admin_model.find_by_id(str(visit['doctorId'])) if visit.get('doctorId') else None
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)
        elements = []
        
        # Add header
        self._add_header(elements, "Visit Summary")
        
        # Patient info
        if patient:
            self._add_patient_info(elements, patient)
        
        # Visit info
        visit_date = visit.get('visitDate', visit.get('createdAt'))
        date_str = visit_date.strftime("%B %d, %Y") if visit_date else "N/A"
        
        elements.append(Paragraph("Visit Details", self.styles['SectionHeader']))
        visit_info = [
            ['Visit Date:', date_str],
            ['Doctor:', doctor.get('name', 'N/A') if doctor else 'N/A']
        ]
        
        visit_table = Table(visit_info, colWidths=[2*inch, 4*inch])
        visit_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(visit_table)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Chief complaint
        if visit.get('chiefComplaint'):
            elements.append(Paragraph("Chief Complaint", self.styles['SectionHeader']))
            elements.append(Paragraph(visit['chiefComplaint'], self.styles['Normal']))
            elements.append(Spacer(1, 0.15 * inch))
        
        # Diagnosis
        if visit.get('diagnosis'):
            elements.append(Paragraph("Diagnosis", self.styles['SectionHeader']))
            diagnosis_text = ', '.join(visit['diagnosis']) if isinstance(visit['diagnosis'], list) else visit['diagnosis']
            elements.append(Paragraph(diagnosis_text, self.styles['Normal']))
            elements.append(Spacer(1, 0.15 * inch))
        
        # Treatment plan
        if visit.get('treatmentPlan'):
            elements.append(Paragraph("Treatment Plan", self.styles['SectionHeader']))
            elements.append(Paragraph(visit['treatmentPlan'], self.styles['Normal']))
            elements.append(Spacer(1, 0.15 * inch))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
