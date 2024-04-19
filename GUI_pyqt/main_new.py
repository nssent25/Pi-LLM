import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QTextEdit, QWidget, QVBoxLayout, QProgressDialog, QSizePolicy, QSpacerItem, QGraphicsEllipseItem, QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QPixmap, QIcon, QMovie, QImage, QPainter, QPen, QFont, QColor, QPainterPath, QBrush
from PyQt5.QtCore import QTimer, QTime, Qt, QDateTime, pyqtProperty, QPropertyAnimation, QRectF, Qt, QRect, QPoint
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
        self.setupUI()

    def setupUI(self):
        # Setup the home screen
        self.startRecordButton = QLabel(self.parent())
        self.homeAnimation = QMovie('assets/homeView.gif')    
        self.startRecordButton.setMovie(self.homeAnimation)
        self.startRecordButton.resize(1080, 1080)
        self.startRecordButton.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.homeAnimation.start()
        self.startRecordButton.mousePressEvent = self.onStartListen

    def onStartListen(self, event):
        # Transition to the recording UI and start recording
        self.parent().transitionToRecord()

    def hide(self):
        # Hide the home screen
        self.startRecordButton.hide()

    def show(self):
        # Show the home screen
        self.startRecordButton.show()

class RecordingView(QWidget):
    def __init__(self, parent=None):
        super(RecordingView, self).__init__(parent)
        self.setupUI()

    def setupUI(self):
        # Setup recording animation
        self.stopRecordButton = QLabel(self.parent())
        self.recordingAnimation = QMovie('assets/Voice assistant motion effect.gif')
        self.loadingAnimation = QMovie('assets/homeView.gif')
        self.stopRecordButton.setMovie(self.recordingAnimation)
        self.stopRecordButton.resize(1080, 1080)
        self.stopRecordButton.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.stopRecordButton.mousePressEvent = self.onStopListen
        self.hide()
        
    def onStopListen(self, event=None):
        # Go back to the home screen to stop recording
        self.recordingAnimation.stop()
        self.parent().processRecording()

    def record(self):
        # Start the recording animation
        self.recordingAnimation.start()
        self.stopRecordButton.show()

    def loadingScreen(self):
        # Show the processing screen after stopping recording
        self.stopRecordButton.setMovie(self.loadingAnimation)
        self.stopRecordButton.show()
        self.loadingAnimation.start()

    def stopLoadingScreen(self):
        # Show the processing screen after stopping recording
        self.loadingAnimation.stop()
        self.stopRecordButton.setMovie(self.recordingAnimation)

    def hide(self):
        # Hide the recording screen and stop the timer
        self.recordingAnimation.stop()
        self.stopRecordButton.hide()

    def show(self):
        # Show the recording screen and start the timer
        self.recordingAnimation.start()
        self.stopRecordButton.show()

