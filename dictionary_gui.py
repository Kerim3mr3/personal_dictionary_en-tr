import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLineEdit, QPushButton, QLabel, QMessageBox,
                            QHBoxLayout, QFrame, QSizePolicy)
from docx import Document
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
from docx.shared import RGBColor
from deep_translator import GoogleTranslator
import asyncio
import urllib.request
from functools import lru_cache
import pandas as pd
from datetime import datetime
import os

# Veri tabanı dosyası
DATABASE_FILE = "sozluk.json"
WORD_FILE = "Personal_Dictionary.xlsx"

class DictionaryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Önce veritabanını yükle
        self.excel_file = "Personal_Dictionary.xlsx"
        self.database = self.load_database()
        
        # Sonra UI'ı başlat
        self.init_ui()
        
        # İnternet bağlantısı kontrolü
        self.internet_available = True
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.check_internet_connection)
        self.connection_timer.start(30000)
        
        # Translator'ı başlat
        self.translator = GoogleTranslator(source='en', target='tr')
        
        # İlk internet kontrolü
        self.check_internet_connection()

    def init_ui(self):
        self.setWindowTitle("Modern Sözlük Uygulaması")
        
        # İkon ekleme
        self.setWindowIcon(QIcon('images/dictionary_icon.ico'))
        
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
        self.word_count_label = QLabel(self)
        self.word_count_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 12px;
                margin-top: 5px;
            }
        """)
        self.update_word_count()  # Kelime sayısını güncelle

        # Github ve Temizle butonları için horizontal layout
        self.button_layout = QHBoxLayout()
        
        # Github butonu
        self.github_button = QPushButton("Github", self)
        self.github_button.setFixedSize(100, 30)
        self.github_button.setCursor(Qt.PointingHandCursor)
        self.github_button.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        self.github_button.clicked.connect(self.open_github)
        
        # Temizle butonu
        self.clear_button = QPushButton("Sözlüğü Temizle", self)
        self.clear_button.setFixedSize(100, 30)
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.clear_button.clicked.connect(self.clear_dictionary)
        
        # Butonları yan yana ekle
        self.button_layout.addWidget(self.github_button)
        self.button_layout.addWidget(self.clear_button)
        self.button_layout.setSpacing(10)
        self.button_layout.setAlignment(Qt.AlignCenter)
        
        # Ana layout'a kelime sayısı ve butonları ekle
        bottom_layout.addWidget(self.word_count_label, alignment=Qt.AlignCenter)
        bottom_layout.addLayout(self.button_layout)
        
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

    def load_database(self):
        """Excel dosyasından veritabanını yükle"""
        try:
            if os.path.exists(self.excel_file):
                df = pd.read_excel(self.excel_file)
                return {row['English'].lower(): row['Turkish'] for _, row in df.iterrows()}
            else:
                # İlk kez çalıştırılıyorsa boş Excel dosyası oluştur
                df = pd.DataFrame(columns=['English', 'Turkish', 'Date'])
                
                # Excel yazıcı oluştur
                with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                    
                    # Excel çalışma sayfasını al
                    worksheet = writer.sheets['Sheet1']
                    
                    # Başlık satırını sarı yap
                    from openpyxl.styles import PatternFill
                    yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
                    
                    # Başlıkları formatla
                    for cell in worksheet[1]:
                        cell.fill = yellow_fill
                    
                    # Sütun genişliklerini ayarla
                    worksheet.column_dimensions['A'].width = 20
                    worksheet.column_dimensions['B'].width = 20
                    worksheet.column_dimensions['C'].width = 15
                
                return {}
        except Exception as e:
            print(f"Excel okuma hatası: {e}")
            return {}

    def save_word(self):
        """Yeni kelimeyi Excel'e kaydet"""
        try:
            word = self.word_input.text().strip().lower()
            meaning = self.meaning_input.text().strip()
            
            if not word or not meaning:
                QMessageBox.warning(self, "Uyarı", "Kelime ve anlamı boş olamaz!")
                return

            # Mevcut Excel dosyasını oku
            if os.path.exists(self.excel_file):
                df = pd.read_excel(self.excel_file)
            else:
                df = pd.DataFrame(columns=['English', 'Turkish', 'Date'])

            # Kelime zaten var mı kontrol et
            if word in df['English'].str.lower().values:
                QMessageBox.warning(self, "Uyarı", "Bu kelime zaten sözlükte mevcut!")
                return

            # Yeni satır ekle
            new_row = {
                'English': word,
                'Turkish': meaning,
                'Date': datetime.now().strftime("%Y-%m-%d")  # Sadece tarih bilgisi
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # Excel yazıcı oluştur
            with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
                
                # Excel çalışma sayfasını al
                worksheet = writer.sheets['Sheet1']
                
                # Başlık satırını sarı yap
                from openpyxl.styles import PatternFill, Font
                yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
                red_font = Font(color='FF0000')
                blue_font = Font(color='0000FF')
                
                # Başlıkları formatla
                for cell in worksheet[1]:
                    cell.fill = yellow_fill
                
                # Sütunları formatla (2. satırdan itibaren)
                for row in worksheet.iter_rows(min_row=2):
                    # İngilizce kelimeler kırmızı
                    row[0].font = red_font
                    # Türkçe kelimeler mavi
                    row[1].font = blue_font
                
                # Sütun genişliklerini ayarla
                worksheet.column_dimensions['A'].width = 20
                worksheet.column_dimensions['B'].width = 20
                worksheet.column_dimensions['C'].width = 15
            
            # RAM'deki sözlüğü güncelle
            self.database[word] = meaning

            self.result_label.setText(f"'{word}' kelimesi başarıyla kaydedildi!")
            self.result_label.setStyleSheet("color: #27ae60;")
            self.word_input.clear()
            self.meaning_input.clear()
            self.hide_input_fields()

            # Kelime kaydedildikten sonra sayıyı güncelle
            self.update_word_count()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kayıt sırasında hata oluştu: {str(e)}")

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

    def check_internet_connection(self):
        """İnternet bağlantısını kontrol et"""
        try:
            urllib.request.urlopen('http://google.com', timeout=1)
            was_available = self.internet_available
            self.internet_available = True
            
            # Eğer internet yeni bağlandıysa kullanıcıyı bilgilendir
            if not was_available:
                self.result_label.setText("İnternet bağlantısı kuruldu!")
                self.result_label.setStyleSheet("color: #27ae60;")
        except:
            was_available = self.internet_available
            self.internet_available = False
            
            # Eğer internet yeni kesildiyse kullanıcıyı bilgilendir
            if was_available:
                QMessageBox.warning(
                    self,
                    "Bağlantı Hatası",
                    "İnternet bağlantısı kesildi!\n\n"
                    "• Çeviri özelliği çalışmayacak\n"
                    "• Mevcut kelimeler görüntülenebilir\n"
                    "• Yeni kelime eklemek için internet bağlantısı gerekli",
                    QMessageBox.Ok
                )

    def search_word(self):
        try:
            word = self.word_input.text().strip().lower()
            if not word:
                self.result_label.setText("Lütfen bir kelime girin!")
                self.result_label.setStyleSheet("color: #e74c3c;")
                return

            # Veritabanı araması (RAM'den)
            if word in self.database:
                message = (
                    f"Bu kelime sözlüğünüzde bulunuyor!\n\n"
                    f"İngilizce: {word}\n"
                    f"Türkçe Anlamı: {self.database[word]}"
                )
                self.result_label.setText(message)
                self.result_label.setStyleSheet("color: #27ae60;")  # Yeşil renk
                self.hide_input_fields()
                return

            # İnternet bağlantısı kontrolü artık daha hızlı
            if self.internet_available:
                translated_word = self.translate_word(word)
                message = (
                    "Bu kelime sözlüğünüzde bulunmuyor.\n\n"
                    f"Önerilen Türkçe karşılığı: {translated_word}\n\n"
                    "Kaydetmek isterseniz Türkçe anlamını girin."
                )
            else:
                message = (
                    "Bu kelime sözlüğünüzde bulunmuyor.\n\n"
                    "Çeviri için internet bağlantısı gerekli.\n"
                    "Lütfen bağlantınızı kontrol edin."
                )
                translated_word = ""
            
            self.show_input_fields(message, translated_word)

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {str(e)}")

    @lru_cache(maxsize=1000)  # Son 1000 çeviriyi önbellekte tut
    def translate_word(self, word):
        """Google Translate API kullanarak çeviri yap"""
        try:
            if not self.internet_available:
                return "İnternet bağlantısı yok"
            
            translation = self.translator.translate(text=word)
            return translation
        except Exception as e:
            print(f"Çeviri hatası: {e}")
            return "çeviri yapılamadı"

    def add_word(self):
        """Yeni kelime ekle butonuna tıklandığında"""
        try:
            word = self.word_input.text().strip().lower()
            meaning = self.meaning_input.text().strip()
            
            if not word or not meaning:
                QMessageBox.warning(self, "Uyarı", "Kelime ve anlamı boş olamaz!")
                return

            # Kelimeyi kaydet
            self.save_word()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kelime eklenirken hata oluştu: {str(e)}")

    def update_word_count(self):
        """Kelime sayısını güncelle"""
        count = len(self.database)
        self.word_count_label.setText(f"Sözlüğünüzde {count} kelime bulunuyor")

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
        super().closeEvent(event)

    def cancel_add(self):
        """İptal butonuna tıklandığında"""
        self.word_input.clear()
        self.meaning_input.clear()
        self.hide_input_fields()
        self.result_label.clear()

    def open_github(self):
        """GitHub sayfasını aç"""
        import webbrowser
        webbrowser.open('https://github.com/Kerim3mr3/personal_dictionary_en-tr')

    def hide_input_fields(self):
        """Input alanlarını gizle"""
        self.meaning_input.setVisible(False)
        self.add_button.setVisible(False)
        self.cancel_button.setVisible(False)
        self.meaning_label.setVisible(False)

    def show_input_fields(self, message, translated_word=""):
        """Input alanlarını göster"""
        self.result_label.setText(message)
        self.result_label.setStyleSheet("color: #e74c3c;")
        self.meaning_label.setVisible(True)
        self.meaning_input.setVisible(True)
        self.meaning_input.setText(translated_word)
        self.add_button.setVisible(True)
        self.cancel_button.setVisible(True)
        self.meaning_input.setFocus()

    def clear_dictionary(self):
        """Sözlüğü temizle"""
        reply = QMessageBox.question(
            self,
            'Sözlüğü Temizle',
            'Tüm sözlük verileri silinecek. Bu işlem geri alınamaz!\n\nDevam etmek istediğinize emin misiniz?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # Varsayılan seçenek No
        )

        if reply == QMessageBox.Yes:
            try:
                # Boş DataFrame oluştur
                df = pd.DataFrame(columns=['English', 'Turkish', 'Date'])
                
                # Excel yazıcı oluştur
                with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                    
                    # Excel çalışma sayfasını al
                    worksheet = writer.sheets['Sheet1']
                    
                    # Başlık satırını sarı yap
                    from openpyxl.styles import PatternFill
                    yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
                    
                    # Başlıkları formatla
                    for cell in worksheet[1]:
                        cell.fill = yellow_fill
                    
                    # Sütun genişliklerini ayarla
                    worksheet.column_dimensions['A'].width = 20
                    worksheet.column_dimensions['B'].width = 20
                    worksheet.column_dimensions['C'].width = 15

                # RAM'deki sözlüğü temizle
                self.database.clear()
                
                # Input alanlarını temizle
                self.word_input.clear()
                self.meaning_input.clear()
                self.result_label.clear()
                self.hide_input_fields()
                
                # Başarı mesajı göster
                QMessageBox.information(
                    self,
                    "Başarılı",
                    "Sözlük başarıyla temizlendi!",
                    QMessageBox.Ok
                )
                
                # Sonuç etiketini güncelle
                self.result_label.setText("Sözlük temizlendi!")
                self.result_label.setStyleSheet("color: #27ae60;")

                # Sözlük temizlendikten sonra sayıyı güncelle
                self.update_word_count()

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Hata",
                    f"Sözlük temizlenirken bir hata oluştu:\n{str(e)}",
                    QMessageBox.Ok
                )

def main():
    app = QApplication(sys.argv)
    window = DictionaryApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 