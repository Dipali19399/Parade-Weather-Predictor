import sys
import os
import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QScrollArea, QFrame, 
                             QPushButton, QLineEdit, QStackedWidget, QSizePolicy,
                             QGraphicsDropShadowEffect, QMessageBox, QFileDialog,
                             QDateEdit, QComboBox, QGroupBox, QTextEdit, QGridLayout,
                             QScrollBar)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty, QPoint, QDate
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient, QPalette, QFontDatabase

# Import your backend
from backend import WeatherPredictor

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedHeight(45)
        self.setStyleSheet("""
            CustomTitleBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1565C0, stop:0.5 #1976D2, stop:1 #1E88E5);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 2px solid #42A5F5;
            }
        """)
        
        # Add blue shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(33, 150, 243, 150))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 8, 15, 8)
        layout.setSpacing(15)
        
        # App icon and title
        title_layout = QHBoxLayout()
        title_layout.setSpacing(12)
        
        # App icon
        icon_label = QLabel("🌤️")
        icon_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 5px;
            }
        """)
        title_layout.addWidget(icon_label)
        
        # Title label
        title_label = QLabel("Parade Weather Predictor")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: 600;
                font-family: 'Segoe UI';
            }
        """)
        title_layout.addWidget(title_label)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Window controls with better styling
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        
        # Minimize button
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setFixedSize(28, 28)
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.35);
            }
        """)
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        
        # Maximize/Restore button
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setFixedSize(28, 28)
        self.maximize_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.35);
            }
        """)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        
        # Close button
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 100, 100, 0.3);
                border: 1px solid rgba(255, 100, 100, 0.5);
                border-radius: 5px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 100, 100, 0.5);
                border: 1px solid rgba(255, 100, 100, 0.7);
            }
            QPushButton:pressed {
                background: rgba(255, 100, 100, 0.7);
            }
        """)
        self.close_btn.clicked.connect(self.parent.close)
        
        controls_layout.addWidget(self.minimize_btn)
        controls_layout.addWidget(self.maximize_btn)
        controls_layout.addWidget(self.close_btn)
        layout.addLayout(controls_layout)
        
        self.setLayout(layout)
        
        # Dragging functionality
        self.dragging = False
        self.drag_position = QPoint()
        
    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.maximize_btn.setText("□")
        else:
            self.parent.showMaximized()
            self.maximize_btn.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragging:
            self.parent.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

class ModernWeatherInputPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumHeight(400)  # Use minimum height instead of fixed
        self.setMinimumWidth(550)
        self.setMaximumWidth(650)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.setStyleSheet("""
            ModernWeatherInputPanel {
                background: rgba(20, 25, 35, 0.95);
                border-radius: 20px;
                border: 2px solid rgba(66, 165, 245, 0.3);
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(35, 25, 35, 25)  # Reduced margins slightly
        layout.setSpacing(20)
        
        # Title with icon
        title_layout = QHBoxLayout()
        title_icon = QLabel("🌤️")
        title_icon.setStyleSheet("color: #4FC3F7; font-size: 28px;")
        title_layout.addWidget(title_icon)
        
        title = QLabel("Weather Prediction")
        title.setStyleSheet("""
            QLabel {
                color: #E3F2FD;
                font-size: 22px;
                font-weight: 600;
                font-family: 'Segoe UI';
            }
        """)
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Input grid layout
        input_grid = QGridLayout()
        input_grid.setVerticalSpacing(20)  # Space between rows
        input_grid.setHorizontalSpacing(25)  # Space between columns
        
        # City input
        city_label = QLabel("City Name:")
        city_label.setStyleSheet("""
            QLabel {
                color: #BBDEFB; 
                font-size: 14px; 
                font-weight: 500;
                padding: 5px 0px;
            }
        """)
        city_label.setMinimumWidth(120)  # Ensure consistent label width
        self.city_input = ModernLineEdit()
        self.city_input.setPlaceholderText("Enter city name")
        self.city_input.setText("Simlak")
        input_grid.addWidget(city_label, 0, 0, Qt.AlignLeft)
        input_grid.addWidget(self.city_input, 0, 1)
        
        # State input
        state_label = QLabel("State:")
        state_label.setStyleSheet("""
            QLabel {
                color: #BBDEFB; 
                font-size: 14px; 
                font-weight: 500;
                padding: 5px 0px;
            }
        """)
        state_label.setMinimumWidth(120)
        self.state_input = ModernLineEdit()
        self.state_input.setPlaceholderText("Enter state name")
        self.state_input.setText("Gujarat")
        input_grid.addWidget(state_label, 1, 0, Qt.AlignLeft)
        input_grid.addWidget(self.state_input, 1, 1)
        
        # Country input
        country_label = QLabel("Country:")
        country_label.setStyleSheet("""
            QLabel {
                color: #BBDEFB; 
                font-size: 14px; 
                font-weight: 500;
                padding: 5px 0px;
            }
        """)
        country_label.setMinimumWidth(120)
        self.country_input = ModernLineEdit()
        self.country_input.setPlaceholderText("Enter country name")
        self.country_input.setText("India")
        input_grid.addWidget(country_label, 2, 0, Qt.AlignLeft)
        input_grid.addWidget(self.country_input, 2, 1)
        
        # Date input
        date_label = QLabel("Prediction Date:")
        date_label.setStyleSheet("""
            QLabel {
                color: #BBDEFB; 
                font-size: 14px; 
                font-weight: 500;
                padding: 5px 0px;
            }
        """)
        date_label.setMinimumWidth(120)
        self.date_input = ModernDateEdit()
        self.date_input.setDate(QDate.currentDate().addDays(30))
        input_grid.addWidget(date_label, 3, 0, Qt.AlignLeft)
        input_grid.addWidget(self.date_input, 3, 1)
        
        # Set column stretch to make input fields expand
        input_grid.setColumnStretch(1, 1)
        
        layout.addLayout(input_grid)
        
        # Add spacing before button
        layout.addSpacing(15)
        
        # Predict button with modern style
        predict_btn = QPushButton("🔮 Predict Weather")
        predict_btn.setFixedHeight(48)
        predict_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #42A5F5, stop:1 #1E88E5);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                font-family: 'Segoe UI';
                padding: 12px;
                margin: 5px 0px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #64B5F6, stop:1 #2196F3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1E88E5, stop:1 #1976D2);
            }
        """)
        predict_btn.clicked.connect(self.predict_weather)
        layout.addWidget(predict_btn)
        
        self.setLayout(layout)
    
    def predict_weather(self):
        city = self.city_input.text().strip()
        state = self.state_input.text().strip()
        country = self.country_input.text().strip()
        date = self.date_input.date().toString("yyyy-MM-dd")
        
        if not city or not state or not country:
            QMessageBox.warning(self, "Input Error", "Please fill in all location fields.")
            return
        
        self.parent.predict_weather(city, state, country, date)

class ModernLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            ModernLineEdit {
                background: rgba(255, 255, 255, 0.12);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 12px 15px;
                color: #E3F2FD;
                font-size: 14px;
                font-family: 'Segoe UI';
                selection-background-color: #2196F3;
            }
            ModernLineEdit:focus {
                border: 2px solid #42A5F5;
                background: rgba(255, 255, 255, 0.15);
            }
            ModernLineEdit:hover {
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
        """)
        self.setMinimumHeight(45)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

