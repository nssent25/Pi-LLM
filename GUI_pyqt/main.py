import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QTextEdit, QWidget
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QTimer, QTime
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QIcon
#import the audio recorder class
from audio import AudioRecorder
#import the client class
from client import AudioServerClient


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #make an instance of the audio recorder class
        self.audio_recorder = AudioRecorder()
        #make an instance of the client class
        self.server = AudioServerClient()
        self.setWindowTitle('Hi!')
        self.setGeometry(100, 100, 1080, 1080)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: black;")

        # Load button images (placeholders for your image paths)
        self.start_listen_pic = QPixmap('assets/image_processing20191206-10006-1o4c5ii.jpg')
        #self.home_pic = QPixmap('/Users/cliozhu/Desktop/2024-s/CS431/Pi-LLM-main/GUI_wxpython/image_processing20191206-10006-1o4c5ii.jpg')
        icon = QIcon(self.start_listen_pic)
        #icon_home = QIcon(self.home_pic)


        # Start listen button
        self.start_listen_btn = QPushButton('', self.central_widget)
        self.start_listen_btn.setIcon(icon)
        #self.start_listen_btn.setIcon(self.start_listen_pic)
        self.start_listen_btn.setIconSize(self.start_listen_pic.size())
        self.start_listen_btn.resize(800, 600)
        self.start_listen_btn.move(145, 276)
        self.start_listen_btn.clicked.connect(self.on_start_listen)

        # Stop listen button
        self.stop_listen_btn = QPushButton('Stop', self.central_widget)
        self.stop_listen_btn.resize(80, 60)
        #set button color to be white
        self.stop_listen_btn.setStyleSheet("background-color: white;")
        self.stop_listen_btn.move(900, 600)
        self.stop_listen_btn.clicked.connect(self.on_stop_listen)
        self.stop_listen_btn.hide()

        # Back to home button
        self.back_to_home_btn = QPushButton('Home', self.central_widget)
        #self.back_to_home_btn.setIcon(icon_home)
        #self.back_to_home_btn.setIcon(self.home_pic)
        #self.back_to_home_btn.setIconSize(self.home_pic.size())
        self.back_to_home_btn.setStyleSheet("background-color: white;")
        self.back_to_home_btn.resize(80, 60)
        self.back_to_home_btn.move(900, 700)
        self.back_to_home_btn.clicked.connect(self.on_back_to_home)
        self.back_to_home_btn.hide()

        # Textbox for displaying processed text
        self.textbox = QTextEdit(self.central_widget)
        self.textbox.resize(671, 509)
        self.textbox.move(187, 400)
        self.textbox.setStyleSheet("color: white; background-color: black;")
        self.textbox.hide()

        # Recording Length Display
        self.recording_length_label = QLabel("Recording: 0s", self.central_widget)
        self.recording_length_label.move(145, 50)
        self.recording_length_label.setStyleSheet("color: white;")
        self.recording_length_label.hide()

        self.recording_animation_label = QLabel(self.central_widget)
        self.recording_animation = QMovie('assets/Voice assistant motion effect.gif')  # Update path
        self.recording_animation_label.setMovie(self.recording_animation)
        self.recording_animation_label.resize(800, 600)  # Adjust size as needed
        self.recording_animation_label.move(145, 276)  # Position it as you like
        self.recording_animation_label.hide()

        # Timer for tracking recording length
        self.recording_timer = QTimer(self)
        self.recording_timer.timeout.connect(self.update_recording_length)
        self.recording_start_time = QTime()

    def on_start_listen(self):
        self.transition_to_record()

    # Placeholder for starting the recording
    def start_recording(self):
        #start the recording
        self.audio_recorder.start_recording()
        print("Recording started...")

    def stop_recording_and_process(self):
        self.audio_recorder.stop_recording()
        print("Recording stopped, processing...")
        #send the audio file to the server
        text_re = self.server.send_audio(["recording.wav"])

        return text_re


    def on_stop_listen(self):
        response = self.stop_recording_and_process()
        self.transition_to_display(response)

    def on_back_to_home(self):
        self.transition_to_home()

    def transition_to_home(self):
        self.recording_timer.stop()
        self.stop_listen_btn.hide()
        self.textbox.hide()
        self.recording_length_label.hide()
        self.back_to_home_btn.hide()
        self.start_listen_btn.show()
        self.central_widget.setStyleSheet("background-color: black;")
        self.update()

    def transition_to_record(self):
        self.start_recording()
        self.start_listen_btn.hide()
        self.stop_listen_btn.show()
        self.back_to_home_btn.show()
        self.recording_length_label.show()
        self.recording_start_time.start()
        self.recording_timer.start(1000)  # Update every second
        self.recording_animation_label.show()  # Show the animation
        self.recording_animation.start()  # Start the animation
        self.central_widget.setStyleSheet("background-color: #0e0f20;")




    def transition_to_display(self, response):
        self.recording_timer.stop()
        self.stop_listen_btn.hide()
        self.back_to_home_btn.show()
        self.textbox.show()
        self.textbox.setText(response)
        #play the audio
        self.audio_recorder.play_audio("response.wav")
        self.recording_length_label.hide()
        self.recording_animation.stop()  # Stop the animation
        self.recording_animation_label.hide()  # Hide the animation label
        self.central_widget.setStyleSheet("background-color: black;")
        self.update()

    def update_recording_length(self):
        elapsed_time = self.recording_start_time.elapsed() // 1000
        self.recording_length_label.setText(f"Recording Length: {elapsed_time}s")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
