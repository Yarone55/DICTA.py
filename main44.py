import sys
import threading
import speech_recognition as sr
import logging
from PyQt5.QtCore import QUrl, pyqtSlot
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QWidget, QComboBox, QLabel

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class WebBrowserApp(QWidget):
    def __init__(self):
        super(WebBrowserApp, self).__init__()

        self.initUI()
        self.recognizer = sr.Recognizer()
        self.audio_source = sr.Microphone()
        self.is_dictating = False  # New attribute for dictation control

    def initUI(self):
        self.setWindowTitle("Web Browser and Dictation App")

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.browser.back)

        self.forward_button = QPushButton("Forward")
        self.forward_button.clicked.connect(self.browser.forward)

        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self.browser.reload)

        self.start_button = QPushButton("Start Dictation")
        self.start_button.clicked.connect(self.start_dictation)

        self.stop_button = QPushButton("Stop Dictation")
        self.stop_button.setDisabled(True)
        self.stop_button.clicked.connect(self.stop_dictation)

        self.dictation_text = QTextEdit()

        # Create a combo box for the audio source selection
        self.source_combo = QComboBox()
        devices = sr.Microphone.list_microphone_names()
        self.source_combo.addItems(devices)
        self.source_combo.currentIndexChanged.connect(self.change_audio_source)

        # Create a label to act as a "light"
        self.light_label = QLabel()
        self.light_label.setAutoFillBackground(True)
        palette = self.light_label.palette()
        palette.setColor(QPalette.Background, QColor('red'))
        self.light_label.setPalette(palette)

        layout = QVBoxLayout()
        layout.addWidget(self.url_bar)
        layout.addWidget(self.back_button)
        layout.addWidget(self.forward_button)
        layout.addWidget(self.reload_button)
        layout.addWidget(self.source_combo)
        layout.addWidget(self.light_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.dictation_text)
        layout.addWidget(self.browser)

        self.setLayout(layout)

    @pyqtSlot()
    def navigate_to_url(self):
        url = self.url_bar.text()
        self.browser.setUrl(QUrl(url))
        logging.info(f'Navigating to {url}')

    @pyqtSlot()
    def start_dictation(self):
        self.start_button.setDisabled(True)
        self.stop_button.setDisabled(False)
        self.change_light_color('green')
        self.is_dictating = True
        self.dictation_thread = threading.Thread(target=self.dictation)
        self.dictation_thread.start()
        logging.info('Started dictation')

    @pyqtSlot()
    def stop_dictation(self):
        self.start_button.setDisabled(False)
        self.stop_button.setDisabled(True)
        self.change_light_color('red')
        self.is_dictating = False
        logging.info('Stopped dictation')

    @pyqtSlot(int)
    def change_audio_source(self, index):
        devices = sr.Microphone.list_microphone_names()
        self.audio_source = sr.Microphone(device_index=devices.index(self.source_combo.itemText(index)))
        logging.info(f'Changed audio source to {self.source_combo.itemText(index)}')

    def change_light_color(self, color):
        palette = self.light_label.palette()
        palette.setColor(QPalette.Background, QColor(color))
        self.light_label.setPalette(palette)

    def dictation(self):
        while self.is_dictating:
            with self.audio_source as source:
                self.recognizer.adjust_for_ambient_noise(source)
                try:
                    audio = self.recognizer.listen(source, timeout=5.0)
                    text = self.recognizer.recognize_google(audio, language="fr-FR")
                    self.dictation_text.append(text)
                except sr.UnknownValueError:
                    logging.error('Unknown value error')
                except sr.RequestError as e:
                    logging.error(f'Request error: {str(e)}')
                    self.dictation_text.append(
                        f"Erreur lors de la requête au service de reconnaissance vocale : {str(e)}")
                except sr.WaitTimeoutError:
                    logging.info('Listening timeout, continue listening...')
            self.audio_source = sr.Microphone()  # reinitialize the source audio


def main():
    app = QApplication(sys.argv)
    ex = WebBrowserApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
