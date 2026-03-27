"""
Real Hand Gesture Capture Tool
Captures actual sign language gestures from webcam for training
"""

import cv2
import os
import numpy as np
from pathlib import Path
import time

# =============================================
# CONFIGURATION
# =============================================
IMG_SIZE = 64
SAMPLES_PER_GESTURE = 40  # Capture 40 samples per letter
DATA_DIR = "training_data/raw_gestures"
class_names = [chr(65 + i) for i in range(26)]  # A-Z

# =============================================
# CREATE DIRECTORIES
# =============================================
os.makedirs(DATA_DIR, exist_ok=True)

# =============================================
# CAPTURE GESTURES
# =============================================
def capture_gestures():
    """
    Interactive gesture capture interface.
    User will hold up each gesture while the app captures frames.
    """
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[ERROR] Could not open webcam!")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("\n" + "=" * 60)
    print("SIGN LANGUAGE GESTURE CAPTURE")
    print("=" * 60)
    print(f"Total gestures to capture: {len(class_names)}")
    print(f"Samples per gesture: {SAMPLES_PER_GESTURE}")
    print(f"Total samples: {len(class_names) * SAMPLES_PER_GESTURE}")
    print("\nInstructions:")
    print("  - Press SPACE to start capturing for current gesture")
    print("  - Hold gesture steady for 3 seconds (40 frames)")
    print("  - Press ESC to skip gesture")
    print("  - Press Q to quit")
    print("=" * 60 + "\n")
    
    captured_count = {}
    current_gesture_idx = 0
    
    while current_gesture_idx < len(class_names):
        gesture_letter = class_names[current_gesture_idx]
        captured_count[gesture_letter] = 0
        
        print(f"\n[READY] Gesture: {gesture_letter}")
        print(f"Progress: {current_gesture_idx + 1}/{len(class_names)}")
        print("Press SPACE to start capturing (or ESC to skip)...")
        
        capturing = False
        skip_gesture = False
        
        while captured_count[gesture_letter] < SAMPLES_PER_GESTURE:
            ret, frame = cap.read()
            
            if not ret:
                print("[ERROR] Failed to capture frame!")
                break
            
            # Mirror frame
            frame = cv2.flip(frame, 1)
            
            # Display current gesture letter
            display_frame = frame.copy()
            
            if capturing:
                # Green border and counter when capturing
                cv2.rectangle(display_frame, (10, 10), (630, 470), (0, 255, 0), 5)
                cv2.putText(display_frame, f"Capturing {gesture_letter}: {captured_count[gesture_letter] + 1}/{SAMPLES_PER_GESTURE}",
                           (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                cv2.putText(display_frame, "Recording...", (20, 470 - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                # Yellow border when ready
                cv2.rectangle(display_frame, (10, 10), (630, 470), (0, 255, 255), 3)
                cv2.putText(display_frame, f"Ready: {gesture_letter}",
                           (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
                cv2.putText(display_frame, "Press SPACE to capture (ESC to skip)",
                           (20, 470 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            
            cv2.imshow("Gesture Capture", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' ') and not capturing:
                # Start capturing
                capturing = True
                start_time = time.time()
                print(f"[CAPTURING] Please hold the gesture {gesture_letter}...")
            
            elif capturing:
                # Save frame while capturing
                # Resize frame
                resized = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
                
                # Create output directory for this gesture
                gesture_dir = os.path.join(DATA_DIR, gesture_letter)
                os.makedirs(gesture_dir, exist_ok=True)
                
                # Save image
                filename = os.path.join(gesture_dir, f"{gesture_letter}_{captured_count[gesture_letter]:03d}.jpg")
                cv2.imwrite(filename, resized)
                
                captured_count[gesture_letter] += 1
                
                # Stop after required samples
                if captured_count[gesture_letter] >= SAMPLES_PER_GESTURE:
                    capturing = False
                    print(f"[SUCCESS] Captured {SAMPLES_PER_GESTURE} samples for {gesture_letter}!")
                    break
            
            elif key == 27:  # ESC - Skip gesture
                skip_gesture = True
                print(f"[SKIPPED] Gesture {gesture_letter}")
                break
            
            elif key == ord('q'):  # Q - Quit
                print("[QUIT] Exiting capture mode...")
                cap.release()
                cv2.destroyAllWindows()
                return captured_count
        
        current_gesture_idx += 1
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Print summary
    print("\n" + "=" * 60)
    print("CAPTURE SUMMARY")
    print("=" * 60)
    total_captured = sum(captured_count.values())
    print(f"Total samples captured: {total_captured}/{len(class_names) * SAMPLES_PER_GESTURE}")
    for letter, count in captured_count.items():
        status = "✓" if count == SAMPLES_PER_GESTURE else "✗"
        print(f"  {status} {letter}: {count}/{SAMPLES_PER_GESTURE}")
    print("=" * 60)
    
    return captured_count

# =============================================
# VERIFY CAPTURED DATA
# =============================================
def verify_captured_data():
    """
    Verify that captured data exists and show statistics.
    """
    print("\n[INFO] Verifying captured data...")
    
    if not os.path.exists(DATA_DIR):
        print(f"[ERROR] Data directory not found: {DATA_DIR}")
        return False
    
    total_files = 0
    for gesture_letter in class_names:
        gesture_dir = os.path.join(DATA_DIR, gesture_letter)
        if os.path.exists(gesture_dir):
            files = [f for f in os.listdir(gesture_dir) if f.endswith('.jpg')]
            total_files += len(files)
            print(f"  {gesture_letter}: {len(files)} samples")
        else:
            print(f"  {gesture_letter}: 0 samples (NOT CAPTURED)")
    
    print(f"\nTotal samples: {total_files}/{len(class_names) * SAMPLES_PER_GESTURE}")
    
    return total_files > 0

# =============================================
# MAIN
# =============================================
if __name__ == "__main__":
    print("\n🎥 REAL GESTURE DATA CAPTURE TOOL 🎥")
    print("\nThis tool will help you capture real sign language gestures")
    print("for training the model with your actual hand movements.\n")
    
    # Start capturing
    captured = capture_gestures()
    
    # Verify data
    if captured and sum(captured.values()) > 0:
        print("\n✓ Ready to retrain model!")
        print("\nNext step: Run 'python retrain_model_real.py'")
    else:
        print("\n✗ No data captured. Please try again.")
