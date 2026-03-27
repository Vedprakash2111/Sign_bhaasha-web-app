"""
Retrain Model with Real Gesture Data
This script retrains the CNN model using real hand gesture images
captured from actual users (as opposed to synthetic data).
"""

import numpy as np
import cv2
import os
from pathlib import Path
import tensorflow
from tensorflow import keras
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# =============================================
# CONFIGURATION
# =============================================
IMG_SIZE = 64
NUM_CLASSES = 26  # A-Z
BATCH_SIZE = 32
EPOCHS = 150
VALIDATION_SPLIT = 0.2
REAL_DATA_DIR = "training_data/raw_gestures"
SYNTHETIC_DATA_DIR = "training_data/synthetic"  # Optional: for augmentation

class_names = [chr(65 + i) for i in range(NUM_CLASSES)]  # A-Z

print(f"Classes: {class_names}")

# =============================================
# LOAD REAL GESTURE DATA
# =============================================
def load_real_gestures(data_dir=REAL_DATA_DIR):
    """
    Load real hand gesture images from captured data.
    """
    print(f"\n[INFO] Loading real gesture data from {data_dir}...")
    
    X_data = []
    y_data = []
    
    for class_idx, gesture_letter in enumerate(class_names):
        gesture_dir = os.path.join(data_dir, gesture_letter)
        
        if not os.path.exists(gesture_dir):
            print(f"  ⚠ {gesture_letter}: No data found")
            continue
        
        # Load all images for this gesture
        image_files = [f for f in os.listdir(gesture_dir) if f.endswith('.jpg')]
        
        for img_file in image_files:
            img_path = os.path.join(gesture_dir, img_file)
            
            try:
                # Read image
                img = cv2.imread(img_path)
                
                if img is None:
                    continue
                
                # Convert BGR to RGB for display (optional)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Resize to IMG_SIZE
                img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
                
                # Normalize to [0, 1]
                img = img.astype(np.float32) / 255.0
                
                X_data.append(img)
                y_data.append(class_idx)
            
            except Exception as e:
                print(f"  [ERROR] Failed to load {img_file}: {str(e)}")
                continue
        
        print(f"  ✓ {gesture_letter}: {len(image_files)} samples")
    
    X_data = np.array(X_data, dtype=np.float32)
    y_data = np.array(y_data)
    
    print(f"\n[SUCCESS] Loaded {len(X_data)} real gesture samples")
    print(f"Data shape: {X_data.shape}, Labels shape: {y_data.shape}")
    
    return X_data, y_data

# =============================================
# DATA AUGMENTATION
# =============================================
def augment_data(X, y):
    """
    Augment real gesture data with geometric transformations.
    This helps the model generalize better.
    """
    print("\n[INFO] Augmenting data with geometric transformations...")
    
    X_augmented = [X]  # Start with original
    y_augmented = [y]
    
    # Horizontal flip (mirrors the gesture)
    X_flipped = np.array([cv2.flip(img, 1) for img in X])
    X_augmented.append(X_flipped)
    y_augmented.append(y)
    print("  ✓ Added horizontal flips")
    
    # Slight rotation (±10 degrees)
    X_rotated = []
    for img in X:
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        angle = np.random.uniform(-10, 10)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h))
        X_rotated.append(rotated)
    X_augmented.append(np.array(X_rotated))
    y_augmented.append(y)
    print("  ✓ Added rotations (±10°)")
    
    # Slight brightness adjustment
    X_bright = []
    for img in X:
        brightness_delta = np.random.uniform(-0.2, 0.2)
        brightened = np.clip(img + brightness_delta, 0.0, 1.0)
        X_bright.append(brightened)
    X_augmented.append(np.array(X_bright))
    y_augmented.append(y)
    print("  ✓ Added brightness adjustments")
    
    # Concatenate all
    X_final = np.concatenate(X_augmented, axis=0)
    y_final = np.concatenate(y_augmented, axis=0)
    
    print(f"[SUCCESS] Augmented dataset size: {len(X_final)}")
    
    return X_final, y_final

