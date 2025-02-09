import re
import torch
import logging
from typing import List, Dict, Any, Optional, Tuple
from transformers import AutoTokenizer, AutoModelForTokenClassification
from collections import defaultdict

# Entity patterns for rule-based extraction
ENTITY_PATTERNS = {
    'date': r'(?:תאריך|תאריך קבלה|תאריך שחרור)[^:]*:\s*(\d{1,2}[/.]\d{1,2}[/.]\d{4})',
    'gender': r'(?:מגדר|המטופל)[^:]*:\s*(מר|גברת)',
    'age': r'(?:גיל|בן|בת)[^:]*:?\s*(\d+)',
    'fim_score': r'FIM[^:]*:\s*(\d+/\d+|(?:\d+\s*/\s*\d+))',
    'mobility': r'(?:הליכה|ניידות)[^:]*:\s*([^\.]+(?:עם הליכון|עצמאי|זקוק לעזרה|מקל הליכה|כיסא גלגלים)[^\.]*)',
    'diagnoses': r'אבחנות[^:]*:\s*([^\.]+(?:CVA|סוכרת|יתר לחץ דם|COPD)[^\.]*)',
    'admission_source': r'(?:התקבל מ|מקור הפניה)[^:]*:\s*([^\.]+)',
    'holocaust_survivor': r'(?:שואה|ניצול)[^:]*:\s*([^\.]+(?:ניצול שואה|ניצולת שואה|מוכר כניצול)[^\.]*)',
    'living_arrangement': r'(?:מגורים|גר עם)[^:]*:\s*([^\.]+)',
    'floor_number': r'קומה[^:]*:\s*(\d+)',
    'elevator': r'מעלית[^:]*:\s*([^\.]+(?:עם מעלית|ללא מעלית)[^\.]*)',
    'mmse_score': r'MMSE[^:]*:\s*(\d+/\d+)',
    'ecg': r'(?:א\.ק\.ג|אקג)[^:]*:\s*([^\.]+)',
    'bathing': r'רחצה[^:]*:\s*([^\.]+)',
    'eating_status': r'אכילה[^:]*:\s*([^\.]+)',
    'continence': r'(?:סוגרים|שליטה על סוגרים)[^:]*:\s*([^\.]+)',
    'transfers': r'(?:מעברים|העברות)[^:]*:\s*([^\.]+)'
}

# Section patterns for context extraction
SECTION_PATTERNS = {
    'personal_info': r'פרטי[ם\s]*(?:מטופל|אישיים):(.*?)(?:אבחנות|סיבת|$)',
    'diagnoses': r'אבחנות[^:]*:(.*?)(?:הערכת|סיכום|$)',
    'fim_assessment': r'הערכת\s*FIM:(.*?)(?:סיכום|המלצות|$)',
    'discharge_summary': r'סיכום[^:]*:(.*?)(?:המלצות|$)',
    'recommendations': r'המלצות[^:]*:(.*?)(?:חתימה|$)'
}

