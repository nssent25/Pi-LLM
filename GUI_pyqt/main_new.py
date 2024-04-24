import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QTextEdit, QWidget, QVBoxLayout, QSizePolicy, QSpacerItem, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap, QMovie, QImage, QPainter, QPen, QFont, QColor, QPainterPath, QBrush
from PyQt5.QtCore import QTimer, Qt, QDateTime, pyqtProperty, QPropertyAnimation, Qt, QRect, QEasingCurve, QObject, pyqtSignal, QThread
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
        self.loadingAnimation = QMovie('assets/homeView.gif')
        self.loadingScreen = QLabel(self.parent())
        self.loadingScreen.resize(1080, 1080)
        self.loadingScreen.setMovie(self.loadingAnimation)
        self.loadingScreen.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        self.stopRecordButton = QLabel(self.parent())
        self.recordingAnimation = QMovie('assets/recordView.gif')
        self.transitionAnimation = QMovie('assets/homeTransition.gif')
        self.transitionAnimation.setSpeed(250)

        self.stopRecordButton.resize(1080, 1080)
        self.stopRecordButton.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.stopRecordButton.mousePressEvent = self.onStopListen

        self.hide()
        
    def transition(self):
        # transition by making opacity of transitionAnimation 0 to 100
        self.stopRecordButton.setMovie(self.transitionAnimation)
        self.transitionAnimation.start()
        self.stopRecordButton.show()
        self.transitionAnimation.finished.connect(self.record)

    def record(self, event=None):
        # Start the recording animation
        self.stopRecordButton.setMovie(self.recordingAnimation)
        self.stopRecordButton.show()
        self.recordingAnimation.start()

    def onStopListen(self, event=None):
        # Go back to the home screen to stop recording
        self.recordingAnimation.stop()
        # self.stopRecordButton.hide()
        print("onstoplisten called")
        self.showLoadingScreen()
        # self.parent().processRecording()

    def showLoadingScreen(self):
        # Start the loading animation
        self.loadingScreen.raise_()
        self.loadingAnimation.start()
        self.loadingScreen.show()

        # # Apply QGraphicsOpacityEffect to the widget
        # opacityEffect = QGraphicsOpacityEffect(self.loadingScreen)
        # self.loadingScreen.setGraphicsEffect(opacityEffect)

        # # Create QPropertyAnimation to animate the opacity
        # opacityAnimation = QPropertyAnimation(opacityEffect, b"opacity")
        # opacityAnimation.setDuration(500)  # 2 seconds
        # opacityAnimation.setStartValue(0)  # Start at fully transparent
        # opacityAnimation.setEndValue(1)  # End at fully opaque
        # opacityAnimation.setEasingCurve(QEasingCurve.Linear)  # Linear change in opacity
        # opacityAnimation.start()

        self.parent().processRecording()

    def hide(self):
        # Hide the recording screen and stop the timer
        self.recordingAnimation.stop()
        self.stopRecordButton.hide()
        self.loadingAnimation.stop()
        self.loadingScreen.hide()

    def show(self):
        # Show the recording screen and start the timer
        self.recordingAnimation.start()
        self.stopRecordButton.show()