import sys
import threading
import speech_recognition as sr
import logging
from PyQt5.QtCore import QUrl, pyqtSlot
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QWidget, QComboBox, QLabel

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class WebBrowserApp(QWidget):
    def __init__(self):
        super(WebBrowserApp, self).__init__()

        self.initUI()
        self.recognizer = sr.Recognizer()
        self.audio_source = sr.Microphone()
        self.is_dictating = False  # New attribute for dictation control

    def initUI(self):
        self.setWindowTitle("Web Browser and Dictation App")

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.browser.back)

        self.forward_button = QPushButton("Forward")
        self.forward_button.clicked.connect(self.browser.forward)

        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self.browser.reload)

        self.start_button = QPushButton("Start Dictation")
        self.start_button.clicked.connect(self.start_dictation)

        self.stop_button = QPushButton("Stop Dictation")
        self.stop_button.setDisabled(True)
        self.stop_button.clicked.connect(self.stop_dictation)

        self.dictation_text = QTextEdit()

        # Create a combo box for the audio source selection
        self.source_combo = QComboBox()
        devices = sr.Microphone.list_microphone_names()
        self.source_combo.addItems(devices)
        self.source_combo.currentIndexChanged.connect(self.change_audio_source)

        # Create a label to act as a "light"
        self.light_label = QLabel()
        self.light_label.setAutoFillBackground(True)
        palette = self.light_label.palette()
        palette.setColor(QPalette.Background, QColor('red'))
        self.light_label.setPalette(palette)

        layout = QVBoxLayout()
        layout.addWidget(self.url_bar)
        layout.addWidget(self.back_button)
        layout.addWidget(self.forward_button)
        layout.addWidget(self.reload_button)
        layout.addWidget(self.source_combo)
        layout.addWidget(self.light_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.dictation_text)
        layout.addWidget(self.browser)

        self.setLayout(layout)

    @pyqtSlot()
    def navigate_to_url(self):
        url = self.url_bar.text()
        self.browser.setUrl(QUrl(url))
        logging.info(f'Navigating to {url}')

    @pyqtSlot()
    def start_dictation(self):
        self.start_button.setDisabled(True)
        self.stop_button.setDisabled(False)
        self.change_light_color('green')
        self.is_dictating = True
        self.dictation_thread = threading.Thread(target=self.dictation)
        self.dictation_thread.start()
        logging.info('Started dictation')

    @pyqtSlot()
    def stop_dictation(self):
        self.start_button.setDisabled(False)
        self.stop_button.setDisabled(True)
        self.change_light_color('red')
        self.is_dictating = False
        logging.info('Stopped dictation')

    @pyqtSlot(int)
    def change_audio_source(self, index):
        devices = sr.Microphone.list_microphone_names()
        self.audio_source = sr.Microphone(device_index=devices.index(self.source_combo.itemText(index)))
        logging.info(f'Changed audio source to {self.source_combo.itemText(index)}')

    def change_light_color(self, color):
        palette = self.light_label.palette()
        palette.setColor(QPalette.Background, QColor(color))
        self.light_label.setPalette(palette)

    def dictation(self):
        while self.is_dictating:
            with self.audio_source as source:
                self.recognizer.adjust_for_ambient_noise(source)
                try:
                    audio = self.recognizer.listen(source, timeout=5.0)
                    text = self.recognizer.recognize_google(audio, language="fr-FR")
                    self.dictation_text.append(text)
                except sr.UnknownValueError:
                    logging.error('Unknown value error')
                except sr.RequestError as e:
                    logging.error(f'Request error: {str(e)}')
                    self.dictation_text.append(
                        f"Erreur lors de la requête au service de reconnaissance vocale : {str(e)}")
                except sr.WaitTimeoutError:
                    logging.info('Listening timeout, continue listening...')
            self.audio_source = sr.Microphone()  # reinitialize the source audio


def main():
    app = QApplication(sys.argv)
    ex = WebBrowserApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
