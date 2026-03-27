"""
Configuration settings for Sign Language App
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================
# FLASK CONFIGURATION
# =============================================
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'sign-language-secret-2024')

# =============================================
# MODEL CONFIGURATION
# =============================================
MODEL_PATH = os.getenv('MODEL_PATH', 'models/sign_language_model.h5')
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.5'))
IMG_SIZE = 64
NUM_CLASSES = 26
CLASS_NAMES = [chr(65 + i) for i in range(NUM_CLASSES)]  # A-Z

# =============================================
# CAMERA CONFIGURATION
# =============================================
CAMERA_WIDTH = int(os.getenv('CAMERA_WIDTH', '640'))
CAMERA_HEIGHT = int(os.getenv('CAMERA_HEIGHT', '480'))
CAMERA_FPS = int(os.getenv('CAMERA_FPS', '30'))

# =============================================
# FEATURE FLAGS
# =============================================
ENABLE_MEDIAPIPE = os.getenv('ENABLE_MEDIAPIPE', 'True').lower() == 'true'
ENABLE_SOUND_FEEDBACK = os.getenv('ENABLE_SOUND_FEEDBACK', 'True').lower() == 'true'
ENABLE_AUTO_ADD = os.getenv('ENABLE_AUTO_ADD', 'True').lower() == 'true'

# =============================================
# APP SETTINGS
# =============================================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
MAX_PREDICTIONS_HISTORY = int(os.getenv('MAX_PREDICTIONS_HISTORY', '30'))
PREDICTION_UPDATE_INTERVAL = int(os.getenv('PREDICTION_UPDATE_INTERVAL', '500'))

# =============================================
# PATHS
# =============================================
TEMPLATES_DIR = 'templates'
STATIC_DIR = 'static'
MODELS_DIR = 'models'
DATA_DIR = 'data'

# =============================================
# TRAINING CONFIGURATION
# =============================================
BATCH_SIZE = 32
EPOCHS = 50
VALIDATION_SPLIT = 0.2
LEARNING_RATE = 0.001

# =============================================
# FUNCTION: PRINT CONFIG
# =============================================
def print_config():
    """Print current configuration settings."""
    print("\n" + "="*60)
    print("SIGN LANGUAGE APP - CONFIGURATION")
    print("="*60)
    
    print(f"\n[FLASK]")
    print(f"  Environment: {FLASK_ENV}")
    print(f"  Debug: {FLASK_DEBUG}")
    
    print(f"\n[MODEL]")
    print(f"  Path: {MODEL_PATH}")
    print(f"  Confidence Threshold: {CONFIDENCE_THRESHOLD}")
    print(f"  Input Size: {IMG_SIZE}x{IMG_SIZE}")
    print(f"  Classes: {NUM_CLASSES} (A-Z)")
    
    print(f"\n[CAMERA]")
    print(f"  Resolution: {CAMERA_WIDTH}x{CAMERA_HEIGHT}")
    print(f"  FPS: {CAMERA_FPS}")
    
    print(f"\n[FEATURES]")
    print(f"  MediaPipe: {'Enabled' if ENABLE_MEDIAPIPE else 'Disabled'}")
    print(f"  Sound Feedback: {'Enabled' if ENABLE_SOUND_FEEDBACK else 'Disabled'}")
    print(f"  Auto-Add: {'Enabled' if ENABLE_AUTO_ADD else 'Disabled'}")
    
    print(f"\n[TRAINING]")
    print(f"  Batch Size: {BATCH_SIZE}")
    print(f"  Epochs: {EPOCHS}")
    print(f"  Validation Split: {VALIDATION_SPLIT}")
    
    print("="*60 + "\n")

# =============================================
# FUNCTION: VALIDATE CONFIG
# =============================================
def validate_config():
    """Validate configuration settings."""
    errors = []
    
    if not 0 <= CONFIDENCE_THRESHOLD <= 1:
        errors.append("CONFIDENCE_THRESHOLD must be between 0 and 1")
    
    if CAMERA_WIDTH < 320 or CAMERA_HEIGHT < 240:
        errors.append("Camera resolution too low (minimum 320x240)")
    
    if CAMERA_FPS < 1 or CAMERA_FPS > 60:
        errors.append("Camera FPS must be between 1 and 60")
    
    if errors:
        print("\n[WARNING] Configuration validation warnings:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True

if __name__ == '__main__':
    # Example: validate and print config
    if validate_config():
        print_config()
    else:
        print("\n[ERROR] Configuration validation failed!")
        exit(1)
