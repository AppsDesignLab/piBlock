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

class PiBlockStartupScreen(Screen):

    def __init__(self, **kwargs):
        super(PiBlockStartupScreen, self).__init__(**kwargs)
        Logger.debug("kwargs = {}".format(kwargs.keys()))
        self.piBlockEngine = kwargs['piBlockEngine']

        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        Logger.debug("Screen {}...".format(self))
        Logger.debug("Screen IDs = {}".format(self.ids.keys()))
        Logger.debug("Screen Manager = {}".format(self.manager))
        Logger.debug("Screen piBlockEngine = {}".format(self.piBlockEngine))
        # Logger.debug("Screen Manager Root = {}".format(self.manager.root.ids.keys()))
        # Logger.debug("App = {}".format(PiBlockApp()))

    def on_enter(self):
        Logger.debug("Entering Screen '{}'...".format(self.name))

        Logger.debug("Scheduling Once Off Tasks...")
        Clock.schedule_once(lambda dt: self.manager.loadCommonUI(), 0.1)
        # Clock.schedule_once(lambda dt: self.loadStaticInfo(), 0.2)
        Logger.debug("Scheduling Once Off Tasks...Done!")

        Logger.debug("Scheduling Common Recurring Tasks...")
        self.manager.scheduleCommonUpdates()
        Logger.debug("Scheduling Comnmon Recurring Tasks...Done!")

        Logger.debug("Scheduling Screen Specific Recurring Tasks...")
        Clock.schedule_interval(self.updateSystemInfo, 1)
        Logger.debug("Scheduling Screen Specific Recurring Tasks...Done!")

        Logger.debug("Entering Screen '{}'...Done!".format(self.manager.current))

    def on_pre_leave(self):
        Logger.debug("Pre-Leaving Screen '{}'...".format(self.name))
        
        self.manager.unscheduleCommonUpdates()

        Clock.unschedule(self.updateSystemInfo)

        Logger.debug("Pre-Leaving Screen '{}'...Done!".format(self.name))

    #-------------------------------------------------------------
    # Screen Element References And UI Updates
    #-------------------------------------------------------------
    def updateSystemInfo(self, nap):

        Logger.debug("Updating System Info...")

        self.getUptimeLabel().text = "[i]Running for:[/i] [b]{}[/b]".format(time.strftime('%H Hrs, %M Mins, %S Secs', time.gmtime(Clock.get_boottime())))
        self.getFPSLabel().text = "[i]Avg FPS:[/i] [b]{0:.2f}[b]".format(Clock.get_fps())

        Logger.debug("Updating System Info...Done!")

    def getStartedLabel(self):
        return self.ids['laststartedlabel']

    def getDefaultCurrencyLabel(self):
        return self.ids['defaultcurrencylabel']

    def getSSHAddressLabel(self):
         return self.ids['sshaddresslabel']

    def getEmailLabel(self):
        return self.ids['emaillabel']

    def getControlPortLabel(self):
        return self.ids['controlportlabel']

    def getTimeoutLabel(self):
        return self.ids['timeoutlabel']

    def getSmileyIconImage(self):
        return self.ids['smileyIconImage']

    def getFPSLabel(self):
        return self.ids['fpslabel']

    def getUptimeLabel(self):
        return self.ids['uptimelabel']

    def getPBMainBannerImage(self):
        return self.ids['pbMainBannerImage']
