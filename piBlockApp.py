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
ADLSMALLLOGO = IMAGESFOLDER + 'appsDesignLogo64.png'
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

    @property
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

        Logger.debug("Initialising...")
        
        super(PiBlockApp, self).__init__(**kwargs)

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
        self.status = None
        
        # self.status = 'Initialised'

        Logger.debug("Initialising...Done!")

    #-------------------------------------------------------------
    # Overriden Methods
    #-------------------------------------------------------------

    def on_start(self):
        Logger.debug("on_start...")

        # self.root.current = 'startup'
        # self.currentScreen = self.root.ids['startup']

        self.testGUITreeRefs()

        Clock.schedule_once(lambda dt: self.loadStaticImages(), 0.1)
        Clock.schedule_once(lambda dt: self.loadStaticInfo(), 0.2)
        Clock.schedule_once(lambda dt: self.loadQuoteInfo(), 0.3)
        Clock.schedule_once(lambda dt: self.startControlServer(), 0.1)
        Clock.schedule_once(lambda dt: self.initialiseScreenManager(), 0.2)

        Logger.debug("Scheduling Running Tasks...")
        
        
        # Clock.schedule_once(lambda dt: self.loadQuoteInfo(), 0.3)
        Clock.schedule_interval(self.updateStatusInfo, 1)
        Clock.schedule_interval(self.updateClockInfo, 1)
        Clock.schedule_interval(self.updateQuoteInfo, 60)

        Logger.debug("Scheduling Running Tasks...Done!")

        # self.getHeaderStatusLabel().text = "Status: [b]{}[/b]".format(self.status)

        # Clock.schedule_interval(self.updateSystemInfo, 1)

        Logger.debug("on_start...Done!")

    #-------------------------------------------------------------
    # Convenience Methods
    #-------------------------------------------------------------

    def loadStaticImages(self):
        Logger.debug("Loading & Setting Static Images...")
        print("{}".format(self.bizLogoImagePath))
        print("{}".format(self.pbSmallLogoImagePath))
        print("{}".format(self.adlSmallLogoImagePath))

        try:
            self.getHeaderBizLogo().source = str(self.bizLogoImagePath)
        
        except Exception as e:
            Logger.error("Error Loading Business Logo Image file at path '{}' beacause:\n{}".format(self.bizLogoImagePath, e.message))

        try:
            self.getFooterPBLogoThumbnailImage().source = str(self.pbSmallLogoImagePath)
        
        except Exception as e:
            Logger.error("Error Loading Business Logo Image file at path '{}' beacause:\n{}".format(self.pbSmallLogoImagePath, e.message))

        try:
            self.getFooterADLLogoThumbnailImage().source = str(self.adlSmallLogoImagePath)
        
        except Exception as e:
            Logger.error("Error Loading Business Logo Image file at path '{}' beacause:\n{}".format(self.adlSmallLogoImagePath, e.message))

        Logger.debug("Loading & Setting Static Images...Done!")

    def loadStaticInfo(self):
        Logger.debug("Loading Static Info...")

        self.getHeaderQuoteSrcLabel().text = "[i]source: {}".format(self.piBlockEngine.pricingLookupURL)

        Logger.debug("Loading Static Info...Done!")

    def loadQuoteInfo(self):
        Logger.debug("Loading Quote Info...")

        Logger.debug("Default Currency = {}".format(self.piBlockEngine.defaultCurrency))

        if self.piBlockEngine.defaultCurrency != None:
            Logger.debug("Setting Quote Info...")

            self.getHeaderQuoteBTCRateLabel().text = "[b]{} {}1.00[/b] = [b]{} BTC[/b]".format(self.piBlockEngine.defaultCurrency, self.piBlockEngine.defaultCurrencySymbol, self.piBlockEngine.rateForBTC(self.piBlockEngine.defaultCurrency))
            self.getHeaderQuoteCurrencyRateLabel().text = "[b]1 BTC[/b] = [b]{} {}{}[/b]".format(self.piBlockEngine.defaultCurrency, self.piBlockEngine.defaultCurrencySymbol, self.piBlockEngine.rateForCurrency(self.piBlockEngine.defaultCurrency))

        Logger.debug("Loading & Setting Quote Info...Done!")

    def updateStatusInfo(self, nap):
        Logger.debug("Update Status Objects...")
        self.getHeaderStatusLabel().text = "Status: [b]{}[/b]".format(self.status)
        Logger.debug("Update Status Objects...Done!")


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

    def themeColor(self):
        Logger.debug("ThemeColor Requested...")

        Logger.debug("ThemeColor Requested...Done!")

        return get_color_from_hex(THEMECOLOR)

    def initialiseScreenManager(self):

        Logger.debug("Initialising ScreenManager...")

        kwargs = {'piBlockApp': self}

        Logger.debug("Passing KWARGS = {}".format(kwargs))

        self.screenManager = PiBlockScreenManager(**kwargs)

        self.getContentLayout().add_widget(self.screenManager)

        self.screenManager.add_widget(PiBlockStartupScreen(name='startup', piBlockEngine=self.piBlockEngine))
        self.screenManager.add_widget(PiBlockTenderScreen(name='tender', piBlockEngine=self.piBlockEngine))

        self.screenManager.current = 'startup'
        self.currentScreen = 'startup'

        self.status = 'Initialised'

        Logger.debug("Initialising ScreenManager...Done!")

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

        Logger.debug("BEFORE: self.currentScreen = {}".format(self.currentScreen))
        
        if self.isAppStatusInitialised():

            Window.clearcolor = get_color_from_hex('#FFFFFF')

            self.screenManager.current = 'tender'
            self.currentScreen = 'tender'
            
            self.status = 'Tendering'

            Logger.debug("AFTER: sself.currentScreen = {}".format(self.currentScreen))

        else:

            raise "PiBlock cannot move into the Tendering State because it is in a '{}' state.".format(self.status)

    def moveOutOfTenderingState(self):

        Logger.debug("BEFORE: self.currentScreen = {}".format(self.currentScreen))
        
        if self.isAppStatusTendering():

            Window.clearcolor = get_color_from_hex('#FFFFFF')

            self.screenManager.current = 'startup'
            self.currentScreen = 'startup'

            self.status = 'Initialised'
            
            Logger.debug("AFTER: self.currentScreen = {}".format(self.currentScreen))

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
    # Common Screen Element References And UI Updates
    #-------------------------------------------------------------

    def getHeader(self):
        #currentScreen = self.get_screen(self.current)
        #Logger.debug("PiBlockScreenManager's Current Screen is {}".format(self.root.ids.keys()))
        Logger.debug("Header IDs = {}".format(self.root.ids['header'].ids.keys()))

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
        Logger.debug("Header IDs = {}".format(self.root.ids['footer'].ids.keys()))
        return self.root.ids['footer']

    def getFooterPBLogoThumbnailImage(self):
        return self.getFooter().ids['pblogothumbnail']

    def getFooterADLLogoThumbnailImage(self):
        return self.getFooter().ids['adllogothumbnail']

    def getContentLayout(self):
        return self.root.ids['content']

    #-------------------------------------------------------------
    # SomeTests
    #-------------------------------------------------------------

    def testGUITreeRefs(self):

        Logger.debug("Testing GUI Tree References...")

        Logger.debug("Root IDs = {}".format(self.root.ids.keys()))
        # Logger.debug("Ids in Current Screen = {}".format(self.currentScreen.ids.keys()))
        Logger.debug("Header IDs = {}".format(self.getHeader().ids.keys()))
        Logger.debug("Header BizLogo IDs = {}".format(self.getHeaderBizLogo()))
        Logger.debug("Header Clock IDs = {}".format(self.getHeaderClock().ids.keys()))
        Logger.debug("Header Time IDs = {}".format(self.getHeaderClockTimeLabel()))
        Logger.debug("Header Date IDs = {}".format(self.getHeaderClockDateLabel()))
        Logger.debug("Header Status Label IDs = {}".format(self.getHeaderStatusLabel()))

        Logger.debug("Header Quote IDs = {}".format(self.getHeaderQuote().ids.keys()))
        Logger.debug("Header Quote Btc Rate IDs = {}".format(self.getHeaderQuoteBTCRateLabel()))
        Logger.debug("Header Quote Currency Rate IDs = {}".format(self.getHeaderQuoteCurrencyRateLabel()))
        Logger.debug("Header Quote Src Rate IDs = {}".format(self.getHeaderQuoteSrcLabel()))

        Logger.debug("Footer IDs = {}".format(self.getFooter().ids.keys()))
        Logger.debug("Footer PBLogoThumbnailImage IDs = {}".format(self.getFooterPBLogoThumbnailImage()))
        Logger.debug("Footer PBLogoThumbnailImage IDs = {}".format(self.getFooterADLLogoThumbnailImage()))

        Logger.debug("Testing GUI Tree References...Done!")



if __name__ == '__main__':
    # Config.set('graphics', 'width', '1280')
    # Config.set('graphics', 'height', '720')  # 16:9
    Config.set('graphics', 'resizable', '1')
    Config.set('graphics', 'borderless', '1')
    Config.set('input', 'mouse', 'mouse,disable_multitouch')
    Config.set('kivy', 'log_enable', 1)
    Config.set('kivy', 'log_level', 'debug')
    LabelBase.register(name='Roboto', fn_regular=FONTSFOLDER  + 'Roboto-Light.ttf', fn_bold=FONTSFOLDER  + 'Roboto-Bold.ttf', fn_italic=FONTSFOLDER + 'Roboto-LightItalic.ttf')
    LabelBase.register(name='RobotoCondensed', fn_regular=FONTSFOLDER + 'RobotoCondensed-Light.ttf', fn_bold=FONTSFOLDER  + 'RobotoCondensed-Regular.ttf')
    # Window.fullscreen = True
    # Window.size = (960, 540)
    Window.clearcolor = get_color_from_hex('#FFFFFF')
    PiBlockApp().run()