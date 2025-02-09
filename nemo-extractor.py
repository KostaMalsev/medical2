from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Tuple, Dict, List
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
import uvicorn
import re
from fuzzywuzzy import fuzz
import pandas as pd
from datetime import datetime
from tabulate import tabulate
import traceback

from nemo_parser import validate_documents





app = FastAPI()


tokenizer = AutoTokenizer.from_pretrained("hebrew-medical-ner-final")
model = AutoModelForTokenClassification.from_pretrained("hebrew-medical-ner-final")

params_df = pd.read_csv('transformed_parameters.csv')



FIELD_PATTERNS = {
    'patient_id': r'(?:ת\.?ז\.?:?\s*|מספר\s*תיק\s*רפואי:?\s*)(\d{9})',
    'name': r'(?:שם:?\s*|ת\/המטופל:?\s*)([א-ת\s]+)',
    'admission_date': r'תאריך\s*קבלה:?\s*(\d{2}[./]\d{1,2}[./]\d{4})',
    'discharge_date': r'תאריך\s*שחרור:?\s*(\d{2}[./]\d{1,2}[./]\d{4})',
    'gender': r'(?:מגדר:?\s*|:?\s*)(מר|גברת|זכר|נקבה)',
    'age_at_admission': r'(?:גיל:?\s*(?:בן|בת)?\s*|בן\s*)(\d+)',
    'holocaust_survivor': r'(?:ניצול|ניצולת)\s*שואה|מוכר\s*כניצול\s*שואה',
    #'living_arrangement': r'(?:גר\s*(?:עם)?:?\s*|עם:?\s*)([^\.]+)',
    'floor_number': r'קומה:?\s*(\d+)',
    'elevator': r'(?:מעלית:?\s*|:?\s*)(?:עם|ללא)\s*מעלית',
    #'mobility': r'(?:הליכה|ניידות):?\s*([^\.]+)',
    #'transfers': r'(?:העברות|מעברים):?\s*([^\.]+)',
    #'dressing': r'(?:לבוש|הלבשה):?\s*([^\.]+)',
    #'bathing': r'(?:רחצה|אמבטיה|מקלחת):?\s*([^\.]+)',
    #'eating_status': r'(?:אכילה):?\s*([^\.]+)',
    #'continence': r'(?:שליטה\s*על\s*סוגרים|טיפול\s*בסוגרים):?\s*([^\.]+)',
    #'cognitive_status': r'(?:מצב\s*קוגניטיבי|קוגניטיבי):?\s*([^\.]+)',
    'mmse_score': r'MMSE:?\s*(\d+)\/30',
    'fim_score': r'FIM\s*(?:סה"כ|בקבלה|בשחרור)?:?\s*(\d+)\/126',
    #'physical_examination': r'(?:בדיקה\s*גופנית|בדיקה\s*בקבלה):?\s*([^\.]+)',
    #'diagnoses': r'(?:אבחנות\s*(?:עיקריות)?:?\s*|[\.\d]+\s*)([^\.]+)',
    'admission_reason': r'(?:סיבת\s*(?:קבלה|אשפוז|הפניה)|התקבל\s*עקב):?\s*([^\.]+)',
    'admission_source': r'(?:התקבל|הגיע)\s*מ:?\s*([^\.]+)',
    #'medications_type': r'(?:תרופות|טיפול\s*תרופתי):?\s*([^\.]+)',
    'allergies': r'אלרגיות:?\s*([^\.]+)',
    'tests': r'(?:בדיקות|בדיקה):?\s*([^\.]+)',
    'rehabilitation_type': r'סוג\s*שיקום:?\s*([^\.]+)',
    'past_procedures': r'(?:פרוצדורות|טיפולים)\s*(?:בעבר|קודמים):?\s*([^\.]+)',
    'residence_type': r'(?:סוג\s*(?:מגורים|דיור)|מקום\s*מגורים):?\s*([^\.]+)',
    'stairs_count': r'מדרגות:?\s*([\d]+)',
    'general_appearance': r'מראה\s*כללי:?\s*([^\.]+)',
    'assistive_devices': r'(?:אביזרי|עזרי)\s*עזר:?\s*([^\.]+)',
    'pressure_ulcer': r'פצעי\s*לחץ:?\s*([^\.]+)',
    'pain_level': r'(?:רמת|עוצמת)\s*כאב:?\s*([^\.]+)',
    'sleep_issues': r'בעיות\s*שינה:?\s*([^\.]+)',
    'constipation': r'עצירות:?\s*([^\.]+)',
    'handedness': r'(?:דומיננטיות|יד\s*דומיננטית):?\s*([^\.]+)',
    'education_years': r'(?:שנות\s*לימוד|השכלה):?\s*(\d+)\s*(?:שנים)?',
    'covid_vaccine': r'חיסון\s*קורונה:?\s*([^\.]+)',
    'previous_functioning': r'תפקוד\s*קודם:?\s*([^\.]+)',
    'outdoor_mobility': r'ניידות\s*(?:בחוץ|מחוץ\s*לבית):?\s*([^\.]+)',
    'aid_law': r'(?:חוק\s*סיעוד|גמלת\s*סיעוד):?\s*([^\.]+)',
    'cognitive_assessment': r'הערכה\s*קוגניטיבית:?\s*([^\.]+)',
    'consciousness': r'(?:הכרה|מצב\s*הכרה):?\s*([^\.]+)',
    'sensation': r'תחושה:?\s*([^\.]+)',
    'gross_strength': r'כוח\s*גס:?\s*([^\.]+)',
    'ecg': r'(?:א\.?ק\.?ג|EKG|ECG):?\s*([^\.]+)',
    'nursing_care_claim': r'(?:תביעת\s*סיעוד|תביעה\s*לגמלת\s*סיעוד):?\s*([^\.]+)',
    #'language_communication': r'(?:תקשורת|שפה|הבעה):?\s*([^\.]+)',
    'mood': r'מצב\s*רוח:?\s*([^\.]+)',
    'appetite': r'תיאבון:?\s*([^\.]+)',
    'anxiety': r'חרדה:?\s*([^\.]+)',
    'hospitalization_extension': r'הארכת\s*אשפוז:?\s*([^\.]+)'
}


