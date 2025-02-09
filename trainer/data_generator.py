import pandas as pd
import random
import datetime
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import os

def load_parameters():
    """Load and validate the parameters from CSV."""
    try:
        df = pd.read_csv('../transformed_parameters.csv')
        print(f"Loaded {len(df)} parameters from CSV")
        return df
    except Exception as e:
        print(f"Error loading parameters: {e}")
        raise

def create_realistic_values() -> Dict[str, List[str]]:
    """Create realistic values for medical entities."""
    return {
        'gender': ['מר', 'גברת'],
        
        'age_at_admission': ['75', '82', '68', '91', '70', '88', '65', '73'],
        
        'admission_date': [
            '01.02.2025', '15.02.2025', '20.02.2025',
            '01/02/2025', '15/02/2025', '20/02/2025'
        ],
        
        'admission_source': [
            'בי"ח', 'מיון', 'מחלקה פנימית', 'מחלקה אורתופדית', 
            'מחלקה נוירולוגית', 'פנימית א', 'פנימית ב', 'מחלקת שיקום'
        ],
        
        'discharge_date': [
            '05.02.2025', '19.02.2025', '25.02.2025',
            '05/02/2025', '19/02/2025', '25/02/2025'
        ],
        
        'discharge_destination': [
            'ביתו', 'מוסד סיעודי', 'בית אבות', 'דיור מוגן',
            'מחלקה סיעודית', 'אשפוז המשך'
        ],
        
        'holocaust_survivor': [
            'ניצול שואה', 'ניצולת שואה', 'מוכר כניצול שואה',
            'ניצול שואה מוכר', 'ניצולת שואה מוכרת'
        ],
        
        'living_arrangement': [
            'בן זוג', 'לבד', 'בת זוג', 'משפחה', 'ילדים', 'מטפל צמוד',
            'גר עם בן זוג', 'גרה עם בת זוג', 'גר עם המשפחה'
        ],
        
        'floor_number': ['1', '2', '3', '4', '5', '6', '7'],
        
        'elevator': ['עם מעלית', 'ללא מעלית', 'יש מעלית', 'אין מעלית'],
        
        'mobility': [
            'עם הליכון', 'עצמאי', 'זקוק לעזרה', 'עם מקל הליכה',
            'כיסא גלגלים', 'הליכה עם תמיכה', 'מרותק למיטה',
            'הליכה עצמאית', 'זקוק לעזרה בהליכה', 'עצמאי בהליכה',
            'הליכה עם הליכון', 'ניידות עם הליכון'
        ],
        
        'transfers': [
            'זקוק לעזרה קלה', 'עצמאי', 'תלוי חלקית', 'זקוק להשגחה',
            'זקוק לעזרה מלאה', 'עצמאי עם השגחה', 'זקוק לתמיכה',
            'עצמאי במעברים', 'זקוק לעזרה במעברים'
        ],
        
        'dressing': [
            'עצמאי בפלג גוף עליון', 'זקוק לעזרה', 'עצמאי', 'תלוי חלקית',
            'זקוק לעזרה מלאה', 'עצמאי עם השגחה', 'עצמאי בלבוש',
            'זקוק לעזרה בלבוש', 'עצמאי בהלבשה'
        ],
        
        'bathing': [
            'זקוק להשגחה במקלחת', 'עצמאי', 'זקוק לעזרה', 'תלוי חלקית',
            'זקוק לעזרה מלאה', 'עצמאי עם השגחה', 'עצמאי ברחצה',
            'זקוק לעזרה ברחצה', 'עצמאי במקלחת'
        ],
        
        'eating_status': [
            'עצמאי', 'זקוק לעזרה בחיתוך', 'אוכל לבד', 'זקוק להאכלה',
            'אכילה עם השגחה', 'זקוק לעזרה חלקית', 'עצמאי באכילה',
            'זקוק לעזרה באכילה', 'אוכל באופן עצמאי'
        ],
        
        'continence': [
            'שליטה מלאה', 'חלקית', 'ללא שליטה', 'שליטה יום', 'שליטה לילה',
            'שליטה מלאה בסוגרים', 'ללא שליטה בסוגרים'
        ],
        
        'ecg': [
            'קצב סינוס', 'תקין', 'פרפור פרוזדורים', 'היפרטרופיה', 'איסכמיה',
            'קצב סינוס תקין', 'פרפור פרוזדורים עם קצב מהיר'
        ],
        
        'mmse_score': [
            '29/30', '28/30', '25/30', '30/30', '27/30', '24/30',
            '29', '28', '25', '30', '27', '24'
        ],
        
        'fim_score': [
            '5', '6', '4', '7', '3', '8',
            '60/126', '88/126', '90/126', '100/126',
            '4/7', '6/7', '3/7', '5/7', '7/7'
        ],
        
        'diagnoses': [
            'CVA', 'שבר צוואר ירך', 'מחלת ריאות חסימתית',
            'יתר לחץ דם', 'סוכרת', 'אי ספיקת לב',
            'פרקינסון', 'דמנציה', 'אוסטאופורוזיס',
            'CVA איסכמי', 'אירוע מוחי איסכמי', 'שבר בצוואר הירך',
            'מחלת לב איסכמית', 'יתר לחץ דם', 'סוכרת סוג 2'
        ],
        
        'physical_examination': [
            'תקין', 'ללא ממצאים חריגים',
            'חולשה בגפה ימין', 'חולשה בגפה שמאל',
            'ירידה בטווחי תנועה', 'כאב בתנועה',
            'חולשה בגפיים תחתונות', 'חולשה בפלג גוף ימין',
            'ירידה בטווחי התנועה בכתף'
        ]
    }

