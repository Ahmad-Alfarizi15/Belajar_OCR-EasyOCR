import sys
import easyocr
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit, QMessageBox, QFrame
)
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt
import os

# Fix error libiomp
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

class OCRApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📖 OCR EasyOCR GUI")
        self.setGeometry(200, 100, 900, 650)
        self.setStyleSheet("background-color: #f4f4f9;")

        # OCR reader
        self.reader = easyocr.Reader(['en', 'id'])

        # Label Gambar
        self.label_image = QLabel("📷 Gambar akan ditampilkan di sini")
        self.label_image.setAlignment(Qt.AlignCenter)
        self.label_image.setFixedSize(600, 400)
        self.label_image.setFrameShape(QFrame.StyledPanel)
        self.label_image.setStyleSheet(
            "background-color: white; border: 2px dashed #aaa; font-size: 14px;"
        )

        # Tombol
        self.btn_open = QPushButton("📂 Buka Gambar")
        self.btn_open.setStyleSheet(self.button_style())
        self.btn_open.clicked.connect(self.open_image)

        self.btn_ocr = QPushButton("🔍 Jalankan OCR")
        self.btn_ocr.setStyleSheet(self.button_style())
        self.btn_ocr.clicked.connect(self.run_ocr)
        self.btn_ocr.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_open)
        button_layout.addWidget(self.btn_ocr)

        # Output OCR
        self.label_output = QLabel("📝 Hasil OCR:")
        self.label_output.setFont(QFont("Arial", 11, QFont.Bold))
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setStyleSheet(
            "background-color: white; border: 1px solid #ccc; font-size: 13px;"
        )

        # Layout utama
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.addWidget(self.label_image, alignment=Qt.AlignCenter)
        layout.addLayout(button_layout)
        layout.addWidget(self.label_output)
        layout.addWidget(self.text_output)

        self.setLayout(layout)

        # Variabel internal
        self.image = None
        self.image_path = ""

    def button_style(self):
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Gambar", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.image_path = file_path
            self.image = cv2.imread(file_path)
            self.show_image(self.image)
            self.btn_ocr.setEnabled(True)
            self.text_output.clear()

    def show_image(self, img_cv):
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        qt_img = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img).scaled(
            self.label_image.width(), self.label_image.height(), Qt.KeepAspectRatio
        )
        self.label_image.setPixmap(pixmap)

    def run_ocr(self):
        if self.image is None:
            QMessageBox.warning(self, "Error", "⚠️ Gambar belum dipilih!")
            return

        results = self.reader.readtext(self.image)
        self.text_output.clear()

        for (bbox, text, prob) in results:
            self.text_output.append(f"{text} (confidence: {prob:.2f})")
            top_left = tuple([int(val) for val in bbox[0]])
            bottom_right = tuple([int(val) for val in bbox[2]])
            cv2.rectangle(self.image, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(
                self.image, text, top_left,
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2
            )

        self.show_image(self.image)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OCRApp()
    window.show()
    sys.exit(app.exec_())
