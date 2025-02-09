from dataclasses import dataclass
import argparse
import json
import logging
from typing import List, Dict, Any
import re

@dataclass
class FieldOption:
    """Class for storing field options."""
    field: str
    options: List[str]

class DocumentProcessor:
    def __init__(self, model_path: str, confidence_threshold: float = 0.7):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self._setup_patterns()

    def _setup_patterns(self):
        """Setup regex patterns for entity extraction."""
        self.PATTERNS = {
            'patient_id': r'ת\.?ז\.?:?\s*(\d{9})',
            'name': r'שם:?\s*([א-ת\s]+)',
            'admission_date': r'תאריך\s*קבלה:?\s*(\d{2}[./]\d{2}[./]\d{4})',
            'discharge_date': r'תאריך\s*שחרור:?\s*(\d{2}[./]\d{2}[./]\d{4})',
            'gender': r'מגדר:?\s*(מר|גברת)',
            'age': r'גיל:?\s*(?:בן|בת)\s*(\d+)',
            'fim_score': r'FIM:?\s*(\d+)(?:/126)?',
            'mmse_score': r'MMSE:?\s*(\d+)(?:/30)?'
        }

    def process_document(self, text: str) -> Dict[str, Any]:
        """Process a document and extract information."""
        try:
            return {
                'entities': self._extract_entities(text),
                'sections': self._extract_sections(text),
                'original_text': text
            }
        except Exception as e:
            logging.error(f"Error processing document: {str(e)}")
            raise

    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text using patterns."""
        entities = []
        for field, pattern in self.PATTERNS.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                entity_text = match.group(1) if len(match.groups()) > 0 else match.group(0)
                entities.append({
                    'text': entity_text,
                    'label': field,
                    'confidence': 1.0,  # Pattern matches get high confidence
                    'start': match.start(),
                    'end': match.end()
                })
        return entities

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract document sections."""
        sections = {}
        section_patterns = {
            'personal_info': r'פרטים\s*אישיים:(.*?)(?:מקור|$)',
            'admission_info': r'מקור\s*הפניה:(.*?)(?:מצב|$)',
            'physical_exam': r'בדיקה\s*גופנית:(.*?)(?:אבחנות|$)',
            'diagnoses': r'אבחנות:(.*?)(?:המלצות|$)',
            'recommendations': r'המלצות:(.*?)(?:$)'
        }

        for section, pattern in section_patterns.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                sections[section] = match.group(1).strip()

        return sections

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def read_text(text: str) -> List[str]:
    """Read text and return list of texts to process."""
    return [line.strip() for line in text.split('\n') if line.strip()]

def read_file(file_path: str) -> List[str]:
    """Read file and return list of texts to process."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def save_results(results: List[Dict], output_file: str):
    """Save results to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def print_entity_stats(results: List[Dict[str, Any]]):
    """Print statistics about extracted entities."""
    entity_counts = {}
    confidence_sums = {}
    
    for doc in results:
        for entity in doc['entities']:
            label = entity['label']
            if label not in entity_counts:
                entity_counts[label] = 0
                confidence_sums[label] = 0
            entity_counts[label] += 1
            confidence_sums[label] += entity['confidence']
    
    print("\nEntity Statistics:")
    print("=" * 60)
    print(f"{'Entity Type':<25} {'Count':<8} {'Avg Confidence':<15}")
    print("-" * 60)
    
    for label in sorted(entity_counts.keys()):
        count = entity_counts[label]
        avg_conf = confidence_sums[label] / count
        print(f"{label:<25} {count:<8} {avg_conf:.4f}")

def print_section_stats(results: List[Dict[str, Any]]):
    """Print statistics about extracted sections."""
    section_counts = {}
    
    for doc in results:
        for section in doc['sections'].keys():
            section_counts[section] = section_counts.get(section, 0) + 1
    
    print("\nSection Statistics:")
    print("=" * 40)
    print(f"{'Section Type':<25} {'Count':<8}")
    print("-" * 40)
    
    for section in sorted(section_counts.keys()):
        print(f"{section:<25} {section_counts[section]:<8}")

def validate_documents(
    model_path: str = 'hebrew-medical-ner-final',
    input_file: str = '',
    output_file: str = "validation_results.json",
    text: str = 'empty',
    confidence_threshold: float = 0.7
):
    """Run validation on documents."""
    # Initialize processor
    processor = DocumentProcessor(
        model_path=model_path,
        confidence_threshold=confidence_threshold
    )
    
    # Read input texts
    if(len(text) > 0):
        texts = read_text(text)
    else:
        logging.info(f"Reading texts from {input_file}")
        texts = read_file(input_file)    
    logging.info(f"Found {len(texts)} texts to process")
    
    # Process each text
    results = []
    entities = {}
    for i, text in enumerate(texts, 1):
        logging.info(f"Processing text {i}/{len(texts)}")
        try:
            result = processor.process_document(text)
            print(f"\nDocument {i}:")
            print("=" * 80)
            print("\nExtracted Entities:")
            for entity in result['entities']:
                print(f"  • {entity['label']}: '{entity['text']}' "
                      f"(confidence: {entity['confidence']:.4f})")
                entities[entity['label']] = entity['text']
            
            if result['sections']:
                print("\nExtracted Sections:")
                for section, content in result['sections'].items():
                    print(f"\n{section}:")
                    print(content[:200] + "..." if len(content) > 200 else content)
            
            results.append(result)
            
        except Exception as e:
            logging.error(f"Error processing document {i}: {str(e)}")
            continue
    
    print_entity_stats(results)
    print_section_stats(results)
    
    save_results(results, output_file)
    logging.info(f"Results saved to {output_file}")
    
    return entities

def main():
    parser = argparse.ArgumentParser(description='Validate Hebrew Medical NER')
    
    parser.add_argument(
        '--model_path',
        default='hebrew-medical-ner/final',
        help='Path to the trained model'
    )
    
    parser.add_argument(
        '--input_file',
        default='results/searchable_text.csv',
        help='File containing texts to analyze'
    )
    
    parser.add_argument(
        '--output_file',
        default='validation_results.json',
        help='Output JSON file for results'
    )
    
    parser.add_argument(
        '--confidence',
        type=float,
        default=0.7,
        help='Confidence threshold for entity extraction'
    )
    
    args = parser.parse_args()
    
    setup_logging()
    
    try:
        validate_documents(
            model_path=args.model_path,
            input_file=args.input_file,
            output_file=args.output_file,
            confidence_threshold=args.confidence
        )
    except Exception as e:
        logging.error(f"Validation failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()