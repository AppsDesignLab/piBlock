#!/usr/local/bin/python3
# coding=utf-8
import sys
import os
import cmd
import time
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
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics.context_instructions import Color
from kivy.support import install_twisted_reactor
install_twisted_reactor()
from twisted.internet import protocol, reactor
# from twisted.logger import Logger
from time import strftime
from piBlockEngine import PiBlockEngine
from piBlockConfig import PiBlockConfig
from piBlockBTCQuote import PiBlockBTCQuote
# from piBlockControlServer import PiBlockControlServerFactory, PiBlockControlServer
from piBlockSSHControlServer import PiBlockSSHControlServer

RECOURCESFOLDER = 'resources/'
FONTSFOLDER = RECOURCESFOLDER + 'fonts/'
IMAGESFOLDER = RECOURCESFOLDER + 'images/'
PBBANNER = IMAGESFOLDER + 'pbMainBanner.png'
PBLOGOSMALL = IMAGESFOLDER + 'pbLogoSmall.png'
ADLLOGOSMALL = IMAGESFOLDER + 'AppsDesignLogo64.png'
SMILEY1 = IMAGESFOLDER + 'Smiley-1.png'
BIZLOGO = IMAGESFOLDER + 'bizLogo.png'
THEMECOLOR = '#34AADC'

