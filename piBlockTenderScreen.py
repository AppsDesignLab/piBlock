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

class PiBlockTenderScreen(Screen):

    def __init__(self, **kwargs):
        super(PiBlockTenderScreen, self).__init__(**kwargs)
        Logger.debug("kwargs = {}".format(kwargs.keys()))
        self.piBlockEngine = kwargs['piBlockEngine']
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        Logger.debug("Screen {}...".format(self))
        Logger.debug("Screen IDs = {}".format(self.ids.keys()))
        Logger.debug("Screen Manager = {}".format(self.manager))
        Logger.debug("Screen piBlockEngine = {}".format(self.piBlockEngine))

    def on_enter(self):
        Logger.debug("Entering Screen '{}'...".format(self.name))

        Logger.debug("Scheduling Once Off Tasks...")
        Clock.schedule_once(lambda dt: self.manager.loadCommon, 0.1)
        # Clock.schedule_once(lambda dt: self.loadStaticInfo(), 0.2)
        Logger.debug("Scheduling Once Off Tasks...Done!")

        Logger.debug("Scheduling Common Recurring Tasks...")
        Clock.schedule_interval(self.manager.updateCommon, 1)
        Logger.debug("Scheduling Comnmon Recurring Tasks...Done!")

        Logger.debug("Entering Screen '{}'...Done!".format(self.manager.current))

    def on_leave(self):
        Logger.debug("Leaving Screen '{}'...".format(self.name))
        
        Clock.unschedule(self.manager.updateCommon)

        Logger.debug("Leaving Screen '{}'...Done!".format(self.name))



    #-------------------------------------------------------------
    # Common UI Element Updates
    #-------------------------------------------------------------