def create_medical_document_templates() -> List[str]:
    """Create templates that mimic real medical documents."""
    return [
        # Discharge letter template
        """מכתב שחרור
        תאריך: {discharge_date}
        
        פרטי מטופל:
        {gender} בן {age_at_admission}
        
        תאריך קבלה: {admission_date}
        התקבל מ{admission_source}
        
        אבחנות עיקריות:
        {diagnoses}
        
        בדיקות בקבלה:
        א.ק.ג: {ecg}
        MMSE: {mmse_score}
        FIM: {fim_score}
        
        מצב בשחרור:
        {mobility}
        {transfers}
        {eating_status}
        
        שוחרר ל{discharge_destination}""",
        
        # Status update template
        """עדכון סטטוס רפואי
        
        {gender} {age_at_admission}
        {holocaust_survivor}
        
        מצב תפקודי:
        ניידות: {mobility}
        מעברים: {transfers}
        רחצה: {bathing}
        הלבשה: {dressing}
        אכילה: {eating_status}
        שליטה על סוגרים: {continence}
        
        בדיקה גופנית: {physical_examination}""",
        
        # Social assessment template
        """הערכה סוציאלית
        
        {gender} בן {age_at_admission}
        {holocaust_survivor}
        
        מצב מגורים:
        גר {living_arrangement}
        קומה {floor_number}
        {elevator}
        
        תפקוד:
        {mobility}
        {eating_status}
        {bathing}""",
        
        # Short status template
        """{gender} {age_at_admission}
        {mobility}
        {physical_examination}
        FIM: {fim_score}"""
    ]

def create_bio_labels(tokens: List[str], value: str, field: str) -> List[str]:
    """Create BIO scheme labels for tokens."""
    labels = ["O"] * len(tokens)
    value_tokens = value.split()
    
    # Convert to lowercase for case-insensitive matching
    token_text = " ".join(tokens).lower()
    value_text = " ".join(value_tokens).lower()
    
    # Find all occurrences
    start_idx = 0
    while True:
        try:
            pos = token_text.index(value_text, start_idx)
            token_start = len(token_text[:pos].split())
            
            if token_start < len(tokens):
                labels[token_start] = f"B-{field}"
                for i in range(token_start + 1, min(token_start + len(value_tokens), len(tokens))):
                    labels[i] = f"I-{field}"
            
            start_idx = pos + 1
        except ValueError:
            break
    
    return labels

