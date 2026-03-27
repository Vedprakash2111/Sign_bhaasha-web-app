# 🚀 Quick Start Guide - Sign Language App

## 📋 Prerequisites

- Python 3.8 or higher
- Working webcam
- Modern web browser
- 2-5 GB disk space

---

## ⚡ 5-Minute Setup

### Step 1: Open Terminal/Command Prompt

```bash
cd "C:\Users\vedpr\OneDrive\Documents\Desktop\sign language"
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

⏱️ **Takes ~3-5 minutes**

### Step 4: Train the Model

```bash
python train_model.py
```

⏱️ **Takes ~5-10 minutes** (first time only)

Watch the training progress:
- Model building
- Data generation
- Training epochs (50 total)
- Training graphs saved to `models/training_history.png`

### Step 5: Start the App

```bash
python app.py
```

You'll see:
```
[INFO] Initializing Sign Language Web App...
[SUCCESS] App initialized successfully!
Access the app at: http://localhost:5000
```

### Step 6: Open in Browser

Navigate to: **http://localhost:5000**

---

## 🎮 First Test

1. Allow camera permission
2. Position your hand in frame
3. Make an 'A' sign language gesture
4. See prediction on screen
5. Click "Add" to build text

---

## ✨ Key Features to Try

### 📝 Add Text
```
Button: Click "Add" or press Space key
Keyboard: Space = Add, Backspace = Delete, Delete = Clear all
```

### 🔊 Read Text
```
Button: "Read Aloud" 
Browser will speak your created message
```

### 📋 Copy Text
```
Button: "Copy to Clipboard"
Paste with Ctrl+V anywhere
```

### 🎨 Settings
```
Auto-add high confidence predictions
Enable/disable sound feedback
Show/hide hand landmarks
```

---

## 🐞 Common Issues

### ❌ Webcam Error

```
[ERROR] Could not open webcam
```

**Fix:**
- Check camera permissions
- Close other apps using camera
- Run: `python app.py`

### ❌ Model Not Found

```
[ERROR] Model file not found: models/sign_language_model.h5
```

**Fix:**
```bash
python train_model.py
```

### ❌ Port Already in Use

```
Address already in use
```

**Fix:**
```bash
# Kill process using port 5000
# Or change port in app.py line 188:
app.run(port=5001)
```

### ❌ Slow Performance

- Reduce resolution in `app.py` (line ~102):
```python
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)   # was 640
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  # was 480
```

---

## 📊 File Checklist

After installation, you should have:

```
✅ app.py                          (Flask app)
✅ train_model.py                  (Model trainer)
✅ requirements.txt                (Dependencies)
✅ README.md                       (Full documentation)
✅ QUICKSTART.md                   (This file)

✅ utils/
   ├── __init__.py
   └── predict.py                  (Prediction logic)

✅ templates/
   └── index.html                  (Web interface)

✅ static/
   ├── css/style.css               (Styling)
   └── js/main.js                  (JavaScript)

✅ models/
   ├── sign_language_model.h5      (After training)
   └── training_history.png        (After training)
```

---

## 🎯 Next Steps

1. **Test locally** - Make sure everything works
2. **Collect real data** - Train with actual hand gestures for better accuracy
3. **Customize** - Modify colors, add more gestures, customize text
4. **Deploy** - Use Render or Railway for online access
5. **Share** - Help others communicate with sign language!

---

## 🔧 Advanced Usage

### Test Just the Model

```bash
python -c "from utils.predict import test_predictor; test_predictor()"
```

### Clear Trained Model

```bash
rm models/sign_language_model.h5
python train_model.py
```

### Change Confidence Threshold

In `utils/predict.py`, line 14:
```python
CONFIDENCE_THRESHOLD = 0.5  # Change to 0.7 for stricter
```

### Custom Port

In `app.py`, line 188:
```python
app.run(port=8000)  # Changed from 5000
```

---

## 📞 Help at Each Stage

| Issue | Command to Try |
|-------|---|
| Dependencies error | `pip install --upgrade pip` |
| Python not found | Check Python is installed: `python --version` |
| Import error | `pip install -r requirements.txt` again |
| Model training stuck | Press Ctrl+C, then `python train_model.py` |
| Webcam frozen | Close app (Ctrl+C), restart browser, `python app.py` |

---

## 🎓 Learning Path

**Beginner** → Try the app as-is  
**Intermediate** → Read the README.md for detailed explanations  
**Advanced** → Modify code, add features, use GPU acceleration  
**Expert** → Deploy online, integrate with other apps  

---

## 💡 Pro Tips

1. **Good Lighting** - Brighter lighting = better recognition
2. **Hand Visibility** - Keep entire hand in frame
3. **Steady Gestures** - Hold gesture 1-2 seconds
4. **Practice** - Each person's gestures are unique
5. **Feedback** - Watch confidence scores to improve

---

## 🚀 Ready?

```
1. pip install -r requirements.txt
2. python train_model.py
3. python app.py
4. http://localhost:5000
```

**Let's go! 🤝**

---

For more help, see `README.md` →
