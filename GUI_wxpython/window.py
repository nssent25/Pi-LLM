
# -*- coding:utf-8 -*-
import wx.adv
import wx.lib.buttons as lib_button
from wx.adv import Animation, AnimationCtrl
import wx
import time

class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title='Hi!', size=(1080, 1080),name='frame',style=541072384)
        self.home = wx.Panel(self)
        self.home.SetBackgroundColour((0,0,0,255))
        self.Centre()
        #self.animation = AnimationCtrl(self.home, 1, Animation('/Users/cliozhu/Desktop/Voice assistant motion effect.gif'), pos=(50, 76), size=(100, 10))
        #self.animation.Play()
        startlisten_pic = wx.Image(r'/image_processing20191206-10006-1o4c5ii.jpg').ConvertToBitmap()
        self.startlisten = lib_button.ThemedGenBitmapTextButton(self.home,size=(800, 600),pos=(145, 276),bitmap=startlisten_pic,label='',name='genbutton')
        #self.animation = AnimationCtrl(self.home, 1, Animation('/Users/cliozhu/Desktop/Voice assistant motion effect.gif'), size=(800, 600),pos=(145, 276))
        #self.animation.Hide() 
        self.timer = wx.Timer(self)
        self.animation = wx.adv.AnimationCtrl(self.home,size=(800, 600),pos=(145, 276),name='animationctrl',style=2097152)
        self.animation.Hide()
        self.animation.LoadFile(r'/Voice assistant motion effect.gif')
        self.startlisten.Bind(wx.EVT_BUTTON,self.startlisten_anbdj)
        self.home.Bind(wx.EVT_KEY_DOWN,self.startlisten_axmj)
        self.home.Bind(wx.EVT_KEY_UP,self.startlisten_skmj)

        

    def startlisten_anbdj(self,event):
        self.home.SetBackgroundColour((14,16,32,255))
        self.Refresh()
        self.Update() 
        #self.animation = AnimationCtrl(self.home, 1, Animation('/Users/cliozhu/Desktop/Voice assistant motion effect.gif'), size=(800, 600),pos=(145, 276))
        self.animation.Show()
        self.animation.Play()
        
    def startlisten_axmj(self,event):
        self.home.SetBackgroundColour((14,16,32,255)) 
        self.Refresh()
        self.Update() 
        self.animation.Show()
        self.animation.Play()
    
    def startlisten_skmj(self,event):
        self.home.SetBackgroundColour((0,0,0,255))
        self.Refresh()
        self.Update()  
        self.animation.Stop()
        self.animation.Hide()
        #send the voice to the server
        #print response
        self.textbook = wx.TextCtrl(self.home,size=(671, 509),pos=(187, 400),value='',name='text',style=16)
        self.textbook.SetForegroundColour((255, 255, 255, 255))
        self.textbook.SetOwnBackgroundColour((0, 0, 0, 255))
        self.textbook.SetValue("Loading . . . . . .")
        # self.Refresh()
        # self.Update()
        # #self.textbook.SetValue(response)
        # self.textbook.SetValue("Hello, how can I help you?")
        # self.timer.Start(10000, oneShot=True)
        # while self.timer.IsRunning():
        #     continue
        # self.timer.Stop()
        # self.Refresh()
        # self.Update()
        # self.textbook.Hide()

        
    


class myApp(wx.App):
    def  OnInit(self):
        self.frame = Frame()
        self.frame.Show(True)
        return True

if __name__ == '__main__':
    app = myApp()
    app.MainLoop()
