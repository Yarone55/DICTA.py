import sys
import os

import numpy as np
from PyQt5.QtCore import Qt, QUrl, QTimer, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon, QImage, QPixmap, QColor, QKeySequence
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QPlainTextEdit, QColorDialog,
    QFileDialog, QComboBox, QDialog, QMessageBox, QButtonGroup, QShortcut
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtMultimedia import QSoundEffect
import speech_recognition as sr
import threading
import time
import datetime
import subprocess
from playsound import playsound
import pandas as pd
from pydub import AudioSegment
from pydub.playback import play
from pynput.keyboard import Listener as KeyboardListener
import keyboard
import datetime
import subprocess


def execute_audio_file(file_path):
    os.startfile(file_path)


class BrowserWindow(QMainWindow):
    def __init__(self):
        # Version
        self.version_project = "0.0.1"
        # Init HIM components
        super().__init__()
        self.gif_indicator = None
        self.browser_thread = None
        self.remaining_time = None
        self.countdown_timer = None
        self.button_action_next_call = None
        self.execute_file_button_8 = None
        self.execute_file_button_3 = None
        self.button_action_non_renew = None
        self.button_action_presentation = None
        self.button_action_not_interested = None
        self.button_action_sale = None
        self.button_action_busy = None
        self.microphone_combo2 = None
        self.create_command_button = None
        self.action_entry = None
        self.command_entry = None
        self.microphone_muted = None
        self.mute_microphone_button = None
        self.microphone_combo = None
        self.save_button = None
        self.voice_label = None
        self.voice_stop_button = None
        self.voice_button = None
        self.load_commands_button = None
        self.browse_audio_button = None
        self.stop_gif_button = None
        self.search_gif_button = None
        self.gif_url_input = None
        self.forward_button = None
        self.back_button = None
        self.address_bar = None
        self.web_view = None
        self.setWindowTitle(f"Project15 - V{self.version_project}")
        self.setWindowIcon(QIcon("assets/images/icons/Logo_AI_V3_55x57.png"))
        self.keyboard_listener = KeyboardListener(on_press=self.on_keyboard_press)
        self.keyboard_listener.start()
        self.last_button_used = None
        self.voice_input_output = QPlainTextEdit()
        self.voice_input_output.setReadOnly(True)
        self.voice_input_output.setMinimumHeight(40)
        self.voice_input_output.setMaximumHeight(40)
        self.open_file_buttons = []
        self.open_file_paths = []
        self.open_file_signals = []

        self.initialize_web_view()
        self.initialize_address_bar()
        self.initialize_navigation_buttons()

        self.initialize_search_gif_widgets()
        # self.initialize_console_output()
        self.initialize_gif_indicator()
        self.pause_system_button = QPushButton("Pause System")
        self.pause_system_button.clicked.connect(self.pause_system)
        self.initialize_browse_audio_button()
        self.initialize_load_commands_button()
        self.initialize_voice_command_widgets()

        self.audio_file_path = ""
        self.audio_player = QSoundEffect()

        self.gif_timer = QTimer()
        self.gif_timer.timeout.connect(self.search_gif)

        self.listener = sr.Recognizer()
        self.audio_file_path = ""
        self.audio_player = QSoundEffect()

        self.populate_microphone_combo()

        self.custom_commands = {}

        self.command_list_dialog = QDialog(self)
        self.command_list_dialog.setWindowTitle("Loaded Commands")
        self.command_list_dialog.setModal(True)
        self.command_list_dialog_layout = QVBoxLayout()
        self.command_list_dialog.setLayout(self.command_list_dialog_layout)

        self.setup_layout()
        self.setup_shortcuts()

    def logger_trace_log(self, message, from_act=""):
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        if from_act == "":
            from_act = "[undefined]"
        self.voice_input_output.appendPlainText(f"[{dt_string}][{from_act}] - {message}")

    def execute_file(self, file_way):
        if os.path.exists(file_way):
            self.logger_trace_log(f"Executing file: {file_way}", "execute_file")
            os.startfile(file_way)
            return True
        else:
            self.logger_trace_log(f"Fichier '{file_way}' non trouvé", "execute_file")
            return False

    def pause_system(self):
        self.close()

    def initialize_web_view(self):
        self.web_view = QWebEngineView()
        self.web_view.load(QUrl(
            "https://vicibox-001.vicibox.avalon-informatique.fr/agc/vicidial.php?"
            "relogin=YES&VD_login=3001&VD_campaign=2013GSM&phone_login=2001"
            "&phone_pass=PhoneDefaultPasswordLogin1234&VD_pass=UserDefaultPass1234"))

    def initialize_address_bar(self):
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.open_url)

    def initialize_navigation_buttons(self):
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.web_view.back)
        self.forward_button = QPushButton("Forward")
        self.forward_button.clicked.connect(self.web_view.forward)

    def initialize_search_gif_widgets(self):
        self.gif_url_input = QLineEdit()
        self.search_gif_button = QPushButton("Start Search")
        self.search_gif_button.clicked.connect(self.start_gif_search)
        self.stop_gif_button = QPushButton("Stop Search")
        self.stop_gif_button.clicked.connect(self.stop_gif_search)
        self.stop_gif_button.setEnabled(False)

    def initialize_gif_indicator(self):
        self.gif_indicator = QLabel("GIF Not Found")
        self.gif_indicator.setAlignment(Qt.AlignCenter)
        self.gif_indicator.setFixedHeight(30)

    def initialize_browse_audio_button(self):
        self.browse_audio_button = QPushButton("Browse Audio")
        self.browse_audio_button.clicked.connect(self.browse_audio_file)

    def initialize_load_commands_button(self):
        self.load_commands_button = QPushButton("Load Commands")
        self.load_commands_button.clicked.connect(self.load_commands)

    def initialize_voice_command_widgets(self):
        self.voice_button = QPushButton("Start Voice Command")
        self.voice_button.clicked.connect(self.start_listening)
        self.voice_stop_button = QPushButton("Stop Listening")
        self.voice_stop_button.clicked.connect(self.stop_listening)
        self.voice_stop_button.setEnabled(False)
        self.voice_label = QLabel()
        self.voice_label.setFixedHeight(40)
        self.save_button = QPushButton("Save Commands")
        self.save_button.clicked.connect(self.save_commands)

        self.microphone_combo = QComboBox()
        self.microphone_combo.currentIndexChanged.connect(self.select_microphone)

        self.mute_microphone_button = QPushButton("Mute Microphone")
        self.mute_microphone_button.clicked.connect(self.toggle_microphone_mute)

        self.microphone_muted = False

        self.command_entry = QLineEdit()
        self.action_entry = QLineEdit()
        self.create_command_button = QPushButton("Create Command")
        self.create_command_button.clicked.connect(self.create_command)

        self.microphone_combo2 = QComboBox()  # Deuxième tableau déroulant pour le microphone
        self.populate_microphone_combo2()
        self.microphone_combo2.currentIndexChanged.connect(self.select_microphone2)

        self.button_action_busy = QPushButton("busy")
        self.button_action_busy.clicked.connect(self.action_busy)
        self.button_action_busy.setShortcut("*")

        self.button_action_sale = QPushButton("sale")
        self.button_action_sale.clicked.connect(self.action_sale)
        self.button_action_sale.setShortcut("+")

        self.button_action_not_interested = QPushButton("pas inter")
        self.button_action_not_interested.clicked.connect(self.action_not_interested)
        self.button_action_not_interested.setShortcut("/")


        # layout.addWidget(self.execute_file_button)

    def action_not_interested(self):
        self.web_view.page().runJavaScript("""
              hangup_customer_button_click('','','','','YES');
          """)
        time.sleep(2)  # Pause de 2 secondes
        self.web_view.page().runJavaScript("""
              DispoSelectContent_create('NI','ADD','YES');
          """)
        time.sleep(1)  # Pause de 1 seconde
        self.web_view.page().runJavaScript("""
              DispoSelect_submit('','','YES');
          """)
        self.logger_trace_log("Action => Pas intéressé", "action_not_interested")
        self.search_gif_button.setEnabled(False)
        self.stop_gif_button.setEnabled(True)
        self.gif_url_input.setText("https://vicibox-001.vicibox.avalon-informatique.fr/agc/images/agc_live_call_ON.gif")
        self.start_gif_search()

    def setup_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.voice_label)
        address_layout = QHBoxLayout()
        address_layout.addWidget(self.back_button)
        address_layout.addWidget(self.forward_button)
        address_layout.addWidget(self.address_bar)
        layout.addWidget(self.pause_system_button)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Set GIF URL:"))
        search_layout.addWidget(self.gif_url_input)
        search_layout.addWidget(self.search_gif_button)
        search_layout.addWidget(self.stop_gif_button)

        voice_layout = QHBoxLayout()
        voice_layout.addWidget(self.voice_button)
        voice_layout.addWidget(self.voice_stop_button)
        voice_layout.addWidget(self.microphone_combo)
        voice_layout.addWidget(self.voice_label)
        voice_layout.addWidget(self.mute_microphone_button)
        voice_layout.addWidget(self.microphone_combo2)  # Ajout du deuxième tableau déroulant

        command_layout = QHBoxLayout()
        command_layout.addWidget(QLabel("Command:"))
        command_layout.addWidget(self.command_entry)
        command_layout.addWidget(QLabel("Action:"))
        command_layout.addWidget(self.action_entry)
        command_layout.addWidget(self.create_command_button)

        file_buttons_layout = QHBoxLayout()
        file_buttons_layout.addWidget(self.browse_audio_button)
        file_buttons_layout.addWidget(self.load_commands_button)
        file_buttons_layout.addWidget(self.save_button)
        file_buttons_layout.addWidget(self.button_action_busy)
        file_buttons_layout.addWidget(self.button_action_sale)
        file_buttons_layout.addWidget(self.button_action_not_interested)

        actions_buttons_layout = QHBoxLayout()






        self.execute_file_button_4 = QPushButton("bubu")
        self.execute_file_button_4.clicked.connect(self.execute_file_4)
        self.execute_file_button_4.setShortcut("R")
        actions_buttons_layout.addWidget(self.execute_file_button_4)


        self.execute_file_button_9 = QPushButton("presentation")
        self.execute_file_button_9.clicked.connect(self.execute_file_9)
        self.execute_file_button_9.setShortcut("1")
        actions_buttons_layout.addWidget(self.execute_file_button_9)

        self.execute_file_button_10 = QPushButton("non renouve")
        self.execute_file_button_10.clicked.connect(self.execute_file_10)
        self.execute_file_button_10.setShortcut("2")
        actions_buttons_layout.addWidget(self.execute_file_button_10)

        self.execute_file_button_11 = QPushButton("bonne")
        self.execute_file_button_11.clicked.connect(self.execute_file_11)
        self.execute_file_button_11.setShortcut("3")
        actions_buttons_layout.addWidget(self.execute_file_button_11)

        self.execute_file_button_12 = QPushButton("argent")
        self.execute_file_button_12.clicked.connect(self.execute_file_12)
        self.execute_file_button_12.setShortcut("4")
        actions_buttons_layout.addWidget(self.execute_file_button_12)
        self.button_action_next_call = QPushButton("Appel suivant")
        self.button_action_next_call.clicked.connect(self.action_next_dial)
        self.button_action_next_call.setShortcut(".")
        actions_buttons_layout.addWidget(self.button_action_next_call)
        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        layout.addLayout(address_layout)
        layout.addWidget(self.web_view)
        layout.addLayout(search_layout)
        layout.addWidget(self.gif_indicator)
        layout.addLayout(voice_layout)
        layout.addLayout(command_layout)
        layout.addWidget(self.voice_input_output)
        layout.addLayout(file_buttons_layout)
        layout.addLayout(actions_buttons_layout)
        main_widget.setLayout(layout)
    def on_keyboard_press(self, key):
        self.logger_trace_log(f"Key Pressed: {key}", "on_keyboard_press")

    def populate_microphone_combo(self):
        microphones = sr.Microphone.list_microphone_names()
        self.microphone_combo.clear()
        self.microphone_combo.addItems(microphones)

    def populate_microphone_combo2(self):  # Remplir le deuxième tableau déroulant avec les microphones disponibles
        microphones = sr.Microphone.list_microphone_names()
        self.microphone_combo2.clear()
        self.microphone_combo2.addItems(microphones)

    def select_microphone2(self):
        selected_microphone = self.microphone_combo2.currentText()
        index = self.microphone_combo2.currentIndex()
        self.listener = sr.Recognizer()
        self.listener.energy_threshold = 4000
        self.listener.pause_threshold = 0.5
        self.listener.phrase_threshold = 0.5
        self.listener.dynamic_energy_adjustment_ratio = 1.5
        self.listener.dynamic_energy_adjustment_damping = 0.15
        self.listener.dynamic_energy_adjustment_attack = 1.0
        self.listener.dynamic_energy_adjustment_decay = 0.8
        with sr.Microphone(device_index=index) as source:
            self.listener.adjust_for_ambient_noise(source)

    def select_microphone(self):
        selected_microphone = self.microphone_combo.currentText()
        index = self.microphone_combo.currentIndex()
        self.listener = sr.Recognizer()
        self.listener.energy_threshold = 4000
        self.listener.pause_threshold = 0.5
        self.listener.phrase_threshold = 0.5
        self.listener.dynamic_energy_adjustment_ratio = 1.5
        self.listener.dynamic_energy_adjustment_damping = 0.15
        self.listener.dynamic_energy_adjustment_attack = 1.0
        self.listener.dynamic_energy_adjustment_decay = 0.8
        with sr.Microphone(device_index=index) as source:
            self.listener.adjust_for_ambient_noise(source)

    @pyqtSlot()
    def save_commands(self):
        if hasattr(self, "custom_commands"):
            df = pd.DataFrame(list(self.custom_commands.items()), columns=['Command', 'Action'])
            file_path, _ = QFileDialog.getSaveFileName(None, "Save Commands", "", "Excel files (*.xls *.xlsx)")
            if file_path:
                df.to_excel(file_path, index=False)

    def load_commands(self):
        file_path, _ = QFileDialog.getOpenFileName(None, "Load Commands", "", "Excel files (*.xls *.xlsx)")
        if file_path:
            try:
                df = pd.read_excel(file_path)
                self.custom_commands = dict(zip(df['Command'], df['Action']))
                self.show_command_list()
                self.logger_trace_log("Commands loaded successfully.", "load_commands")
            except Exception as e:
                self.logger_trace_log(f"Error loading commands: {str(e)}", "load_commands")

    def show_command_list(self):
        self.command_list_dialog.setWindowTitle("Loaded Commands")

        while self.command_list_dialog_layout.count():
            item = self.command_list_dialog_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for command, action in self.custom_commands.items():
            command_label = QLabel(f"{command}: {action}")
            self.command_list_dialog_layout.addWidget(command_label)

        self.command_list_dialog.show()

    def open_url(self):
        url = self.address_bar.text()
        self.web_view.load(QUrl(url))
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.logger_trace_log(f"Opening URL: {url} - Time: {current_time}, Date: {current_date}", "open_url")

    def start_gif_search(self):
        self.search_gif_button.setEnabled(False)
        self.stop_gif_button.setEnabled(True)
        self.gif_timer.start(2000)  # Refresh every 2 seconds
        time.sleep(2)  # Pause de 1 seconde

    def stop_gif_search(self):
        self.search_gif_button.setEnabled(True)
        self.stop_gif_button.setEnabled(False)
        self.gif_timer.stop()

    def search_gif(self):
        gif_url = self.gif_url_input.text()

        self.gif_indicator.setText("")

        page = self.web_view.page()
        page.runJavaScript(f"""
            (function() {{
                var images = document.getElementsByTagName('img');
                var gifTrouve = false;
                for (var i = 0; i < images.length; i++) {{
                    var src = images[i].getAttribute('src');
                    if (src === '{gif_url}') {{
                        gifTrouve = true;
                        break;
                    }}
                }}
                return gifTrouve;
            }})()
        """, self.handle_gif_search_result)

    def handle_gif_search_result(self, gif_found):
        if gif_found:
            self.gif_indicator.setText("GIF Found")
            if self.audio_file_path:
                time.sleep(1)
                self.open_audio_file()
                self.stop_gif_search()
            else:
                self.show_gif_found_message()
        else:
            self.gif_indicator.setText("GIF Not Found")

    def show_gif_found_message(self):
        self.logger_trace_log(f"The GIF has been found !", "show_gif_found_message")

    def mute_microphone_for_duration(self, duration):
        self.toggle_microphone_mute()
        time.sleep(duration)
        self.toggle_microphone_mute()

    def setup_shortcuts(self):
        mute_shortcut = QShortcut(QKeySequence(Qt.Key_0), self)  # Remplacer Qt.Key_M par Qt.Key_0
        mute_shortcut.activated.connect(self.toggle_microphone_mute)








    def execute_file_4(self):
        self.logger_trace_log("Action => Occupé", "action_busy")

        self.web_view.page().runJavaScript("""
                      hangup_customer_button_click('','','','','YES');
                  """)
        time.sleep(1)  # Pause de 2 secondes
        self.web_view.page().runJavaScript("""
                              DispoSelectContent_create('B','ADD','YES');
                          """)
        time.sleep(1)  # Pause de 1 seconde
        self.web_view.page().runJavaScript("""
                      DispoSelect_submit('','','YES');
                  """)
        self.search_gif_button.setEnabled(False)
        self.stop_gif_button.setEnabled(True)
        self.gif_url_input.setText("https://vicibox-001.vicibox.avalon-informatique.fr/agc/images/agc_live_call_ON.gif")
        self.start_gif_search()


    def execute_file_9(self):
        self.logger_trace_log(f"Action => ER", "execute_file_9")
        if self.last_button_used:
            self.last_button_used.setStyleSheet("")
        self.last_button_used = self.execute_file_button_9
        self.last_button_used.setStyleSheet("background-color: blue;")
        QTimer.singleShot(600, self.start_countdown_9)

    def update_countdown_9(self):
        self.remaining_time -= 1
        if self.remaining_time >= 0:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            self.voice_label.setText(
                f"Countdown: {self.remaining_time} second(s) - Time: {current_time}, Date: {current_date}")
        else:
            self.voice_label.setText("Countdown finished")
            self.countdown_timer.stop()

    def start_countdown_9(self):
        # Lancer le compte à rebours
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown_9)
        self.remaining_time = 24  # Durée du compte à rebours en secondes
        self.update_countdown_9()  # Mettre à jour le label dès le début
        self.countdown_timer.start(1000)  # Mettre à jour le label toutes les secondes
        keyboard.press("a")  # Simulation de la pression de la touche "A"
        keyboard.release("a")  # Relâchement de la touche "A"
    def execute_file_10(self):
        self.logger_trace_log(f"Action => ER", "execute_file_10")
        if self.last_button_used:
            self.last_button_used.setStyleSheet("")
        self.last_button_used = self.execute_file_button_10
        self.last_button_used.setStyleSheet("background-color: blue;")
        QTimer.singleShot(600, self.start_countdown_10)

    def update_countdown_10(self):
        self.remaining_time -= 1
        if self.remaining_time >= 0:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            self.voice_label.setText(
                f"Countdown: {self.remaining_time} second(s) - Time: {current_time}, Date: {current_date}")
        else:
            self.voice_label.setText("Countdown finished")
            self.countdown_timer.stop()

    def start_countdown_10(self):
        # Lancer le compte à rebours
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown_10)
        self.remaining_time = 24  # Durée du compte à rebours en secondes
        self.update_countdown_10()  # Mettre à jour le label dès le début
        self.countdown_timer.start(1000)  # Mettre à jour le label toutes les secondes
        keyboard.press("b")  # Simulation de la pression de la touche "A"
        keyboard.release("b")  # Relâchement de la touche "A"
    def execute_file_11(self):
        self.logger_trace_log(f"Action => ER", "execute_file_11")
        if self.last_button_used:
            self.last_button_used.setStyleSheet("")
        self.last_button_used = self.execute_file_button_11
        self.last_button_used.setStyleSheet("background-color: blue;")
        QTimer.singleShot(600, self.start_countdown_11)

    def update_countdown_11(self):
        self.remaining_time -= 1
        if self.remaining_time >= 0:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            self.voice_label.setText(
                f"Countdown: {self.remaining_time} second(s) - Time: {current_time}, Date: {current_date}")
        else:
            self.voice_label.setText("Countdown finished")
            self.countdown_timer.stop()
    def start_countdown_11(self):
        # Lancer le compte à rebours
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown_11)
        self.remaining_time = 24  # Durée du compte à rebours en secondes
        self.update_countdown_10()  # Mettre à jour le label dès le début
        self.countdown_timer.start(1000)  # Mettre à jour le label toutes les secondes
        keyboard.press("3")  # Simulation de la pression de la touche "A"
        keyboard.release("3")  # Relâchement de la touche "A"



    def execute_file_12(self):
        self.logger_trace_log(f"Action => ER", "execute_file_12")
        if self.last_button_used:
            self.last_button_used.setStyleSheet("")
        self.last_button_used = self.execute_file_button_12
        self.last_button_used.setStyleSheet("background-color: blue;")
        QTimer.singleShot(600, self.start_countdown_12)

    def update_countdown_12(self):
        self.remaining_time -= 1
        if self.remaining_time >= 0:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            self.voice_label.setText(
                f"Countdown: {self.remaining_time} second(s) - Time: {current_time}, Date: {current_date}")
        else:
            self.voice_label.setText("Countdown finished")
            self.countdown_timer.stop()

    def start_countdown_12(self):
        # Lancer le compte à rebours
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown_12)
        self.remaining_time = 24  # Durée du compte à rebours en secondes
        self.update_countdown_12()  # Mettre à jour le label dès le début
        self.countdown_timer.start(1000)  # Mettre à jour le label toutes les secondes
        keyboard.press("4")  # Simulation de la pression de la touche "A"
        keyboard.release("4")  # Relâchement de la touche "A"

    def action_next_dial(self):
        self.logger_trace_log("Action => Apple suivant", "action_next_dial")
        self.web_view.page().runJavaScript(f"""
            ManualDialNext('','','','','','0','','','YES');
        """)

    def action_busy(self):
        self.logger_trace_log("Action => Occupé", "action_busy")

        self.web_view.page().runJavaScript("""
                      hangup_customer_button_click('','','','','YES');
                  """)
        time.sleep(1)  # Pause de 2 secondes
        self.web_view.page().runJavaScript("""
                              DispoSelectContent_create('B','ADD','YES');
                          """)
        time.sleep(1)  # Pause de 1 seconde
        self.web_view.page().runJavaScript("""
                      DispoSelect_submit('','','YES');
                  """)
        self.search_gif_button.setEnabled(False)
        self.stop_gif_button.setEnabled(True)
        self.gif_url_input.setText("https://vicibox-001.vicibox.avalon-informatique.fr/agc/images/agc_live_call_ON.gif")
        self.start_gif_search()

    def action_sale(self):
        self.logger_trace_log("Action => Vente", "action_sale")
        self.web_view.page().runJavaScript("""
              hangup_customer_button_click('','','','','YES');
          """)
        time.sleep(1)  # Pause de 2 secondes
        self.web_view.page().runJavaScript("""
              DispoSelectContent_create('SALE','ADD','YES');
          """)
        time.sleep(1)  # Pause de 1 seconde
        self.web_view.page().runJavaScript("""
              DispoSelect_submit('','','YES');
          """)
        self.search_gif_button.setEnabled(False)
        self.stop_gif_button.setEnabled(True)
        self.gif_url_input.setText("https://vicibox-001.vicibox.avalon-informatique.fr/agc/images/agc_live_call_ON.gif")
        self.start_gif_search()
        # Démarrer le compte à rebours après une courte pause
        QTimer.singleShot(600, self.start_countdown)

    def browse_audio_file(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilters(["Audio Files (*.wav *.mp3)"])

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            audio_file_path = selected_files[0]
            self.audio_file_path = audio_file_path
            self.logger_trace_log(f"Selected audio file: {audio_file_path}", "browse_audio_file")

    def open_file(self, button_index):
        file_path = self.open_file_paths[button_index]
        if file_path:
            self.logger_trace_log(f"Opening file {file_path}", "open_file")

    def open_audio_file(self):
        if os.path.exists(self.audio_file_path):
            try:
                subprocess.run(['start', self.audio_file_path], shell=True)
            except Exception as e:
                self.logger_trace_log(f"Error opening file: {str(e)}", "open_audio_file")
        else:
            self.logger_trace_log(f"File not found.", "open_audio_file")

    def start_listening(self):
        self.voice_label.setText("Listening...")
        self.voice_button.setEnabled(False)
        self.voice_stop_button.setEnabled(True)
        self.browser_thread = threading.Thread(target=self.listen_commands)
        self.browser_thread.start()

    def stop_listening(self):
        if hasattr(self, "listener") and self.listener is not None:
            self.listener = sr.Recognizer()
        self.voice_stop_button.setEnabled(False)
        self.voice_button.setEnabled(True)
        self.voice_label.setText("Listening stopped.")

    def listen_commands(self):
        while True:
            try:
                with sr.Microphone() as source:
                    if not self.microphone_muted:
                        self.listener.adjust_for_ambient_noise(source, duration=0.5)
                        audio = self.listener.listen(source, phrase_time_limit=4)
                        command = self.listener.recognize_google(audio, language='fr-FR')
                        command = command.lower()
                        if command.strip() != "":
                            self.process_command(command)
                            self.logger_trace_log(f"CLIENT: {command}", "listen_commands")
                    else:
                        time.sleep(0.1)
            except sr.UnknownValueError:
                self.voice_label.setText("Command not recognized. Please repeat.")
            except sr.RequestError:
                self.voice_label.setText("Unable to access Google Speech Recognition. Please try again.")

    def process_command(self, command):
        self.voice_label.setText(f"Command received: {command}")
        action_executed = False
        if hasattr(self, "custom_commands"):
            for key, value in self.custom_commands.items():
                if key in command:
                    actions = value.split(",")
                    for action in actions:
                        if action.startswith("pause"):
                            duration = float(action.split(":")[1].strip())
                            self.execute_pause(duration)
                        elif action.startswith("audio"):
                            audio_file = action.split(":")[1].strip()
                            self.audio_file_path = audio_file
                            self.logger_trace_log(f"Audio file set: {audio_file}", "process_command")
                            self.execute_file_spec()
                        elif action.startswith("key"):
                            key_name = action.split(":")[1].strip()
                            self.press_key(key_name)
                        elif action.startswith("Présentation"):
                            self.action_presentation()
                        elif action.startswith("Bonne chance"):
                            self.action_non_renew()
                        elif action.startswith("Non renouvelable"):
                            self.execute_file_3()
                        elif action.startswith("bubu"):
                            self.execute_file_4()
                        else:
                            subprocess.run(action, shell=True)
                    action_executed = True
                    break

        if not action_executed:
            self.voice_label.setText("No matching action found.")

    def execute_pause(self, duration):
        self.voice_label.setText(f"Pause for {duration} second(s)...")
        time.sleep(duration)
        self.voice_label.setText("Pause completed.")

    def press_key(self, key_name):
        pass

    def create_command(self):
        command = self.command_entry.text()
        action = self.action_entry.text()
        if command and action:
            if not hasattr(self, "custom_commands"):
                self.custom_commands = {}
            self.custom_commands[command] = action
            self.logger_trace_log(f"Command '{command}' created: {action}", "create_command")
        else:
            self.logger_trace_log(f"Please enter both command and action.", "create_command")

        self.command_entry.clear()
        self.action_entry.clear()

    def toggle_microphone_mute(self):
        selected_microphone = self.microphone_combo.currentText()
        index = self.microphone_combo.currentIndex()
        self.microphone_muted = not self.microphone_muted
        if self.microphone_muted:
            audio = sr.Microphone.get_pyaudio().PyAudio()
            # device_info = audio.get_device_info_by_index(index)
            device_info = audio.get_default_input_device_info()['index']
            # device_info = audio.
            audio.set_input_device_volume(device_info, 0.0)
            # with sr.Microphone(device_index=index) as source:
            #    self.listener.adjust_for_ambient_noise(source.mute)
            self.mute_microphone_button.setText("Unmute Microphone")
            self.voice_label.setText("Microphone muted.")
        else:
            self.mute_microphone_button.setText("Mute Microphone")
            self.voice_label.setText("Microphone unmuted.")

    def closeEvent(self, event):
        result = QMessageBox.question(self, "Confirmation fermeture",
                                      "Êtes vous sur de vouloir quitter Project15 ?",
                                      QMessageBox.Yes | QMessageBox.No)
        event.ignore()

        if result == QMessageBox.Yes:
            event.accept()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = BrowserWindow()
    browser.show()
    sys.exit(app.exec_())
