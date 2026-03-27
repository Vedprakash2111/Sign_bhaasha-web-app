"""
Prediction utilities for Sign Language Recognition
Handles model loading, image preprocessing, and prediction
Includes MediaPipe hand detection for better accuracy
"""

import numpy as np
import cv2
import tensorflow as tf
from pathlib import Path
import os

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("[WARNING] MediaPipe not installed. Install with: pip install mediapipe")

# =============================================
# CONFIGURATION
# =============================================
IMG_SIZE = 64
NUM_CLASSES = 26
CLASS_NAMES = [chr(65 + i) for i in range(NUM_CLASSES)]  # A-Z
CONFIDENCE_THRESHOLD = 0.5

# =============================================
# MODEL LOADER
# =============================================
class SignLanguagePredictor:
    """
    Main predictor class for sign language recognition.
    Handles model loading, preprocessing, and predictions.
    """
    
    def __init__(self, model_path='models/sign_language_model.h5', verbose=False):
        """
        Initialize the predictor with a trained model.
        
        Args:
            model_path (str): Path to the trained .h5 model file
            verbose (bool): Print debug information
        """
        self.model = None
        self.model_path = model_path
        self.verbose = verbose
        self.last_prediction = None
        self.prediction_confidence = 0
        
        # Initialize MediaPipe if available
        if MEDIAPIPE_AVAILABLE:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            self.mp_drawing = mp.solutions.drawing_utils
            if self.verbose:
                print("[INFO] MediaPipe initialized successfully")
        else:
            self.hands = None
            self.mp_drawing = None
        
        # Load model
        self.load_model()
    
    def load_model(self):
        """Load the trained model from disk."""
        if not os.path.exists(self.model_path):
            print(f"[ERROR] Model file not found: {self.model_path}")
            print("[HINT] Run 'python train_model.py' first to create the model")
            return False
        
        try:
            self.model = tf.keras.models.load_model(self.model_path)
            if self.verbose:
                print(f"[SUCCESS] Model loaded from {self.model_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load model: {str(e)}")
            return False
    
    def preprocess_frame(self, frame):
        """
        Preprocess frame for model prediction.
        
        Args:
            frame (np.ndarray): Input frame from webcam
        
        Returns:
            tuple: (processed_frame, original_frame)
        """
        try:
            # Resize to model input size
            processed = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
            
            # Normalize to [0, 1]
            processed = processed.astype(np.float32) / 255.0
            
            # Add batch dimension
            processed = np.expand_dims(processed, axis=0)
            
            return processed, frame
        except Exception as e:
            print(f"[ERROR] Preprocessing failed: {str(e)}")
            return None, frame
    
    def predict(self, frame):
        """
        Make prediction on a single frame.
        
        Args:
            frame (np.ndarray): Input frame from webcam
        
        Returns:
            dict: {
                'predicted_character': str,
                'confidence': float,
                'all_predictions': dict (all classes with confidence)
            }
        """
        if self.model is None:
            return {
                'predicted_character': '?',
                'confidence': 0.0,
                'all_predictions': {},
                'error': 'Model not loaded'
            }
        
        try:
            # Preprocess
            processed, _ = self.preprocess_frame(frame)
            if processed is None:
                return {'error': 'Preprocessing failed'}
            
            # Predict
            predictions = self.model.predict(processed, verbose=0)
            confidence_scores = predictions[0]
            
            # Get top prediction
            predicted_idx = np.argmax(confidence_scores)
            predicted_char = CLASS_NAMES[predicted_idx]
            confidence = float(confidence_scores[predicted_idx])
            
            # Store for tracking
            self.last_prediction = predicted_char
            self.prediction_confidence = confidence
            
            # Create predictions dict for all classes
            all_predictions = {
                CLASS_NAMES[i]: float(confidence_scores[i])
                for i in range(len(CLASS_NAMES))
            }
            
            return {
                'predicted_character': predicted_char if confidence > CONFIDENCE_THRESHOLD else '?',
                'confidence': confidence,
                'all_predictions': all_predictions
            }
        
        except Exception as e:
            print(f"[ERROR] Prediction failed: {str(e)}")
            return {
                'predicted_character': '?',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def detect_hand_landmarks(self, frame):
        """
        Detect hand landmarks using MediaPipe.
        
        Args:
            frame (np.ndarray): Input frame
        
        Returns:
            tuple: (frame_with_landmarks, hand_detected)
        """
        if not MEDIAPIPE_AVAILABLE or self.hands is None:
            return frame, False
        
        try:
            # Mirror the frame horizontally for selfie view
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS
                    )
                return frame, True
            
            return frame, False
        
        except Exception as e:
            if self.verbose:
                print(f"[WARNING] Hand detection failed: {str(e)}")
            return frame, False
    
    def get_prediction_display_text(self):
        """Get formatted text for display."""
        if self.last_prediction is None:
            return "Initializing...", 0
        
        confidence_percent = int(self.prediction_confidence * 100)
        return f"'{self.last_prediction}'", confidence_percent

# =============================================
# UTILITY FUNCTIONS
# =============================================
def get_predictor(model_path='models/sign_language_model.h5'):
    """
    Factory function to get a predictor instance.
    Handles error checking.
    """
    predictor = SignLanguagePredictor(model_path=model_path, verbose=True)
    if predictor.model is None:
        print("[ERROR] Failed to initialize predictor")
        return None
    return predictor

def draw_prediction_on_frame(frame, prediction_char, confidence, x=20, y=50):
    """
    Draw prediction text on frame.
    
    Args:
        frame (np.ndarray): Input frame
        prediction_char (str): Predicted character
        confidence (float): Confidence score (0-1)
        x, y (int): Position for text
    
    Returns:
        np.ndarray: Frame with drawn text
    """
    frame = frame.copy()
    
    # Draw background for text
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.5
    thickness = 2
    color_bg = (30, 180, 100)  # Green
    color_text = (255, 255, 255)  # White
    
    text = f"Predicted: {prediction_char} ({int(confidence*100)}%)"
    
    # Get text size for background
    (text_width, text_height), baseline = cv2.getTextSize(
        text, font, font_scale, thickness
    )
    
    # Draw background rectangle
    cv2.rectangle(
        frame,
        (x - 5, y - text_height - 10),
        (x + text_width + 5, y + baseline + 5),
        color_bg,
        -1
    )
    
    # Draw text
    cv2.putText(
        frame,
        text,
        (x, y),
        font,
        font_scale,
        color_text,
        thickness
    )
    
    return frame

def draw_fps_on_frame(frame, fps, x=10, y=30):
    """Draw FPS counter on frame."""
    frame = frame.copy()
    text = f"FPS: {fps:.1f}"
    cv2.putText(
        frame,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )
    return frame

# =============================================
# TEST FUNCTION
# =============================================
def test_predictor():
    """Test the predictor with a random image."""
    print("\n" + "="*60)
    print("TESTING PREDICTOR")
    print("="*60)
    
    predictor = get_predictor()
    
    if predictor is None:
        print("[ERROR] Predictor initialization failed")
        return
    
    # Create random test image
    test_image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    
    # Make prediction
    result = predictor.predict(test_image)
    
    print(f"\nPrediction Result:")
    print(f"  Character: {result['predicted_character']}")
    print(f"  Confidence: {result['confidence']:.2%}")
    print(f"\nTop 5 predictions:")
    top_5 = sorted(result['all_predictions'].items(), key=lambda x: x[1], reverse=True)[:5]
    for char, conf in top_5:
        print(f"    {char}: {conf:.2%}")

if __name__ == "__main__":
    test_predictor()
