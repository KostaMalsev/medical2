import os
import json
import torch
import logging
from transformers import (
    AutoTokenizer, 
    AutoModelForTokenClassification, 
    Trainer, 
    TrainingArguments,
    DataCollatorForTokenClassification
)
from datasets import Dataset
import numpy as np
from typing import Dict, List, Any
import seqeval.metrics as seqeval
from data_generator import create_training_examples, load_parameters
from collections import defaultdict

def setup_logging(output_dir: str = "../hebrew-medical-ner"):
    """Setup logging configuration."""
    os.makedirs(output_dir, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(output_dir, 'training.log')),
            logging.StreamHandler()
        ]
    )

def get_labels(params_df):
    """Generate BIO scheme labels from parameter fields."""
    id2label = {0: "O"}
    label_id = 1
    for field in params_df['Field'].unique():
        id2label[label_id] = f"B-{field}"
        id2label[label_id + 1] = f"I-{field}"
        label_id += 2
    return id2label

def encode_dataset(examples: List[Dict[str, Any]], tokenizer, label2id: Dict[str, int]) -> Dataset:
    """Encode dataset with improved subword token handling."""
    features = {
        'input_ids': [],
        'attention_mask': [],
        'labels': []
    }
    
    max_length = 256
    
    for example in examples:
        # Tokenize without creating tensors yet
        encoding = tokenizer(
            example["text"],
            truncation=True,
            padding='max_length',
            max_length=max_length,
            return_tensors=None
        )
        
        # Initialize label ids
        label_ids = [-100] * max_length
        word_ids = tokenizer(example["text"], return_tensors=None).word_ids()
        
        # Previous word id for tracking subwords
        previous_word_id = None
        
        # Align labels with tokenized words
        for idx, word_id in enumerate(word_ids):
            if word_id is None:
                continue
                
            if word_id != previous_word_id:
                # First token of a word
                if word_id < len(example["labels"]):
                    label = example["labels"][word_id]
                    label_ids[idx] = label2id.get(label, 0)
            else:
                # Continuation subword token
                if word_id < len(example["labels"]):
                    label = example["labels"][word_id]
                    if label.startswith("B-"):
                        label = "I-" + label[2:]  # Convert B- to I- for continuation
                    label_ids[idx] = label2id.get(label, 0)
            
            previous_word_id = word_id
        
        features['input_ids'].append(encoding['input_ids'])
        features['attention_mask'].append(encoding['attention_mask'])
        features['labels'].append(label_ids)
    
    return Dataset.from_dict(features)

def compute_metrics(id2label, label2id):
   def compute(eval_pred) -> Dict[str, float]:
       """
       Compute NER evaluation metrics using seqeval.
       Args:
           eval_pred: Tuple of predictions and labels from trainer
       Returns:
           Dictionary containing metrics
       """
       predictions, labels = eval_pred
       predictions = np.argmax(predictions, axis=2)

       # Remove ignored index (special tokens) and convert to string labels
       true_predictions = []
       true_labels = []
       
       for prediction, label in zip(predictions, labels):
           pred_list = []
           label_list = []
           
           for p, l in zip(prediction, label):
               if l != -100:  # Ignore special tokens
                   pred_list.append(id2label[p])
                   label_list.append(id2label[l])
                   
           true_predictions.append(pred_list)
           true_labels.append(label_list)

       # Calculate main metrics
       results = {
           "accuracy": seqeval.accuracy_score(true_labels, true_predictions),
           "precision": seqeval.precision_score(true_labels, true_predictions),
           "recall": seqeval.recall_score(true_labels, true_predictions),
           "f1": seqeval.f1_score(true_labels, true_predictions)
       }

       # Calculate per-entity metrics
       per_entity_metrics = {}
       
       # Get unique entity types (removing B- and I- prefixes)
       entity_types = set()
       for label in label2id.keys():
           if label != "O":
               entity_types.add(label.split("-")[1])
       
       # Calculate metrics for each entity type
       for entity in entity_types:
           entity_preds = [[label if label.endswith(entity) else "O" for label in seq] 
                         for seq in true_predictions]
           entity_labels = [[label if label.endswith(entity) else "O" for label in seq]
                          for seq in true_labels]
           
           per_entity_metrics[entity] = {
               "precision": seqeval.precision_score(entity_labels, entity_preds),
               "recall": seqeval.recall_score(entity_labels, entity_preds),
               "f1": seqeval.f1_score(entity_labels, entity_preds)
           }

       results["per_entity"] = per_entity_metrics
       return results

   return compute

