#!/usr/local/bin/python3
# coding=utf-8
import os
import cmd
import time
import readline
import socket
import logging
import subprocess
from cmd import Cmd

from piBlockConfig import PiBlockConfig
from piBlockBTCQuote import PiBlockBTCQuote

class FileFormatError(Exception):
    pass

class UnsupportedCurrencyError(Exception):
    pass

class PiBlockEngine():

    #
    # Constructor
    #
    def __init__(self):

        self.logger = self.getPiBlockLogger()
        self.initialiseConstants()
        
        self.logger.debug('Loading Config...')
        self.logger.debug('Config Filename = {}'.format(self.configFileName))
        self.config = PiBlockConfig(self.configFileName)
        self.logger.debug('Loading Config... Done!')

        self.logger.debug("Initialising Lookup Object...")
        self.logger.debug("Config... Price Lookup URL = {}".format(self.config.get_configValueForKey('pricingLookupURL')))
        self.btcPricingLookup = PiBlockBTCQuote(self.config.get_configValueForKey('pricingLookupURL'))
        self.logger.debug("Initialising Lookup Object...Done!")

    #-------------------------------------------------------------
    # Getters & Setters
    #-------------------------------------------------------------

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        self._config = config

    @property
    def btcPricingLookup(self):
        return self._btcPricingLookup

    @btcPricingLookup.setter
    def btcPricingLookup(self, pricingLookup):
        self._btcPricingLookup = pricingLookup

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description
    
    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, author):
        self._author = author

    @property
    def vendor(self):
        return self._vendor

    @vendor.setter
    def vendor(self, vendor):
        self._vendor = vendor

    @property
    def buildDate(self):
        return self._buildDate

    @buildDate.setter
    def buildDate(self, buildDate):
        self._buildDate = buildDate

    @property
    def aboutText(self):
        return self._aboutText

    @aboutText.setter
    def aboutText(self, aboutText):
        self._aboutText = aboutText

    @property
    def configFileName(self):
        return self._configFileName

    @configFileName.setter
    def configFileName(self, configFileName):
        self._configFileName = configFileName

    # RSAKeyLocation=/Users/abrarpeer/.ssh/id_rsa
    # defaultCurrency=AUD
    # lastDailyTxCount=0
    # sshport=2020
    # pricingLookupURL=https://blockchain.info/ticker
    # kpub=xpub661MyMwAqRbcGKB9ueCJFMVrE2EV7VvV3SReyoCv3U95UyH7XiPLiwgmN567J5Tg5kWhnBSiVa5Fz3vJKLyqKpnguJ3fdTURtwXJ5Ldjpk9
    # timeout=90000
    # blockchainInterfaceURL=www.blockchain.info
    # email=peerlabs@gmail.com

    @property
    def rsaKeyLocation(self):
        return self.config.get_configValueForKey('RSAKeyLocation')

    @property
    def defaultCurrency(self):
        return self.config.get_configValueForKey('defaultCurrency')

    @property
    def defaultCurrencySymbol(self):
        return self.btcPricingLookup.getSymbolForCurrency(self.defaultCurrency)

    @property
    def pricingLookupURL(self):
        return self.config.get_configValueForKey('pricingLookupURL')

    @property
    def lastDailyTxCount(self):
        return self.config.get_configValueForKey('lastDailyTxCount')

    @property
    def sshPort(self):
        return int(self.config.get_configValueForKey('sshport'))

    @property
    def kpub(self):
        return self.config.get_configValueForKey('kpub')

    @property
    def timeout(self):
        return self.config.get_configValueForKey('timeout')

    @property
    def blockchainInterfaceURL(self):
        return self.config.get_configValueForKey('blockchainInterfaceURL')

    @property
    def email(self):
        return self.config.get_configValueForKey('email')

    #-------------------------------------------------------------
    # Action Methods : General
    #-------------------------------------------------------------
    def quitPiBlock(self,args):
        self.logger.debug('Shutting Down PiBlock...')
        time.sleep(1.0)
        self.logger.debug('Shutting Down piBlock...Done!\n============================================================')
        os.system('clear')
        #raise SystemExit
        os._exit(1)

    #-------------------------------------------------------------
    # Action Methods : Config
    #-------------------------------------------------------------

    def getConfigKeyList(self):
        self.logger.debug("Processing Command to get list of all config keys...")

        self.logger.debug("Processing Command to get list of all config keys...Done!")

        return self.config.getConfigKeys()


    def getConfigValueForKey(self, key):
        self.logger.debug("Attempting to get Config Value for key = '{}'...".format(key))
        return self.config.get_configValueForKey(key)

    def getVerboseConfigData(self):
        self.logger.debug('Getting Verbose Config Data...')
        return self.config.getVerboseConfig()

    def addConfig(self, key, value):
        self.logger.debug('Processing Command to add Config Setting...')
        self.logger.debug('Checking to see if arguments were provided...')

        if not key or not value:
            self.logger.debug('Empty key or value provided...')
            self.logger.debug('Processing Command to add Config Setting...Aborted!')
            self.console.messageConsole("\nNo arguments provided. <addConfig> command expects only 2 arguments, seperated by a ' '.\n")
        else:
            if not self.doesConfigKeyExist(key):
                self.logger.debug("Attempting to Add key '{}' with value '{}'...".format(key, value))
                self.config.addKeyValue(key, value)
                self.logger.debug('Processing Command to add Config Setting...Done!')
            else:
                originalValue = self.config.get_configValueForKey(key)
                self.logger.debug("Key {} already exists with value '{}'...".format(key, originalValue))
                self.logger.debug('Processing Command to add Config Setting...Aborted!')

    def updateConfig(self, key, value):
        self.logger.debug('Processing Command to update Config Setting...')
        self.logger.debug('Checking to see if arguments were provided...')

        if not key or not value:
            self.logger.debug('Empty key or value provided...')
            self.logger.debug('Processing Command to update Config Setting...Aborted!')
            # self.console.messageConsole("\nNo arguments provided. <updateConfig> command expects only 2 arguments, seperated by a ' '.\n")
        else:
            if not self.doesConfigKeyExist(key):
                self.logger.debug("No Key {} exists...".format(key))
                # self.console.messageConsole("\nCannot Process Command because there is no config setting for '{}'.\nIf you wanted to add this '{}' setting with the value '{}', use the addConfig command.".format(key, key, value))
                self.logger.debug('Processing Command to update Config Setting...Aborted!')
            else:
                originalValue = self.config.get_configValueForKey(key)
                self.logger.debug("Attempting to Update key '{}' with current value '{}' to '{}'...".format(key, originalValue, value))
                self.config.updateKeyValue(key, value)
                self.logger.debug('Processing Command to update Config Setting...Done!')


    #-------------------------------------------------------------
    # Action Methods : Lookup
    #-------------------------------------------------------------
    def getListOfSupportedCurrencies(self):

        self.logger.debug("Attempting to get Currencies Supported for Exchange Rate...")

        self.logger.debug("Attempting to get Currencies Supported for Exchange Rate...Done!")

        self.logger.debug("List of Supported Currencies: {}".format(self.btcPricingLookup.listOfSupportedCurrencies))

        return self.btcPricingLookup.listOfSupportedCurrencies

    def getSymbolForCurrency(self, currency):

        curr = currency.upper()

        self.logger.debug("Querying Symbol for Currency '{}' ...".format(curr))

        if curr in self.getListOfSupportedCurrencies():

            currencySymbol = self.btcPricingLookup.getSymbolForCurrency(curr)
            
            self.logger.debug("Querying Symbol for Currency '{}' ...Done!".format(curr))

            return currencySymbol

        else:

            raise UnsupportedCurrencyError

    def rateForCurrency(self, currency):

        if currency.upper():

            self.logger.debug("Looking Up Currency Rate for '{}'...".format(currency.upper()))
            self.logger.debug("Looking Up Currency Rate for '{}'...Done!".format(currency.upper()))
            
            return self.btcPricingLookup.btcRateForCurrency(currency.upper())

        else:
            defaultCurrency = self.config['defaultCurrency']
            self.logger.debug("Looking Up Currency Rate for '{}'...".format(defaultCurrency))
            self.logger.debug("Looking Up Currency Rate for '{}'...Done!".format(currency))

            return self.btcPricingLookup.btcRateForCurrency(defaultCurrency)

    def rateForBTC(self, currency):

        if currency.upper():

            self.logger.debug("Looking Up BTC Rate for '{}'...".format(currency.upper()))
            self.logger.debug("Looking Up BTC Rate for '{}'...Done!".format(currency.upper()))
            
            return self.btcPricingLookup.currencyRateForBTC(currency.upper())

        else:
            defaultCurrency = self.config['defaultCurrency']
            self.logger.debug("Looking Up BTC Rate for '{}'...".format(defaultCurrency))
            self.logger.debug("Looking Up BTC Rate for '{}'...Done!".format(currency))

            return self.btcPricingLookup.currencyRateForBTC(currency.upper())

    def convertToBTC(self, amount, currency):

        self.logger.debug("Converting to BTC...")

        curr = currency.upper()

        if not curr:

            defaultCurrency = self.defaultCurrency

            curr = defaultCurrency

        try:
            self.logger.debug("Checking Argument 'amount = {}' is a float...".format(amount))
            checkNumber = float(amount)

        except (ValueError, Exception) as e:
            self.logger.debug("Converting to BTC...Aborted!")
            raise e

        amountFloat = float(amount)

        if self.btcPricingLookup.isSupportedCurrency(curr):

            self.logger.debug("Querying Currency Symbol...")

            currencySymbol = self.getSymbolForCurrency(curr)

            self.logger.debug("Querying BTC Rate...")
            
            rate = self.rateForBTC(curr)

            self.logger.debug("Converting all values to float...")

            rateFloat = float(rate)
            
            self.logger.debug("Calculating...")

            finalAmountFloat = rateFloat*amountFloat

            finalAmount = "{0:.9f}".format(finalAmountFloat)
            self.logger.debug("Rate is {} BTC per {}1.00".format(self.rateForCurrency(curr), currencySymbol))
            self.logger.debug("Amount Queried is {} {}{}".format(curr, currencySymbol, amountFloat))
            self.logger.debug("Final Amount is {}".format(finalAmountFloat))

            self.logger.debug("Converting to BTC...Done!")

            return finalAmountFloat

        else:

            self.logger.debug("An error has occured. The Currency '{}' is not Supported by PiBlock!".format(curr))
            self.logger.debug('Raising this exception!')
            self.logger.debug("Converting to BTC...Aborted!")
            raise UnsupportedCurrencyError("The Currency '{}' is not Supported by PiBlock!".format(curr))

    def convertToCurrency(self, amount, currency):

        self.logger.debug("Converting to Currency...")

        curr = currency.upper()

        if not curr:

            defaultCurrency = self.config['defaultCurrency']

            curr = defaultCurrency

        try:
            self.logger.debug("Checking Argument 'amount = {}' is a float...".format(amount))
            checkNumber = float(amount)

        except (ValueError, Exception) as e:
            self.logger.debug("Converting to BTC...Aborted!")
            raise e

        amountFloat = float(amount)

        if self.btcPricingLookup.isSupportedCurrency(curr):

            self.logger.debug("Querying Currency Symbol...")

            currencySymbol = self.getSymbolForCurrency(curr)

            self.logger.debug("Querying BTC Rate...")
            
            rate = self.rateForCurrency(curr)

            self.logger.debug("Converting all values to float...")

            rateFloat = float(rate)
            
            self.logger.debug("Calculating...")

            finalAmountFloat = rateFloat*amountFloat

            formattedFinalAmount = "{0:.2f}".format(finalAmountFloat)
            self.logger.debug("Rate is {} BTC per {}1.00".format(self.rateForCurrency(curr), currencySymbol))
            self.logger.debug("Amount Queried is {} BTC".format(amountFloat))
            self.logger.debug("Final Amount is {} {}{} ".format(curr, currencySymbol, formattedFinalAmount))

            self.logger.debug("Converting to BTC...Done!")

            return finalAmountFloat

        else:

            self.logger.debug("An error has occured. The Currency '{}' is not Supported by PiBlock!".format(curr))
            self.logger.debug('Raising this exception!')
            self.logger.debug("Converting to BTC...Aborted!")
            raise UnsupportedCurrencyError("The Currency '{}' is not Supported by PiBlock!".format(curr))


    #-------------------------------------------------------------
    # Testing Methods
    #-------------------------------------------------------------
    def test(self):
        self.logger.debug("Testing Subroutine...")

        test = subprocess.Popen(["kivy", "main.py", self], stdout=subprocess.PIPE)
        output = test.communicate()[0]
        self.console.messageConsole(output)

        self.logger.debug("Testing Subroutine...Done!")

        

    #-------------------------------------------------------------
    # Convenience Methods
    #-------------------------------------------------------------
        

    def doesConfigKeyExist(self, key):
        self.logger.debug("Check Existence of Config Setting '{}'...".format(key))
        
        if self.config.get_configValueForKey(key) == None:
            self.logger.debug("Config Setting '{}' Does not Exist...".format(key))
            self.logger.debug("Check Existence of Config Setting '{}'...Done!".format(key))
            return False
        else:
            self.logger.debug("Config Setting '{}' Exists...".format(key))
            self.logger.debug("Check Existence of Config Setting '{}'...Done!".format(key))
            return True

    def initialiseConstants(self):
        self.logger.debug('Initialising Constants...')
        self.title = 'Welcome to piBlock, A Real-Time Bitcoin transaction processing utility.'
        self.description = 'piBlock is a simple uitlity to process and subsequently store bitcoin transactions.You message piBlock with your currency amount and piBlock will present a user with a Bitcoin Transaction Address and the equivalent amount of BTC. piBlock will then poll the blockchain to see if the transaction has been processed. piBlock will inform the issuer if the timeout has expired. Should a validated transaction appear on the blockchain, piBlock will inform the issuer. If the Amount on the blockchain is different than the one that was expected, piBlock will inform the issuer accordingly.'
        self.version = '0.1'
        self.author = 'Abrar Peer'
        self.vendor = 'Apps Design Lab'
        self.buildDate = 'July 2015'
        self.configFileName = 'piBlockConfig.txt'
        self.aboutText = self.title +'\nAuthor: ' + self.author + '\nVersion: ' + self.version + '\nSoftware Vendor: ' + self.vendor + '\nBuild Date: ' + self.buildDate
        # self.gui = None
        self.logger.debug('Initialising Constants...Done!')

    #-------------------------------------------------------------
    # Logger
    #-------------------------------------------------------------

    def getPiBlockLogger(self):
        logger = logging.getLogger(__name__)
        loggingFileHandler = logging.FileHandler('piBlock.log')
        loggingFormatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        loggingFileHandler.setFormatter(loggingFormatter)
        logger.addHandler(loggingFileHandler)
        logger.setLevel(logging.DEBUG)
        return logger
