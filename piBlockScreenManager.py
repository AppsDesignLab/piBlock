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
        # Logger.debug("Screen Manager Root = {}".format(self.root.ids.keys()))
        # Logger.debug("App = {}".format(PiBlockApp()))



    #-------------------------------------------------------------
    # Common UI Element Updates
    #-------------------------------------------------------------

    def loadCommon(self):
        self.loadQuoteInfo()
        self.loadStaticInfo()

    def updateCommon(self, nap):
        self.updateStatusInfo(1)
        self.updateClockInfo(1)
        self.updateQuoteInfo(15)

    def loadQuoteInfo(self):
        Logger.debug("Updating Quote Info...")

        Logger.debug("Default Currency = {}".format(self.app.piBlockEngine.defaultCurrency))

        if self.app.piBlockEngine.defaultCurrency != None:
            Logger.debug("Setting Quote Info...")

            self.getHeaderQuoteBTCRateLabel().text = "[b]{} {}1.00[/b] = [b]{} BTC[/b]".format(self.app.piBlockEngine.defaultCurrency, self.app.piBlockEngine.defaultCurrencySymbol, self.app.piBlockEngine.rateForBTC(self.app.piBlockEngine.defaultCurrency))
            self.getHeaderQuoteCurrencyRateLabel().text = "[b]1 BTC[/b] = [b]{} {}{}[/b]".format(self.app.piBlockEngine.defaultCurrency, self.app.piBlockEngine.defaultCurrencySymbol, self.app.piBlockEngine.rateForCurrency(self.app.piBlockEngine.defaultCurrency))

        Logger.debug("Loading & Setting Quote Info...Done!")

    def loadStaticInfo(self):
        Logger.debug("Loading Static Info...")

        self.getHeaderQuoteSrcLabel().text = "[i]source: {}".format(self.app.piBlockEngine.pricingLookupURL)
        self.loadStaticImages()

        Logger.debug("Loading Static Info...Done!")

    def loadStaticImages(self):
        Logger.debug("Loading & Setting Static Images...")
        print("{}".format(self.app.bizLogoImagePath))

        self.getHeaderBizLogo().source = str(self.app.bizLogoImagePath)
        self.getFooterPBLogoThumbnailImage().source = str(self.app.pbSmallLogoImagePath)
        self.getFooterADLLogThumbNailImage().source = str(self.app.adlSmallLogoImagePath)

        Logger.debug("Loading & Setting Static Images...Done!")

    def updateStatusInfo(self, nap):
        Logger.debug("Update Status Objects...")
        self.getHeaderStatusLabel().text = "Status: [b]{}[/b]".format(self.app.status)
        Logger.debug("Update Status Objects...Done!")


    def updateClockInfo(self, nap):
        Logger.debug("Update ClockUI Objects...")

        self.getHeaderClockDateLabel().text = strftime('[b]%A, %d %b %Y[/b]')
        self.getHeaderClockTimeLabel().text = strftime('[b]%I:%M[/b]:%S %p')

        Logger.debug("Update ClockUI Objects...Done!")

    def updateQuoteInfo(self, nap):
        Logger.debug("Updating Quote Info...")

        Logger.debug("Default Currency = {}".format(self.app.piBlockEngine.defaultCurrency))

        if self.app.piBlockEngine.defaultCurrency != None:
            Logger.debug("Setting Quote Info...")

            self.getHeaderQuoteBTCRateLabel().text = "[b]{} {}1.00[/b] = [b]{} BTC[/b]".format(self.app.piBlockEngine.defaultCurrency, self.app.piBlockEngine.defaultCurrencySymbol, self.app.piBlockEngine.rateForBTC(self.app.piBlockEngine.defaultCurrency))
            self.getHeaderQuoteCurrencyRateLabel().text = "[b]1 BTC[/b] = [b]{} {}{}[/b]".format(self.app.piBlockEngine.defaultCurrency, self.app.piBlockEngine.defaultCurrencySymbol, self.app.piBlockEngine.rateForCurrency(self.app.piBlockEngine.defaultCurrency))

        Logger.debug("Loading & Setting Quote Info...Done!")

    #-------------------------------------------------------------
    # Common Screen Element References And UI Updates
    #-------------------------------------------------------------

    def getHeader(self):
        currentScreen = self.get_screen(self.current)
        Logger.debug("PiBlockScreenManager's Current Screen is {}".format(currentScreen))
        Logger.debug("Current Screen's IDs = {}".format(currentScreen.ids.keys()))
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

    def getFooterADLLogThumbNailImage(self):
        return self.getFooter().ids['adllogothumbnail']