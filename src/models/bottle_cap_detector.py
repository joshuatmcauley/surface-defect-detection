from src.models.detector import DefectDetector
import cv2
import numpy as np
from ultralytics import YOLO

class BottleCapDetector(DefectDetector):
    def __init__(self, model_path='yolov8n.pt'):
        super().__init__(model_path)
        self.model = YOLO(model_path)
        # Define class names
        self.class_names = ['good', 'hole', 'melted', 'scratch', 'stain']
        print("YOLO model loaded successfully")

    def detect_defects(self, frame):
        """Detect defects in the frame"""
        try:
            # Run YOLO detection
            results = self.model(frame)
            
            # Process results
            defect_detected = False
            confidence = 0.0
            defect_details = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    conf = float(box.conf)
                    if conf > 0.5:  # Confidence threshold
                        defect_detected = True
                        confidence = max(confidence, conf)
                        
                        # Get box coordinates
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        defect_details.append({
                            'bbox': (x1, y1, x2, y2),
                            'confidence': conf,
                            'class': int(box.cls)
                        })
            
            return defect_detected, confidence, defect_details
            
        except Exception as e:
            print(f"Error in detection: {str(e)}")
            return False, 0.0, []

    def draw_detection_results(self, frame, defect_details):
        """Draw detection results on the frame"""
        for defect in defect_details:
            x1, y1, x2, y2 = defect['bbox']
            conf = defect['confidence']
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw confidence
            label = f"Confidence: {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame
