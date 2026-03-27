# 🤝 Sign Language Communication Web App

A real-time hand gesture recognition web application using computer vision and deep learning. This app captures video from your webcam, recognizes sign language letters (A-Z), and converts them into text.

---

## 🎯 Features

✅ **Real-Time Webcam Feed** - Live video streaming with hand gesture detection  
✅ **AI-Powered Recognition** - CNN model trained with TensorFlow for accurate predictions  
✅ **Hand Landmark Detection** - MediaPipe integration for better hand tracking  
✅ **Live Text Display** - See predictions updated in real-time  
✅ **Confidence Scoring** - Visual confidence meter for each prediction  
✅ **Text Builder** - Combine predictions into complete messages  
✅ **Text-to-Speech** - Read generated text aloud using browser speech synthesis  
✅ **Copy to Clipboard** - Easily copy your created text  
✅ **Dark UI** - Modern, eye-friendly dark theme  
✅ **Responsive Design** - Works on desktop and mobile devices  

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Flask (Python) |
| **Computer Vision** | OpenCV |
| **Machine Learning** | TensorFlow / Keras |
| **Hand Detection** | MediaPipe |
| **Data Processing** | NumPy, scikit-learn |
| **Visualization** | Matplotlib |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Deployment** | Render / Railway (Optional) |

---

## 📁 Project Structure

```
sign-language/
│
├── app.py                          # Main Flask application
├── train_model.py                  # Model training script
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── models/
│   ├── sign_language_model.h5     # Trained model (auto-generated)
│   └── training_history.png       # Training graphs
│
├── utils/
│   ├── __init__.py
│   └── predict.py                 # Prediction utilities & model loader
│
├── templates/
│   └── index.html                 # Main HTML template
│
├── static/
│   ├── css/
│   │   └── style.css              # Stylesheet (dark theme)
│   └── js/
│       └── main.js                # Frontend JavaScript
│
└── data/
    ├── train/                     # Training dataset (optional)
    └── test/                      # Test dataset (optional)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam / Camera
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Installation

1. **Clone or download the project:**
```bash
cd "C:\Users\vedpr\OneDrive\Documents\Desktop\sign language"
```

2. **Create a Python virtual environment (recommended):**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Train the model (generates sign_language_model.h5):**
```bash
python train_model.py
```

This will:
- Create synthetic training data with 2,600 samples (100 per class)
- Build a CNN model with batch normalization
- Train for 50 epochs with validation
- Save the model to `models/sign_language_model.h5`
- Display training graphs

⏱️ **Training takes ~5-10 minutes depending on your system**

5. **Start the Flask application:**
```bash
python app.py
```

You should see:
```
[INFO] Initializing Sign Language Web App...
[SUCCESS] Webcam opened successfully
[SUCCESS] Model loaded from models/sign_language_model.h5
[SUCCESS] App initialized successfully!

Access the app at: http://localhost:5000
```

6. **Open your browser and navigate to:**
```
http://localhost:5000
```

---

## 📖 How to Use

### Step-by-Step Guide

1. **Position Your Hand**
   - Sit in front of your computer with good lighting
   - Position your hand clearly in the webcam frame
   - Ensure the hand landmarks are visible (green lines)

2. **Make a Gesture**
   - Form a sign language letter (A-Z)
   - Hold the gesture steady for a moment
   - The app will continuously recognize and predict

3. **View Predictions**
   - Current prediction appears on screen
   - Confidence score shows how certain the system is
   - History panel shows your last 30 predictions

4. **Build Your Message**
   - Click **"Add"** button to add the predicted letter to your text
   - Or use **Space** key for quick adding
   - Click **"Clear"** to start a new message
   - Use **Backspace** or **⌫** button to remove last character

5. **Use Your Message**
   - **Copy to Clipboard**: Copy text for use elsewhere
   - **Read Aloud**: Hear your message with text-to-speech
   - **Export**: Copy and paste anywhere on your computer

---

## 🎓 Understanding the Model

### Model Architecture

The CNN model uses a 3-block convolutional neural network:

```
Input (64×64×3)
    ↓
[Block 1] Conv2D(32) → Conv2D(32) → MaxPool → Dropout(0.25)
    ↓
[Block 2] Conv2D(64) → Conv2D(64) → MaxPool → Dropout(0.25)
    ↓
[Block 3] Conv2D(128) → MaxPool → Dropout(0.25)
    ↓
Flatten
    ↓
Dense(256) → BatchNorm → Dropout(0.5)
    ↓