class DocumentProcessor:
    def __init__(self, model_path: str, confidence_threshold: float = 0.7):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.confidence_threshold = confidence_threshold
        
        # Setup device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def preprocess_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove metadata and file paths
        text = re.sub(r'(?:discharge-letter|sample_form)\.pdf,\d+,', '', text)
        text = re.sub(r'file:///.*?\.html', '', text)
        text = re.sub(r'\d+/\d+/\d+,\s+\d+:\d+\s+[AP]M', '', text)
        
        # Fix quotation marks and spaces
        text = text.replace('"""', '"').replace('""', '"').replace('"', '')
        text = re.sub(r'\s+', ' ', text)
        
        # Clean special characters but preserve Hebrew and numbers
        text = re.sub(r'[^\u0590-\u05FF\w\s\d:./,-]', ' ', text)
        
        return text.strip()

    def extract_pattern_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using regex patterns."""
        entities = []
        
        for entity_type, pattern in ENTITY_PATTERNS.items():
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                entity_text = match.group(1).strip()
                if self.validate_entity(entity_text, entity_type):
                    entities.append({
                        'text': entity_text,
                        'label': entity_type,
                        'confidence': 1.0,  # Rule-based matches get high confidence
                        'start': match.start(1),
                        'end': match.end(1)
                    })
        
        return entities

    def validate_entity(self, text: str, label: str, confidence: float = 1.0) -> bool:
        """Validate extracted entities."""
        if confidence < self.confidence_threshold:
            return False
            
        if not text or len(text.strip()) < 2:
            return False

        if label == 'fim_score':
            if '/' not in text:
                return False
            try:
                num, total = map(int, text.replace(' ', '').split('/'))
                return total in [7, 126] and 0 <= num <= total
            except:
                return False

        if label == 'date':
            try:
                parts = re.split(r'[./]', text)
                if len(parts) != 3:
                    return False
                day, month, year = map(int, parts)
                return 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100
            except:
                return False

        if label == 'age':
            try:
                age = int(text)
                return 0 <= age <= 120
            except:
                return False

        return True

    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract document sections."""
        sections = {}
        
        for section_name, pattern in SECTION_PATTERNS.items():
            match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
            if match:
                section_text = match.group(1).strip()
                if section_text:
                    sections[section_name] = section_text
        
        return sections



    def extract_ner_entities(tokens: List[str], labels: List[str], parameters: List[FieldOption]) -> Dict[str, str]:
        """
        Extract named entities from tokens and labels with improved preprocessing and pattern matching.
        
        Args:
            tokens: List of tokens from the tokenizer
            labels: List of corresponding BIO labels
            parameters: List of FieldOption objects containing valid field values
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        current_entity = []
        current_label = ""
        skip_tokens = {tokenizer.sep_token, tokenizer.pad_token, tokenizer.cls_token, 
                    '[PAD]', '[SEP]', '[CLS]', '[UNK]'}

        # Helper function to clean and normalize text
        def clean_text(text: str) -> str:
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = re.sub(r'[\u200f\u200e]', '', text)  # Remove RTL/LTR marks
            text = re.sub(r'[«»""״׳]', '', text)  # Remove quotation marks
            text = text.strip()
            return text

        # Helper function to process entity text and find best match
        def process_entity(entity_tokens: List[str], field: str) -> Optional[str]:
            if not entity_tokens:
                return None
                
            text = tokenizer.convert_tokens_to_string(entity_tokens)
            text = clean_text(text)
            
            # Skip if text is too short or contains only special characters
            if len(text) < 2 or not re.search(r'[\u0590-\u05FF\w]', text):
                return None
                
            # Get field options and find best match
            param = next((p for p in parameters if p.field == field), None)
            if not param or not param.options:
                return None
                
            # Special handling for certain fields
            if field == 'fim_score':
                match = re.search(r'(\d+)(?:/126)?', text)
                if match:
                    score = int(match.group(1))
                    if 0 <= score <= 126:
                        return str(score)
                        
            elif field == 'mmse_score':
                match = re.search(r'(\d+)(?:/30)?', text)
                if match:
                    score = int(match.group(1))
                    if 0 <= score <= 30:
                        return str(score)
                        
            # General fuzzy matching for other fields
            return fuzzy_find_match(text, param.options, threshold=60)

        # Process tokens and labels
        for idx, (token, label) in enumerate(zip(tokens, labels)):
            if token in skip_tokens:
                continue
                
            # Handle subword tokens (starting with ##)
            is_subword = token.startswith('##')
            clean_token = token[2:] if is_subword else token
            
            if label.startswith("B-"):
                # Process previous entity if exists
                if current_entity:
                    if matched_value := process_entity(current_entity, current_label):
                        entities[current_label] = matched_value
                
                # Start new entity
                current_label = label[2:]
                current_entity = [clean_token]
                
            elif label.startswith("I-") and current_label == label[2:]:
                # Continue current entity
                current_entity.append(clean_token)
                
            elif label == "O" and current_entity:
                # Process and reset current entity
                if matched_value := process_entity(current_entity, current_label):
                    entities[current_label] = matched_value
                current_entity = []
                current_label = ""
                
            # Handle subwords that don't have a specific label
            elif is_subword and current_entity:
                current_entity.append(clean_token)
        
        # Process final entity if exists
        if current_entity and current_label:
            if matched_value := process_entity(current_entity, current_label):
                entities[current_label] = matched_value
        
        return entities

    def _add_entity(self, entities: List[Dict], tokens: List[str], label: str, scores: List[float]):
        """Add an entity to the list after validation."""
        if not tokens or not label:
            return
            
        text = self.tokenizer.convert_tokens_to_string(tokens)
        text = re.sub(r'\s+', ' ', text).strip()
        confidence = sum(scores) / len(scores)
        
        if self.validate_entity(text, label, confidence):
            entities.append({
                'text': text,
                'label': label,
                'confidence': confidence
            })

    def merge_entities(self, pattern_entities: List[Dict], model_entities: List[Dict]) -> List[Dict]:
        """Merge entities from both sources, removing duplicates and conflicts."""
        all_entities = []
        seen = set()
        
        # Sort entities by confidence
        sorted_entities = sorted(
            pattern_entities + model_entities,
            key=lambda x: (-x['confidence'], -len(x['text']))
        )
        
        for entity in sorted_entities:
            key = (entity['text'], entity['label'])
            if key not in seen:
                seen.add(key)
                all_entities.append(entity)
        
        return all_entities

    def process_document(self, text: str) -> Dict[str, Any]:
        """Process a document and extract all information."""
        # Clean text
        cleaned_text = self.preprocess_text(text)
        if not cleaned_text:
            return {"entities": [], "sections": {}, "original_text": text}
        
        # Extract entities using both methods
        pattern_entities = self.extract_pattern_entities(cleaned_text)
        model_entities = self.extract_model_entities(cleaned_text)
        
        # Merge entities
        merged_entities = self.merge_entities(pattern_entities, model_entities)
        
        # Extract sections
        sections = self.extract_sections(cleaned_text)
        
        return {
            "entities": merged_entities,
            "sections": sections,
            "original_text": text
        }

def main():
    """Example usage of the document processor."""
    # Example text
    text = """
    מכתב שחרור
    תאריך: 05/02/2025
    
    פרטי מטופל:
    מר בן 75
    FIM: 60/126
    
    אבחנות עיקריות:
    CVA איסכמי
    """
    
    # Initialize processor
    processor = DocumentProcessor("../hebrew-medical-ner/final")
    
    # Process document
    results = processor.process_document(text)
    
    # Print results
    print("\nExtracted Entities:")
    for entity in results["entities"]:
        print(f"  • {entity['label']}: '{entity['text']}' "
              f"(confidence: {entity['confidence']:.4f})")
    
    print("\nExtracted Sections:")
    for section, content in results["sections"].items():
        print(f"\n{section}:")
        print(content)

if __name__ == "__main__":
    main()