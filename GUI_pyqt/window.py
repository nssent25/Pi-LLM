
# This is the main file for the GUI. It creates a window with a start button that transitions to a recording screen when clicked.
import wx
import wx.adv
import wx.lib.buttons as lib_button
from wx.adv import AnimationCtrl
import time

# Placeholder for starting the recording
def start_recording():
    
    print("Recording started...")

# Placeholder for stopping the recording and sending the file to another program
def stop_recording_and_process():
    print("Recording stopped, processing...")
    return "This is the text returned from the processing. Replace with actual processing output."

class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title='Hi!', size=(1080, 1080))
        self.home_panel = wx.Panel(self)
        self.home_panel.SetBackgroundColour((0, 0, 0, 255))
        self.Centre()

        # Load button images (placeholders for your image paths)

        startlisten_pic = wx.Image('/Users/cliozhu/Desktop/2024-s/CS431/Pi-LLM-main/GUI_wxpython/image_processing20191206-10006-1o4c5ii.jpg').ConvertToBitmap()
        home_pic = wx.Image('/Users/cliozhu/Desktop/2024-s/CS431/Pi-LLM-main/GUI_wxpython/image_processing20191206-10006-1o4c5ii.jpg').ConvertToBitmap()

        # Start listen button
        self.startlisten = lib_button.ThemedGenBitmapTextButton(self.home_panel, size=(800, 600), pos=(145, 276), bitmap=startlisten_pic, label='', name='startButton')
        self.startlisten.Bind(wx.EVT_BUTTON, self.on_start_listen)

        # Stop listen button
        self.stoplisten = wx.Button(self.home_panel, size=(800, 600), pos=(145, 800), label='Stop', name='stopButton')
        self.stoplisten.Bind(wx.EVT_BUTTON, self.on_stop_listen)
        self.stoplisten.Hide()

        # Back to home button
        self.backtohome = lib_button.ThemedGenBitmapTextButton(self.home_panel, size=(80, 60), pos=(900, 700), bitmap=home_pic, label='Home', name='homeButton')
        self.backtohome.Bind(wx.EVT_BUTTON, self.on_back_to_home)
        self.backtohome.Hide()

        # Animation Control for GIF
        self.animation = AnimationCtrl(self.home_panel, pos=(145, 276), size=(800, 600), name='animationCtrl')
        self.animation.LoadFile('/Users/cliozhu/Desktop/2024-s/CS431/Pi-LLM-main/GUI_wxpython/Voice assistant motion effect.gif')
        self.animation.Hide()

        # Textbox for displaying processed text
        self.textbook = wx.TextCtrl(self.home_panel, size=(671, 509), pos=(187, 400), value='', name='text', style=wx.TE_MULTILINE)
        self.textbook.SetForegroundColour((255, 255, 255))
        self.textbook.SetBackgroundColour((0, 0, 0))
        self.textbook.Hide()

        # Recording Length Display
        self.recording_length_label = wx.StaticText(self.home_panel, label="Recording Length: 0s", pos=(145, 50))
        self.recording_length_label.Hide()

        # Timer for tracking recording length
        self.recording_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_recording_length, self.recording_timer)
        self.recording_start_time = None

    def on_start_listen(self, event):
        self.transition_to_record()

    def on_stop_listen(self, event):
        response = stop_recording_and_process()
        self.transition_to_display(response)

    def on_back_to_home(self, event):
        self.transition_to_home()

    def transition_to_home(self):
        self.recording_timer.Stop()
        self.animation.Stop()
        self.animation.Hide()
        self.stoplisten.Hide()
        self.textbook.Hide()
        self.recording_length_label.Hide()
        self.backtohome.Hide()
        self.startlisten.Show()
        self.home_panel.SetBackgroundColour((0, 0, 0, 255))
        self.Refresh()

    def transition_to_record(self):
        start_recording()
        self.startlisten.Hide()
        self.stoplisten.Show()
        self.backtohome.Show()
        self.animation.Show()
        self.animation.Play()
        self.recording_length_label.Show()
        self.recording_start_time = time.time()
        self.recording_timer.Start(1000)  # Update every second
        self.home_panel.SetBackgroundColour((14, 15, 32, 255))
        self.Refresh()

    def transition_to_display(self, response):
        self.recording_timer.Stop()
        self.animation.Stop()
        self.animation.Hide()
        self.stoplisten.Hide()
        self.backtohome.Show()
        self.textbook.Show()
        self.textbook.SetValue(response)
        self.recording_length_label.Hide()
        self.home_panel.SetBackgroundColour((0, 0, 0, 255))
        self.Refresh()

    def update_recording_length(self, event):
        if self.recording_start_time:
            elapsed_time = int(time.time() - self.recording_start_time)
            self.recording_length_label.SetLabel(f"Recording Length: {elapsed_time}s")

class myApp(wx.App):
    def OnInit(self):
        frame = Frame()
        frame.Show(True)
        return True

if __name__ == '__main__':
    app = myApp()
    app.MainLoop()
