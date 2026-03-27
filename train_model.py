"""
Sign Language Recognition Model Training Script
This script trains a CNN model to recognize hand gestures (A-Z)
Uses TensorFlow/Keras with a simple yet effective architecture
"""

import numpy as np
import tensorflow
from tensorflow import keras
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
import os
import cv2
import matplotlib.pyplot as plt
from pathlib import Path

# =============================================
# 1. CONFIGURATION
# =============================================
IMG_SIZE = 64
NUM_CLASSES = 26  # A-Z
BATCH_SIZE = 32
EPOCHS = 200
VALIDATION_SPLIT = 0.2

class_names = [chr(65 + i) for i in range(NUM_CLASSES)]  # A-Z

print(f"Classes: {class_names}")

# =============================================
# 2. CREATE SYNTHETIC TRAINING DATA
# =============================================
def create_synthetic_data(num_samples_per_class=100):
    """
    Create synthetic training data with random hand-like patterns.
    In production, collect real hand gesture images.
    """
    print("\n[INFO] Creating synthetic training data...")
    
    X_train = []
    y_train = []
    
    for class_idx in range(NUM_CLASSES):
        print(f"Generating samples for class {class_names[class_idx]} ({class_idx + 1}/{NUM_CLASSES})")
        
        for sample in range(num_samples_per_class):
            # Create random hand-like pattern
            img = np.zeros((IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8)
            
            # Add random shapes to simulate hand features
            num_shapes = np.random.randint(5, 15)
            
            for _ in range(num_shapes):
                x = np.random.randint(0, IMG_SIZE)
                y = np.random.randint(0, IMG_SIZE)
                radius = np.random.randint(3, 15)
                
                # Add some color variation (skin-like tones)
                color = (
                    np.random.randint(150, 220),  # B
                    np.random.randint(100, 170),  # G
                    np.random.randint(100, 170)   # R
                )
                
                cv2.circle(img, (x, y), radius, color, -1)
            
            # Add some noise to make it more realistic
            noise = np.random.normal(0, 5, (IMG_SIZE, IMG_SIZE, 3))
            img = np.clip(img.astype(float) + noise, 0, 255).astype(np.uint8)
            
            X_train.append(img)
            y_train.append(class_idx)
    
    X_train = np.array(X_train, dtype=np.float32) / 255.0
    y_train = np.array(y_train)
    
    print(f"[SUCCESS] Created {len(X_train)} training samples")
    print(f"Data shape: {X_train.shape}, Labels shape: {y_train.shape}")
    
    return X_train, y_train

# =============================================
# 3. BUILD CNN MODEL
# =============================================
def create_model():
    """
    Create a CNN model for hand gesture classification.
    Architecture: Conv2D -> MaxPool -> Conv2D -> MaxPool -> Dense -> Dropout -> Dense
    """
    print("\n[INFO] Building CNN model...")
    
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
        optimizer=keras.optimizers.Adam(learning_rate=0.002),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("[SUCCESS] Model created successfully!")
    model.summary()
    
    return model

# =============================================
# 4. TRAIN MODEL
# =============================================
def train_model(model, X_train, y_train):
    """
    Train the CNN model.
    """
    print("\n[INFO] Training model...")
    
    # Split data into train and validation
    X_train_split, X_val, y_train_split, y_val = train_test_split(
        X_train, y_train, 
        test_size=VALIDATION_SPLIT, 
        random_state=42,
        stratify=y_train
    )
    
    # Define callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
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
    
    return history

# =============================================
# 5. SAVE MODEL
# =============================================
def save_model(model, model_path='models/sign_language_model.h5'):
    """
    Save the trained model.
    """
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save(model_path)
    print(f"\n[SUCCESS] Model saved to {model_path}")

# =============================================
# 6. PLOT TRAINING HISTORY
# =============================================
def plot_history(history, save_path='models/training_history.png'):
    """
    Plot training and validation metrics.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 4))
    
    # Accuracy
    axes[0].plot(history.history['accuracy'], label='Train Accuracy')
    axes[0].plot(history.history['val_accuracy'], label='Val Accuracy')
    axes[0].set_title('Model Accuracy')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Accuracy')
    axes[0].legend()
    axes[0].grid(True)
    
    # Loss
    axes[1].plot(history.history['loss'], label='Train Loss')
    axes[1].plot(history.history['val_loss'], label='Val Loss')
    axes[1].set_title('Model Loss')
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
# 7. MAIN EXECUTION
# =============================================
if __name__ == "__main__":
    print("=" * 60)
    print("SIGN LANGUAGE RECOGNITION - MODEL TRAINING")
    print("=" * 60)
    
    # Create synthetic data
    X_train, y_train = create_synthetic_data(num_samples_per_class=500)
    
    # Build model
    model = create_model()
    
    # Train model
    history = train_model(model, X_train, y_train)
    
    # Save model
    save_model(model)
    
    # Plot history
    plot_history(history)
    
    print("\n" + "=" * 60)
    print("✓ TRAINING COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: python train_model.py (this creates the model)")
    print("2. Run: python app.py (to start the Flask app)")
    print("3. Open: http://localhost:5000 in your browser")
