import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QTextEdit, QWidget, QVBoxLayout, QProgressDialog, QSizePolicy, QSpacerItem, QGraphicsEllipseItem, QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QPixmap, QIcon, QMovie, QImage, QPainter, QPen, QFont, QColor, QPainterPath
from PyQt5.QtCore import QTimer, QTime, Qt, QDateTime, pyqtProperty, QPropertyAnimation, QRectF
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
        # Setup the home screen
        self.start_listen_label = QLabel(self.parent())
        self.start_listen_animation = QMovie('assets/homeView.gif')    
        self.start_listen_label.setMovie(self.start_listen_animation)
        self.start_listen_label.resize(1080, 1080)
        self.start_listen_label.setAlignment(Qt.AlignCenter)
        self.start_listen_animation.start()
        self.start_listen_label.mousePressEvent = self.on_start_listen

    def on_start_listen(self, event):
        # Transition to the recording UI and start recording
        self.parent().transition_to_record()

    def hide(self):
        # Hide the home screen
        self.start_listen_label.hide()

    def show(self):
        # Show the home screen
        self.start_listen_label.show()

class RecordingView(QWidget):
    def __init__(self, parent=None):
        super(RecordingView, self).__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # Setup recording animation
        self.recording_animation_label = QLabel(self.parent())
        self.recording_animation = QMovie('assets/Voice assistant motion effect.gif')
        self.loading_animation = QMovie('assets/homeView.gif')
        self.recording_animation_label.setMovie(self.recording_animation)
        self.recording_animation_label.resize(1080, 1080)
        self.recording_animation_label.setAlignment(Qt.AlignCenter)
        self.recording_animation_label.mousePressEvent = self.on_stop_listen
        self.hide()
        
    def on_stop_listen(self, event=None):
        # Go back to the home screen to stop recording
        self.recording_animation.stop()
        self.parent().stop_recording_and_process()

    def record(self):
        # Start the recording animation
        self.recording_animation.start()
        self.recording_animation_label.show()

    def loading_screen(self):
        # Show the processing screen after stopping recording
        self.recording_animation_label.setMovie(self.loading_animation)
        self.recording_animation_label.show()
        self.loading_animation.start()

    def stop_loading_screen(self):
        # Show the processing screen after stopping recording
        self.loading_animation.stop()
        self.recording_animation_label.setMovie(self.recording_animation)


    def hide(self):
        # Hide the recording screen and stop the timer
        self.recording_animation.stop()
        self.recording_animation_label.hide()

    def show(self):
        # Show the recording screen and start the timer
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
        font = QFont('Helvetica', 24)
        self.input_prompt_label.setFont(font)
        self.input_prompt_label.setStyleSheet("color: white;")
        self.input_prompt_label.setWordWrap(True)
        self.input_prompt_label.setFixedWidth(600)
        self.input_prompt_label.setAlignment(Qt.AlignCenter)

        # Adjust the size policy to allow vertical expansion
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.input_prompt_label.setSizePolicy(sizePolicy)
        # Create spacer items
        spacer_top = QSpacerItem(20, 165, QSizePolicy.Minimum, QSizePolicy.Fixed)
        small_spacer = QSpacerItem(20, 16, QSizePolicy.Minimum, QSizePolicy.Fixed)  # Small spacer between text and image
        spacer_bottom = QSpacerItem(20, 165, QSizePolicy.Minimum, QSizePolicy.Fixed)

        # Add the widgets and spacers to the layout
        layout.addItem(spacer_top)
        layout.addWidget(self.input_prompt_label)
        layout.setAlignment(self.input_prompt_label, Qt.AlignTop | Qt.AlignHCenter)
        layout.addItem(small_spacer)  # Add the small spacer here
        layout.addWidget(self.image_label)
        layout.setAlignment(self.image_label, Qt.AlignVCenter | Qt.AlignHCenter)
        layout.addItem(spacer_bottom)

        self.hide()

    def hide(self):
        # Hide the image view
        self.image_label.clear()
        self.image_label.hide()
        self.input_prompt_label.hide()

    def show(self):
        # Show the image view
        self.image_label.show()
        self.input_prompt_label.show()

    def display(self, response):
        # Convert the base64 image data to QPixmap and display it
        image = self.base64_to_image(response)
        self.image_label.setPixmap(image)
        self.input_prompt_label.setText(f'<b><font color="grey">Prompt:</font></b> {response["input"]}')
        self.show()

    def base64_to_image(self, response):
        # Convert base64 string to QPixmap
        img_bytes = base64.b64decode(response['response'])
        image = QImage.fromData(img_bytes)
        pixmap = QPixmap.fromImage(image)
        filename = 'saved/' + response['input'] + str(QDateTime.currentMSecsSinceEpoch()) + '.jpg'
        pixmap.save(filename)
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
        self.setWindowFlags(Qt.FramelessWindowHint) # no title bar
        self.setGeometry(0, 0, self.width, self.height)

        # Setup the central widget with a black background
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.central_widget.setLayout(self.layout)
        self.central_widget.setStyleSheet("background-color: black;")
        self.currentWidget = None

        # instantiate the different views
        self.homeView = HomeView(self)
        self.recordingView = RecordingView(self)
        self.chatView = ChatView(self)
        self.imageView = ImageView(self)
        self.translationView = TranslationView(self)
        self.setup_back_to_home_button()
        self.setup_stop_listen_button()

    def setup_stop_listen_button(self):
        # Setup the stop listen button
        self.stop_listen_btn = QPushButton('Stop', self)
        self.stop_listen_btn.resize(80, 60)
        self.stop_listen_btn.setStyleSheet("background-color: white;")
        self.stop_listen_btn.move(900, 600)
        self.stop_listen_btn.clicked.connect(self.stop_recording_and_process)
        self.stop_listen_btn.hide()

    def setup_back_to_home_button(self):
        # Setup the back to home button
        self.back_to_home_btn = QPushButton('Home', self)
        self.back_to_home_btn.setStyleSheet("background-color: white;")
        self.back_to_home_btn.resize(80, 60)
        self.back_to_home_btn.move(900, 700)
        self.back_to_home_btn.clicked.connect(self.transition_to_home)
        self.back_to_home_btn.hide()

    def hide_widgets(self):
        # Hide all widgets
        self.homeView.hide()
        self.recordingView.hide()
        self.chatView.hide()
        self.imageView.hide()
        self.translationView.hide()
        self.stop_listen_btn.hide()
        self.back_to_home_btn.hide()

    def transition_to_record(self):
        # Transition to the recording screen and start recording
        self.homeView.hide()
        self.central_widget.setStyleSheet("background-color: #0e0f20;")
        self.audio_recorder.start_recording()
        self.recordingView.record()
        print("Recording started...")

    def stop_recording_and_process(self):
        # Stop recording and process the audio file
        self.audio_recorder.stop_recording()
        self.recordingView.loading_screen()
        print("Recording stopped, processing...")

        # Create a QProgressDialog
        # progress = QProgressDialog("Thinking...", None, 0, 1, self)
        # progress.setWindowModality(Qt.WindowModal)
        # progress.show()
        # QApplication.processEvents()

        # Process the audio file
        response = self.server.send_audio("recording.wav")
        print("Processing complete!")
        # Close the QProgressDialog
        # progress.setValue(1)
        # progress.close()

        self.recordingView.stop_loading_screen()
        self.recordingView.hide()

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
        self.stop_listen_btn.show()
        self.back_to_home_btn.show()
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
