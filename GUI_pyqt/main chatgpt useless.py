import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QTextEdit, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer, QTime, Qt, QPropertyAnimation, QRect
from PyQt5.QtGui import QPixmap, QIcon
from audio import AudioRecorder
from client import AudioServerClient

class HomeView(QWidget):
    def __init__(self, parent=None):
        super(HomeView, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.start_listen_btn = QPushButton("Start Listening", self)
        self.start_listen_btn.clicked.connect(self.parent().on_start_listen)

class RecordingView(QWidget):
    def __init__(self, parent=None):
        super(RecordingView, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.stop_listen_btn = QPushButton("Stop", self)
        self.stop_listen_btn.clicked.connect(self.parent().on_stop_listen)
        self.recording_length_label = QLabel("Recording: 0s", self)

class TextView(QWidget):
    def __init__(self, parent=None):
        super(TextView, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.textbox = QTextEdit(self)
        self.back_to_home_btn = QPushButton('Home', self)
        self.back_to_home_btn.clicked.connect(self.parent().on_back_to_home)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.audio_recorder = AudioRecorder()
        self.server = AudioServerClient()
        self.setup_ui()

    def setup_ui(self):
        self.setGeometry(0, 0, 800, 600)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.home_view = HomeView(self)
        self.recording_view = RecordingView(self)
        self.text_view = TextView(self)

        self.stack = QVBoxLayout(self.central_widget)
        self.stack.addWidget(self.home_view)
        self.stack.addWidget(self.recording_view)
        self.stack.addWidget(self.text_view)

        self.home_view.show()
        self.recording_view.hide()
        self.text_view.hide()

    def on_start_listen(self):
        self.show_view(self.recording_view)
        self.audio_recorder.start_recording()
        print("Recording started...")

    def on_stop_listen(self):
        self.audio_recorder.stop_recording()
        print("Recording stopped, processing...")
        response = self.server.send_audio("recording.wav")
        self.process_response(response)

    def on_back_to_home(self):
        self.show_view(self.home_view)

    def process_response(self, response):
        text_response = f"User: {response.json()['input']}\nAssistant: {response.json()['response']}\n"
        self.text_view.textbox.setText(text_response)
        self.show_view(self.text_view)

    def show_view(self, view):
        """ Transition between views with an optional animation """
        for widget in (self.home_view, self.recording_view, self.text_view):
            widget.hide()
        view.show()
        # Optionally, add animations here

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
