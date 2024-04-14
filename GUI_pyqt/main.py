import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QTextEdit, QWidget
from PyQt5.QtGui import QPixmap, QIcon, QMovie, QPainter, QPen, QColor
from PyQt5.QtCore import QTimer, QTime, Qt
from audio import AudioRecorder  # Import the AudioRecorder class
from client import AudioServerClient  # Import the AudioServerClient class

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize the main window, audio recorder, and server client
        self.audio_recorder = AudioRecorder()
        self.server = AudioServerClient()
        self.height = 1080
        self.width = 1080
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(0, 0, self.width, self.height)

        # Setup the central widget with a black background
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: black;")
        self.setup_start_listen_button()
        self.setup_stop_listen_button()
        self.setup_back_to_home_button()
        self.setup_textbox()
        self.setup_recording_length_label()
        self.setup_recording_animation()
        self.setup_recording_timer()

    def setup_start_listen_button(self):
        # Setup the start listen button with an image icon
        self.start_listen_pic = QPixmap('assets/image_processing20191206-10006-1o4c5ii.jpg')
        # Scale the QPixmap
        scaled_pic = self.start_listen_pic.scaled(self.start_listen_pic.size() * 1.5, 
                                                  Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon = QIcon(scaled_pic)
        self.start_listen_btn = QPushButton('', self.central_widget)
        self.start_listen_btn.setIcon(icon)
        self.start_listen_btn.setIconSize(scaled_pic.size())
        self.start_listen_btn.resize(scaled_pic.width(), scaled_pic.height())
        # Calculate the top-left position to center the button at (540, 540)
        x = self.width // 2 - self.start_listen_btn.width() // 2
        y = self.height // 2 - self.start_listen_btn.height() // 2
        self.start_listen_btn.move(x, y)

        self.start_listen_btn.clicked.connect(self.on_start_listen)

    def setup_stop_listen_button(self):
        # Setup the stop listen button
        self.stop_listen_btn = QPushButton('Stop', self.central_widget)
        self.stop_listen_btn.resize(80, 60)
        self.stop_listen_btn.setStyleSheet("background-color: white;")
        self.stop_listen_btn.move(900, 600)
        self.stop_listen_btn.clicked.connect(self.on_stop_listen)
        self.stop_listen_btn.hide()

    def setup_back_to_home_button(self):
        # Setup the back to home button
        self.back_to_home_btn = QPushButton('Home', self.central_widget)
        self.back_to_home_btn.setStyleSheet("background-color: white;")
        self.back_to_home_btn.resize(80, 60)
        self.back_to_home_btn.move(900, 700)
        self.back_to_home_btn.clicked.connect(self.on_back_to_home)
        self.back_to_home_btn.hide()

    def setup_textbox(self):
        # Setup the textbox for displaying processed text
        self.textbox = QTextEdit(self.central_widget)
        self.textbox.resize(671, 509)
        self.textbox.move(187, 200)
        self.textbox.setStyleSheet("color: white; background-color: black;")
        self.textbox.hide()

    def setup_recording_length_label(self):
        # Setup the recording length label
        self.recording_length_label = QLabel("Recording: 0s", self.central_widget)
        self.recording_length_label.move(145, 50)
        self.recording_length_label.setStyleSheet("color: white;")
        self.recording_length_label.hide()

    def setup_recording_animation(self):
        # Setup recording animation
        self.recording_animation_label = QLabel(self.central_widget)
        self.recording_animation = QMovie('assets/Voice assistant motion effect.gif')
        self.recording_animation_label.setMovie(self.recording_animation)
        self.recording_animation_label.resize(800, 600)
        self.recording_animation_label.move(145, 276)
        self.recording_animation_label.hide()

    def setup_recording_timer(self):
        # Timer setup for tracking recording length
        self.recording_timer = QTimer(self)
        self.recording_timer.timeout.connect(self.update_recording_length)
        self.recording_start_time = QTime()

    def on_start_listen(self):
        # Transition to the recording UI and start recording
        self.transition_to_record()

    def start_recording(self):
        # Start audio recording
        self.audio_recorder.start_recording()
        print("Recording started...")

    def stop_recording_and_process(self):
        # Stop recording and process the audio file
        self.audio_recorder.stop_recording()
        print("Recording stopped, processing...")
        response = self.server.send_audio("recording.wav")
        return response

    def on_stop_listen(self):
        # Handle stop listening: stop timer, process audio, and update UI
        self.recording_timer.stop()
        self.stop_listen_btn.hide()
        self.back_to_home_btn.show()
        self.textbox.show()
        self.textbox.setText("Processing...")
        response = self.stop_recording_and_process()
        self.process_response(response)

    def on_back_to_home(self):
        # Transition back to the home screen
        self.transition_to_home()

    def transition_to_home(self):
        # Reset UI elements to initial state (home screen)
        self.recording_timer.stop()
        self.stop_listen_btn.hide()
        self.textbox.hide()
        self.recording_length_label.hide()
        self.back_to_home_btn.hide()
        self.start_listen_btn.show()
        self.central_widget.setStyleSheet("background-color: black;")
        self.update()

    def transition_to_record(self):
        # Transition to the recording screen and start recording
        self.start_recording()
        self.start_listen_btn.hide()
        self.stop_listen_btn.show()
        self.back_to_home_btn.show()
        self.recording_length_label.show()
        self.recording_start_time.start()
        self.recording_timer.start(1000)
        self.recording_animation_label.show()
        self.recording_animation.start()
        self.central_widget.setStyleSheet("background-color: #0e0f20;")

    def process_response(self, response):
        # Process the response from the server after recording
        text_response = 'User: ' + response.json()['input'] + '\nAssistant: ' + response.json()['response'] + '\n'
        print(text_response)
        self.transition_to_display_text(text_response)

    def transition_to_display_text(self, response):
        # Display the server response text and update UI
        self.recording_timer.stop()
        self.stop_listen_btn.hide()
        self.back_to_home_btn.show()
        self.textbox.show()
        self.textbox.setText(response)
        self.recording_length_label.hide()
        self.recording_animation.stop()
        self.recording_animation_label.hide()
        self.central_widget.setStyleSheet("background-color: black;")
        self.update()

    def update_recording_length(self):
        # Update the recording length display
        elapsed_time = self.recording_start_time.elapsed() // 1000
        self.recording_length_label.setText(f"Recording: {elapsed_time}s")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