class ModernDateEdit(QDateEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCalendarPopup(True)
        self.setStyleSheet("""
            ModernDateEdit {
                background: rgba(255, 255, 255, 0.12);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 10px 15px;
                color: #E3F2FD;
                font-size: 14px;
                font-family: 'Segoe UI';
                min-height: 20px;
            }
            ModernDateEdit:focus {
                border: 2px solid #42A5F5;
                background: rgba(255, 255, 255, 0.15);
            }
            ModernDateEdit:hover {
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            ModernDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid rgba(255, 255, 255, 0.2);
            }
            ModernDateEdit::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #BBDEFB;
                width: 0px;
                height: 0px;
            }
        """)
        self.setMinimumHeight(45)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Fix calendar styling
        self.calendarWidget().setStyleSheet("""
            QCalendarWidget {
                background: rgba(25, 30, 40, 0.98);
                border: 2px solid rgba(66, 165, 245, 0.3);
                border-radius: 10px;
                color: #E3F2FD;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QCalendarWidget QWidget {
                alternate-background-color: rgba(255, 255, 255, 0.05);
            }
            QCalendarWidget QToolButton {
                background: rgba(66, 165, 245, 0.2);
                color: #E3F2FD;
                font-size: 13px;
                font-weight: 600;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                margin: 2px;
            }
            QCalendarWidget QToolButton:hover {
                background: rgba(66, 165, 245, 0.4);
            }
            QCalendarWidget QMenu {
                background: rgba(30, 35, 45, 0.98);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: #E3F2FD;
                font-family: 'Segoe UI';
            }
            QCalendarWidget QSpinBox {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                color: #E3F2FD;
                padding: 5px;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background: rgba(255, 255, 255, 0.05);
                color: #E3F2FD;
                selection-background-color: #42A5F5;
                selection-color: white;
                outline: 0;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: rgba(255, 255, 255, 0.3);
            }
        """)

class PredictionResultCard(QFrame):
    def __init__(self, title, value, unit="", icon="", parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.setStyleSheet("""
            PredictionResultCard {
                background: rgba(30, 35, 45, 0.9);
                border-radius: 15px;
                border: 1px solid rgba(66, 165, 245, 0.2);
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)
        
        # Title with icon
        title_layout = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("color: #4FC3F7; font-size: 18px;")
            title_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #BBDEFB;
                font-size: 13px;
                font-weight: 500;
                font-family: 'Segoe UI';
                letter-spacing: 0.5px;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Value
        value_label = QLabel(f"{value}{unit}")
        value_label.setStyleSheet("""
            QLabel {
                color: #E3F2FD;
                font-size: 32px;
                font-weight: 300;
                font-family: 'Segoe UI';
            }
        """)
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        self.setLayout(layout)

class WeatherConditionDisplay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            WeatherConditionDisplay {
                background: rgba(25, 30, 40, 0.95);
                border-radius: 20px;
                border: 2px solid rgba(66, 165, 245, 0.3);
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)
        
        # Current weather section
        current_layout = QVBoxLayout()
        current_layout.setSpacing(10)
        current_layout.setAlignment(Qt.AlignCenter)
        
        self.temp_label = QLabel("--°")
        self.temp_label.setStyleSheet("""
            QLabel {
                color: #E3F2FD;
                font-size: 64px;
                font-weight: 200;
                font-family: 'Segoe UI';
            }
        """)
        self.temp_label.setAlignment(Qt.AlignCenter)
        current_layout.addWidget(self.temp_label)
        
        self.condition_label = QLabel("Enter location to get weather prediction")
        self.condition_label.setStyleSheet("""
            QLabel {
                color: #BBDEFB;
                font-size: 20px;
                font-weight: 400;
                font-family: 'Segoe UI';
            }
        """)
        self.condition_label.setAlignment(Qt.AlignCenter)
        current_layout.addWidget(self.condition_label)
        
        self.location_label = QLabel("Simlak, Gujarat")
        self.location_label.setStyleSheet("""
            QLabel {
                color: #90CAF9;
                font-size: 16px;
                font-weight: 300;
                font-family: 'Segoe UI';
            }
        """)
        self.location_label.setAlignment(Qt.AlignCenter)
        current_layout.addWidget(self.location_label)
        
        layout.addLayout(current_layout)
        
        # Day type section
        self.day_type_frame = QFrame()
        self.day_type_frame.setStyleSheet("""
            QFrame {
                background: rgba(66, 165, 245, 0.15);
                border-radius: 12px;
                border: 1px solid rgba(66, 165, 245, 0.3);
            }
        """)
        day_type_layout = QVBoxLayout(self.day_type_frame)
        day_type_layout.setContentsMargins(20, 12, 20, 12)
        
        self.day_type_label = QLabel("Weather Condition")
        self.day_type_label.setStyleSheet("""
            QLabel {
                color: #4FC3F7;
                font-size: 18px;
                font-weight: 600;
                font-family: 'Segoe UI';
                text-align: center;
            }
        """)
        day_type_layout.addWidget(self.day_type_label)
                        
        self.confidence_label = QLabel("Select date and location to predict")
        self.confidence_label.setStyleSheet("""
            QLabel {
                color: #81D4FA;
                font-size: 13px;
                font-weight: 400;
                font-family: 'Segoe UI';
                text-align: center;
            }
        """)
        day_type_layout.addWidget(self.confidence_label)
        
        layout.addWidget(self.day_type_frame)
        
        # Metrics grid
        metrics_layout = QGridLayout()
        metrics_layout.setVerticalSpacing(15)
        metrics_layout.setHorizontalSpacing(15)
        
        self.metrics = {}
        metric_configs = [
            ("🌡️", "TEMPERATURE", "temp_card", 0, 0),
            ("🌧️", "RAIN PROBABILITY", "rain_prob_card", 0, 1),
            ("💧", "EXPECTED RAINFALL", "rainfall_card", 1, 0),
            ("💨", "WIND SPEED", "wind_card", 1, 1)
        ]
        
        for icon, title, name, row, col in metric_configs:
            card = PredictionResultCard(title, "--", "", icon)
            self.metrics[name] = card
            metrics_layout.addWidget(card, row, col)
        
        layout.addLayout(metrics_layout)
        self.setLayout(layout)
    
    def update_display(self, prediction_data):
        if not prediction_data:
            return
        
        # Update main weather info
        self.temp_label.setText(f"{prediction_data.get('temperature', '--')}°")
        self.condition_label.setText(prediction_data.get('condition', 'Unknown'))
        self.location_label.setText(f"{prediction_data.get('city', '')}, {prediction_data.get('state', '')}")
        
        # Update day type
        self.day_type_label.setText(prediction_data.get('day_type_description', 'Unknown'))
        self.confidence_label.setText(f"ML Confidence: {prediction_data.get('ml_confidence', 0)}%")
        
        # Update metrics
        self.metrics['temp_card'].layout().itemAt(1).widget().setText(f"{prediction_data.get('temperature', '--')}")
        self.metrics['rain_prob_card'].layout().itemAt(1).widget().setText(f"{prediction_data.get('rain_probability', '--')}")
        self.metrics['rainfall_card'].layout().itemAt(1).widget().setText(f"{prediction_data.get('expected_rainfall', '--')}")
        self.metrics['wind_card'].layout().itemAt(1).widget().setText(f"{prediction_data.get('wind_speed', '--')}")

class ProfessionalImageBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation_type = "default"
        self.images = {}
        self.load_images()
        self.current_opacity = 1.0
        self.target_opacity = 1.0
        
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        
        self.fade_timer = QTimer(self)
        self.fade_timer.timeout.connect(self.update_fade)
        self.fade_timer.start(50)
        
    def load_images(self):
        # Get the directory where frontend.py is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(current_dir, "images")
        
        # Define image mappings with exact file names in your images folder
        image_mappings = {
            "default": ["default.jpg"],
            "sunny": ["sunny.jpg", "sunny.png", "sunny.avif", "sunny.webp"],
            "cloudy": ["cloudy.jpg", "cloudy.png", "cloudy.avif", "cloudy.webp", "overcast.jpg"],
            "rainy": ["rainy.jpg", "rainy.png", "rainy.avif", "rainy.webp", "rain.jpg"],
            "thunderstorm": ["thunderstorm.webp", "thunderstrom.webp", "thunderstorm.jpg", "thunderstorm.png", "thunderstorm.avif", "storm.jpg"],
            "night": ["night.jpg", "night.png", "night.avif", "night.webp", "clear_night.jpg"],
            "snowy": [ "tmp.jpeg", "snowy.png", "snowy.avif", "snowy.webp", "snow.jpg"],
            "foggy": [ "tmp.jpeg", "foggy.png", "foggy.avif", "foggy.webp", "fog.jpg"],
            "windy": [ "tmp.jpeg", "windy.png", "windy.avif", "windy.webp"]
        }
        
        print(f"📁 Looking for images in: {images_dir}")
        
        for weather_type, filenames in image_mappings.items():
            self.images[weather_type] = None
            
            # First try the images directory
            for filename in filenames:
                image_path = os.path.join(images_dir, filename)
                if os.path.exists(image_path):
                    try:
                        pixmap = QPixmap(image_path)
                        if not pixmap.isNull():
                            self.images[weather_type] = pixmap
                            print(f"✅ Loaded background image: {image_path}")
                            break
                    except Exception as e:
                        print(f"❌ Error loading {image_path}: {e}")
            
            # If not found in images directory, try current directory
            if self.images[weather_type] is None:
                for filename in filenames:
                    image_path = os.path.join(current_dir, filename)
                    if os.path.exists(image_path):
                        try:
                            pixmap = QPixmap(image_path)
                            if not pixmap.isNull():
                                self.images[weather_type] = pixmap
                                print(f"✅ Loaded background image: {image_path}")
                                break
                        except Exception as e:
                            print(f"❌ Error loading {image_path}: {e}")
            
            # If still not found, create fallback
            if self.images[weather_type] is None:
                self.create_fallback_image(weather_type)
                print(f"⚠️ Using fallback background for: {weather_type}")
        
        # Print summary of loaded images
        loaded_count = sum(1 for img in self.images.values() if img is not None)
        print(f"📊 Loaded {loaded_count}/{len(self.images)} background images")
        
    def create_fallback_image(self, weather_type):
        pixmap = QPixmap(800, 600)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        color_schemes = {
            "default": [(30, 40, 50), (20, 30, 40)],
            "sunny": [(255, 193, 7), (255, 152, 0)],
            "cloudy": [(120, 144, 156), (84, 110, 122)],
            "rainy": [(69, 90, 100), (55, 71, 79)],
            "thunderstorm": [(38, 50, 56), (26, 35, 39)],
            "night": [(26, 35, 39), (13, 19, 23)],
            "snowy": [(224, 247, 250), (178, 235, 242)],
            "foggy": [(176, 190, 197), (144, 164, 174)],
            "windy": [(129, 212, 250), (66, 165, 245)]
        }
        
        colors = color_schemes.get(weather_type, [(30, 40, 50), (20, 30, 40)])
        gradient = QLinearGradient(0, 0, 0, 600)
        gradient.setColorAt(0, QColor(*colors[0]))
        gradient.setColorAt(1, QColor(*colors[1]))
        painter.fillRect(pixmap.rect(), gradient)
        
        painter.end()
        self.images[weather_type] = pixmap
                
    def set_animation_type(self, anim_type):
        if anim_type != self.animation_type:
            self.animation_type = anim_type
            self.target_opacity = 0.0
            self.update()
                
    def update_fade(self):
        if self.current_opacity != self.target_opacity:
            if self.target_opacity == 0.0:
                self.current_opacity = max(0.0, self.current_opacity - 0.05)
                if self.current_opacity == 0.0:
                    self.target_opacity = 1.0
            else:
                self.current_opacity = min(1.0, self.current_opacity + 0.05)
            self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
        
        if self.animation_type in self.images and self.images[self.animation_type] is not None:
            pixmap = self.images[self.animation_type]
            scaled_pixmap = pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            painter.setOpacity(self.current_opacity)
            painter.drawPixmap(x, y, scaled_pixmap)
        else:
            painter.setOpacity(self.current_opacity)
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor(30, 40, 50))
            gradient.setColorAt(1, QColor(20, 30, 40))
            painter.fillRect(self.rect(), gradient)
        painter.end()

class ScrollableContentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(25)
        
        # Header with time and title
        header_frame = QFrame()
        header_frame.setStyleSheet("QFrame { background: transparent; border: none; }")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        
        # App title
        title_label = QLabel("Parade Weather Predictor")
        title_label.setStyleSheet("""
            QLabel {
                color: #E3F2FD;
                font-size: 28px;
                font-weight: 300;
                font-family: 'Segoe UI';
                text-align: center;
                background: rgba(30, 35, 45, 0.8);
                border-radius: 12px;
                padding: 15px;
                border: 1px solid rgba(66, 165, 245, 0.2);
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Time display
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                color: #BBDEFB;
                font-size: 15px;
                font-weight: 400;
                font-family: 'Segoe UI';
                background: rgba(35, 40, 50, 0.8);
                border-radius: 10px;
                padding: 10px 20px;
                border: 1px solid rgba(66, 165, 245, 0.2);
            }
        """)
        self.time_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.time_label)
        
        layout.addWidget(header_frame)
        
        # Centered input panel
        input_container = QWidget()
        input_container.setStyleSheet("QWidget { background: transparent; }")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        input_layout.addStretch()
        self.input_panel = ModernWeatherInputPanel(self.parent())
        input_layout.addWidget(self.input_panel)
        input_layout.addStretch()
        
        layout.addWidget(input_container)
        
        # Add spacing between input and prediction
        layout.addSpacing(20)
        
        # Prediction display panel
        self.prediction_panel = WeatherConditionDisplay()
        self.prediction_panel.setVisible(False)
        layout.addWidget(self.prediction_panel)
        
        # Add stretchable space at the bottom
        layout.addStretch()

class ProfessionalWeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parade Weather Predictor")
        self.setGeometry(100, 100, 1200, 900)
        self.setMinimumSize(1100, 800)
        
        # Remove default title bar and set frameless window
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Initialize backend
        self.weather_predictor = None
        self.setup_backend()
        
        self.setup_ui()
        self.setup_animations()
        
    def setup_backend(self):
        try:
            self.weather_predictor = WeatherPredictor()
            print("✅ Backend initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing backend: {e}")
            QMessageBox.critical(self, "Backend Error", 
                               f"Failed to initialize weather predictor: {str(e)}")
    
    def setup_ui(self):
        central_widget = QWidget()
        central_widget.setAttribute(Qt.WA_TranslucentBackground)
        central_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(20, 25, 35, 0.98), 
                    stop:1 rgba(30, 35, 45, 0.98));
                border-radius: 12px;
                border: 1px solid rgba(66, 165, 245, 0.2);
            }
        """)
        self.setCentralWidget(central_widget)
        
        # Main vertical layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add custom title bar with blue shadow
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
                outline: none;
            }
            QScrollBar:vertical {
                background: rgba(30, 35, 45, 0.8);
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: rgba(66, 165, 245, 0.6);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(66, 165, 245, 0.8);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # Create scrollable content widget
        self.scroll_content = ScrollableContentWidget(self)
        self.scroll_area.setWidget(self.scroll_content)
        
        main_layout.addWidget(self.scroll_area)
        
        # Background widget
        self.background = ProfessionalImageBackground(central_widget)
        self.background.lower()
        
    def setup_animations(self):
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()
        
    def predict_weather(self, city, state, country, date):
        if not self.weather_predictor:
            QMessageBox.critical(self, "Error", "Weather predictor not initialized!")
            return
        
        try:
            # Show loading state
            self.scroll_content.prediction_panel.condition_label.setText("Predicting weather...")
            self.scroll_content.prediction_panel.temp_label.setText("...")
            
            # Show prediction panel
            self.scroll_content.prediction_panel.setVisible(True)
            
            # Make prediction using backend
            prediction = self.weather_predictor.predict_single_day(city, state, country, date)
            
            if isinstance(prediction, str):
                # Error case
                QMessageBox.warning(self, "Prediction Error", prediction)
                self.scroll_content.prediction_panel.condition_label.setText("Prediction failed")
                self.scroll_content.prediction_panel.temp_label.setText("--°")
            else:
                # Success case - update UI
                self.update_ui_with_prediction(prediction)
                
        except Exception as e:
            QMessageBox.critical(self, "Prediction Error", f"An error occurred: {str(e)}")
            self.scroll_content.prediction_panel.condition_label.setText("Prediction error")
            self.scroll_content.prediction_panel.temp_label.setText("--°")
    
    def update_ui_with_prediction(self, prediction):
        # Update prediction display
        self.scroll_content.prediction_panel.update_display(prediction)
        
        # Update background based on day type
        day_type = prediction.get('day_type', 'sunny')
        weather_mapping = {
            'thunderstorm': 'thunderstorm',
            'heavy_rain': 'rainy',
            'rainy': 'rainy',
            'moderate_rain': 'rainy',
            'light_rain': 'cloudy',
            'cloudy_rainy': 'cloudy',
            'cloudy': 'cloudy',
            'sunny_hot': 'sunny',
            'sunny_warm': 'sunny',
            'sunny_pleasant': 'sunny',
            'sunny_cool': 'sunny',
            'sunny_cold': 'sunny'
        }
        
        background_type = weather_mapping.get(day_type, 'default.jpg')
        self.background.set_animation_type(background_type)
        
    def update_time(self):
        current_time = datetime.now().strftime("%I:%M %p").lstrip('0')
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        self.scroll_content.time_label.setText(f"🕒 {current_time} • {current_date}")
        
    def resizeEvent(self, event):
        self.background.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

def create_sample_images():
    """Create sample images directory if needed"""
    if not os.path.exists("images"):
        os.makedirs("images")
        print("📁 Created 'images' directory for weather backgrounds")

if __name__ == "__main__":
    create_sample_images()
    
    app = QApplication(sys.argv)
    
    # Set modern font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    app.setStyle("Fusion")
    app.setAttribute(Qt.AA_UseSoftwareOpenGL)
    
    window = ProfessionalWeatherApp()
    window.show()
    
    sys.exit(app.exec_())