def create_training_examples(min_examples: int = 10) -> List[Dict[str, Any]]:
    """Generate diverse training examples."""
    examples = []
    realistic_values = create_realistic_values()
    document_templates = create_medical_document_templates()
    
    # Generate examples from medical document templates
    for template in document_templates:
        for _ in range(50):  # Generate 50 examples per template
            # Fill in random values
            field_values = {}
            for field, values in realistic_values.items():
                if f"{{{field}}}" in template:
                    field_values[field] = random.choice(values)
            
            try:
                # Create text and find entities
                text = template.format(**field_values)
                tokens = text.split()
                labels = ["O"] * len(tokens)
                
                # Label entities
                for field, value in field_values.items():
                    tmp_labels = create_bio_labels(tokens, value, field)
                    # Merge labels, preferring B/I over O
                    for i, label in enumerate(tmp_labels):
                        if label != "O":
                            labels[i] = label
                
                examples.append({
                    "tokens": tokens,
                    "labels": labels,
                    "text": text
                })
                
            except Exception as e:
                print(f"Error generating example: {e}")
                continue
    
    # Add variations with different date formats
    date_fields = ['admission_date', 'discharge_date']
    for field in date_fields:
        for _ in range(30):
            date = datetime.datetime.now() + datetime.timedelta(days=random.randint(-30, 30))
            date_formats = ['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d']
            for date_format in date_formats:
                date_str = date.strftime(date_format)
                text = f"תאריך {field.replace('_date', '')}: {date_str}"
                tokens = text.split()
                labels = create_bio_labels(tokens, date_str, field)
                examples.append({
                    "tokens": tokens,
                    "labels": labels,
                    "text": text
                })
    
    # Ensure minimum number of examples
    while len(examples) < min_examples:
        examples.extend(random.sample(examples, min(len(examples), min_examples - len(examples))))
    
    print(f"Generated {len(examples)} training examples")
    
    # Print statistics
    field_counts = defaultdict(int)
    for example in examples:
        for label in example["labels"]:
            if label != "O":
                field = label.split("-")[1]
                field_counts[field] += 1
    
    print("\nField distribution in examples:")
    for field, count in sorted(field_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{field}: {count}")
    
    return examples[:min_examples]

def save_examples(examples: List[Dict[str, Any]], output_dir: str = "data"):
    """Save generated examples for inspection."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save full examples
    with open(os.path.join(output_dir, "training_examples.txt"), 'w', encoding='utf-8') as f:
        for i, example in enumerate(examples[:10], 1):  # Save first 10 examples
            f.write(f"\nExample {i}:\n")
            f.write(f"Text: {example['text']}\n")
            f.write("Entities:\n")
            for token, label in zip(example['tokens'], example['labels']):
                if label != "O":
                    f.write(f"  {token}: {label}\n")
            f.write("-" * 80 + "\n")
    
    print(f"Saved example inspection to {output_dir}/training_examples.txt")

if __name__ == "__main__":
    # Test data generation
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate training examples for NER')
    parser.add_argument('--min_examples', type=int, default=5000,
                    help='Minimum number of examples to generate')
    parser.add_argument('--output_dir', default='data',
                    help='Directory to save example inspections')
    
    args = parser.parse_args()
    
    try:
        # Generate examples
        print("Generating training examples...")
        examples = create_training_examples(min_examples=args.min_examples)
        
        # Save example inspections
        print("\nSaving example inspections...")
        save_examples(examples, args.output_dir)
        
        # Print some example statistics
        print("\nExample distributions:")
        field_lengths = defaultdict(list)
        for example in examples:
            current_entity = []
            current_field = None
            
            for token, label in zip(example['tokens'], example['labels']):
                if label.startswith('B-'):
                    if current_entity:
                        field_lengths[current_field].append(len(current_entity))
                    current_entity = [token]
                    current_field = label[2:]
                elif label.startswith('I-'):
                    current_entity.append(token)
                elif current_entity:
                    field_lengths[current_field].append(len(current_entity))
                    current_entity = []
                    current_field = None
            
            if current_entity:
                field_lengths[current_field].append(len(current_entity))
        
        print("\nEntity length statistics:")
        for field, lengths in field_lengths.items():
            if lengths:
                avg_length = sum(lengths) / len(lengths)
                max_length = max(lengths)
                min_length = min(lengths)
                print(f"{field}:")
                print(f"  Average tokens: {avg_length:.2f}")
                print(f"  Min tokens: {min_length}")
                print(f"  Max tokens: {max_length}")
                print(f"  Total instances: {len(lengths)}")
        
        print("\nExample text from first generated example:")
        print("-" * 80)
        print(examples[0]['text'])
        print("-" * 80)
        print("\nEntities in first example:")
        for token, label in zip(examples[0]['tokens'], examples[0]['labels']):
            if label != "O":
                print(f"{token}: {label}")
        
    except Exception as e:
        print(f"Error generating examples: {e}")
        raise