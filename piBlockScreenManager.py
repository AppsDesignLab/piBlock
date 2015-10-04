#!/usr/local/bin/python3
# coding=utf-8
import time
from time import strftime
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics import Color
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.properties import ObjectProperty
from kivy.properties import ObservableDict
from kivy.logger import Logger
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.graphics.context_instructions import Color

class PiBlockScreenManager(ScreenManager):
    
    def __init__(self, **kwargs):
        Logger.debug("Initialising PiBlockScreenManager...")
        
        super(PiBlockScreenManager, self).__init__(**kwargs)

        Logger.debug("Recieved KWARGS = {}".format(kwargs.keys()))
        self.app = kwargs['piBlockApp']
        self.transition = FadeTransition()

        Clock.schedule_once(self._finish_init)

        Logger.debug("Initialising PiBlockScreenManager..Done!")

    def _finish_init(self, dt):
        Logger.debug("Screen Manager {}...".format(self))
        # Logger.debug("Screen IDs = {}".format(self.ids.keys()))
        # Logger.debug("Screen Manager = {}".format(self.manager))
        # Logger.debug("Screen piBlockEngine = {}".format(self.piBlockEngine))
        # Logger.debug("Screen Manager Root = {}".format(self.root.ids.keys()))
        # Logger.debug("App = {}".format(PiBlockApp()))



    #-------------------------------------------------------------
    # Common UI Element Updates
    #-------------------------------------------------------------

    # def loadCommonUI(self):
    #     self.loadQuoteInfo()
    #     self.loadStaticInfo()

    # def scheduleCommonUpdates(self):
    #     Clock.schedule_interval(self.updateStatusInfo, 1)
    #     Clock.schedule_interval(self.updateClockInfo, 1)
    #     Clock.schedule_interval(self.updateQuoteInfo, 60)

    # def unscheduleCommonUpdates(self):
    #     Clock.unschedule(self.updateStatusInfo)
    #     Clock.unschedule(self.updateClockInfo)
    #     Clock.unschedule(self.updateQuoteInfo)







    

    