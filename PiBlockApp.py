#!/usr/local/bin/python3
# coding=utf-8
import sys
import os
import cmd
import time
from time import strftime
import readline
import socket
import logging
import urllib3.request
import json
import threading
import logging
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

from piBlockEngine import PiBlockEngine
from piBlockConfig import PiBlockConfig
from piBlockBTCQuote import PiBlockBTCQuote
from piBlockSSHControlServer import PiBlockSSHControlServer
from piBlockScreenManager import PiBlockScreenManager
from piBlockTenderScreen import PiBlockTenderScreen
from piBlockStartupScreen import PiBlockStartupScreen


RECOURCESFOLDER = 'resources/'
FONTSFOLDER = RECOURCESFOLDER + 'fonts/'
IMAGESFOLDER = RECOURCESFOLDER + 'images/'

#COMMON IMAGES
PBSMALLLOGO = IMAGESFOLDER + 'pbLogoSmall.png'
ADLSMALLLOGO = IMAGESFOLDER + 'AppsDesignLogo32.png'
BIZLOGO = IMAGESFOLDER + 'bizLogo.png'
#STARTUP SCREEN IMAGES
PBBANNER = IMAGESFOLDER + 'pbMainBanner.png'
STARTUPSMILEY = IMAGESFOLDER + 'startupSmiley.png'
#TENDER SCREEN IMAGES
ACPTBTC = IMAGESFOLDER + 'acceptBitcoin.png'
TENDERSMILEY= IMAGESFOLDER + 'tenderSmiley.png'

THEMECOLOR = '#34AADC'