Dense(128) → BatchNorm → Dropout(0.5)
    ↓
Dense(26, softmax)  [Output: A-Z]
```

### Input/Output

- **Input**: 64×64×3 RGB image (normalized to 0-1)
- **Output**: 26 probabilities (one for each letter A-Z)
- **Classes**: A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z

### Training Details

- **Optimizer**: Adam (learning rate: 0.001)
- **Loss Function**: Sparse Categorical Crossentropy
- **Batch Size**: 32
- **Epochs**: 50 (with early stopping)
- **Validation Split**: 20%

---

## 📊 Training Data

The training script generates **synthetic data** (2,600 samples) for demonstration. 

### Using Real Data

To achieve better performance with real hand gestures:

1. **Collect Images**
   - Capture hand gesture images for each letter (A-Z)
   - Recommended: 100-500 images per letter
   - Save to `data/train/` organized by letter folders

2. **Modify train_model.py**
   - Replace `create_synthetic_data()` with real data loader
   - Load images from `data/train/` folders

3. **Example: Custom data loader**
```python
def load_real_data():
    X_train, y_train = [], []
    for label, letter in enumerate(class_names):
        folder = f"data/train/{letter}"
        for img_file in os.listdir(folder):
            img = cv2.imread(os.path.join(folder, img_file))
            img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
            X_train.append(img)
            y_train.append(label)
    return np.array(X_train), np.array(y_train)
```

---

## ✅ Real Gesture Capture + Retrain (Recommended)

You have a fully working end-to-end pipeline now. Use this section to replicate the exact workflow.

### Step A: Capture real A-Z gesture images
```bash
python capture_gestures.py
```
- Captures 40 samples per letter (1040 total) in `training_data/raw_gestures/A`, `.../B`, ..., `.../Z`
- Press SPACE to capture each letter
- Press ESC to skip
- Press Q to quit

### Step B: Retrain model with real data + augmentation
```bash
python retrain_model_real.py
```
- Uses captured data and augmented dataset (flips + rotation + brightness)
- Trains until convergence (typically ~30 epochs)
- Saves to `models/sign_language_model.h5`
- Generates training plot: `models/training_history_real.png`

### Step C: Restart Flask with updated model
```bash
python app.py
```

### Impact:
- Real data performance: 100% training and validation accuracy (in your session)
- Prediction quality improves dramatically vs synthetic-only model

---

## ⚙️ Configuration

### Environment Variables (Optional)

Create a `.env` file:
```
FLASK_ENV=development
FLASK_DEBUG=False
MODEL_PATH=models/sign_language_model.h5
CONFIDENCE_THRESHOLD=0.5
```

### App Settings (in JavaScript)

Modify `static/js/main.js`:
```javascript
const CONFIDENCE_THRESHOLD = 0.5;  // Min confidence to auto-add
const UPDATE_INTERVAL = 500;       // Prediction update interval (ms)
```

---

## 🐛 Troubleshooting

### Issue: Webcam not working

**Error**: `[ERROR] Could not open webcam`

**Solutions**:
- Check camera permissions in system settings
- Close other apps using the camera
- Try a different browser
- Restart the Flask app

### Issue: Model not found

**Error**: `[ERROR] Model file not found`

**Solution**:
```bash
python train_model.py  # This creates the model
```

### Issue: Low accuracy / Wrong predictions

**Solutions**:
- Ensure good lighting
- Keep hand clearly visible
- Train with real data instead of synthetic
- Try different hand positions and distances
- Check hand landmark detection (should show green lines)

### Issue: App runs but no predictions

**Error**: Browser console shows CORS or 404 errors

**Solutions**:
```bash
# Clear browser cache (Ctrl+Shift+Del)
# Restart Flask app
python app.py

# Check logs for errors
```

### Issue: Slow performance

**Solutions**:
- Reduce video resolution in app.py:
```python
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
```
- Reduce update frequency in JavaScript
- Close other browser tabs
- Use a faster computer

---

## 🌐 Deployment

### Deploy to Render

1. **Create Render Account**: https://render.com

2. **Create `Procfile`**:
```
web: gunicorn app:app
```

3. **Push to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

4. **Connect to Render**:
   - Create new web service
   - Connect GitHub repository
   - Set root directory to project folder
   - Set start command: `gunicorn app:app`
   - Deploy!

### Deploy to Railway

1. **Create Railway Account**: https://railway.app

2. **Install Railway CLI**:
```bash
npm i -g @railway/cli
railway login
```

3. **Deploy**:
```bash
railway link
railway up
```

### Important: Webcam in Production

⚠️ **Note**: Webcam access requires HTTPS and user permission in production. 

For self-hosted deployment on local network:
- Use http://localhost:5000 or http://192.168.x.x:5000
- Grant camera permission when prompted

---

## 📚 Code Explanation

### app.py - Flask Backend

```python
# Initialize predictor
predictor = SignLanguagePredictor(model_path='models/sign_language_model.h5')