class FieldOption(BaseModel):
    field: str
    options: List[str]

class TextInput(BaseModel):
    text: str
    parameters: List[FieldOption]

def normalize_text(text: str) -> str:
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def normalize_date(date_str: str) -> str:
    formats = ['%d/%m/%Y', '%d.%m.%Y', '%Y/%m/%d', '%Y.%m.%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime('%d/%m/%Y')
        except ValueError:
            continue
    raise ValueError('Invalid date format')

def extract_date(text: str, date_type: str) -> str:
    # Specific patterns for each date type
    if date_type == 'admission':
        patterns = [
            r'תאריך\s*קבלה:?\s*(\d{1,2}[./]\d{1,2}[./]\d{4})',
            r'התקבל\s*ב:?\s*(\d{1,2}[./]\d{1,2}[./]\d{4})',
            r'קבלה:?\s*(\d{1,2}[./]\d{1,2}[./]\d{4})'
        ]
    else:  # discharge
        patterns = [
            r'תאריך\s*שחרור:?\s*(\d{1,2}[./]\d{1,2}[./]\d{4})',
            r'שוחרר\s*ב:?\s*(\d{1,2}[./]\d{1,2}[./]\d{4})',
            r'שחרור:?\s*(\d{1,2}[./]\d{1,2}[./]\d{4})'
        ]

    # Try specific patterns first
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return normalize_date(match.group(1))
            except ValueError:
                continue

    # Generic date pattern as fallback
    date_pattern = r'(\d{1,2}[./]\d{1,2}[./]\d{4})'
    dates = re.findall(date_pattern, text)
    if dates:
        try:
            return normalize_date(dates[0])
        except ValueError:
            pass

    return 'not_found'



def match_pattern(text: str) -> Dict[str, str]:
    """
    Extract additional information using regex patterns
    """
    additional_info = {}
    
    for field, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, text, re.UNICODE)
        if match:
            if field in ['admission_date', 'discharge_date']:
                additional_info[field] = normalize_date(match.group(1).strip())
            else:
                additional_info[field] = match.group(1).strip()
    return additional_info


