from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QStatusBar, QFrame, QSpinBox,
                             QComboBox, QSlider, QGridLayout, QScrollArea,
                             QFileDialog, QGroupBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
import cv2
import numpy as np
import os
from datetime import datetime
from picamera2 import Picamera2
import libcamera
from ultralytics import YOLO

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Defect Detection System")
        
        # Initialize variables
        self.camera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.captured_images = []
        self.current_confidence = 0.85
        self.save_directory = "captured_images"
        self.current_product_type = "Bottle Caps"
        self.detector = None
        
        # Initialize detection model
        self.model = YOLO('yolov8n.pt')
        
        # Create save directory if it doesn't exist
        os.makedirs(self.save_directory, exist_ok=True)
        
        # Set up UI
        self.setup_ui()
        
        # Set window size and show
        self.setMinimumSize(1000, 800)
        self.show()
        
    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Main Detection Layout
        detection_layout = QHBoxLayout()
        
        # Left panel - Camera feed
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Camera feed
        camera_frame = QFrame()
        camera_frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        camera_layout = QVBoxLayout(camera_frame)
        self.image_label = QLabel()
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setAlignment(Qt.AlignCenter)
        camera_layout.addWidget(self.image_label)
        left_layout.addWidget(camera_frame)
        
        detection_layout.addWidget(left_panel)
        
        # Right panel - Controls
        right_panel = QWidget()
        right_panel.setMaximumWidth(300)
        right_layout = QVBoxLayout(right_panel)
        
        # Camera controls group
        camera_group = QGroupBox("Camera Controls")
        camera_controls = QVBoxLayout(camera_group)
        
        self.start_button = QPushButton("Start Camera")
        self.start_button.clicked.connect(self.toggle_camera)
        self.capture_button = QPushButton("Capture Image")
        self.capture_button.clicked.connect(self.capture_image)
        self.capture_button.setEnabled(False)
        
        camera_controls.addWidget(self.start_button)
        camera_controls.addWidget(self.capture_button)
        right_layout.addWidget(camera_group)
        
        # Detection settings group
        detection_group = QGroupBox("Detection Settings")
        detection_layout = QVBoxLayout(detection_group)
        
        # Confidence threshold slider
        detection_layout.addWidget(QLabel("Confidence Threshold:"))
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(int(self.current_confidence * 100))
        self.confidence_slider.valueChanged.connect(self.update_confidence)
        detection_layout.addWidget(self.confidence_slider)
        self.confidence_label = QLabel(f"Threshold: {self.current_confidence:.2f}")
        detection_layout.addWidget(self.confidence_label)
        
        right_layout.addWidget(detection_group)
        
        # Status group
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        self.status_label = QLabel("Camera: Stopped")
        self.detection_label = QLabel("No defects detected")
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.detection_label)
        right_layout.addWidget(status_group)
        
        detection_layout.addWidget(right_panel)
        main_layout.addLayout(detection_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def toggle_camera(self):
        if self.timer.isActive():
            self.stop_camera()
        else:
            self.start_camera()
            
    def start_camera(self):
        if self.camera is None:
            try:
                self.camera = Picamera2()
                
                # Configure camera with basic settings
                preview_config = self.camera.create_preview_configuration(
                    main={
                        "size": (1280, 720),
                        "format": "RGB888"
                    },
                    transform=libcamera.Transform(hflip=1, vflip=1),
                    buffer_count=4
                )
                
                self.camera.configure(preview_config)
                
                # Set basic controls
                self.camera.set_controls({
                    "FrameRate": 30.0,
                    "ExposureTime": 20000,
                    "AnalogueGain": 1.0
                })
                
                self.camera.start()
                
            except Exception as e:
                print(f"Error starting camera: {str(e)}")
                self.camera = None
                return
        
        self.timer.start(30)  # ~30 FPS
        self.start_button.setText("Stop Camera")
        self.capture_button.setEnabled(True)
        self.status_label.setText("Camera: Running")
        self.statusBar().showMessage("Camera running")
        
    def stop_camera(self):
        self.timer.stop()
        if self.camera is not None:
            self.camera.stop()
            self.camera.close()
            self.camera = None
        self.start_button.setText("Start Camera")
        self.capture_button.setEnabled(False)
        self.status_label.setText("Camera: Stopped")
        self.statusBar().showMessage("Camera stopped")
        
    def update_frame(self):
        """Update the camera feed"""
        if self.camera is not None:
            try:
                # Capture frame
                frame = self.camera.capture_array()
                
                # Convert to BGR for OpenCV
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # Process frame if detector is active
                if self.detector is not None:
                    try:
                        # Run detection
                        defect_detected, confidence, defect_details = self.detector.detect_defects(frame)
                        
                        # Draw results
                        frame = self.detector.draw_detection_results(frame, defect_details)
                        
                        # Update status
                        if defect_detected:
                            self.detection_label.setText(f"Defects detected! Confidence: {confidence:.2f}")
                            self.detection_label.setStyleSheet("color: red;")
                        else:
                            self.detection_label.setText("No defects detected")
                            self.detection_label.setStyleSheet("color: green;")
                    except Exception as e:
                        print(f"Error in detection: {str(e)}")
                        self.detection_label.setText("Detection error")
                        self.detection_label.setStyleSheet("color: yellow;")
                
                # Convert to RGB for display
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to QImage
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                
                # Scale and display
                pixmap = QPixmap.fromImage(q_image)
                scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
                
            except Exception as e:
                print(f"Error updating frame: {str(e)}")
                self.statusBar().showMessage(f"Error: {str(e)}")
        
    def capture_image(self):
        if self.camera is None:
            return
            
        try:
            frame = self.camera.capture_array()
            if frame is not None:
                # Create filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(self.save_directory, f"captured_image_{timestamp}.jpg")
                
                # Save the image
                cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                self.statusBar().showMessage(f"Image saved as {filename}")
                
        except Exception as e:
            print(f"Error capturing image: {str(e)}")
            self.statusBar().showMessage(f"Error capturing image: {str(e)}")
    
    def update_confidence(self):
        self.current_confidence = self.confidence_slider.value() / 100
        self.confidence_label.setText(f"Threshold: {self.current_confidence:.2f}")
    
    def closeEvent(self, event):
        self.stop_camera()
        event.accept()