class StartupScreen(Screen):

    def __init__(self, **kwargs):
        super(StartupScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        Logger.debug("Screen {}...".format(self))
        Logger.debug("Screen IDs = {}".format(self.ids.keys()))
        Logger.debug("Screen Manager = {}".format(self.manager))
        Logger.debug("App = {}".format(PiBlockApp))
        # Clock.schedule_once(lambda dt: self.app.updateQuoteInfo(0), 0.1)
        # Clock.schedule_once(lambda dt: PiBlockApp.loadStaticInfo(), 0.5)
        # Clock.schedule_once(lambda dt: PiBlockApp.loadStaticImages())
        # Clock.schedule_interval(PiBlockApp.updateClockInfo, 1)
        # Clock.schedule_interval(PiBlockApp.updateQuoteInfo, 60)

        Clock.schedule_interval(self.updateSystemInfo, 2)

    def updateSystemInfo(self, nap):

        Logger.debug("Updating System Info...")

        self.getUptimeLabel().text = "[i]Running for:[/i] [b]{}[/b]".format(time.strftime('%H Hrs, %M Mins, %S Secs', time.gmtime(Clock.get_boottime())))
        self.getFPSLabel().text = "[i]Avg FPS:[/i] [b]{0:.2f}[b]".format(Clock.get_fps())
        Logger.debug("Updating System Info...Done!")

    #-------------------------------------------------------------
    # Common Screen Element References
    #-------------------------------------------------------------
    #['laststartedlabel', 'defaultcurrencylabel', 'sshaddresslabel', 'emaillabel', 'controlportlabel', 'timeoutlabel', 'smileyIcon', 'fpslabel', 'uptimelabel', 'pbMainBanner']

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







class TenderScreen(Screen):
    pass

class PiBlockScreenManager(ScreenManager):
    pass

class PiBlockApp(App):

    #-------------------------------------------------------------
    # Getters & Setters
    #-------------------------------------------------------------

    @property
    def uptime(self):
        return time.gmtime(Clock.get_boottime())

    @property
    def sshControlAddressCmd(self):
        return "ssh user@{} -p {}".format(self.sshHostName, self.piBlockEngine.sshPort)

    @property
    def smiley1Image(self):
        return SMILEY1

    @property
    def pbBannerImage(self):
        return PBBANNER

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
        self.status = None
        self.sshHostAddress = None
        self.sshHostName = None
        self.sshPort = None
        self.controlServer = None
        self.currentScreen = None

        Logger.debug("Initialising...Done!")

    #-------------------------------------------------------------
    # Overriden Methods
    #-------------------------------------------------------------

    def on_start(self):
        Logger.debug("on_start...")

        self.root.current = 'startup'

        self.currentScreen = self.root.ids['startup']

        Logger.debug("ROOT IDS = {}".format(self.root.ids.keys()))
        Logger.debug("ROOT IDS in Current Screen = {}".format(self.currentScreen.ids.keys()))

        self.testCommonGUITreeRefsInCurrentScreen()

        Logger.debug("Scheduling Running Tasks...")
        Clock.schedule_once(lambda dt: self.loadStaticInfo(), 0.5)
        Clock.schedule_once(lambda dt: self.startControlServer(), 0.1)
        Clock.schedule_once(lambda dt: self.loadQuoteInfo(), 0.3)
        
        Clock.schedule_interval(self.updateClockInfo, 1)
        Clock.schedule_interval(self.updateQuoteInfo, 60)

        Logger.debug("Scheduling Running Tasks...Done!")

        self.status = 'Initialised'
        self.getHeaderStatusLabel().text = "Status: [b]{}[/b]".format(self.status)

        # Clock.schedule_interval(self.updateSystemInfo, 1)

        Logger.debug("on_start...Done!")

    #-------------------------------------------------------------
    # Convenience Methods
    #-------------------------------------------------------------

    def updateClockInfo(self, nap):
        Logger.debug("Update ClockUI Objects...")

        self.getHeaderClockDateLabel().text = strftime('[b]%A, %d %b %Y[/b]')
        self.getHeaderClockTimeLabel().text = strftime('[b]%I:%M[/b]:%S %p')

        Logger.debug("Update ClockUI Objects...Done!")

    def updateQuoteInfo(self, nap):
        Logger.debug("Updating Quote Info...")

        Logger.debug("Default Currency = {}".format(self.piBlockEngine.defaultCurrency))

        if self.piBlockEngine.defaultCurrency != None:
            Logger.debug("Setting Quote Info...")

            self.getHeaderQuoteBTCRateLabel().text = "[b]{} {}1.00[/b] = [b]{} BTC[/b]".format(self.piBlockEngine.defaultCurrency, self.piBlockEngine.defaultCurrencySymbol, self.piBlockEngine.rateForBTC(self.piBlockEngine.defaultCurrency))
            self.getHeaderQuoteCurrencyRateLabel().text = "[b]1 BTC[/b] = [b]{} {}{}[/b]".format(self.piBlockEngine.defaultCurrency, self.piBlockEngine.defaultCurrencySymbol, self.piBlockEngine.rateForCurrency(self.piBlockEngine.defaultCurrency))

        Logger.debug("Loading & Setting Quote Info...Done!")

    def loadStaticInfo(self):
        Logger.debug("Loading Static Info...")

        self.getHeaderQuoteSrcLabel().text = "[i]source: {}".format(self.piBlockEngine.pricingLookupURL)
        self.loadStaticImages()

        Logger.debug("Loading Static Info...Done!")

    def loadQuoteInfo(self):
        Logger.debug("Updating Quote Info...")

        Logger.debug("Default Currency = {}".format(self.piBlockEngine.defaultCurrency))

        if self.piBlockEngine.defaultCurrency != None:
            Logger.debug("Setting Quote Info...")

            self.getHeaderQuoteBTCRateLabel().text = "[b]{} {}1.00[/b] = [b]{} BTC[/b]".format(self.piBlockEngine.defaultCurrency, self.piBlockEngine.defaultCurrencySymbol, self.piBlockEngine.rateForBTC(self.piBlockEngine.defaultCurrency))
            self.getHeaderQuoteCurrencyRateLabel().text = "[b]1 BTC[/b] = [b]{} {}{}[/b]".format(self.piBlockEngine.defaultCurrency, self.piBlockEngine.defaultCurrencySymbol, self.piBlockEngine.rateForCurrency(self.piBlockEngine.defaultCurrency))

        Logger.debug("Loading & Setting Quote Info...Done!")
    

    def loadStaticImages(self):
        Logger.debug("Loading & Setting Static Images...")

        self.getHeaderBizLogo().source = BIZLOGO
        self.getFooterPBLogoThumbnailImage().source = PBLOGOSMALL
        self.getFooteraADLLogThumbNailImage().source = ADLLOGOSMALL

        Logger.debug("Loading & Setting Static Images...Done!")

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
    # Common Screen Element References
    #-------------------------------------------------------------

    def getHeader(self):
        return self.root.ids['header']

    def getHeaderStatusLabel(self):
        return self.getHeader().ids['statuslabel']

    def getHeaderClock(self):
        return self.getHeader().ids['clock']

    def getHeaderClockTimeLabel(self):
        return self.getHeaderClock().ids['time']

    def getHeaderClockDateLabel(self):
        return self.getHeaderClock().ids['date']

    def getHeaderBizLogo(self):
        return self.getHeader().ids['bizlogo']

    def getHeaderQuote(self):
        return self.getHeader().ids['quote']

    def getHeaderQuoteBTCRateLabel(self):
        return self.getHeaderQuote().ids['quotebtcratelabel']

    def getHeaderQuoteCurrencyRateLabel(self):
        return self.getHeaderQuote().ids['quotecurrencyratelabel']

    def getHeaderQuoteSrcLabel(self):
        return self.getHeaderQuote().ids['quotesrclabel']

    def getFooter(self):
        return self.root.ids['footer']

    def getFooterPBLogoThumbnailImage(self):
        return self.getFooter().ids['pblogothumbnail']

    def getFooteraADLLogThumbNailImage(self):
        return self.getFooter().ids['adllogothumbnail']

    #-------------------------------------------------------------
    # SomeTests
    #-------------------------------------------------------------

    def testCommonGUITreeRefsInCurrentScreen(self):

        Logger.debug("Ids in Current = {}".format(self.root.ids.keys()))
        Logger.debug("Ids in Current Screen = {}".format(self.currentScreen.ids.keys()))
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
    Config.set('graphics', 'width', '640')
    Config.set('graphics', 'height', '360')  # 16:9
    Config.set('graphics', 'resizable', '0')
    Config.set('input', 'mouse', 'mouse,disable_multitouch')
    Config.set('kivy', 'log_enable', 1)
    Config.set('kivy', 'log_level', 'debug')
    LabelBase.register(name='Roboto', fn_regular=FONTSFOLDER  + 'Roboto-Light.ttf', fn_bold=FONTSFOLDER  + 'Roboto-Bold.ttf', fn_italic=FONTSFOLDER + 'Roboto-LightItalic.ttf')
    LabelBase.register(name='RobotoCondensed', fn_regular=FONTSFOLDER + 'RobotoCondensed-Light.ttf', fn_bold=FONTSFOLDER  + 'RobotoCondensed-Regular.ttf')
    Window.clearcolor = get_color_from_hex('#FFFFFF')
    PiBlockApp().run()