def get_field_options(field: str) -> List[str]:
    try:
        field_row = params_df[params_df['Field'] == field].iloc[0]
        return [val for val in field_row[['Value 1', 'Value 2', 'Value 3', 'Value 4', 'Value 5', 
                                        'Value 6', 'Value 7', 'Value 8', 'Value 9', 'Value 10', 
                                        'Value 11']].dropna()]
    except (IndexError, KeyError):
        return []

def fuzzy_find_match(text: str, options: List[str], threshold: int = 5) -> str:
    if not text or not options:
        return 'not_found'
        
    best_match = None
    best_score = 0
    
    text = text.strip().lower()
    for opt in options:
        score = fuzz.token_sort_ratio(text, opt.lower())
        if score > threshold and score > best_score:
            best_match = opt
            best_score = score
            
    return best_match or 'not_found'

def validate_fields(entities: Dict[str, str], text: str) -> Dict[str, str]:
    # Mobility validations
    if entities.get('mobility', 'not_found') == 'not_found':
        if 'הליכון' in text.lower():
            entities['mobility'] = 'עם הליכון'
        elif 'כסא גלגלים' in text.lower():
            entities['mobility'] = 'כסא גלגלים'

    # FIM score validation
    if entities.get('fim_score', 'not_found') == 'not_found':
        fim_matches = re.findall(r'FIM[^0-9]*(\d+)(?:\/126)?', text)
        if fim_matches:
            entities['fim_score'] = fim_matches[-1]

    # Living arrangement validation
    if entities.get('living_arrangement', 'not_found') == 'not_found':
        for arrangement in ['לבד', 'בן זוג', 'בת זוג', 'משפחה']:
            if arrangement in text:
                entities['living_arrangement'] = arrangement
                break

    # Dates validation
    if entities.get('admission_date', 'not_found') == 'not_found':
        entities['admission_date'] = extract_date(text, 'admission')
    if entities.get('discharge_date', 'not_found') == 'not_found':
        entities['discharge_date'] = extract_date(text, 'discharge')

    return entities


#def extract_ner_entities(tokens: List[str], labels: List[str], parameters: List[FieldOption]) -> Dict[str, str]:
def extract_ner_entities(text) -> Dict[str, str]:

    return validate_documents(text=text)
    


def extract_entities(text: str, parameters: List[FieldOption]) -> Dict[str, str]:
    
    text = normalize_text(text)
    
    entities = {}

    # Validate and enhance results
    entities = validate_fields(entities, text)
    
    # Add additional info extraction
    additional_info = match_pattern(text)
    entities.update(additional_info)

    # NER Processing
    ner_entities = extract_ner_entities(text)

    entities.update(ner_entities)

    # Print ner-entities info as table
    print_entities(ner_entities)


    # Fill missing fields with not_found
    for param in parameters:
        if param.field not in entities:
            entities[param.field] = 'not_found'


    return entities


# Function to print the entities as a table
def print_entities(entities):
    # Convert entities dictionary to a list of lists for tabulate
    entities_table = [[key, value] for key, value in entities.items()]
    print(tabulate(entities_table, headers=['Field', 'Value'], tablefmt='grid'))
        
@app.post("/query")
async def query(input: TextInput):
    entities = extract_entities(input.text, input.parameters)
    #print(input.text)
    return {"response": entities}
    

@app.get("/healthcheck")
async def healthcheck():
    try:
        sample = "חולה עם CVA איסכמי בהמיספרה שמאלית"
        sample_params = [FieldOption(field="diagnoses", options=get_field_options("diagnoses"))]
        entities = extract_entities(sample, sample_params)
        return {"status": "healthy", "sample_entities": entities}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)