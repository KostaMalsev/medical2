import json
from typing import Dict, List, Any
from collections import defaultdict

def load_ground_truth() -> Dict[str, List[Dict[str, str]]]:
    """Load ground truth annotations."""
    return {
        "discharge_letter_1": [
            {"label": "admission_date", "text": "01/01/2025"},
            {"label": "discharge_date", "text": "05/02/2025"},
            {"label": "fim_score", "text": "4/7"},
            {"label": "fim_score", "text": "6/7"},
            {"label": "diagnoses", "text": "CVA איסכמי"},
            {"label": "diagnoses", "text": "יתר לחץ דם"},
            {"label": "diagnoses", "text": "סוכרת"}
        ],
        "discharge_letter_2": [
            {"label": "fim_score", "text": "60/126"},
            {"label": "fim_score", "text": "88/126"},
            {"label": "mobility", "text": "הליכה עם הליכון"}
        ],
        "sample_form": [
            {"label": "gender", "text": "מר"},
            {"label": "age_at_admission", "text": "75"},
            {"label": "admission_date", "text": "01.02.2025"},
            {"label": "holocaust_survivor", "text": "מוכר כניצול שואה"},
            {"label": "living_arrangement", "text": "בן זוג"},
            {"label": "floor_number", "text": "2"},
            {"label": "elevator", "text": "עם מעלית"},
            {"label": "ecg", "text": "קצב סינוס"},
            {"label": "mmse_score", "text": "29/30"},
            {"label": "fim_score", "text": "5"},
            {"label": "diagnoses", "text": "CVA"},
            {"label": "diagnoses", "text": "Diabetes Mellitus"},
            {"label": "diagnoses", "text": "COPD"}
        ]
    }

def evaluate_predictions(predictions: List[Dict[str, Any]], ground_truth: Dict[str, List[Dict[str, str]]]):
    """Evaluate model predictions against ground truth."""
    results = {
        "total_gt": 0,
        "total_pred": 0,
        "correct": 0,
        "incorrect": 0,
        "missed": 0,
        "by_entity": defaultdict(lambda: {"correct": 0, "incorrect": 0, "missed": 0, "total_gt": 0})
    }
    
    # Count ground truth totals
    for doc_entities in ground_truth.values():
        results["total_gt"] += len(doc_entities)
        for entity in doc_entities:
            results["by_entity"][entity["label"]]["total_gt"] += 1
    
    # Count predictions
    results["total_pred"] = sum(len(pred["entities"]) for pred in predictions)
    
    # Match predictions to ground truth
    for doc_id, doc_gt in ground_truth.items():
        doc_pred = predictions[int(doc_id.split("_")[-1]) - 1]["entities"]
        
        # Convert to sets for easier matching
        gt_set = {(e["label"], e["text"]) for e in doc_gt}
        pred_set = {(e["label"], e["text"]) for e in doc_pred}
        
        # Find matches and mismatches
        correct = gt_set & pred_set
        missed = gt_set - pred_set
        incorrect = pred_set - gt_set
        
        # Update overall stats
        results["correct"] += len(correct)
        results["incorrect"] += len(incorrect)
        results["missed"] += len(missed)
        
        # Update per-entity stats
        for label, text in correct:
            results["by_entity"][label]["correct"] += 1
        for label, text in incorrect:
            results["by_entity"][label]["incorrect"] += 1
        for label, text in missed:
            results["by_entity"][label]["missed"] += 1
    
    # Calculate metrics
    if results["total_pred"] > 0:
        precision = results["correct"] / results["total_pred"]
    else:
        precision = 0
        
    if results["total_gt"] > 0:
        recall = results["correct"] / results["total_gt"]
    else:
        recall = 0
        
    if precision + recall > 0:
        f1 = 2 * (precision * recall) / (precision + recall)
    else:
        f1 = 0
    
    print("\nOverall Metrics:")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"Correct: {results['correct']}")
    print(f"Incorrect: {results['incorrect']}")
    print(f"Missed: {results['missed']}")
    
    print("\nPer-Entity Metrics:")
    for entity, stats in sorted(results["by_entity"].items()):
        if stats["total_gt"] > 0:
            entity_precision = stats["correct"] / (stats["correct"] + stats["incorrect"])
            entity_recall = stats["correct"] / stats["total_gt"]
            if entity_precision + entity_recall > 0:
                entity_f1 = 2 * (entity_precision * entity_recall) / (entity_precision + entity_recall)
            else:
                entity_f1 = 0
                
            print(f"\n{entity}:")
            print(f"  Precision: {entity_precision:.4f}")
            print(f"  Recall: {entity_recall:.4f}")
            print(f"  F1 Score: {entity_f1:.4f}")
            print(f"  Correct/Total: {stats['correct']}/{stats['total_gt']}")

def main():
    # Load predictions
    with open('test_results.json', 'r', encoding='utf-8') as f:
        predictions = json.load(f)
    
    # Load ground truth
    ground_truth = load_ground_truth()
    
    # Evaluate predictions
    evaluate_predictions(predictions, ground_truth)

if __name__ == "__main__":
    main()