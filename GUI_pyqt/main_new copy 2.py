import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QTextEdit, QWidget, QVBoxLayout, QProgressDialog, QSizePolicy, QSpacerItem
from PyQt5.QtGui import QPixmap, QIcon, QMovie, QImage, QPainter, QPen, QFont, QColor, QPainterPath
from PyQt5.QtCore import QTimer, QTime, Qt, QDateTime, QPropertyAnimation, QRect, QEasingCurve
#import time # Import the time module
from audio import AudioRecorder  # Import the AudioRecorder class
from client import AudioServerClient  # Import the AudioServerClient class
import base64

class CircleWidget(QWidget): # unused
    def __init__(self, parent=None):
        super(CircleWidget, self).__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.white, 2))  # Set pen color and width
        painter.setBrush(Qt.NoBrush)  # No fill
        painter.drawEllipse(self.width()//2 - 540, self.height()//2 - 540, 1080, 1080)

class HomeView(QWidget):
    def __init__(self, parent=None):
        super(HomeView, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # Setup the start listen button with an image icon
        self.start_listen_pic = QPixmap('assets/recordButton.jpg')
        # Scale the QPixmap
        scaled_pic = self.start_listen_pic.scaled(self.start_listen_pic.size() * 2, 
                                                  Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon = QIcon(scaled_pic)
        self.start_listen_btn = QPushButton('', self.parent())
        self.start_listen_btn.setIcon(icon)
        self.start_listen_btn.setIconSize(scaled_pic.size())
        self.start_listen_btn.resize(scaled_pic.width(), scaled_pic.height())
        # Calculate the top-left position to center the button at (540, 540)
        x = self.parent().width // 2 - self.start_listen_btn.width() // 2
        y = self.parent().height // 2 - self.start_listen_btn.height() // 2
        self.start_listen_btn.move(x, y)
        # Make the button colorless
        self.start_listen_btn.setStyleSheet("background-color: transparent; border: none;")
        self.start_listen_btn.clicked.connect(self.on_start_listen)

    def on_start_listen(self):
        # Transition to the recording UI and start recording
        self.hide()
        self.parent().transition_to_record()

    def hide(self):
        # Hide the home screen
        self.start_listen_btn.hide()

    def show(self):
        # Show the home screen
        self.start_listen_btn.show()

class RecordingView(QWidget):
    def __init__(self, parent=None):
        super(RecordingView, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setup_recording_length_label()
        self.setup_recording_animation()
        self.setup_recording_timer()
        self.setup_stop_listen_button()
        self.setup_back_to_home_button()
        self.hide()
        
    def record(self):
        self.stop_listen_btn.show()
        self.back_to_home_btn.show()
        self.recording_length_label.show()
        self.recording_start_time.start()
        self.recording_timer.start(1000)
        self.recording_animation_label.show()
        self.recording_animation.start()

    def setup_recording_length_label(self):
        # Setup the recording length label
        self.recording_length_label = QLabel("Recording: 0s", self.parent())
        self.recording_length_label.move(145, 50)
        self.recording_length_label.setStyleSheet("color: white;")
        self.recording_length_label.hide()

    def setup_recording_animation(self):
        # Setup recording animation
        self.recording_animation_label = QLabel(self.parent())
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

    def update_recording_length(self):
        # Update the recording length display
        elapsed_time = self.recording_start_time.elapsed() // 1000
        self.recording_length_label.setText(f"Recording: {elapsed_time}s")

    def setup_stop_listen_button(self):
        # Setup the stop listen button
        self.stop_listen_btn = QPushButton('Stop', self.parent())
        self.stop_listen_btn.resize(80, 60)
        self.stop_listen_btn.setStyleSheet("background-color: white;")
        self.stop_listen_btn.move(900, 600)
        self.stop_listen_btn.clicked.connect(self.on_stop_listen)
        self.stop_listen_btn.hide()

    def setup_back_to_home_button(self):
        # Setup the back to home button
        self.back_to_home_btn = QPushButton('Home', self.parent())
        self.back_to_home_btn.setStyleSheet("background-color: white;")
        self.back_to_home_btn.resize(80, 60)
        self.back_to_home_btn.move(900, 700)
        self.back_to_home_btn.clicked.connect(self.on_back_to_home)
        self.back_to_home_btn.hide()

    def on_stop_listen(self):
        # Handle stop listening: stop timer, process audio, and update UI
        self.recording_timer.stop()
        self.recording_animation.stop()
        self.recording_animation_label.hide()
        self.back_to_home_btn.show()
        self.parent().stop_recording_and_process()

    def on_back_to_home(self):
        # Transition back to the home screen
        self.hide()
        self.parent().transition_to_home()

    def hide(self):
        # Hide the recording screen and stop the timer
        self.recording_timer.stop()
        self.recording_length_label.hide()
        self.stop_listen_btn.hide()
        self.back_to_home_btn.hide()
        self.recording_animation.stop()
        self.recording_animation_label.hide()

    def show(self):
        # Show the recording screen and start the timer
        self.recording_timer.start()
        self.recording_length_label.show()
        self.stop_listen_btn.show()
        self.back_to_home_btn.show()
        self.recording_animation.start()
        self.recording_animation_label.show()

class ChatView(QWidget):
    def __init__(self, parent=None):
        super(ChatView, self).__init__(parent)
        self.setup_ui()
        self.conversation = []

    def setup_ui(self):
        # Setup the textbox for displaying processed text
        self.textbox = QTextEdit(self.parent())
        self.textbox.resize(671, 509)
        self.textbox.move(187, 200)
        self.textbox.setStyleSheet("color: white; background-color: black;")
        self.hide()

    def hide(self):
        # Hide the chat screen
        self.textbox.hide()

    def show(self):
        # Show the chat screen
        self.textbox.show()

    def display(self, response):
        # Display the text in the chat screen
        text = 'User: ' + response['input'] + '\nAssistant: ' + response['response'] + '\n'
        self.conversation.append(text)
        screen = '\n'.join(self.conversation)
        #self.textbox.setText(text)
        self.textbox.setText(screen)
        self.show()

class RoundedImageLabel(QLabel):
    def __init__(self, radius, parent=None):
        super(RoundedImageLabel, self).__init__(parent)
        self.radius = radius

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        painter.setClipPath(path)
        if self.pixmap():
            painter.drawPixmap(self.rect(), self.pixmap())

class ImageView(QWidget):
    def __init__(self, parent=None):
        super(ImageView, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # Create a QLabel to display the image
        self.image_size = 700
        self.image_label = RoundedImageLabel(self.image_size // 10)
        self.image_label.setGeometry(0, 0, self.image_size, self.image_size)

        # Create a QVBoxLayout
        layout = QVBoxLayout(self)

        # Create a QLabel to display the input prompt
        self.input_prompt_label = QLabel(self)
        font = QFont('Helvetica', 20)
        self.input_prompt_label.setFont(font)
        self.input_prompt_label.setStyleSheet("color: white;")

        # Create spacer items
        spacer_top = QSpacerItem(20, 165, QSizePolicy.Minimum, QSizePolicy.Fixed)
        spacer_bottom = QSpacerItem(20, 165, QSizePolicy.Minimum, QSizePolicy.Fixed)

        # Add the widgets and spacers to the layout
        layout.addItem(spacer_top)
        layout.addWidget(self.input_prompt_label)
        layout.setAlignment(self.input_prompt_label, Qt.AlignTop | Qt.AlignHCenter)
        layout.addWidget(self.image_label)
        layout.setAlignment(self.image_label, Qt.AlignVCenter | Qt.AlignHCenter)
        layout.addItem(spacer_bottom)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.hide()

    def animateOut(self):
        # Animate the widget moving to the bottom of the screen
        screen_geometry = QApplication.desktop().availableGeometry()
        end_geometry = QRect(self.geometry().left(), screen_geometry.bottom(), self.geometry().width(), self.geometry().height())

        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(end_geometry)
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()
        self.animation.finished.connect(self.hide)

    def hide(self):
        # Hide the image view
        self.image_label.clear()
        self.image_label.hide()
        self.input_prompt_label.hide()

    def show(self):
        # Show the image view
        self.image_label.show()
        self.input_prompt_label.show()
        # Animate the widget moving from the bottom of the screen
        screen_geometry = QApplication.desktop().availableGeometry()
        start_geometry = QRect(self.geometry().left(), screen_geometry.bottom(), self.geometry().width(), self.geometry().height())
        end_geometry = self.geometry()

        self.animation.setStartValue(start_geometry)
        self.animation.setEndValue(end_geometry)
        self.animation.setDuration(500)  # Duration in milliseconds
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def display(self, response):
        # Convert the base64 image data to QPixmap and display it
        image = self.base64_to_image(response['response'])
        #save the image to a file
        #get current time in milliseconds
        time = QDateTime.currentMSecsSinceEpoch()
        filenname = response['input'] + str(time) +'.jpg'
        image.save(filenname)
        self.image_label.setPixmap(image)
        self.input_prompt_label.setText(f'<b><font color="grey">Prompt:</font></b> {response["input"]}')
        self.show()

    def base64_to_image(self, base64_str):
        # Convert base64 string to QPixmap
        img_bytes = base64.b64decode(base64_str)
        image = QImage.fromData(img_bytes)
        pixmap = QPixmap.fromImage(image)
        pixmap = pixmap.scaled(self.image_size, self.image_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return pixmap

class TranslationView(QWidget):
    def __init__(self, parent=None):
        super(TranslationView, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # Set the style of the widget to look like a rounded rectangle card
        self.setStyleSheet("""
            QWidget {
                border: 1px solid #000;
                border-radius: 10px;
                padding: 10px;
                background-color: gray;
                color: white;
            }
            QTextEdit {
                background-color: gray;
                color: white;
            }
        """)

        # Create a vertical layout to stack the widgets
        layout = QVBoxLayout(self)

        # Label and text edit for source language
        self.sourceLangLabel = QLabel("Source Language:", self)
        layout.addWidget(self.sourceLangLabel)
        self.sourceLangText = QLabel(self)
        layout.addWidget(self.sourceLangText)

        # Label and text edit for destination language
        self.destLangLabel = QLabel("Destination Language:", self)
        layout.addWidget(self.destLangLabel)
        self.destLangText = QLabel(self)
        layout.addWidget(self.destLangText)

        # Label and text edit for original text
        self.originalTextLabel = QLabel("Original Text:", self)
        layout.addWidget(self.originalTextLabel)
        self.originalText = QTextEdit(self)
        self.originalText.setReadOnly(True)
        layout.addWidget(self.originalText)

        # Label and text edit for translated text
        self.translatedTextLabel = QLabel("Translated Text:", self)
        layout.addWidget(self.translatedTextLabel)
        self.translatedText = QTextEdit(self)
        self.translatedText.setReadOnly(True)
        layout.addWidget(self.translatedText)

        # Set the main layout of the widget
        self.setLayout(layout)
        self.hide()

    def hide(self):
        # Hide the translation view
        self.sourceLangLabel.hide()
        self.sourceLangText.hide()
        self.destLangLabel.hide()
        self.destLangText.hide()
        self.originalTextLabel.hide()
        self.originalText.hide()
        self.translatedTextLabel.hide()
        self.translatedText.hide()

    def show(self):
        # Show the translation view
        self.sourceLangLabel.show()
        self.sourceLangText.show()
        self.destLangLabel.show()
        self.destLangText.show()
        self.originalTextLabel.show()
        self.originalText.show()
        self.translatedTextLabel.show()
        self.translatedText.show()

    def display(self, response):
        # Method to update the text fields with the translation data
        self.sourceLangText.setText(response['source'])
        self.destLangText.setText(response['language'])
        self.originalText.setText(response['input'])
        self.translatedText.setText(response['response'])
        self.show()  # Ensure the widget is visible when updated

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
        self.layout = QVBoxLayout(self.central_widget)
        self.central_widget.setLayout(self.layout)
        self.central_widget.setStyleSheet("background-color: black;")
        self.currentWidget = None
        self.homeView = HomeView(self)
        self.recordingView = RecordingView(self)
        self.chatView = ChatView(self)
        self.imageView = ImageView(self)
        self.translationView = TranslationView(self)

    def hide_widgets(self):
        # Hide all widgets
        self.homeView.hide()
        self.recordingView.hide()
        self.chatView.hide()
        self.imageView.hide()
        self.translationView.hide()

    def transition_to_record(self):
        # Transition to the recording screen and start recording
        self.central_widget.setStyleSheet("background-color: #0e0f20;")
        self.audio_recorder.start_recording()
        self.recordingView.record()
        print("Recording started...")

    def stop_recording_and_process(self):
        # Stop recording and process the audio file
        self.audio_recorder.stop_recording()
        print("Recording stopped, processing...")

        # Create a QProgressDialog
        progress = QProgressDialog("Thinking...", None, 0, 1, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()

        # Process the audio file
        response = self.server.send_audio("recording.wav")

        # Close the QProgressDialog
        progress.setValue(1)
        progress.close()

        self.process_response(response)

    def process_response(self, response):
        # Process the response from the server after recording
        response = response.json()
        self.central_widget.setStyleSheet("background-color: black;")
        if response['task'] == 'Image Generation':
            self.imageView.display(response)
            self.currentWidget = self.imageView
            self.layout.addWidget(self.currentWidget)
        elif response['task'] == 'Translation':
            self.translationView.display(response)
            self.currentWidget = self.translationView
            self.layout.addWidget(self.currentWidget)
        else:
            self.chatView.display(response)
        self.update()

    def transition_to_home(self):
        # Reset UI elements to initial state (home screen)
        if self.currentWidget:
            print('removing current widget')
            self.layout.removeWidget(self.currentWidget)
            self.currentWidget = None
        self.hide_widgets()
        self.central_widget.setStyleSheet("background-color: black;")
        self.homeView.raise_()
        self.homeView.show()
        self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())