class PiBlockApp(App):

    #-------------------------------------------------------------
    # Getters & Setters
    #-------------------------------------------------------------

    @property
    def pbSmallLogoImagePath(self):
        return "{}".format(PBSMALLLOGO)

    property
    def adlSmallLogoImagePath(self):
        return "{}".format(ADLSMALLLOGO)

    @property
    def bizLogoImagePath(self):
        return "{}".format(BIZLOGO)

    @property
    def pbBannerImagePath(self):
        return "{}".format(PBBANNER)

    @property
    def startupSmileyImagePath(self):
        return "{}".format(STARTUPSMILEY)
    
    @property
    def acceptBitcoinImagePath(self):
        return "{}".format(ACPTBTC)

    @property
    def tenderSmileyImagePath(self):
        return "{}".format(TENDERSMILEY)

    @property
    def uptime(self):
        return time.gmtime(Clock.get_boottime())

    @property
    def sshControlAddressCmd(self):
        return "ssh user@{} -p {}".format(self.sshHostName, self.piBlockEngine.sshPort)

    @property
    def lastStartupTime(self):
        return self._lastStartupTime

    @lastStartupTime.setter
    def lastStartupTime(self, lastStartupTime):
        self._lastStartupTime = lastStartupTime

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def fps(self):
        return Clock.get_fps()

    @property
    def sshHostAddress(self):
        return self._sshHostAddress

    @sshHostAddress.setter
    def sshHostAddress(self, sshHostAddress):
        self._sshHostAddress = sshHostAddress

    @property
    def sshHostName(self):
        return self._sshHostName

    @sshHostName.setter
    def sshHostName(self, sshHostName):
        self._sshHostName = sshHostName

    @property
    def currentScreen(self):
        return self._currentScreen

    @currentScreen.setter
    def currentScreen(self, currentScreen):
        self._currentScreen = currentScreen

    def __init__(self, **kwargs):
        
        super(PiBlockApp, self).__init__(**kwargs)

        Logger.debug("Initialising...")

        Logger.debug("Starting PiBlockEngine...")
        self.piBlockEngine = PiBlockEngine()
        Logger.debug("Starting PiBlockEngine...Done!")

        self.lastStartupTime = strftime('%Y/%-m/%-d %H:%M:%S')
        
        self.sshHostAddress = None
        self.sshHostName = None
        self.sshPort = None
        self.controlServer = None
        self.screenManager = None
        self.currentScreen = None

        self.status = 'Initialised'

        Logger.debug("Initialising...Done!")


    def build(self):

        kwargs = {'piBlockApp': self}

        self.screenManager = PiBlockScreenManager(**kwargs)

        self.screenManager.add_widget(PiBlockStartupScreen(name='startup', piBlockEngine=self.screenManager.app.piBlockEngine))
        self.screenManager.add_widget(PiBlockTenderScreen(name='tender', piBlockEngine=self.screenManager.app.piBlockEngine))

        self.status = 'Initialised'

        return self.screenManager

    #-------------------------------------------------------------
    # Overriden Methods
    #-------------------------------------------------------------

    def on_start(self):
        Logger.debug("on_start...")

        # self.root.current = 'startup'
        # self.currentScreen = self.root.ids['startup']
        

        # Logger.debug("ROOT IDS = {}".format(self.screenManager.current.ids.keys()))
        # Logger.debug("ROOT IDS in Current Screen = {}".format(self.currentScreen.ids.keys()))

        # self.testCommonGUITreeRefsInCurrentScreen()

        Logger.debug("Scheduling Running Tasks...")
        # Clock.schedule_once(lambda dt: self.loadStaticInfo(), 0.5)
        Clock.schedule_once(lambda dt: self.startControlServer(), 0.1)
        # Clock.schedule_once(lambda dt: self.loadQuoteInfo(), 0.3)
        
        # Clock.schedule_interval(self.updateClockInfo, 1)
        # Clock.schedule_interval(self.updateQuoteInfo, 60)

        Logger.debug("Scheduling Running Tasks...Done!")

        # self.getHeaderStatusLabel().text = "Status: [b]{}[/b]".format(self.status)

        # Clock.schedule_interval(self.updateSystemInfo, 1)

        Logger.debug("on_start...Done!")

    #-------------------------------------------------------------
    # Convenience Methods
    #-------------------------------------------------------------

    def themeColor(self):
        Logger.debug("ThemeColor Requested...")

        Logger.debug("ThemeColor Requested...Done!")

        return get_color_from_hex(THEMECOLOR)

    def getConfigValueForKey(self, key):

        if key == 'RSAKeyLocation':
            return self.piBlockEngine.rsaKeyLocation
        elif key == 'defaultCurrency':
            return self.piBlockEngine.defaultCurrency
        elif key == 'defaultCurrencySymbol':
            return self.piBlockEngine.defaultCurrencySymbol
        elif key == 'pricingLookupURL':
            return self.piBlockEngine.pricingLookupURL
        elif key == 'lastDailyTxCount':
            return self.piBlockEngine.lastDailyTxCount
        elif key == 'sshPort':
            return self.piBlockEngine.sshPort
        elif key == 'kpub':
            return self.piBlockEngine.kpub
        elif key == 'timeout':
            return self.piBlockEngine.timeout
        elif key == 'blockchainInterfaceURL':
            return self.piBlockEngine.blockchainInterfaceURL
        elif key == 'email':
            return self.piBlockEngine.email
        else:
            if self.piBlockEngine.config.get_configValueForKey(key) != None:
                return self.piBlockEngine.config.get_configValueForKey(key)
            else:
                return "Unknown"

    def moveIntoTenderingState(self):

        Logger.debug("BEFORE: self.root.current = {}".format(self.root.current))
        
        if self.isAppStatusInitialised():

            self.screenManager.current = 'tender'
            
            self.status = 'Tendering'

            Logger.debug("AFTER: self.root.current = {}".format(self.root.current))

        else:

            raise "PiBlock cannot move into the Tendering State because it is in a '{}' state.".format(self.status)

    def moveOutOfTenderingState(self):

        Logger.debug("BEFORE: self.root.current = {}".format(self.root.current))
        
        if self.isAppStatusTendering():

            self.screenManager.current = 'startup'

            self.status = 'Initialised'
            
            Logger.debug("AFTER: self.root.current = {}".format(self.root.current))

        else:

            raise "PiBlock cannot move out of the Tendering State because it is in a '{}' state.".format(self.status)   

    def isAppStatusProcessing(self):
        if self.status == 'Processing':
            return True
        else:
            return False

    def isAppStatusTendering(self):
        if self.status == 'Tendering':
            return True
        else: 
            return False

    def isAppStatusInitialised(self):

        if self.status == 'Initialised':
            return True
        else:
            return False

    #-------------------------------------------------------------
    # PiBlock SSH Control Server Convenience Methods
    #-------------------------------------------------------------
    def startControlServer(self):
        Logger.debug("Starting Control Server...")
        # self.piBlockEngine.startControlServer()

        if not self.controlServer:
            Logger.debug("Initialise PiBlock SSH Host...")

            try:            
                self.shhHostName = socket.gethostname()
                Logger.debug("SSH HostName: {}".format(self.shhHostName))
                self.sshHostAddress = socket.gethostbyname(self.shhHostName)

                Logger.debug("SSH HostAddress: {}".format(self.sshHostAddress))

            except Exception as e:
                Logger.warning("Failed to initialise PiBlock SSH Host because: {}".format(e.message))
        
            Logger.debug("Initialise PiBlock SSH Host...Done!")

        try:

            self.controlServer = PiBlockSSHControlServer(self, int(self.piBlockEngine.sshPort))
            #self.controlServer.startSSHServer()
        except BaseException as e:
            Logger.warning("Could Not start SSH Server because:\n{}".format(e.message))

            Logger.debug("Starting Control Server...Done!")

    def on_controlServerConnected(self, conn):
        Logger.debug("Control Server Connected!\n Connection Details: {}".format(conn))

        self.controlServerConn = conn

    def on_controlMsgRcvd(self, data):
        Logger.debug("A Control Message was recieved: {} from connection {}".format(data, self.controlServerConn))


    #-------------------------------------------------------------
    # SomeTests
    #-------------------------------------------------------------

    def testCommonGUITreeRefsInCurrentScreen(self):

        Logger.debug("Ids in Current = {}".format(self.root.ids.keys()))
        # Logger.debug("Ids in Current Screen = {}".format(self.currentScreen.ids.keys()))
        Logger.debug("Ids in Current Screen Header = {}".format(self.getHeader().ids.keys()))
        
        Logger.debug("Ids in Current Screen Header BizLogo = {}".format(self.getHeaderBizLogo()))

        Logger.debug("Ids in Current Screen Header Clock = {}".format(self.getHeaderClock().ids.keys()))
        Logger.debug("Ids in Current Screen Header Time = {}".format(self.getHeaderClockTimeLabel()))
        Logger.debug("Ids in Current Screen Header Date = {}".format(self.getHeaderClockDateLabel()))

        Logger.debug("Ids in Current Screen Header Status Label = {}".format(self.getHeaderStatusLabel()))

        Logger.debug("Ids in Current Screen Header Quote = {}".format(self.getHeaderQuote().ids.keys()))
        Logger.debug("Ids in Current Screen Header Quote Btc Rate = {}".format(self.getHeaderQuoteBTCRateLabel()))
        Logger.debug("Ids in Current Screen Header Quote Currency Rate = {}".format(self.getHeaderQuoteCurrencyRateLabel()))
        Logger.debug("Ids in Current Screen Header Quote Src Rate = {}".format(self.getHeaderQuoteSrcLabel()))

        Logger.debug("Ids in Current Screen Footer = {}".format(self.getFooter().ids.keys()))

if __name__ == '__main__':
    # Config.set('graphics', 'width', '1280')
    # Config.set('graphics', 'height', '720')  # 16:9
    Config.set('graphics', 'resizable', '1')
    Config.set('input', 'mouse', 'mouse,disable_multitouch')
    Config.set('kivy', 'log_enable', 1)
    Config.set('kivy', 'log_level', 'debug')
    LabelBase.register(name='Roboto', fn_regular=FONTSFOLDER  + 'Roboto-Light.ttf', fn_bold=FONTSFOLDER  + 'Roboto-Bold.ttf', fn_italic=FONTSFOLDER + 'Roboto-LightItalic.ttf')
    LabelBase.register(name='RobotoCondensed', fn_regular=FONTSFOLDER + 'RobotoCondensed-Light.ttf', fn_bold=FONTSFOLDER  + 'RobotoCondensed-Regular.ttf')
    # Window.fullscreen = True
    Window.size = (960, 540)
    Window.clearcolor = get_color_from_hex('#FFFFFF')
    PiBlockApp().run()