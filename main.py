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
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.stacklayout import StackLayout
from kivy.graphics.context_instructions import Color
from kivy.support import install_twisted_reactor
install_twisted_reactor()
from twisted.internet import protocol, reactor
# from twisted.logger import Logger
from time import strftime
from piBlockEngine import PiBlockEngine
from piBlockConsole import PiBlockConsole
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

class PiBlockApp(App):

    #-------------------------------------------------------------
    # Getters & Setters
    #-------------------------------------------------------------

    @property
    def uptime(self):
        return self._uptime

    @uptime.setter
    def uptime(self, uptime):
        self._uptime = uptime
        if self._uptime != None:
            self.root.ids.uptimelabel.text = "Running Time: [b]{}[/b]".format(self._uptime)

    @property
    def lastStartupTime(self):
        return self._lastStartupTime

    @lastStartupTime.setter
    def lastStartupTime(self, lastStartupTime):
        self._lastStartupTime = lastStartupTime
        if self._lastStartupTime != None:
            self.root.ids.laststartedlabel.text = "Started @ [b]{}[/b]".format(self._lastStartupTime)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status
        if self._status != None:
            self.root.ids.statuslabel.text = "Status: [b]{}[/b]".format(self._status)

    @property
    def defaultCurrency(self):
        return self._defaultCurrency 

    @defaultCurrency.setter
    def defaultCurrency(self, defaultCurrency):
        self._defaultCurrency = defaultCurrency
        if self._defaultCurrency != None:
            self.defaultCurrencySymbol = self.piBlockEngine.getSymbolForCurrency(self._defaultCurrency)
            self.root.ids.defaultcurrencylabel.text = "Default Currency: [b]{} {}[/b]".format(self._defaultCurrency, self.defaultCurrencySymbol)

    @property
    def defaultCurrencySymbol(self):
        return self._defaultCurrencySymbol

    @defaultCurrencySymbol.setter
    def defaultCurrencySymbol(self, defaultCurrencySymbol):
        self._defaultCurrencySymbol = defaultCurrencySymbol

    @property
    def currencyRate(self):
        return self._currencyRate

    @currencyRate.setter
    def currencyRate(self, currencyRate):
        self._currencyRate = currencyRate
        if self._currencyRate != None:
            self.root.ids.quotecurrencyratelabel.text = "[b]1 BTC[/b] = [b]{} {}{}[/b]".format(self.defaultCurrency, self.defaultCurrencySymbol, self._currencyRate)

    @property 
    def btcRate(self):
        return self._btcRate

    @btcRate.setter
    def btcRate(self, btcRate):
        self._btcRate = btcRate
        if self._btcRate != None:
            self.root.ids.quotebtcratelabel.text = "[b]{} {}1.00[/b] = [b]{} BTC[/b]".format(self.defaultCurrency, self.defaultCurrencySymbol, self._btcRate)

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = timeout
        if self._timeout != None:
            self.root.ids.timeoutlabel.text = "BTC Tx Processing Timeout: [b]{}[/b] secs".format(self._timeout)

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email
        if self._email != None:
            self.root.ids.emaillabel.text = "Email: [b]{}[/b]".format(self._email)

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, fps):
        self._fps = fps
        if self._fps != None:
            self.root.ids.fpslabel.text = "Avg Framerate: [b]{0:.2f} FPS[/b]".format(self._fps)

    @property
    def quoteSrc(self):
        return self._quoteSrc

    @quoteSrc.setter
    def quoteSrc(self, quoteSrc):
        self._quoteSrc = quoteSrc
        if self._quoteSrc != None:
            self.root.ids.quotesrclabel.text = "source: [i][b]{}[/b][/i]".format(self._quoteSrc)

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
    def sshport(self):
        return self._sshport

    @sshport.setter
    def sshport(self, sshport):
        self._sshport = sshport
        if self._sshport != None:
            self.root.ids.controlportlabel.text = "Control Port: [b]{}[b]".format(self._sshport)

    def __init__(self, **kwargs):
        
        super(PiBlockApp, self).__init__(**kwargs)

        Logger.debug("Initialising...")
        self.uptime = None
        self.lastStartupTime = None
        self.status = None
        self.defaultCurrency = None
        self.defaultCurrencySymbol = None

        #--
        self.currencyRate = None
        self.btcRate = None
        self.timeout = None
        self.email = None
        self.fps = None

        #--
        # self.latestQuote = None
        self.quoteSrc = None
        self.sshHostAddress = None
        self.sshHostName = None
        self.sshport = None

        Logger.debug("Initialising...Done!")

    #-------------------------------------------------------------
    # Overriden Methods
    #-------------------------------------------------------------

    def on_start(self):
        Logger.debug("on_start...")

        Logger.debug("Starting PiBlockEngine...")
        self.piBlockEngine = PiBlockEngine()
        Logger.debug("Starting PiBlockEngine...Done!")

        Logger.debug("Scheduling Running Tasks...")
        Clock.schedule_once(lambda dt: self.loadStaticInfo(), 0.5)
        Clock.schedule_once(lambda dt: self.startControlServer(), 0.1)
        Clock.schedule_once(lambda dt: self.updateQuoteInfo(0), 0.1)
        Clock.schedule_interval(self.updateClockInfo, 1)
        Clock.schedule_interval(self.updateSystemInfo, 1)
        Clock.schedule_interval(self.updateQuoteInfo, 60)
        Logger.debug("Scheduling Running Tasks...Done!")

        self.status = 'Initialised'
        # self.root.ids.statuslabel.text = "Status: [b]{}[/b]".format()

        Logger.debug("on_start...Done!")

    #-------------------------------------------------------------
    # Convenience Methods
    #-------------------------------------------------------------

    def startControlServer(self):
        Logger.debug("Starting Control Server...")
        # self.piBlockEngine.startControlServer()
        self.controlServer = PiBlockSSHControlServer(self)
        # self.controlServer.startSSHServer()

        Logger.debug("Starting Control Server...Done!")

    def updateClockInfo(self, nap):
        Logger.debug("Update ClockUI Objects...")

        self.root.ids.date.text = strftime('[b]%A, %d %b %Y[/b]')
        self.root.ids.time.text = strftime('[b]%I:%M[/b]:%S %p')

        Logger.debug("Update ClockUI Objects...Done!")

    def updateSystemInfo(self, nap):
        Logger.debug("Updating System Info...")

        self.uptime = "{}".format(time.strftime('%H:%M:%S', time.gmtime(Clock.get_boottime())))
        self.fps = Clock.get_fps()
        Logger.debug("Updating System Info...Done!")

    def updateQuoteInfo(self, nap):
        Logger.debug("Updating Quote Info...")

        Logger.debug("Default Currency = {}".format(self.defaultCurrency))

        if self.defaultCurrency != None:
            Logger.debug("Setting Quote Info...")
            self.btcRate = self.piBlockEngine.rateForBTC(self.defaultCurrency)
            self.currencyRate = self.piBlockEngine.rateForCurrency(self.defaultCurrency)

        Logger.debug("Loading & Setting Quote Info...Done!")

    def loadStaticInfo(self):
        Logger.debug("Loading Static Info...")

        self.defaultCurrency = self.piBlockEngine.getConfigValueForKey('defaultCurrency')
        self.quoteSrc = self.piBlockEngine.getConfigValueForKey('pricingLookupURL')
        self.timeout = int(self.piBlockEngine.getConfigValueForKey('timeout'))/1000
        self.sshport = self.piBlockEngine.getConfigValueForKey('sshport')
        self.email = self.piBlockEngine.getConfigValueForKey('email')
        self.lastStartupTime = strftime('%Y/%-m/%-d %H:%M:%S')

        self.loadStaticImages()

        self.initSshHost()

        self.root.ids.sshaddresslabel.text = 'Control Server: [b]ssh <user>@{} -p {}[/b]'.format(self.sshHostAddress, self.sshport)

        Logger.debug("Loading Static Info...Done!")
    

    def loadStaticImages(self):
        Logger.debug("Loading & Setting Static Images...")

        self.root.ids.bizlogo.source = BIZLOGO
        self.root.ids.pbLogoSmallFooter.source = PBLOGOSMALL
        self.root.ids.adlLogoSmallFooter.source = ADLLOGOSMALL
        self.root.ids.smileyIcon.source = SMILEY1
        self.root.ids.pbMainBanner.source = PBBANNER

        Logger.debug("Loading & Setting Static Images...Done!")

    def initSshHost(self):
        Logger.debug("Initialise PiBlock SSH Host Address...")
        
        self.shhHostName = socket.gethostname()
        Logger.debug("SSH HostName: {}".format(self.shhHostName))
        self.sshHostAddress = socket.gethostbyname(self.shhHostName)

        Logger.debug("SSH HostAddress: {}".format(self.sshHostAddress))
        Logger.debug("Initialise PiBlock SSH Host Address...Done!")

    def themeColor(self):
        Logger.debug("ThemeColor Requested...")

        Logger.debug("ThemeColor Requested...Done!")

        return get_color_from_hex(THEMECOLOR)

    #-------------------------------------------------------------
    # PiBlock Control Server Methods
    #-------------------------------------------------------------

    def on_controlServerConnected(self, conn):
        Logger.debug("Control Server Connected!\n Connection Details: {}".format(conn))

        self.controlServerConn = conn

    def on_controlMsgRcvd(self, data):
        Logger.debug("A Control Message was recieved: {} from connection {}".format(data, self.controlServerConn))

    def disconnect(self):
        print('-- disconnecting')
        if self.conn:
            self.conn.loseConnection()
            del self.conn

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