class ChatView(QWidget):
    def __init__(self, parent=None):
        super(ChatView, self).__init__(parent)
        self.setupUI()
        self.conversation = []

    def setupUI(self):
        # Setup the textbox for displaying processed text
        self.textbox = QTextEdit(self.parent())
        self.textbox.setReadOnly(True)
        self.textbox.setFont(QFont('Helvetica', 24))
        self.textbox.resize(671, 671)
        self.textbox.move(204, 204)
        self.textbox.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textbox.setStyleSheet("color: white; background-color: black;")
        self.hide()

    def hide(self):
        # Hide the chat screen
        self.textbox.hide()

    def show(self):
        # Show the chat screen
        self.textbox.show()

    def display(self, response):
        # Display the text in the chat screen with HTML formatting
        userText = f'<i><font color="#9c9c9c">{response["input"]}</font></i>'
        assistantText = f'{response["response"]}'
        text = f'{userText}<br>{assistantText}<br><br>'
        self.conversation.append(text)
        screen = ''.join(self.conversation)  # Use ''.join to concatenate without additional newlines
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
        self.setupUI()

    def setupUI(self):
        # Create a QLabel to display the image
        self.imageSize = 700
        self.imageLabel = RoundedImageLabel(self.imageSize // 10)
        self.imageLabel.setGeometry(0, 0, self.imageSize, self.imageSize)

        # Create a QVBoxLayout
        layout = QVBoxLayout(self)

        # Create a QLabel to display the input prompt
        self.inputPromptLabel = QLabel(self)
        font = QFont('Helvetica', 24)
        self.inputPromptLabel.setFont(font)
        self.inputPromptLabel.setStyleSheet("color: white;")
        self.inputPromptLabel.setWordWrap(True)
        self.inputPromptLabel.setFixedWidth(600)
        self.inputPromptLabel.setAlignment(Qt.AlignCenter)

        # Adjust the size policy to allow vertical expansion
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.inputPromptLabel.setSizePolicy(sizePolicy)
        # Create spacer items
        topSpacer = QSpacerItem(20, 80, QSizePolicy.Minimum, QSizePolicy.Minimum)
        smallSpacer = QSpacerItem(20, 16, QSizePolicy.Minimum, QSizePolicy.Fixed)  # Small spacer between text and image
        bottomSpacer = QSpacerItem(20, 165, QSizePolicy.Minimum, QSizePolicy.Fixed)

        # Add the widgets and spacers to the layout
        layout.addItem(topSpacer)
        layout.addWidget(self.inputPromptLabel)
        layout.setAlignment(self.inputPromptLabel, Qt.AlignTop | Qt.AlignHCenter)
        layout.addItem(smallSpacer)  # Add the small spacer here
        layout.addWidget(self.imageLabel)
        layout.setAlignment(self.imageLabel, Qt.AlignVCenter | Qt.AlignHCenter)
        layout.addItem(bottomSpacer)

        self.hide()

    def hide(self):
        # Hide the image view
        self.imageLabel.clear()
        self.imageLabel.hide()
        self.inputPromptLabel.hide()

    def show(self):
        # Show the image view
        self.imageLabel.show()
        self.inputPromptLabel.show()

    def display(self, response):
        # Convert the base64 image data to QPixmap and display it
        image = self.base64ToImg(response)
        self.imageLabel.setPixmap(image)
        self.inputPromptLabel.setText(f'<b><font color="grey">Prompt:</font></b> {response["input"]}')
        self.show()

    def base64ToImg(self, response):
        # Convert base64 string to QPixmap
        imgDat = base64.b64decode(response['response'])
        image = QImage.fromData(imgDat)
        pixmap = QPixmap.fromImage(image)
        filename = 'saved/' + response['input'] + str(QDateTime.currentMSecsSinceEpoch()) + '.jpg'
        pixmap.save(filename)
        pixmap = pixmap.scaled(self.imageSize, self.imageSize, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return pixmap

class TranslationView(QWidget):
    def __init__(self, parent=None):
        super(TranslationView, self).__init__(parent)
        self.setupUI()

    def setupUI(self):
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

class RoundButton(QPushButton):
    def __init__(self, title, parent=None):
        super(RoundButton, self).__init__(title, parent)
        self.title = title
        self.setFont(QFont('Material Icons Outlined', 48))

        # Connect signals to change the button state
        self.pressed.connect(self.onPressed)
        self.released.connect(self.onReleased)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # For smooth edges
        
        # Set colors based on the button's state
        if self.isDown():  # If the button is pressed
            brushColor = QColor(255, 255, 255, 45)  # Semi-transparent red
            penColor = QColor(255, 255, 255, 45)
        else:  # Default state
            brushColor = QColor(255, 255, 255, 25)  # Very transparent white
            penColor = QColor(255, 255, 255, 25)
        
        painter.setBrush(QBrush(brushColor, Qt.SolidPattern))
        painter.setPen(QPen(penColor))
        painter.drawEllipse(0, 0, self.width(), self.height())  # Draw a circle/ellipse that fills the button

        # Set text color
        painter.setPen(QPen(Qt.white))
        painter.drawText(QRect(0, 0, self.width(), self.height()), Qt.AlignCenter, self.title)

    def onPressed(self):
        self.pressed = True
        self.update()  # Trigger a repaint to update the button's appearance

    def onReleased(self):
        self.pressed = False
        self.update()  # Trigger a repaint to update the button's appearance

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize the main window, audio recorder, and server client
        self.audioRecorder = AudioRecorder()
        self.server = AudioServerClient() 
        self.height = 1080
        self.width = 1080
        self.setWindowFlags(Qt.FramelessWindowHint) # no title bar
        self.setGeometry(0, 0, self.width, self.height)

        # Setup the central widget with a black background
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.layout = QVBoxLayout(self.mainWidget)
        self.mainWidget.setLayout(self.layout)
        self.mainWidget.setStyleSheet("background-color: black;")
        self.currentWidget = None

        # instantiate the different views
        self.homeView = HomeView(self)
        self.recordingView = RecordingView(self)
        self.chatView = ChatView(self)
        self.imageView = ImageView(self)
        self.translationView = TranslationView(self)
        self.setupBackToHomeButton()
        self.setupStopListenButton()

    def setupStopListenButton(self):
        # Setup the stop listen button
        self.stopListenBtn = RoundButton(chr(0xF053), self)
        size = 75  # Set both width and height to 60 for a circle
        self.stopListenBtn.resize(size, size)
        self.stopListenBtn.move(455, 960)
        self.stopListenBtn.clicked.connect(self.processRecording)
        self.stopListenBtn.hide()

    def setupBackToHomeButton(self):
        # Setup the back to home button using the custom RoundButton class
        self.backToHomeBtn = RoundButton(chr(0xE5E0), self)
        size = 75  # Set both width and height to 60 for a circle
        self.backToHomeBtn.resize(size, size)
        self.backToHomeBtn.move(550, 960)
        self.backToHomeBtn.clicked.connect(self.transitionToHome)
        self.backToHomeBtn.hide()

    def hideWidgets(self):
        # Hide all widgets
        self.homeView.hide()
        self.recordingView.hide()
        self.chatView.hide()
        self.imageView.hide()
        self.translationView.hide()
        self.stopListenBtn.hide()
        self.backToHomeBtn.hide()

    def transitionToRecord(self):
        # Transition to the recording screen and start recording
        self.homeView.hide()
        self.mainWidget.setStyleSheet("background-color: #0e0f20;")
        self.audioRecorder.start_recording()
        self.recordingView.record()
        print("Recording started...")

    def processRecording(self):
        # Stop recording and process the audio file
        self.audioRecorder.stop_recording()
        self.recordingView.loadingScreen()
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
        self.recordingView.stopLoadingScreen()
        self.recordingView.hide()
        self.processResponse(response)

    def processResponse(self, response):
        # Process the response from the server after recording
        response = response.json()
        self.mainWidget.setStyleSheet("background-color: black;")
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
        self.stopListenBtn.show()
        self.backToHomeBtn.show()
        self.update()

    def transitionToHome(self):
        # Reset UI elements to initial state (home screen)
        if self.currentWidget:
            print('removing current widget')
            self.layout.removeWidget(self.currentWidget)
            self.currentWidget = None
        self.hideWidgets()
        self.mainWidget.setStyleSheet("background-color: black;")
        self.homeView.raise_()
        self.homeView.show()
        self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