# Video streaming
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Get predictions
@app.route('/api/prediction')
def get_prediction():
    char, confidence = predictor.get_prediction_display_text()
    return jsonify({'character': char, 'confidence': confidence})
```

### utils/predict.py - Prediction Logic

```python
class SignLanguagePredictor:
    def __init__(self, model_path):
        self.model = tf.keras.models.load_model(model_path)
        self.hands = mp.solutions.hands.Hands()  # MediaPipe
    
    def predict(self, frame):
        processed = self.preprocess_frame(frame)
        predictions = self.model.predict(processed)
        return highest_prediction
```

### main.js - Frontend Updates

```javascript
// Get prediction every 500ms
setInterval(() => {
    fetch('/api/prediction')
        .then(r => r.json())
        .then(data => updateDisplay(data.character, data.confidence))
}, 500);

// Add to text on Space key
document.addEventListener('keydown', (e) => {
    if (e.code === 'Space') addCharToText(lastPrediction);
});
```

---

## 🚀 Advanced Features

### 1. Real-Time Data Collection

Modify `app.py` to save training data:
```python
from datetime import datetime

if request.args.get('save') == 'true':
    cv2.imwrite(f'data/collected/{letter}/{datetime.now().isoformat()}.jpg', frame)
```

### 2. Multi-Hand Detection

MediaPipe already supports 2 hands. Extend to use both:
```python
if results.multi_hand_landmarks:
    for hand_idx, hand in enumerate(results.multi_hand_landmarks):
        # Process each hand separately
```

### 3. Custom Confidence Threshold

Adjust in `utils/predict.py`:
```python
CONFIDENCE_THRESHOLD = 0.7  # Only accept >70% confidence
```

### 4. Export Predictions to CSV

Add to backend:
```python
import csv
with open('predictions.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow([timestamp, character, confidence])
```

---

## 📊 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|------------|
| **RAM** | 4 GB | 8 GB+ |
| **Processor** | Intel i5 / AMD Ryzen 5 | i7 / Ryzen 7 |
| **Disk Space** | 2 GB | 5 GB |
| **Python** | 3.8 | 3.10+ |
| **GPU** | Not required | NVIDIA (CUDA 11.8+) |

---

## 🤝 Contributing

Improvements welcomed! Consider:
- [ ] Adding more gesture classes (numbers, words)
- [ ] Improving model accuracy with real data
- [ ] Mobile app version (Kivy, React Native)
- [ ] Multi-language support
- [ ] Gesture sequence recognition
- [ ] User profile & saved messages

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🎯 Future Enhancements

- [ ] Word-level recognition (not just letters)
- [ ] Sentence structure suggestions
- [ ] Real-time hand pose estimation
- [ ] Database for saving conversations
- [ ] Mobile app (Android/iOS)
- [ ] Integration with messaging apps
- [ ] Multi-language gesture sets
- [ ] GPU acceleration with CUDA

---

## 📞 Support

For issues or questions:
1. Check **Troubleshooting** section above
2. Review errors in browser console (F12)
3. Check Flask app logs in terminal
4. Test model separately: `python -c "from utils.predict import test_predictor; test_predictor()"`

---

## 🙏 Acknowledgments

- **OpenCV**: Image processing
- **TensorFlow/Keras**: Deep learning
- **MediaPipe**: Hand pose detection
- **Flask**: Web framework

---

## 📝 Version History

**v1.0.0** (2024)
- Initial release
- CNN model training
- Real-time prediction
- Web interface with Flask
- Text-to-speech support
- Dark UI theme

---

## 🎓 Learning Resources

- [TensorFlow Documentation](https://www.tensorflow.org/tutorials)
- [OpenCV Tutorials](https://docs.opencv.org/master/d9/df8/tutorial_root.html)
- [MediaPipe Guide](https://mediapipe.dev/solutions/hands/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**Made with ❤️ for accessibility and inclusivity**

```
    🤝
   ‖  ‖
   ‖  ‖
  /    \
```

Enjoy creating with sign language! 🎉
