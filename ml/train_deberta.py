"""
Train DeBERTa v3 Base for 98-99% Accuracy
Optimized model for CPU training with excellent performance.
"""

import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os
from tqdm import tqdm

# Configuration for DeBERTa v3 Base (Optimal for CPU)
MODEL_NAME = 'microsoft/deberta-v3-base'
MAX_LEN = 128
BATCH_SIZE = 8  # Increased batch size for base model
ACCUMULATION_STEPS = 4  # Effective batch size = 8 * 4 = 32
EPOCHS = 3
LEARNING_RATE = 2e-5  # Standard LR for base model
DATA_PATH = 'ml/data/ultra_large_reviews.csv'
MODEL_SAVE_PATH = 'ml/models/deberta_sentiment'

class MessReviewDataset(Dataset):
    def __init__(self, reviews, targets, tokenizer, max_len):
        self.reviews = reviews
        self.targets = targets
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.reviews)

    def __getitem__(self, item):
        review = str(self.reviews[item])
        target = self.targets[item]

        encoding = self.tokenizer.encode_plus(
            review,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            return_attention_mask=True,
            return_tensors='pt',
            truncation=True
        )

        return {
            'review_text': review,
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'targets': torch.tensor(target, dtype=torch.long)
        }

def train_epoch(model, data_loader, loss_fn, optimizer, device, scheduler, n_examples):
    model = model.train()
    losses = []
    correct_predictions = 0
    
    optimizer.zero_grad()

    progress_bar = tqdm(data_loader, desc="Training", unit="batch")
    
    for i, d in enumerate(progress_bar):
        input_ids = d["input_ids"].to(device)
        attention_mask = d["attention_mask"].to(device)
        targets = d["targets"].to(device)

        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        logits = outputs.logits
        _, preds = torch.max(logits, dim=1)
        loss = loss_fn(logits, targets)
        
        # Normalize loss for gradient accumulation
        loss = loss / ACCUMULATION_STEPS
        losses.append(loss.item() * ACCUMULATION_STEPS)
        
        correct_predictions += torch.sum(preds == targets)

        loss.backward()
        
        if (i + 1) % ACCUMULATION_STEPS == 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()
        
        progress_bar.set_postfix({'loss': np.mean(losses)})

    return correct_predictions.double() / n_examples, np.mean(losses)

def eval_model(model, data_loader, loss_fn, device, n_examples):
    model = model.eval()
    losses = []
    correct_predictions = 0

    with torch.no_grad():
        for d in tqdm(data_loader, desc="Evaluating", unit="batch"):
            input_ids = d["input_ids"].to(device)
            attention_mask = d["attention_mask"].to(device)
            targets = d["targets"].to(device)

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )
            
            logits = outputs.logits
            _, preds = torch.max(logits, dim=1)
            loss = loss_fn(logits, targets)

            correct_predictions += torch.sum(preds == targets)
            losses.append(loss.item())

    return correct_predictions.double() / n_examples, np.mean(losses)

def main():
    print("=" * 70)
    print("🚀 TRAINING DeBERTa v3 LARGE FOR >99% ACCURACY")
    print("=" * 70)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    if device.type == 'cpu':
        print("⚠️  WARNING: Training DeBERTa Large on CPU is extremely intensive.")
        print("   Using Gradient Accumulation to manage memory.")

    # Load data
    print(f"\n📂 Loading data from {DATA_PATH}...")
    if not os.path.exists(DATA_PATH):
        print("❌ Data file not found!")
        return

    df = pd.read_csv(DATA_PATH)
    print(f"✓ Loaded {len(df)} reviews")
    
    df['sentiment_code'] = df['sentiment'].map({'bad': 0, 'good': 1})
    
    # Use subset for demonstration if needed, but user asked for full training
    # df = df.sample(n=20000) # Uncomment to speed up testing
    
    df_train, df_test = train_test_split(df, test_size=0.1, random_state=42)
    df_val, df_test = train_test_split(df_test, test_size=0.5, random_state=42)
    
    print(f"  - Training: {len(df_train)}")
    print(f"  - Validation: {len(df_val)}")
    print(f"  - Test: {len(df_test)}")

    # Tokenizer
    print("\n🔧 Initializing DeBERTa tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    train_dataset = MessReviewDataset(
        reviews=df_train.review.to_numpy(),
        targets=df_train.sentiment_code.to_numpy(),
        tokenizer=tokenizer,
        max_len=MAX_LEN
    )
    
    val_dataset = MessReviewDataset(
        reviews=df_val.review.to_numpy(),
        targets=df_val.sentiment_code.to_numpy(),
        tokenizer=tokenizer,
        max_len=MAX_LEN
    )
    
    test_dataset = MessReviewDataset(
        reviews=df_test.review.to_numpy(),
        targets=df_test.sentiment_code.to_numpy(),
        tokenizer=tokenizer,
        max_len=MAX_LEN
    )

    train_data_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_data_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)
    test_data_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

    # Model
    print("\n🤖 Initializing DeBERTa v3 Large model...")
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=2
    )
    model = model.to(device)

    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
    total_steps = len(train_data_loader) * EPOCHS // ACCUMULATION_STEPS
    
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(total_steps * 0.1), # 10% warmup
        num_training_steps=total_steps
    )

    loss_fn = torch.nn.CrossEntropyLoss().to(device)

    print("\n🏋️ Starting training...")
    best_accuracy = 0

    for epoch in range(EPOCHS):
        print(f"\nEpoch {epoch + 1}/{EPOCHS}")
        print("-" * 10)

        train_acc, train_loss = train_epoch(
            model,
            train_data_loader,
            loss_fn,
            optimizer,
            device,
            scheduler,
            len(df_train)
        )

        print(f"Train loss {train_loss:.4f} accuracy {train_acc:.4f}")

        val_acc, val_loss = eval_model(
            model,
            val_data_loader,
            loss_fn,
            device,
            len(df_val)
        )

        print(f"Val   loss {val_loss:.4f} accuracy {val_acc:.4f}")

        if val_acc > best_accuracy:
            os.makedirs(MODEL_SAVE_PATH, exist_ok=True)
            print(f"💾 Saving improved model to {MODEL_SAVE_PATH}...")
            model.save_pretrained(MODEL_SAVE_PATH)
            tokenizer.save_pretrained(MODEL_SAVE_PATH)
            best_accuracy = val_acc
            
            if best_accuracy > 0.99:
                print("🏆 99% ACCURACY ACHIEVED! Stopping early.")
                break

    print("\n" + "=" * 70)
    print("📈 Final Evaluation")
    print("=" * 70)
    
    test_acc, _ = eval_model(
        model,
        test_data_loader,
        loss_fn,
        device,
        len(df_test)
    )
    
    print(f"🎯 Final Test Accuracy: {test_acc.item():.4f} ({test_acc.item()*100:.2f}%)")

if __name__ == "__main__":
    main()
