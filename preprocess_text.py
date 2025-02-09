import re
import torch
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from transformers import PreTrainedTokenizer
import logging
from datetime import datetime

@dataclass
class TokenMapping:
    pattern: str
    replacement: str
    priority: int = 0

class HebrewMedicalPreprocessor:
    def __init__(self):
        # Token patterns for specific entities
        self.entity_patterns = {
            'diagnosis': [
                TokenMapping(r'איסכמי', '[DIAG]ISCHEMIC[/DIAG]', 2),
                TokenMapping(r'המיספרה', '[DIAG]HEMISPHERE[/DIAG]', 2),
                TokenMapping(r'סוכרת', '[DIAG]DIABETES[/DIAG]', 2),
                TokenMapping(r'יתר לחץ דם', '[DIAG]HYPERTENSION[/DIAG]', 3)
            ],
            'section': [
                TokenMapping(r'אבחנות(?:\s*עיקריות)?:', '[SECTION]DIAGNOSES[/SECTION]', 3),
                TokenMapping(r'טיפול תרופתי:', '[SECTION]MEDICATIONS[/SECTION]', 3),
                TokenMapping(r'המלצות(?:\s*בשחרור)?:', '[SECTION]RECOMMENDATIONS[/SECTION]', 3),
                TokenMapping(r'סיכום ותוכנית:', '[SECTION]SUMMARY[/SECTION]', 3)
            ],
            'treatment': [
                TokenMapping(r'פיזיותרפיה', '[TREATMENT]PHYSIO[/TREATMENT]', 2),
                TokenMapping(r'שיקום', '[TREATMENT]REHAB[/TREATMENT]', 2),
                TokenMapping(r'ריפוי בעיסוק', '[TREATMENT]OCCUPATIONAL[/TREATMENT]', 2)
            ],
            'score': [
                TokenMapping(r'FIM(?:\s*סה"כ)?:?\s*(\d+)(?:/126)?', r'[SCORE]FIM_\1/126[/SCORE]', 4),
                TokenMapping(r'MMSE:?\s*(\d+)(?:/30)?', r'[SCORE]MMSE_\1/30[/SCORE]', 4)
            ],
            'status': [
                TokenMapping(r'עצמאי', '[STATUS]INDEPENDENT[/STATUS]', 1),
                TokenMapping(r'חלקי', '[STATUS]PARTIAL[/STATUS]', 1),
                TokenMapping(r'תקין', '[STATUS]NORMAL[/STATUS]', 1),
                TokenMapping(r'לקוי', '[STATUS]IMPAIRED[/STATUS]', 1)
            ],
            'field': [
                TokenMapping(r'תאריך קבלה:?\s*(\d{1,2}/\d{1,2}/\d{4})', r'[DATE]ADMISSION_\1[/DATE]', 3),
                TokenMapping(r'תאריך שחרור:?\s*(\d{1,2}/\d{1,2}/\d{4})', r'[DATE]DISCHARGE_\1[/DATE]', 3),
                TokenMapping(r'תאריך לידה:?\s*(\d{1,2}/\d{1,2}/\d{4})', r'[DATE]BIRTH_\1[/DATE]', 3),
                TokenMapping(r'ת\.?ז\.?:?\s*(\d{9})', r'[ID]\1[/ID]', 3)
            ]
        }

        # Special case patterns that need to be processed first
        self.special_patterns = {
            'fim_details': TokenMapping(
                r'(\d+)\s*/\s*7(?:\s*,\s*)?(\d+)\s*/\s*7',
                r'[SCORE]FIM_ITEM_\1_\2[/SCORE]',
                5
            ),
            'dates': TokenMapping(
                r'(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{4})',
                r'\1/\2/\3',
                5
            )
        }

    def preprocess(self, text: str) -> str:
        """
        Main preprocessing function.
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text
        """
        if not text:
            return ""

        # Initial cleaning
        text = self._basic_clean(text)
        
        # Process special patterns first
        for pattern in sorted(self.special_patterns.values(), key=lambda x: -x.priority):
            text = re.sub(pattern.pattern, pattern.replacement, text)

        # Process entity patterns by priority
        all_patterns = []
        for patterns in self.entity_patterns.values():
            all_patterns.extend(patterns)
            
        for pattern in sorted(all_patterns, key=lambda x: -x.priority):
            text = re.sub(pattern.pattern, pattern.replacement, text)

        # Normalize spaces and final cleanup
        return self._final_clean(text)

    def _basic_clean(self, text: str) -> str:
        """Basic text cleaning."""
        # Remove diacritics
        text = re.sub(r'[\u0591-\u05C7]', '', text)
        
        # Fix common OCR errors
        text = re.sub(r'["""״׳]', '"', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s*([:.,-])\s*', r' \1 ', text)
        
        # Normalize multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def _final_clean(self, text: str) -> str:
        """Final cleanup after processing."""
        # Clean up spaces around special tokens
        text = re.sub(r'\s*\[', ' [', text)
        text = re.sub(r'\]\s*', '] ', text)
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Clean up spaces around punctuation
        text = re.sub(r'\s*([:.,-])\s*', r'\1 ', text)
        
        return text.strip()

def prepare_text_for_model(text: str, tokenizer) -> Tuple[Dict[str, torch.Tensor], torch.Tensor]:
    """
    Prepare text for model with improved tokenization.
    
    Args:
        text: Input text
        tokenizer: Tokenizer instance
        
    Returns:
        Tuple of (model inputs, offset mapping)
    """
    # Create preprocessor
    preprocessor = HebrewMedicalPreprocessor()
    
    # Preprocess text
    processed_text = preprocessor.preprocess(text)
    
    # Tokenize
    inputs = tokenizer(
        processed_text,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt",
        return_offsets_mapping=True,
        add_special_tokens=True
    )
    
    # Extract offset mapping
    offset_mapping = inputs.pop('offset_mapping')
    
    return inputs, offset_mapping