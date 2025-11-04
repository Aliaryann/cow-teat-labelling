from ultralytics import YOLO

# Load trained model
model = YOLO('models/best_teat_detector.pt')

# Test on validation set
results = model.val()

# Test on single image
# results = model('path/to/test/image.jpg')
# results[0].show()  # Display results
# results[0].save('results/detection.jpg')  # Save results