class ChatView(QWidget):
    def __init__(self, parent=None):
        super(ChatView, self).__init__(parent)
        self.setupUI()
        #self.conversation = []

    def setupUI(self):
        # Setup the textbox for displaying processed text
        self.textbox = QTextEdit(self.parent())
        self.textbox.setReadOnly(True)
        self.textbox.setFont(QFont('Helvetica', 24))
        self.textbox.resize(760, 700)
        # center on 1080x1080 screen
        self.textbox.move(160, 190)
        self.textbox.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textbox.setStyleSheet("color: white; background-color: black; border: 0px;")
        self.timer = QTimer() # Create a QTimer to contol animation
        self.timer.timeout.connect(self.display_next_character)
        self.hide()

    def hide(self):
        # Hide the chat screen
        self.textbox.hide()

    def show(self):
        # Show the chat screen
        self.textbox.show()

    def display_next_character(self):
        if self.text_index < len(self.current_text):
            self.textbox.setText(self.current_text[:self.text_index])
            self.text_index += 1
        else:
            self.timer.stop()  # Stop the timer when the full conversation is displayed

    def display(self, response):
        # Display the text in the chat screen with HTML formatting
        userText = f'<i><font color="#9c9c9c">{response["input"]}</font></i>'
        assistantText = f'{response["response"]}'
        self.textbox.setText(userText)
        self.text_index = len(userText)
        self.current_text = f'{userText}<br>{assistantText}<br><br>'
        self.timer.start(30)  # Start/restart the tim

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

        # create two textboxes for the original and translated text
        self.textbox_org = QTextEdit(self.parent())
        self.textbox_org.setReadOnly(True)
        self.textbox_org.setFont(QFont('Helvetica', 36))
        self.textbox_org.resize(760, 350)
        # center on 1080x1080 screen
        self.textbox_org.move(160, 220)
        self.textbox_tar = QTextEdit(self.parent())
        self.textbox_tar.setReadOnly(True)
        self.textbox_tar.setFont(QFont('Helvetica', 36))
        self.textbox_tar.resize(760, 350)
        # center on 1080x1080 screen
        self.textbox_tar.move(160, 560)
        self.textbox_org.setStyleSheet("color: white; background-color: black; border: 0px;")
        self.textbox_tar.setStyleSheet("color: white; background-color: black; border: 0px;")

        self.hide()

    def hide(self):

        self.textbox_org.hide()
        self.textbox_tar.hide()

    def show(self):
        self.textbox_org.show()
        self.textbox_tar.show()

    def display(self, response):
        # Display the original and translated text with HTML formatting
        originallang = f'<font>{response["input"]}</font>'
        translatlang = f'{response["response"]}'

        # Add the source and destination language tag to the textboxes
        sourcetag = f'<b><font size="1" color="#9c9c9c">{response["source"].capitalize()}</font></b>'
        desttag = f'<b><font size="1" color="#9c9c9c">{response["language"].capitalize()}</font></b>'

        # Add the source and destination language tag to the textboxes
        originallang = f'{sourcetag}<br>{originallang}<br><br>'
        translatlang = f'{desttag}<br>{translatlang}<br><br>'

        # Set the text of the textboxes
        self.textbox_org.setText(originallang)
        self.textbox_tar.setText(translatlang)

        self.show()  # Ensure the widget is visible when updated

class RoundButton(QPushButton):
    def __init__(self, title, parent=None):
        super(RoundButton, self).__init__(title, parent)
        self.title = title
        self.setFont(QFont('Material Icons Outlined', 50))

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

class AudioWorker(QObject):
    finished = pyqtSignal(object)

    def __init__(self, client, audio_file):
        super().__init__()
        self.client = client
        self.audio_file = audio_file

    def run(self):
        response = self.client.send_audio(self.audio_file)
        self.finished.emit(response)

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
        size = 100  # Set both width and height to 60 for a circle
        self.stopListenBtn.resize(size, size)
        self.stopListenBtn.move(600, 930)
        self.stopListenBtn.clicked.connect(self.processRecording)
        self.stopListenBtn.hide()

    def setupBackToHomeButton(self):
        # Setup the back to home button using the custom RoundButton class
        self.backToHomeBtn = RoundButton(chr(0xE5E0), self)
        size = 100  # Set both width and height to 60 for a circle
        self.backToHomeBtn.resize(size, size)
        self.backToHomeBtn.move(405, 930)
        self.backToHomeBtn.clicked.connect(self.transitionToHome)
        self.backToHomeBtn.hide()

    def hideWidgets(self):
        # Hide all widgets
        # self.homeView.hide()
        self.recordingView.hide()
        self.chatView.hide()
        self.imageView.hide()
        self.translationView.hide()
        self.stopListenBtn.hide()
        self.backToHomeBtn.hide()

    def transitionToRecord(self):
        # Transition to the recording screen and start recording
        self.homeView.hide()
        self.audioRecorder.start_recording()
        self.recordingView.transition()
        print("Recording started...")

    def processRecording(self):
        # Stop recording
        self.audioRecorder.stop_recording()
        print("Recording stopped, processing...")

        # Setup the worker and thread
        self.thread = QThread()
        self.worker = AudioWorker(self.server, "recording.wav")
        self.worker.moveToThread(self.thread)
        # Connect signals
        self.worker.finished.connect(self.processResponse)
        self.thread.started.connect(self.worker.run)
        # Cleanup
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Start the thread
        self.thread.start()

    def processResponse(self, response):
        # Process the response from the server after recording
        print("response received")
        self.recordingView.hide()
        response = response.json()
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
        self.homeView.raise_()
        self.homeView.show()
        self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
