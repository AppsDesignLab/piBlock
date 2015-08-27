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
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
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
        Clock.schedule_once(lambda dt: self.loadQuoteInfo(), 0.1)
        Clock.schedule_once(lambda dt: self.loadStaticInfo(), 0.2)
        Logger.debug("Scheduling Once Off Tasks...Done!")

        Logger.debug("Scheduling Common Recurring Tasks...")
        Clock.schedule_interval(self.updateStatusInfo, 1)
        Clock.schedule_interval(self.updateClockInfo, 1)
        Clock.schedule_interval(self.updateQuoteInfo, 15)
        Logger.debug("Scheduling Comnmon Recurring Tasks...Done!")

        Logger.debug("Scheduling Screen Specific Recurring Tasks...")
        Clock.schedule_interval(self.updateSystemInfo, 1)
        Logger.debug("Scheduling Screen Specific Recurring Tasks...Done!")

        Logger.debug("Entering Screen '{}'...Done!".format(self.manager.current))

    #-------------------------------------------------------------
    # Common UI Element Updates
    #-------------------------------------------------------------

    def loadQuoteInfo(self):
        Logger.debug("Updating Quote Info...")

        Logger.debug("Default Currency = {}".format(self.piBlockEngine.defaultCurrency))

        if self.piBlockEngine.defaultCurrency != None:
            Logger.debug("Setting Quote Info...")

            self.manager.getHeaderQuoteBTCRateLabel().text = "[b]{} {}1.00[/b] = [b]{} BTC[/b]".format(self.piBlockEngine.defaultCurrency, self.piBlockEngine.defaultCurrencySymbol, self.piBlockEngine.rateForBTC(self.piBlockEngine.defaultCurrency))
            self.manager.getHeaderQuoteCurrencyRateLabel().text = "[b]1 BTC[/b] = [b]{} {}{}[/b]".format(self.piBlockEngine.defaultCurrency, self.piBlockEngine.defaultCurrencySymbol, self.piBlockEngine.rateForCurrency(self.piBlockEngine.defaultCurrency))

        Logger.debug("Loading & Setting Quote Info...Done!")

    def loadStaticInfo(self):
        Logger.debug("Loading Static Info...")

        self.manager.getHeaderQuoteSrcLabel().text = "[i]source: {}".format(self.piBlockEngine.pricingLookupURL)
        self.loadStaticImages()

        Logger.debug("Loading Static Info...Done!")

    def loadStaticImages(self):
        Logger.debug("Loading & Setting Static Images...")

        self.manager.getHeaderBizLogo().source = BIZLOGO
        self.manager.getFooterPBLogoThumbnailImage().source = PBLOGOSMALL
        self.manager.getFooteraADLLogThumbNailImage().source = ADLLOGOSMALL

        Logger.debug("Loading & Setting Static Images...Done!")

    def updateStatusInfo(self, nap):
        Logger.debug("Update Status Objects...")
        self.manager.getHeaderStatusLabel().text = "Status: [b]{}[/b]".format(self.manager.app.status)
        Logger.debug("Update Status Objects...Done!")


    def updateClockInfo(self, nap):
        Logger.debug("Update ClockUI Objects...")

        self.manager.getHeaderClockDateLabel().text = strftime('[b]%A, %d %b %Y[/b]')
        self.manager.getHeaderClockTimeLabel().text = strftime('[b]%I:%M[/b]:%S %p')

        Logger.debug("Update ClockUI Objects...Done!")

    def updateQuoteInfo(self, nap):
        Logger.debug("Updating Quote Info...")

        Logger.debug("Default Currency = {}".format(self.piBlockEngine.defaultCurrency))

        if self.piBlockEngine.defaultCurrency != None:
            Logger.debug("Setting Quote Info...")

            self.manager.getHeaderQuoteBTCRateLabel().text = "[b]{} {}1.00[/b] = [b]{} BTC[/b]".format(self.piBlockEngine.defaultCurrency, self.piBlockEngine.defaultCurrencySymbol, self.piBlockEngine.rateForBTC(self.piBlockEngine.defaultCurrency))
            self.manager.getHeaderQuoteCurrencyRateLabel().text = "[b]1 BTC[/b] = [b]{} {}{}[/b]".format(self.piBlockEngine.defaultCurrency, self.piBlockEngine.defaultCurrencySymbol, self.piBlockEngine.rateForCurrency(self.piBlockEngine.defaultCurrency))

        Logger.debug("Loading & Setting Quote Info...Done!")

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


