#!/usr/local/bin/python3
# coding=utf-8
import os
import cmd
import time
import readline
import socket
import logging
import json
import urllib3.request

class PiBlockBTCQuote():

    #
    # Constructor
    #
    def __init__(self, pricingLookupURL):
        self.logger = self.getPiBlockBTCQuoteLogger()
        self.logger.debug("Initialising PiBlockBTCQuote with URL = '{}'...".format(pricingLookupURL))
        self.lookupURL = pricingLookupURL
        self.rawData = self.updateQuoteData()
        self.listOfSupportedCurrencies = self.initialiseListOfSupportedCurrencies()
        self.currencySymbolDictionary = self.initialiseCurrencySymbolDictionary()
        self.logger.debug('Initialising PiBlockBTCQuote...Done!')


    #-------------------------------------------------------------
    # Getters
    #-------------------------------------------------------------
    @property
    def lookupURL(self):
        return self._lookupURL

    @lookupURL.setter
    def lookupURL(self, lookupURL):
        self._lookupURL = lookupURL

    @property
    def rawData(self):
        return self._rawData

    @rawData.setter
    def rawData(self, rawData):
        self._rawData = rawData

    @property
    def listOfSupportedCurrencies(self):
        return self._listOfSupportedCurrencies

    @listOfSupportedCurrencies.setter
    def listOfSupportedCurrencies(self, listOfSupportedCurrencies):
        self._listOfSupportedCurrencies = listOfSupportedCurrencies

    @property
    def currencySymbolDictionary(self):
        return self._currencySymbolDictionary

    @currencySymbolDictionary.setter
    def currencySymbolDictionary(self, currencySymbolDictionary):
        self._currencySymbolDictionary = currencySymbolDictionary

    #-------------------------------------------------------------
    # Action Methods
    #-------------------------------------------------------------

    # def getBTCFromAmount(self, cur, amount):

    def isSupportedCurrency(self, currency):
        curr = currency.upper()
        self.logger.debug("Attempting to check if {} is supported...".format(curr))

        if len(curr) == 3:

            if curr in self.listOfSupportedCurrencies:
                self.logger.debug("Currency is supported...")
                self.logger.debug("Attempting to check if {} is supported..Done".format(curr))
                return True
            else:
                self.logger.debug("Currency is not supported...")
                self.logger.debug("Attempting to check if {} is supported..Done".format(curr))
                return False
        else:
            self.logger.debug("Currency is of incorrect legnth...")
            self.logger.debug("Attempting to check if {} is supported..Done".format(curr))
            return False

    def getSymbolForCurrency(self, currency):
        curr = currency.upper()
        self.logger.debug("Attempting to get symbol for currency '{}'...".format(curr))

        if self.isSupportedCurrency(curr):
            self.logger.debug("Attempting to get symbol for currency '{}'...Done!".format(curr))
            return self.currencySymbolDictionary[curr].encode('UTF-8')

        else:
            self.logger.debug("Currency is not supported...")
            self.logger.debug("Attempting to get symbol for currency '{}'...Done!".format(curr))
            return "Unknown"

    def btcRateForCurrency(self, currency):
        
        curr = currency.upper()

        if self.isSupportedCurrency(curr):

            self.updateQuoteData()
            
            self.logger.debug("Attempting to get Exchange Rate for '{}' from {}...".format(curr, self.lookupURL))
            
            intermediaryDictionary = self.rawData[curr]

            self.logger.debug("Intermediary Dictionary for {} = {}".format(curr,intermediaryDictionary))

            self.logger.debug("Attempting to get Exchange Rate for '{}' from {}...Done!".format(curr, self.lookupURL))

            return intermediaryDictionary['last']

    def currencyRateForBTC(self, currency):
        
        curr = currency.upper()

        if self.isSupportedCurrency(curr):

            self.logger.debug("Attempting to get BTC Rate for '{}' from {}...".format(curr, self.lookupURL))

            btcRate = self.btcRateForCurrency(curr)

            self.logger.debug("BTC Rate for '{}' = {}".format(curr,btcRate))

            currencyRate = 1/btcRate

            return "{0:.9f}".format(currencyRate)


        
    #-------------------------------------------------------------
    # Convenience Methods
    #-------------------------------------------------------------
    def updateQuoteData(self):
        self.logger.debug("Attempting to get Exchange Rate from {}...".format(self.lookupURL))

        try:
            http = urllib3.PoolManager()
            r = http.request('GET',self.lookupURL)
            self.logger.debug("Got a response object from {}".format(self.lookupURL))

            if r.status == 200:
                self.logger.debug(" ... with response Code: {}".format(r.status))
                data = json.loads(r.data)
                self.logger.debug("Attempting to get Exchange Rate from {}...Done".format(self.lookupURL))
                return data

            else:
                self.logger.debug('An Exception occured whilst trying to get Exchange Rate Data!')
                print ('An Exception occured whilst trying to get Exchange Rate Data!')
                # self.logger.debug(str(e))
                self.logger.debug('Raising this exception!')
                raise BaseException

            # with urllib3.request.urlopen(self.lookupURL) as url:
            #     response = url.read()
            #     charset = url.info().get_param('charset', 'utf-8')  # UTF-8 is the JSON default
            #     data = json.loads(response.decode(charset))
            #     self.logger.debug("Attempting to get Exchange Rate from {}...Done".format(self.lookupURL))
            #     return data
        except BaseException as e:
            self.logger.debug('An Exception occured whilst trying to get Exchange Rate Data!')
            print ('An Exception occured whilst trying to get Exchange Rate Data!')
            self.logger.debug(str(e))
            self.logger.debug('Raising this exception!')
            raise

    def initialiseListOfSupportedCurrencies(self):
        self.logger.debug("Attempting to Initialise List of Supported Currencies...")

        if self.rawData:

            listOfCurrencies = list()

            for k in sorted(self.rawData.keys()):

                listOfCurrencies.append(k)

            self.logger.debug("Attempting to Initialise List of Supported Currencies...Done!")
            return listOfCurrencies

        self.logger.debug("Attempting to Initialise List of Supported Currencies...Done!")

    def initialiseCurrencySymbolDictionary(self):
        self.logger.debug("Attempting to Initialise Currency Symbol Dictionary...")

        if self.rawData:

            currencySymbolDictionary = dict()

            for k in sorted(self.rawData.keys()):

                intermediaryDictionary = self.rawData[k]

                self.logger.debug("Intermediary Dictionary for {} = {}".format(k,intermediaryDictionary))

                currencySymbolDictionary[k] = intermediaryDictionary['symbol']

            self.logger.debug("Attempting to Initialise Currency Symbol Dictionary...Done!")

            self.logger.debug("Currency Symbol Dictionary = {}...".format(currencySymbolDictionary))

            return currencySymbolDictionary

            #self.logger.debug("Attempting to Initialise List of Supported Currencies...Done!")
            #return listOfCurrencies


        self.logger.debug("Attempting to Initialise Currency Symbol Dictionary...Done!")

    #-------------------------------------------------------------
    # Logger
    #-------------------------------------------------------------
    
    def getPiBlockBTCQuoteLogger(self):
        logger = logging.getLogger(__name__)
        loggingFileHandler = logging.FileHandler('piBlock.log')
        loggingFormatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        loggingFileHandler.setFormatter(loggingFormatter)
        logger.addHandler(loggingFileHandler)
        logger.setLevel(logging.DEBUG)
        return logger