# =============================================
# BUILD IMPROVED CNN MODEL
# =============================================
def create_model():
    """
    Create an improved CNN model with better architecture for real data.
    """
    print("\n[INFO] Building improved CNN model...")
    
    model = models.Sequential([
        # Block 1
        layers.Conv2D(32, (3, 3), activation='relu', padding='same', 
                     input_shape=(IMG_SIZE, IMG_SIZE, 3)),
        layers.BatchNormalization(),
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Block 2
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Block 3
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Flatten and Dense layers
        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        
        # Output layer
        layers.Dense(NUM_CLASSES, activation='softmax')
    ])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("[SUCCESS] Model created successfully!")
    model.summary()
    
    return model

# =============================================
# TRAIN MODEL
# =============================================
def train_model(model, X_train, y_train):
    """
    Train the model on real gesture data.
    """
    print("\n[INFO] Training model on real gesture data...")
    
    # Split data
    X_train_split, X_val, y_train_split, y_val = train_test_split(
        X_train, y_train,
        test_size=VALIDATION_SPLIT,
        random_state=42,
        stratify=y_train
    )
    
    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=8,
            min_lr=0.00001,
            verbose=1
        )
    ]
    
    # Train
    history = model.fit(
        X_train_split, y_train_split,
        validation_data=(X_val, y_val),
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        callbacks=callbacks,
        verbose=1
    )
    
    print("[SUCCESS] Training completed!")
    
    # Print accuracy
    _, train_acc = model.evaluate(X_train_split, y_train_split, verbose=0)
    _, val_acc = model.evaluate(X_val, y_val, verbose=0)
    print(f"\nFinal Metrics:")
    print(f"  Train Accuracy: {train_acc * 100:.2f}%")
    print(f"  Validation Accuracy: {val_acc * 100:.2f}%")
    
    return history

# =============================================
# SAVE MODEL
# =============================================
def save_model(model, model_path='models/sign_language_model_real.h5'):
    """
    Save the trained model.
    """
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save(model_path)
    print(f"\n[SUCCESS] Model saved to {model_path}")

# =============================================
# PLOT TRAINING HISTORY
# =============================================
def plot_history(history, save_path='models/training_history_real.png'):
    """
    Plot training graphs.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 4))
    
    # Accuracy
    axes[0].plot(history.history['accuracy'], label='Train Accuracy')
    axes[0].plot(history.history['val_accuracy'], label='Val Accuracy')
    axes[0].set_title('Model Accuracy (Real Data)')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Accuracy')
    axes[0].legend()
    axes[0].grid(True)
    
    # Loss
    axes[1].plot(history.history['loss'], label='Train Loss')
    axes[1].plot(history.history['val_loss'], label='Val Loss')
    axes[1].set_title('Model Loss (Real Data)')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Loss')
    axes[1].legend()
    axes[1].grid(True)
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    print(f"[SUCCESS] Training history saved to {save_path}")
    plt.show()

# =============================================
# MAIN
# =============================================
if __name__ == "__main__":
    print("=" * 60)
    print("SIGN LANGUAGE - RETRAIN WITH REAL GESTURE DATA")
    print("=" * 60)
    
    # Load real data
    X_real, y_real = load_real_gestures()
    
    if len(X_real) == 0:
        print("\n[ERROR] No real gesture data found!")
        print("Please run 'python capture_gestures.py' first.")
        exit(1)
    
    # Augment data
    X_augmented, y_augmented = augment_data(X_real, y_real)
    
    # Build model
    model = create_model()
    
    # Train model
    history = train_model(model, X_augmented, y_augmented)
    
    # Save model
    save_model(model, 'models/sign_language_model.h5')  # Overwrite original
    
    # Plot history
    plot_history(history)
    
    print("\n" + "=" * 60)
    print("✓ RETRAINING COMPLETE!")
    print("=" * 60)
    print("\nYour model has been updated with real gesture data!")
    print("Restart the Flask app to use the new model:")
    print("  1. Close current Flask app (Ctrl+C)")
    print("  2. Run: python app.py")
    print("  3. Open: http://localhost:5000")