class TenderScreen(Screen):

    def __init__(self, **kwargs):
        super(TenderScreen, self).__init__(**kwargs)
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
        Clock.schedule_once(lambda dt: self.loadQuoteInfo(), 0.1)
        Clock.schedule_once(lambda dt: self.loadStaticInfo(), 0.2)
        Logger.debug("Scheduling Once Off Tasks...Done!")

        Logger.debug("Scheduling Common Recurring Tasks...")
        Clock.schedule_interval(self.updateStatusInfo, 1)
        Clock.schedule_interval(self.updateClockInfo, 1)
        Clock.schedule_interval(self.updateQuoteInfo, 15)
        Logger.debug("Scheduling Comnmon Recurring Tasks...Done!")

        Logger.debug("Entering Screen '{}'...Done!".format(self.manager.current))


    #-------------------------------------------------------------
    # Common UI Element Updates
    #-------------------------------------------------------------

    def loadQuoteInfo(self):
        Logger.debug("Updating Quote Info...")

        Logger.debug("Default Currency = {}".format(self.piBlockEngine.defaultCurrency))

        if self.piBlockEngine.defaultCurrency != None:
            Logger.debug("Setting Quote Info...")

            self.manager.getHeaderQuoteBTCRateLabel().text = "[b]{} {}1.00[/b] = [b]{} BTC[/b]".format(self.piBlockEngine.defaultCurrency, self.piBlockEngine.defaultCurrencySymbol, self.piBlockEngine.rateForBTC(self.piBlockEngine.defaultCurrency))
            self.manager.getHeaderQuoteCurrencyRateLabel().text = "[b]1 BTC[/b] = [b]{} {}{}[/b]".format(self.piBlockEngine.defaultCurrency, self.piBlockEngine.defaultCurrencySymbol, self.piBlockEngine.rateForCurrency(self.piBlockEngine.defaultCurrency))

        Logger.debug("Loading & Setting Quote Info...Done!")

    def loadStaticInfo(self):
        Logger.debug("Loading Static Info...")

        self.manager.getHeaderQuoteSrcLabel().text = "[i]source: {}".format(self.piBlockEngine.pricingLookupURL)
        self.loadStaticImages()

        Logger.debug("Loading Static Info...Done!")

    def loadStaticImages(self):
        Logger.debug("Loading & Setting Static Images...")

        self.manager.getHeaderBizLogo().source = BIZLOGO
        self.manager.getFooterPBLogoThumbnailImage().source = PBLOGOSMALL
        self.manager.getFooteraADLLogThumbNailImage().source = ADLLOGOSMALL

        Logger.debug("Loading & Setting Static Images...Done!")

    def updateStatusInfo(self, nap):
        Logger.debug("Update Status Objects...")
        self.manager.getHeaderStatusLabel().text = "Status: [b]{}[/b]".format(self.manager.app.status)
        Logger.debug("Update Status Objects...Done!")


    def updateClockInfo(self, nap):
        Logger.debug("Update ClockUI Objects...")

        self.manager.getHeaderClockDateLabel().text = strftime('[b]%A, %d %b %Y[/b]')
        self.manager.getHeaderClockTimeLabel().text = strftime('[b]%I:%M[/b]:%S %p')

        Logger.debug("Update ClockUI Objects...Done!")

    def updateQuoteInfo(self, nap):
        Logger.debug("Updating Quote Info...")

        Logger.debug("Default Currency = {}".format(self.piBlockEngine.defaultCurrency))

        if self.piBlockEngine.defaultCurrency != None:
            Logger.debug("Setting Quote Info...")

            self.manager.getHeaderQuoteBTCRateLabel().text = "[b]{} {}1.00[/b] = [b]{} BTC[/b]".format(self.piBlockEngine.defaultCurrency, self.piBlockEngine.defaultCurrencySymbol, self.piBlockEngine.rateForBTC(self.piBlockEngine.defaultCurrency))
            self.manager.getHeaderQuoteCurrencyRateLabel().text = "[b]1 BTC[/b] = [b]{} {}{}[/b]".format(self.piBlockEngine.defaultCurrency, self.piBlockEngine.defaultCurrencySymbol, self.piBlockEngine.rateForCurrency(self.piBlockEngine.defaultCurrency))

        Logger.debug("Loading & Setting Quote Info...Done!")

class PiBlockScreenManager(ScreenManager):
    
    def __init__(self, **kwargs):
        super(PiBlockScreenManager, self).__init__(**kwargs)

        Logger.debug("kwargs = {}".format(kwargs.keys()))
        self.app = kwargs['piBlockApp']
        self.transition = FadeTransition()

        Clock.schedule_once(self._finish_init)

    def _finish_init(self, dt):
        Logger.debug("Screen Manager {}...".format(self))
        # Logger.debug("Screen IDs = {}".format(self.ids.keys()))
        # Logger.debug("Screen Manager = {}".format(self.manager))
        # Logger.debug("Screen piBlockEngine = {}".format(self.piBlockEngine))
        # Logger.debug("Screen Manager Root = {}".format(self.manager.root.ids.keys()))
        # Logger.debug("App = {}".format(PiBlockApp()))


    #-------------------------------------------------------------
    # Common Screen Element References And UI Updates
    #-------------------------------------------------------------

    def getHeader(self):
        currentScreen = self.get_screen(self.current)
        Logger.debug("PiBlockScreenManager's Current Screen is {}".format(currentScreen))
        return currentScreen.ids['header']

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
        currentScreen = self.get_screen(self.current)
        return currentScreen.ids['footer']

    def getFooterPBLogoThumbnailImage(self):
        return self.getFooter().ids['pblogothumbnail']

    def getFooteraADLLogThumbNailImage(self):
        return self.getFooter().ids['adllogothumbnail']


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

        self.screenManager.add_widget(StartupScreen(name='startup', piBlockEngine=self.screenManager.app.piBlockEngine))
        self.screenManager.add_widget(TenderScreen(name='tender', piBlockEngine=self.screenManager.app.piBlockEngine))

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