"""
Sign Language Communication Web App - Flask Backend
Real-time hand gesture recognition using webcam feed
"""

from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np
from utils.predict import SignLanguagePredictor
import threading
import time
from collections import deque
from datetime import datetime

# =============================================
# CONFIGURATION
# =============================================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sign-language-secret-2024'

# Global variables
predictor = None
camera = None
current_frame = None
prediction_history = deque(maxlen=30)  # Keep last 30 predictions
detected_text = ""
lock = threading.Lock()
fps_counter = 0
last_time = time.time()

# =============================================
# INITIALIZATION
# =============================================
def init_app():
    """Initialize the application."""
    global predictor, camera
    
    try:
        print("[INFO] Initializing Sign Language Web App...")
        
        # Load model
        predictor = SignLanguagePredictor(
            model_path='models/sign_language_model.h5',
            verbose=True
        )
        
        if predictor.model is None:
            print("[ERROR] Failed to load model")
            return False
        
        print("[SUCCESS] App initialized successfully!")
        return True
    
    except Exception as e:
        print(f"[ERROR] Initialization failed: {str(e)}")
        return False

# =============================================
# CAMERA HANDLING
# =============================================
class WebcamCapture:
    """Handle webcam capture and frame processing."""
    
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("[ERROR] Could not open webcam")
            self.cap = None
            return
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("[SUCCESS] Webcam opened successfully")
    
    def get_frame(self):
        """Capture a frame from webcam."""
        if self.cap is None:
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            print("[WARNING] Failed to capture frame")
            return None
        
        # Flip frame horizontally for selfie view
        frame = cv2.flip(frame, 1)
        
        return frame
    
    def release(self):
        """Release webcam resources."""
        if self.cap is not None:
            self.cap.release()
            print("[INFO] Webcam released")

# =============================================
# FRAME PROCESSING & PREDICTION
# =============================================
def process_frame(frame):
    """
    Process frame: detect hand, predict gesture, and prepare output.
    
    Returns:
        tuple: (processed_frame, prediction_result)
    """
    global fps_counter, last_time
    
    if frame is None or predictor is None:
        return frame, {}
    
    try:
        # Make prediction
        prediction_result = predictor.predict(frame)
        
        # Detect hand landmarks (optional, requires MediaPipe)
        frame_with_landmarks, hand_detected = predictor.detect_hand_landmarks(frame)
        
        # Draw prediction on frame
        from utils.predict import draw_prediction_on_frame, draw_fps_on_frame
        
        output_frame = draw_prediction_on_frame(
            frame_with_landmarks,
            prediction_result['predicted_character'],
            prediction_result['confidence']
        )
        
        # Calculate FPS
        current_time = time.time()
        fps_counter += 1
        if current_time - last_time > 1:
            fps = fps_counter / (current_time - last_time)
            fps_counter = 0
            last_time = current_time
        else:
            fps = 0
        
        # Draw FPS
        output_frame = draw_fps_on_frame(output_frame, fps)
        
        # Add hand detection status
        status_text = f"Hand Detected: {'Yes' if hand_detected else 'No'}"
        cv2.putText(
            output_frame,
            status_text,
            (20, 480 - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0) if hand_detected else (0, 0, 255),
            2
        )
        
        # Store prediction
        with lock:
            prediction_history.append({
                'character': prediction_result['predicted_character'],
                'confidence': prediction_result['confidence'],
                'timestamp': datetime.now().isoformat()
            })
        
        return output_frame, prediction_result
    
    except Exception as e:
        print(f"[ERROR] Frame processing failed: {str(e)}")
        return frame, {}

def generate_frames():
    """Generate frames for video streaming."""
    camera = WebcamCapture()
    
    if camera.cap is None:
        print("[ERROR] Webcam not available")
        return
    
    while True:
        try:
            frame = camera.get_frame()
            
            if frame is None:
                print("[WARNING] Frame capture failed")
                continue
            
            # Process frame
            processed_frame, prediction = process_frame(frame)
            
            if processed_frame is None:
                continue
            
            # Encode frame to JPEG for streaming
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            
            # Yield frame in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n'
                   b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n\r\n'
                   + frame_bytes + b'\r\n')
        
        except Exception as e:
            print(f"[ERROR] Frame generation failed: {str(e)}")
            continue
    
    camera.release()

# =============================================
# FLASK ROUTES
# =============================================
@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/api/prediction')
def get_prediction():
    """API endpoint to get current prediction."""
    if predictor is None:
        return jsonify({
            'error': 'Predictor not initialized',
            'status': 'error'
        }), 500
    
    with lock:
        char, confidence = predictor.get_prediction_display_text()
    
    return jsonify({
        'character': char,
        'confidence': confidence,
        'status': 'success'
    })

@app.route('/api/history')
def get_history():
    """API endpoint to get prediction history."""
    with lock:
        history = list(prediction_history)
    
    return jsonify({
        'history': history,
        'count': len(history)
    })

@app.route('/api/detected_text', methods=['GET', 'POST'])
def handle_detected_text():
    """Handle detected text operations."""
    global detected_text
    
    if request.method == 'GET':
        return jsonify({
            'text': detected_text,
            'length': len(detected_text)
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        
        if 'action' in data:
            if data['action'] == 'append':
                if 'char' in data:
                    detected_text += data['char']
            elif data['action'] == 'clear':
                detected_text = ""
            elif data['action'] == 'backspace':
                detected_text = detected_text[:-1]
        
        return jsonify({
            'text': detected_text,
            'status': 'success'
        })

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': predictor is not None and predictor.model is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Route not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    print(f"[ERROR] Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

# =============================================
# MAIN EXECUTION
# =============================================
if __name__ == '__main__':
    print("=" * 60)
    print("SIGN LANGUAGE WEB APP - STARTING")
    print("=" * 60)
    
    # Initialize app
    if not init_app():
        print("[ERROR] Failed to initialize app")
        exit(1)
    
    print("\n" + "=" * 60)
    print("✓ APPLICATION READY")
    print("=" * 60)
    print("\nAccess the app at: http://localhost:5000")
    print("Press CTRL+C to stop the server\n")
    
    # Start Flask app
    try:
        app.run(
            debug=False,
            host='0.0.0.0',
            port=5000,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
    except Exception as e:
        print(f"\n[ERROR] Server error: {str(e)}")