def train(
    output_dir: str = "../hebrew-medical-ner",
    num_train_epochs: int = 5,
    batch_size: int = 16,
    learning_rate: float = 5e-5,
    weight_decay: float = 0.01,
    warmup_ratio: float = 0.1,
    save_steps: int = 1000,
    eval_steps: int = 1000,
    min_examples: int = 1000, #5000
    max_examples: int = 1000
) -> None:
    """Train the NER model."""
    # Setup logging
    setup_logging(output_dir)
    logging.info(f"Starting training with output_dir: {output_dir}")
    
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Load and prepare data
        params_df = load_parameters()
        id2label = get_labels(params_df)
        label2id = {v: k for k, v in id2label.items()}
        
        # Initialize tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained("onlplab/alephbert-base")
        model = AutoModelForTokenClassification.from_pretrained(
            "onlplab/alephbert-base",
            num_labels=len(id2label),
            id2label=id2label,
            label2id=label2id
        )
        
        # Generate and encode dataset
        logging.info("Generating training examples...")
        examples = create_training_examples(min_examples=min_examples)[:max_examples]
        
        logging.info("Encoding dataset...")
        dataset = encode_dataset(examples, tokenizer, label2id)
        
        # Split dataset
        dataset = dataset.train_test_split(test_size=0.2)
        logging.info(f"Train size: {len(dataset['train'])}, Test size: {len(dataset['test'])}")
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_train_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            weight_decay=weight_decay,
            warmup_ratio=warmup_ratio,
            evaluation_strategy="steps",
            save_strategy="steps",
            save_steps=save_steps,
            eval_steps=eval_steps,
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            save_total_limit=2,
            logging_dir=os.path.join(output_dir, "logs"),
            logging_steps=100,
            report_to=["none"],
            fp16=False
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=dataset['train'],
            eval_dataset=dataset['test'],
            tokenizer=tokenizer,
            compute_metrics=compute_metrics(id2label, label2id),
            data_collator=DataCollatorForTokenClassification(
                tokenizer,
                pad_to_multiple_of=8
            )
        )
        
        # Train model
        logging.info("Starting training...")
        trainer.train()
        
        # Final evaluation
        logging.info("Performing final evaluation...")
        eval_results = trainer.evaluate()
        
        # Save final model and tokenizer
        final_output_dir = os.path.join(output_dir, "final")
        os.makedirs(final_output_dir, exist_ok=True)
        
        model.save_pretrained(final_output_dir)
        tokenizer.save_pretrained(final_output_dir)
        
        # Save training results and configuration
        config = {
            'id2label': id2label,
            'label2id': label2id,
            'model_name': "hebrew-medical-ner",
            'base_model': "onlplab/alephbert-base",
            'training_params': {
                'epochs': num_train_epochs,
                'batch_size': batch_size,
                'learning_rate': learning_rate,
                'weight_decay': weight_decay,
                'warmup_ratio': warmup_ratio,
                'min_examples': min_examples
            },
            'eval_results': eval_results
        }
        
        with open(os.path.join(final_output_dir, "training_config.json"), 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Training complete! Model saved to {final_output_dir}")
        logging.info(f"Final evaluation results: {eval_results}")
        
    except Exception as e:
        logging.error(f"Error during training: {e}", exc_info=True)
        raise

def main():
    """Main function to run the training pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Hebrew Medical NER model')
    parser.add_argument('--output_dir', default='../hebrew-medical-ner', 
                       help='Output directory for model')
    parser.add_argument('--epochs', type=int, default=5, 
                       help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=16, 
                       help='Batch size')
    parser.add_argument('--learning_rate', type=float, default=5e-5, 
                       help='Learning rate')
    parser.add_argument('--min_examples', type=int, default=5000, 
                       help='Minimum number of training examples')
    
    args = parser.parse_args()
    
    try:
        train(
            output_dir=args.output_dir,
            num_train_epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            min_examples=args.min_examples
        )
    except Exception as e:
        logging.error(f"Training failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()