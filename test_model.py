"""
Test Script for Sign Language Model
Run this to test the model without the web app
"""

import cv2
import numpy as np
from utils.predict import SignLanguagePredictor, draw_prediction_on_frame
import time

def test_model_output():
    """Test the model with a random image."""
    print("\n" + "="*60)
    print("TEST 1: Basic Model Output")
    print("="*60)
    
    predictor = SignLanguagePredictor(verbose=True)
    
    if predictor.model is None:
        print("[ERROR] Failed to load model. Run 'python train_model.py' first.")
        return False
    
    # Create random test image
    test_image = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
    
    # Make prediction
    result = predictor.predict(test_image)
    
    print(f"\n✓ Prediction successful!")
    print(f"  Predicted: {result['predicted_character']}")
    print(f"  Confidence: {result['confidence']:.2%}")
    
    print(f"\n  Top 5 predictions:")
    top_5 = sorted(result['all_predictions'].items(), key=lambda x: x[1], reverse=True)[:5]
    for char, conf in top_5:
        print(f"    {char}: {conf:.2%}")
    
    return True

def test_preprocessor():
    """Test image preprocessing."""
    print("\n" + "="*60)
    print("TEST 2: Image Preprocessing")
    print("="*60)
    
    predictor = SignLanguagePredictor(verbose=False)
    
    # Create test image
    test_image = np.ones((256, 256, 3), dtype=np.uint8) * 128
    cv2.circle(test_image, (128, 128), 50, (200, 100, 50), -1)
    
    # Preprocess
    processed, original = predictor.preprocess_frame(test_image)
    
    if processed is not None:
        print(f"✓ Preprocessing successful!")
        print(f"  Input shape: {original.shape}")
        print(f"  Output shape: {processed.shape}")
        print(f"  Expected shape: (1, 64, 64, 3)")
        print(f"  Output dtype: {processed.dtype}")
        print(f"  Output range: [{processed.min():.2f}, {processed.max():.2f}]")
        return True
    
    return False

def test_webcam():
    """Test webcam capture."""
    print("\n" + "="*60)
    print("TEST 3: Webcam Capture")
    print("="*60)
    print("\nAttempting to open webcam...")
    print("Press 'q' to exit\n")
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Webcam failed to open")
        return False
    
    print("✓ Webcam opened successfully!")
    
    # Get camera properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"\n  Resolution: {width}x{height}")
    print(f"  FPS: {fps}")
    
    # Capture a few frames
    frames_captured = 0
    start_time = time.time()
    
    print(f"\nCapturing frames for 3 seconds...")
    
    while (time.time() - start_time) < 3:
        ret, frame = cap.read()
        if ret:
            frames_captured += 1
        
        if frames_captured % 10 == 0:
            elapsed = time.time() - start_time
            fps = frames_captured / elapsed
            print(f"  Frames: {frames_captured}, FPS: {fps:.1f}")
    
    cap.release()
    
    print(f"\n✓ Captured {frames_captured} frames in ~3 seconds")
    return True

def test_with_webcam():
    """Test model with live webcam feed."""
    print("\n" + "="*60)
    print("TEST 4: Live Prediction with Webcam")
    print("="*60)
    print("\nStarting webcam test...")
    print("- Make hand gestures in front of camera")
    print("- Press 'q' to exit\n")
    
    predictor = SignLanguagePredictor(verbose=False)
    
    if predictor.model is None:
        print("[ERROR] Model not loaded")
        return False
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[ERROR] Webcam not available")
        return False
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip for selfie view
            frame = cv2.flip(frame, 1)
            
            # Make prediction
            result = predictor.predict(frame)
            
            # Draw on frame
            frame = draw_prediction_on_frame(
                frame,
                result['predicted_character'],
                result['confidence']
            )
            
            # Display
            cv2.imshow('Sign Language - Test', frame)
            
            frame_count += 1
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Calculate stats
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        
        print(f"\n✓ Webcam test completed!")
        print(f"  Frames processed: {frame_count}")
        print(f"  Time elapsed: {elapsed:.1f}s")
        print(f"  Average FPS: {fps:.1f}")
        
        return True
    
    except KeyboardInterrupt:
        print("\n[INFO] Test interrupted by user")
        return True
    
    finally:
        cap.release()
        cv2.destroyAllWindows()

def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("SIGN LANGUAGE MODEL - TEST SUITE")
    print("="*60)
    
    tests = [
        ("Model Output", test_model_output),
        ("Image Preprocessing", test_preprocessor),
        ("Webcam Capture", test_webcam),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n[ERROR] Test '{test_name}' failed with exception:")
            print(f"  {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! App is ready to use.")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed. Check errors above.")
        return False

def interactive_mode():
    """Run in interactive mode."""
    print("\n" + "="*60)
    print("SIGN LANGUAGE - INTERACTIVE TEST MODE")
    print("="*60)
    
    print("\nAvailable tests:")
    print("  1. Test model output")
    print("  2. Test preprocessing")
    print("  3. Test webcam capture")
    print("  4. Live prediction with webcam")
    print("  5. Run all tests")
    print("  0. Exit")
    
    while True:
        try:
            choice = input("\nEnter test number (0-5): ").strip()
            
            if choice == '0':
                print("\nGoodbye!")
                break
            elif choice == '1':
                test_model_output()
            elif choice == '2':
                test_preprocessor()
            elif choice == '3':
                test_webcam()
            elif choice == '4':
                test_with_webcam()
            elif choice == '5':
                run_all_tests()
            else:
                print("Invalid choice. Try again.")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("SIGN LANGUAGE MODEL - TEST SCRIPT")
    print("="*60 + "\n")
    
    # Check arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'all':
            run_all_tests()
        elif sys.argv[1] == 'interactive':
            interactive_mode()
        elif sys.argv[1] == 'webcam':
            test_with_webcam()
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Usage: python test_model.py [all|interactive|webcam]")
    else:
        # Default: run main tests
        run_all_tests()
        
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("✓ If all tests passed, you can:")
        print("  - python app.py          (Start the web app)")
        print("  - python test_model.py interactive  (Interactive testing)")
        print("  - python test_model.py webcam      (Live webcam test)")
        print("\n✓ If any test failed, check the errors above")
