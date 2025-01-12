import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLineEdit, QPushButton, QLabel, QMessageBox,
                            QHBoxLayout, QFrame, QSizePolicy)
from docx import Document
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from docx.shared import RGBColor
from googletrans import Translator
import asyncio

# Veri tabanı dosyası
DATABASE_FILE = "sozluk.json"
WORD_FILE = "sozluk.docx"

class DictionaryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Sözlük Uygulaması")
        
        # İkon ekleme
        self.setWindowIcon(QIcon('dictionary_icon.ico'))
        
        self.setGeometry(100, 100, 1024, 900)
        self.setMinimumSize(1024, 900)
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(50, 30, 50, 30)
        main_widget.setLayout(layout)

        # Başlık
        title = QLabel("Modern Sözlük")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)

        # Giriş kartı
        input_card = QFrame()
        input_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 30px;
            }
        """)
        input_card.setMinimumHeight(350)
        
        input_layout = QVBoxLayout()
        input_layout.setSpacing(20)
        input_layout.setContentsMargins(30, 20, 30, 20)
        input_card.setLayout(input_layout)

        # İngilizce kelime bölümü
        eng_label = QLabel("İngilizce Kelime")
        eng_label.setFont(QFont("Arial", 12))
        eng_label.setStyleSheet("color: #2c3e50; padding: 5px;")
        input_layout.addWidget(eng_label)
        
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Aramak istediğiniz kelimeyi girin...")
        self.word_input.setMinimumHeight(40)
        self.word_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        input_layout.addWidget(self.word_input)

        # Türkçe anlam bölümü
        self.meaning_label = QLabel("Türkçe Anlam")
        self.meaning_label.setFont(QFont("Arial", 12))
        self.meaning_label.setStyleSheet("color: #2c3e50; padding: 5px;")
        input_layout.addWidget(self.meaning_label)
        
        self.meaning_input = QLineEdit()
        self.meaning_input.setPlaceholderText("Türkçe anlamını girin...")
        self.meaning_input.setMinimumHeight(40)
        self.meaning_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        input_layout.addWidget(self.meaning_input)
        
        self.meaning_label.setVisible(False)
        self.meaning_input.setVisible(False)

        # Butonlar için yatay layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.setContentsMargins(0, 20, 0, 0)
        
        # Ara butonu
        self.search_button = QPushButton("Ara")
        self.search_button.setMinimumSize(150, 45)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        # Ekle butonu
        self.add_button = QPushButton("Ekle")
        self.add_button.setMinimumSize(150, 45)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        self.add_button.setVisible(False)

        # İptal butonu eklendi
        self.cancel_button = QPushButton("İptal")
        self.cancel_button.setMinimumSize(150, 45)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.cancel_button.setVisible(False)

        # Sözlük Görüntüle butonu
        self.view_dict_button = QPushButton("Sözlüğü Görüntüle")
        self.view_dict_button.setMinimumSize(150, 45)
        self.view_dict_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)

        button_layout.addStretch()
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)  # İptal butonu eklendi
        button_layout.addWidget(self.view_dict_button)
        button_layout.addStretch()

        input_layout.addLayout(button_layout)
        layout.addWidget(input_card)

        # Sonuç kartı
        result_card = QFrame()
        result_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 30px;
                margin-top: 20px;
            }
        """)
        result_card.setMinimumHeight(250)
        
        result_layout = QVBoxLayout()
        result_layout.setContentsMargins(20, 15, 20, 15)
        result_layout.setSpacing(15)
        result_card.setLayout(result_layout)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont("Arial", 14))
        self.result_label.setWordWrap(True)
        self.result_label.setMinimumHeight(150)
        self.result_label.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 14px;
                padding: 20px;
                line-height: 1.6;
                qproperty-alignment: AlignCenter;
            }
        """)
        result_layout.addWidget(self.result_label)
        layout.addWidget(result_card)

        # Alt kısım için yatay layout
        bottom_layout = QHBoxLayout()
        
        # Kelime sayısı göstergesi
        self.word_count_label = QLabel()
        self.word_count_label.setStyleSheet("""
            color: #7f8c8d;
            font-size: 12px;
            padding: 5px;
        """)
        
        # GitHub butonu
        self.github_button = QPushButton("GitHub")
        self.github_button.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                padding: 5px 10px;
                max-width: 100px;
            }
            QPushButton:hover {
                background-color: #2c2c2c;
            }
        """)
        self.github_button.setIcon(QIcon('github_icon.png'))  # GitHub ikonu ekleyebilirsiniz
        self.github_button.clicked.connect(self.open_github)
        
        # Layout'a elemanları ekle
        bottom_layout.addWidget(self.word_count_label)
        bottom_layout.addStretch()  # Ortada boşluk bırak
        bottom_layout.addWidget(self.github_button)
        
        # Ana layout'a bottom layout'u ekle
        layout.addLayout(bottom_layout)

        # Bağlantılar
        self.word_input.returnPressed.connect(self.search_word)
        self.meaning_input.returnPressed.connect(self.add_word)
        self.search_button.clicked.connect(self.search_word)
        self.add_button.clicked.connect(self.add_word)
        self.view_dict_button.clicked.connect(self.open_dictionary)

        # İptal butonu için bağlantı eklendi
        self.cancel_button.clicked.connect(self.cancel_add)

        # Veritabanını yükle ve kelime sayısını güncelle
        self.database = self.load_database()
        self.update_word_count()

        self.translator = Translator()
        # Event loop oluştur
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def load_database(self):
        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_database(self):
        with open(DATABASE_FILE, "w", encoding="utf-8") as file:
            json.dump(self.database, file, ensure_ascii=False, indent=4)

    def update_word_file(self):
        try:
            doc = Document()
            # Başlık stili
            heading = doc.add_heading("Kişisel Sözlük", level=1)
            heading.alignment = 1  # Ortalı
            
            # Sözlüğü alfabetik sıraya göre düzenle
            for english, turkish in sorted(self.database.items()):
                paragraph = doc.add_paragraph()
                # İngilizce kelime (kalın ve kırmızı)
                eng_run = paragraph.add_run(f"{english}")
                eng_run.bold = True
                eng_run.font.color.rgb = RGBColor(255, 0, 0)  # Kırmızı
                
                # Ayraç
                paragraph.add_run(" - ")
                
                # Türkçe kelime (mavi ve normal)
                tr_run = paragraph.add_run(f"{turkish}")
                tr_run.bold = False
                tr_run.font.color.rgb = RGBColor(0, 0, 255)  # Mavi
            
            doc.save(WORD_FILE)
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Word dosyası güncellenirken hata oluştu: {e}")

    def search_word(self):
        try:
            word = self.word_input.text().strip().lower()
            if not word:
                self.result_label.setText("Lütfen bir kelime girin!")
                self.result_label.setStyleSheet("""
                    color: #e74c3c;
                    font-size: 14px;
                    padding: 20px;
                    min-height: 150px;
                    qproperty-alignment: AlignCenter;
                """)
                return

            if word in self.database:
                self.result_label.setText(f"Kelime: {word}\nTürkçe Anlamı: {self.database[word]}")
                self.result_label.setStyleSheet("""
                    color: #27ae60;
                    font-size: 14px;
                    padding: 20px;
                    min-height: 150px;
                    qproperty-alignment: AlignCenter;
                """)
                self.meaning_input.setVisible(False)
                self.add_button.setVisible(False)
                self.cancel_button.setVisible(False)  # İptal butonu gizlendi
                self.meaning_label.setVisible(False)
            else:
                translated_word = self.translate_word(word)
                
                message = (
                    "Sözlüğünüzde bu yeni kelime yok.\n\n"
                    f"Önerilen Türkçe karşılığı: {translated_word}\n\n"
                    "Kaydetmek isterseniz Türkçe anlamını girin."
                )
                
                self.result_label.setText(message)
                self.result_label.setStyleSheet("""
                    color: #e74c3c;
                    font-size: 14px;
                    padding: 20px;
                    line-height: 1.6;
                    min-height: 150px;
                    qproperty-alignment: AlignCenter;
                """)
                
                self.meaning_label.setVisible(True)
                self.meaning_input.setVisible(True)
                self.meaning_input.setText(translated_word)
                self.add_button.setVisible(True)
                self.cancel_button.setVisible(True)  # İptal butonu gösterildi
                self.meaning_input.setFocus()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {str(e)}")

    def translate_word(self, word):
        """Google Translate API kullanarak çeviri yap"""
        try:
            # İngilizce'den Türkçe'ye çeviri
            translation = self.translator.translate(word, src='en', dest='tr')
            return translation.text
        except Exception as e:
            print(f"Çeviri hatası: {e}")
            return "çeviri yapılamadı"

    def add_word(self):
        try:
            word = self.word_input.text().strip().lower()
            meaning = self.meaning_input.text().strip()

            if not meaning:
                self.result_label.setText("Lütfen Türkçe anlamı girin!")
                self.result_label.setStyleSheet("color: #e74c3c;")
                return

            self.database[word] = meaning
            self.save_database()
            self.update_word_file()
            
            self.result_label.setText(f"'{word}' kelimesi sözlüğe eklendi.")
            self.result_label.setStyleSheet("color: #27ae60;")
            self.word_input.clear()
            self.meaning_input.clear()
            self.meaning_input.setVisible(False)
            self.add_button.setVisible(False)
            self.meaning_label.setVisible(False)
            
            QMessageBox.information(self, "Başarılı", "Kelime başarıyla eklendi ve kaydedildi!")
            self.update_word_count()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {str(e)}")

    def update_word_count(self):
        """Kelime sayısını güncelle"""
        count = len(self.database)
        self.word_count_label.setText(f"Sözlükte bulunan kelime sayısı: {count}")

    def open_dictionary(self):
        """Word dosyasını aç"""
        try:
            import os
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(WORD_FILE)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open {WORD_FILE}')
            else:  # Linux
                os.system(f'xdg-open {WORD_FILE}')
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Sözlük dosyası açılırken bir hata oluştu: {e}")

    def closeEvent(self, event):
        """Uygulama kapatılırken event loop'u temizle"""
        self.loop.close()
        super().closeEvent(event)

    def cancel_add(self):
        """İptal butonuna basıldığında çağrılacak metod"""
        # Alanları temizle ve gizle
        self.meaning_input.clear()
        self.meaning_input.setVisible(False)
        self.meaning_label.setVisible(False)
        self.add_button.setVisible(False)
        self.cancel_button.setVisible(False)
        
        # Result label'ı temizle
        self.result_label.clear()
        
        # Word input'u temizle ve fokusla
        self.word_input.clear()
        self.word_input.setFocus()

    def open_github(self):
        """GitHub sayfasını aç"""
        import webbrowser
        webbrowser.open('https://github.com/Kerim3mr3/personal_dictionary_en-tr')

def main():
    app = QApplication(sys.argv)
    window = DictionaryApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 