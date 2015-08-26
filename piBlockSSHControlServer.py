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
import bz2
import hashlib

from kivy.support import install_twisted_reactor
install_twisted_reactor()
from twisted.internet import protocol, reactor

from twisted.conch import avatar, recvline
from twisted.conch.interfaces import IConchUser, ISession
from twisted.conch.ssh import factory, keys, session
from twisted.conch.insults import insults
from twisted.cred import portal, checkers, error
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import IUsernameHashedPassword
from twisted.internet.defer import Deferred
from zope.interface import implements
from piBlockEngine import PiBlockEngine

class PiBlockSSHProtocol(recvline.HistoricRecvLine):

    portal = None
    avatar = None
    logout = None
    ruler = '='
    doc_leader = ""
    doc_header = "Documented commands (type help <topic>):"
    misc_header = "Miscellaneous help topics:"
    undoc_header = "Undocumented commands:"
    nohelp = "*** No help on %s"

    #-------------------------------------------------------------
    #Command: Boilerplate
    #-------------------------------------------------------------

    def __init__(self, user, app):
        self.user = user
        self.app = app
        self.logger = self.getPiBlockControlServerLogger()

    def connectionMade(self):
        recvline.HistoricRecvLine.connectionMade(self)
        self.outputWelcomeBannerText()
        self.do_help()
        self.showPrompt()

    def showPrompt(self):
        print ("User: {}".format(self.user.username))
        print ("Status: {}".format(self.app.status))
        self.terminal.write("{}@PiBlock::{}> ".format(self.user.username, self.app.status))

    def getCommandFunc(self, cmd):
        return getattr(self, 'do_' + cmd, None)

    def lineReceived(self, line):

        self.logger.debug("DEBUG OUTPUT - Line Received: {}".format(line))
        # if not self.avatar:

        line = line.strip()
        if line:
            cmdAndArgs = line.split()
            cmd = cmdAndArgs[0]
            args = cmdAndArgs[1:]

            if cmd == '?':
                cmd = 'help'
            elif cmd == 'cls':
                cmd = 'clear'
            elif cmd == 'q':
                cmd = 'close'
            elif cmd == 'cfg':
                cmd = 'currentConfig'
            elif cmd == 'curr':
                cmd = 'supportedCurrencies'
            elif cmd == 'stat':
                cmd = 'sysStatus'

            func = self.getCommandFunc(cmd)
            if func:
                try:
                    func(*args)
                except Exception, e:
                    self.terminal.nextLine()
                    self.terminal.write("Error: %s" % e)
                    self.terminal.nextLine()
            else:
                self.terminal.nextLine()
                self.terminal.write("No such command {}".format(cmd))
                self.terminal.nextLine()
        
        self.terminal.nextLine()
        self.showPrompt()

    #-------------------------------------------------------------
    #Commands: User - Reset Password
    #-------------------------------------------------------------
    def do_resetPassword(self, *args):

        #DOCUMENTATION BLOCK

        """\nResets a User's Password.\n=========================\n
No Arguments expected but an optional argument or list of arguments can be specified to query values of particular settings.
If no Arguments supplied, piBlock will output all the current configuration setting values.\n
Conditions: User == 'admin' & Status == 'Initialised'
Usage Syntax: 'currentConfig [<key(1) <key(2)> ... <key(n)>]'\n
Example:
piBlock> currentConfig\n
Example to Query Config Value for 'email':
piBlock> currentConfig email\n
Example to Query Multiple Config Values:
piBlock> currentConfig email defaultCurrency timeout\n"""
        
        self.terminal.nextLine()
        self.terminal.write(self.stillToBeImplemented('currentConfig'))
        self.terminal.nextLine()


    #-------------------------------------------------------------
    #Commands: Config - Current Configuration
    #-------------------------------------------------------------
    def do_currentConfig(self, *args):

        #DOCUMENTATION BLOCK

        """\nDisplays PiBlock's Current Configuration Settings.\n==================================================\n
No Arguments expected but an optional argument or list of arguments can be specified to query values of particular settings.
If no Arguments supplied, piBlock will output all the current configuration setting values.\n
Conditions: None\n
Shortcut: 'cfg'
Usage Syntax: 'currentConfig [<key(1) <key(2)> ... <key(n)>]'\n
Example:
piBlock> currentConfig\n
Example to Query Config Value for 'email':
piBlock> currentConfig email\n
Example to Query Multiple Config Values:
piBlock> currentConfig email defaultCurrency timeout\n"""

        self.logger.debug("Started...")

        self.outputTitleText("PiBlock's Current Configuration Settings")

        if len(args) == 0:

            self.logger.debug("Displaying All Current Config Values")
            self.terminal.write(self.app.piBlockEngine.getVerboseConfigData())
            self.terminal.nextLine()
            
        else:

            for configKey in args:

                if not self.app.piBlockEngine.doesConfigKeyExist(configKey):

                    self.logger.debug("No Key {} exists...".format(configKey))

                    self.terminal.write("Config Setting for '{}' does not exist or have a value set.".format(configKey))
                    self.terminal.nextLine()

                else:

                    self.logger.debug("Key {} exists...".format(configKey))

                    configValue = self.app.piBlockEngine.getConfigValueForKey(configKey)

                    self.terminal.write("Config Setting '{}' has value '{}'".format(configKey, configValue))
                    self.terminal.nextLine()

        
        self.terminal.nextLine()

        self.logger.debug("Finished!")

    #-------------------------------------------------------------
    #Commands: Config - Add a Configuration
    #-------------------------------------------------------------

    def do_addConfig(self, *args):

        # DOCUMENTATION BLOCK

        """\nAdds (and saves) a Config Setting.\n==================================\n
Expects 2 Arguments, seperated by a ' '. A <key> for the setting name and <value> for the setting value. Note: <key> must not exist in configuration.\n
Conditions: <key> must Not Exist,  User = 'admin' & Status = 'Initialised'\n
Usage Syntax: 'addConfig <key> <value>'\n
Example:
piBlock> addConfig email someone@somewhere.com\n"""

        self.logger.debug("Started...")

        if not (self.isAdminUser() or self.isAppStatusInitialised()):

            self.terminal.write("[Permission Denied] -  Only Admin user can add a config setting or PiBlock can only add a config setting when it is in the 'Initialised' state.")
            self.terminal.nextLine()
            self.terminal.write("To add a config setting, make sure you are logged in as 'admin' and PiBlock is in the 'Initialised' state.")
            self.nextLine()
            self.nextLine()

        else:

            if len(args) != 2:

                self.terminal.write("[Error] - Invalid number of arguments supplied.")
                self.terminal.nextLine()
                self.terminal.write("""Expects 2 Arguments, seperated by a ' '. A <key> for the setting name and <value> for the setting value. Note: <key> must not exist in configuration.\n
Conditions: <key> must Not Exist,  User = 'admin' & Status = 'Initialised'\n
Usage Syntax: 'addConfig <key> <value>'\n
Example:
piBlock> addConfig email someone@somewhere.com\n""")
                self.terminal.nextLine()
                self.terminal.nextLine()

            else:

                if self.app.piBlockEngine.doesConfigKeyExist(args[0]):

                    originalValue = self.app.piBlockEngine.getConfigValueForKey(args[0])

                    self.terminal.write("[Error] - Cannot Add Config Setting '{}' because it already exists".format(args[0]))
                    self.terminal.nextLine()
                    self.terminal.write("Config Setting for '{}' already exists with value '{}'. Cannot add a setting that already exists in the config. If you wanted to update this '{}' setting with the value '{}', use the updateConfig command by issuing 'updateConfig {} {}'.".format(args[0], originalValue, args[0], args[1], args[0], args[1]))
                    self.terminal.nextLine()
                    self.terminal.write("""Expects 2 Arguments, seperated by a ' '. A <key> for the setting name and <value> for the setting value. Note: <key> must not exist in configuration.\n
Conditions: <key> must Not Exist,  User = 'admin' & Status = 'Initialised'\n
Usage Syntax: 'addConfig <key> <value>'\n
Example:
piBlock> addConfig email someone@somewhere.com\n""")
                    self.terminal.nextLine()
                    self.terminal.nextLine()

                else:

                    self.logger.debug('Valid Number of Arguments were Provided...')
                    self.logger.debug("Attempting to Add Config setting '{}' with value '{}'".format(args[0], args[1]))

                    try:

                        self.app.piBlockEngine.addConfig(args[0], args[1])
                        self.terminal.nextLine()
                        self.terminal.write("Successfully added configuration setting '{}' with value '{}'".format(args[0], args[1]))
                        self.terminal.nextLine()
                        self.outputTitleText("PiBlock's Current Configuration Settings")
                        self.logger.debug("Displaying All Current Config Values")
                        self.terminal.write(self.app.piBlockEngine.getVerboseConfigData())
                        self.terminal.nextLine()
                        self.terminal.nextLine()

                    except BaseException as e:
                        self.terminal.write("[Error] - {}.".format(e.message))
                        self.terminal.nextLine()
                        self.terminal.write("""Expects 2 Arguments, seperated by a ' '. A <key> for the setting name and <value> for the setting value. Note: <key> must not exist in configuration.\n
Conditions: <key> must Not Exist,  User = 'admin' & Status = 'Initialised'\n
Usage Syntax: 'addConfig <key> <value>'\n
Example:
piBlock> addConfig email someone@somewhere.com\n""")
                        self.terminal.nextLine()
                        self.terminal.nextLine()

        self.logger.debug("Finished!")

    #-------------------------------------------------------------
    #Commands: Config - Update a Configuration
    #-------------------------------------------------------------

    def do_updateConfig(self, *args):

        #DOCUMENTATION BLOCK

        """\nUpdates (and saves) a Config Setting.\n=====================================\n
Expects 2 Arguments, seperated by a ' '. A <key> for the setting name and <value> for the setting value. Note: <key> must exist in configuration.\n
Conditions: <key> must Exist,  User = 'admin' & Status = 'Initialised'\n
Usage Syntax: 'updateConfig <key> <value>'\n
Example:
piBlock> updateConfig email someone@somewhere.com\n"""

        self.logger.debug("Started...")

        if not (self.isAdminUser() or self.isAppStatusInitialised()):

            self.terminal.write("[Permission Denied] -  Only Admin user can add a config setting or PiBlock can only add a config setting when it is in the 'Initialised' state.")
            self.terminal.nextLine()
            self.terminal.write("To add a config setting, make sure you are logged in as 'admin' and PiBlock is in the 'Initialised' state.")
            self.nextLine()
            self.nextLine()

        else:

            if len(args) != 2:

                self.terminal.write("[Error] - Invalid number of arguments supplied.")
                self.terminal.nextLine()
                self.terminal.write("""Expects 2 Arguments, seperated by a ' '. A <key> for the setting name and <value> for the setting value. Note: <key> must exist in configuration.\n
Conditions: <key> must Exist,  User = 'admin' & Status = 'Initialised'\n
Usage Syntax: 'updateConfig <key> <value>'\n
Example:
piBlock> updateConfig email someone@somewhere.com\n""")
                self.terminal.nextLine()
                self.terminal.nextLine()

            else:

                if not self.app.piBlockEngine.doesConfigKeyExist(args[0]):

                    self.terminal.write("[Error] - Cannot Update Config Setting '{}' because it does not Exist.".format(args[0]))
                    self.terminal.nextLine()
                    self.terminal.write("Config Setting for '{}' does not exist. Cannot update a setting that does not exists in the config. If you wanted to add this '{}' setting with the value '{}', use the addConfig command by issuing 'addConfig {} {}'.".format(args[0], args[0], args[1], args[0], args[1]))
                    self.terminal.nextLine()
                    self.terminal.write("""Expects 2 Arguments, seperated by a ' '. A <key> for the setting name and <value> for the setting value. Note: <key> must not exist in configuration.\n
Conditions: <key> must Not Exist,  User = 'admin' & Status = 'Initialised'\n
Usage Syntax: 'addConfig <key> <value>'\n
Example:
piBlock> addConfig email someone@somewhere.com\n""")
                    self.terminal.nextLine()
                    self.terminal.nextLine()

                else:

                    self.logger.debug('Valid Number of Arguments were Provided...')
                    self.logger.debug("Attempting to Update Config setting '{}' with value '{}'".format(args[0], args[1]))

                    try:
                        self.app.piBlockEngine.updateConfig(args[0], args[1])
                        self.terminal.nextLine()
                        self.terminal.write("Successfully updated configuration setting '{}' with value '{}'".format(args[0], args[1]))
                        self.terminal.nextLine()
                        self.outputTitleText("PiBlock's Current Configuration Settings")
                        self.logger.debug("Displaying All Current Config Values")
                        self.terminal.write(self.app.piBlockEngine.getVerboseConfigData())
                        self.terminal.nextLine()
                        self.terminal.nextLine()

                    except BaseException as e:
                        self.terminal.write("[Error] - {}.".format(e.message))
                        self.terminal.nextLine()
                        self.terminal.write("""Expects 2 Arguments, seperated by a ' '. A <key> for the setting name and <value> for the setting value. Note: <key> must not exist in configuration.\n
Conditions: <key> must Not Exist,  User = 'admin' & Status = 'Initialised'\n
Usage Syntax: 'addConfig <key> <value>'\n
Example:
piBlock> addConfig email someone@somewhere.com\n""")
                        self.terminal.nextLine()
                        self.terminal.nextLine()

        self.logger.debug("Finished!")

    #-------------------------------------------------------------
    #Commands: Quotation - Get List of supported currencies
    #-------------------------------------------------------------

    def do_supportedCurrencies(self, *args):
        
        #DOCUMENTATION BLOCK

        """\nDisplays a list of PiBlock's Supported Fiat Currencies.\n=======================================================\n
Expects No Arguments.\n
Conditions: None\n
Shortcut: 'curr'
Usage Syntax: 'supportedCurrencies'\n
Example:
piBlock> supportedCurrencies\n"""

        self.logger.debug("Started...")

        self.terminal.nextLine()

        listOfSupportedCurrencies = self.app.piBlockEngine.getListOfSupportedCurrencies()

        listOfOutputCurrText = list()

        for n in range(len(listOfSupportedCurrencies)):
            listOfOutputCurrText.append("({}){}".format(self.app.piBlockEngine.getSymbolForCurrency(listOfSupportedCurrencies[n]), listOfSupportedCurrencies[n]))

        self.print_topics("PiBlock's Current Supported Currencies", listOfOutputCurrText, 15, 80)

        self.logger.debug("Finished!")

    #-------------------------------------------------------------
    #Commands: Quotation - Get Rate for a Currency Pair - Supports Multiple Currency Queries
    #-------------------------------------------------------------

    def do_rate(self, *args):

        #DOCUMENTATION BLOCK
        
        """\nDisplays Rate for BTC-Currency Pair.\n====================================\n
No Arguments expected but an optional argument or list of arguments can be specified for a particular currency quotations. (Note: Currency Identifiers are specified by a 3 character alphabet string.)
If no Arguments supplied, rate quoted is for the Default Currency. It also supports quoting rates for a list of supported currencies. For list of supported currencies by issue the 'supportedCurrencies' command.\n
Conditions: None\n
Usage Syntax: 'rate [<CurrencyIdentifier(1)> <CurrencyIdentifier(2)> ... <CurrencyIdentifier(n)>]'\n
Example to Query Default Currency Rate:
piBlock> rate\n
Example to Query Currency Rate in (€)EURO:
piBlock> rate EUR\n
Example to Query Currency Rate in (€)EURO & ($)USD:
piBlock> rate EUR USD\n"""

        self.logger.debug("Started...")

        self.terminal.nextLine()

        if len(args) == 0:
            
            currency = self.app.piBlockEngine.getConfigValueForKey('defaultCurrency')

            if currency == None:

                self.logger.debug("No Default Currency set!")
                
                self.terminal.write("[WARNING] - Default Currency Not Found! Unable to get any Exchange Rate because there is no 'defaultCurrency' set in the configuration. You need to resolve this immediately.")
                self.terminal.nextLine()

                if self.app.status != 'Initialised':
                    self.terminal.write("- Stop Tendering... (issue 'stopTendering' command)")
                    self.terminal.nextLine()

                if self.user.username != 'admin':
                    self.terminal.write("- Close this session and re-login as admin user")
                    self.terminal.nextLine()

                self.terminal.write("- Add a Config Setting for 'defaultCurrency' setting. (Example: piBlock> addConfig defaultCurrency EUR)")
                self.terminal.nextLine()
                self.terminal.nextLine()
                self.terminal.write("Note: You could re-issue this command 'rate' with a currency specifier.\nExample to Query Currency Rate in (€)EURO:\npiBlock> rate EUR\nPlease consult 'supportedCurrencies' command for a currency identifier")
                self.terminal.nextLine()

            else:

                self.logger.debug("Querying Currency Rate for Default Currency '{}'...".format(currency))

                currencySymbol = self.app.piBlockEngine.getSymbolForCurrency(currency)

                self.outputTitleText("Latest Quote for ({}){}".format(currencySymbol, currency))

                self.terminal.write("{} {}{} buys you 1.0 BTC\n{} {}1.00 buys you {} BTC".format(currency, currencySymbol, self.app.piBlockEngine.rateForCurrency(currency), currency, currencySymbol,  self.app.piBlockEngine.rateForBTC(currency)))
                self.terminal.nextLine()

                self.logger.debug("Querying Currency Rate...Done!") 

        else:

            for curr in args:

                currency = curr.upper()

                if len(currency) == 3:

                    if self.app.piBlockEngine.btcPricingLookup.isSupportedCurrency(currency):

                        currencySymbol = self.app.piBlockEngine.getSymbolForCurrency(currency)

                        self.outputTitleText("Latest Quote for ({}){}".format(currencySymbol, currency))
                        self.terminal.write("{} {}{} buys you 1.0 BTC\n{} {}1.00 buys you {} BTC".format(currency, currencySymbol, self.app.piBlockEngine.rateForCurrency(currency), currency, currencySymbol,  self.app.piBlockEngine.rateForBTC(currency)))
                        self.terminal.nextLine()
                        self.terminal.nextLine()

                    else:

                        self.terminal.write("[WARNING] - Currency Specified: '{}' is not supported by PiBlock.".format(currency))
                        self.terminal.nextLine()
                        self.terminal.write("Please consult the documentation or issue the 'supportedCurrencies' command to get a full list of PiBlock's supported currencies.")
                        self.terminal.nextLine()
                        self.terminal.nextLine()

                else:

                    self.terminal.write("[WARNING] - Currency Specified: '{}' is not supported by PiBlock.".format(currency))
                    self.terminal.nextLine()
                    self.terminal.write("Please consult the documentation or issue the 'supportedCurrencies' command to get a full list of PiBlock's supported currencies.")
                    self.terminal.nextLine()
                    self.terminal.nextLine()

        self.logger.debug("Finished!")

        


    #-------------------------------------------------------------
    #Commands: Quotation - Gets a BTC Amount for Currency Amount
    #-------------------------------------------------------------

    def do_convertToBTC(self, *args):

        #DOCUMENTATION BLOCK

        """\nDisplays a BTC Amount equivalent to the Currency Amount Given.\n==============================================================\n
Expects 1 Argument and a second optional Argument. The 1st argument is the amount of currency to be converted, the second argument is the currency identifier. If there is no second argument specified then piBlock will resolve the calculation in the default currency.\n
Conditions: None\n
Usage Syntax: 'convertToBTC <amount> <currency>'\n
Example:
piBlock> convertToBTC 10\n
Example with specifying a currency:
piBlock> convertToBTC 10 CAD\n"""

        self.logger.debug("Started...")

        if (len(args) < 1) or (len(args) > 2):

            self.terminal.write("[Error] - Invalid number of arguments supplied.")
            self.terminal.nextLine()
            self.terminal.write("""Expects 1 Argument and a second optional Argument. The 1st argument is the amount of currency to be converted, the second argument is the currency identifier. If there is no second argument specified then piBlock will resolve the calculation in the default currency.\n
Conditions: None\n
Usage Syntax: 'convertToBTC <amount> <currency>'\n
Example:
piBlock> convertToBTC 10\n
Example with specifying a currency:
piBlock> convertToBTC 10 CAD""")
            self.terminal.nextLine()
            self.terminal.nextLine()

        else:

            amount = args[0]

            try:

                amountFloat = float(amount)

                currency = self.app.piBlockEngine.getConfigValueForKey("defaultCurrency")

                currencySymbol = self.app.piBlockEngine.getSymbolForCurrency(currency)

                if (len(args) == 2):

                    currency =  args[1]

                    currency = currency.upper()

                    if self.app.piBlockEngine.btcPricingLookup.isSupportedCurrency(currency):
                        
                        currencySymbol = self.app.piBlockEngine.getSymbolForCurrency(currency)

                finalAmountFloat = self.app.piBlockEngine.convertToBTC(amount,currency)
                    
                rate = self.app.piBlockEngine.rateForBTC(currency)
                rateFloat = float(rate)

                formattedAmount = "{0:.2f}".format(amountFloat)
                formattedFinalAmount = "{0:.9f}".format(finalAmountFloat)
            
                self.logger.debug("Rate is {} per {}1.00".format(rateFloat, currencySymbol))
                self.logger.debug("Amount Queried is {} {}{}".format(currency, currencySymbol, amountFloat))
                self.logger.debug("Final Amount is {0:.2f}".format(finalAmountFloat))
                self.outputTitleText("({}) {} Currency Conversion to BTC:".format(currencySymbol, currency))
                self.terminal.write("{} {}{} buys you {} BTC\nRate:{} {}{} buys you 1.00 BTC".format(currency, currencySymbol, formattedAmount, formattedFinalAmount, currency, currencySymbol, self.app.piBlockEngine.rateForCurrency(currency)))
                self.terminal.nextLine()
                self.terminal.nextLine()

            except BaseException as e:

                self.terminal.write("[Error] - {}".format(e.message))
                self.terminal.nextLine()
                self.terminal.write("""Expects 1 Argument and a second optional Argument. The 1st argument is the amount of currency to be converted, the second argument is the currency identifier. If there is no second argument specified then piBlock will resolve the calculation in the default currency.\n
Conditions: None\n
Usage Syntax: 'convertToBTC <amount> <currency>'\n
Example:
piBlock> convertToBTC 10\n
Example with specifying a currency:
piBlock> convertToBTC 10 CAD""")
                self.terminal.nextLine()
                self.terminal.nextLine()

        self.logger.debug("Finished!")

        # self.terminal.nextLine()
        # self.terminal.write(self.stillToBeImplemented('convertToBTC'))
        # self.terminal.nextLine()

    #-------------------------------------------------------------
    #Commands: Quotation - Gets a Currency Amount for BTC Amount
    #-------------------------------------------------------------

    def do_convertToCurrency(self, *args):

        #DOCUMENTATION BLOCK

        """\nDisplays a Currency Amount equivalent to the BTC Amount Given.\n==============================================================\n
Expects 1 Argument and a second optional Argument. The 1st argument is the amount of BTC to be converted, the second argument is the currency identifier. If there is no second argument specified then piBlock will resolve the calculation in the default currency.\n
Conditions: None\n
Usage Syntax: 'convertToCurrency <amount> <currency>'\n
Example:
piBlock> convertToCurrency 1.9020\n
Example with specifying a currency:
piBlock> convertToCurrency 1.9020 CAD\n"""

        self.logger.debug("Started...")

        if (len(args) < 1) or (len(args) > 2):

            self.terminal.write("[Error] - Invalid number of arguments supplied.")
            self.terminal.nextLine()
            self.terminal.write("""Expects 1 Argument and a second optional Argument. The 1st argument is the amount of BTC to be converted, the second argument is the currency identifier. If there is no second argument specified then piBlock will resolve the calculation in the default currency.\n
Conditions: None\n
Usage Syntax: 'convertToCurrency <amount> <currency>'\n
Example:
piBlock> convertToCurrency 1.9020\n
Example with specifying a currency:
piBlock> convertToCurrency 1.9020 CAD""")
            self.terminal.nextLine()
            self.terminal.nextLine()

        else:

            amount = args[0]

            try:

                amountFloat = float(amount)

                currency = self.app.piBlockEngine.getConfigValueForKey("defaultCurrency")

                currencySymbol = self.app.piBlockEngine.getSymbolForCurrency(currency)

                if (len(args) == 2):

                    currency =  args[1]

                    currency = currency.upper()

                    if self.app.piBlockEngine.btcPricingLookup.isSupportedCurrency(currency):
                        
                        currencySymbol = self.app.piBlockEngine.getSymbolForCurrency(currency)

                finalAmountFloat = self.app.piBlockEngine.convertToCurrency(amount,currency)
                
                rate = self.app.piBlockEngine.rateForBTC(currency)
                rateFloat = float(rate)

                amountFloat = float(amount)

                formattedAmount = "{0:.9f}".format(amountFloat)
                formattedFinalAmount = "{0:.2f}".format(finalAmountFloat)
        
                self.logger.debug("Rate is {} BTC per {}1.00".format(rateFloat, currencySymbol))
                self.logger.debug("Amount Queried is {} BTC".format(amountFloat))
                self.logger.debug("Final Amount is {}".format(formattedFinalAmount))
                self.outputTitleText("BTC Conversion to ({}) {}:".format(currencySymbol, currency))
                self.terminal.write("{} BTC buys you {} {}{}\nRate:{} {}{} buys you 1.00 BTC".format(formattedAmount, currency, currencySymbol, formattedFinalAmount, currency, currencySymbol, self.app.piBlockEngine.rateForCurrency(currency)))
                self.terminal.nextLine()
                self.terminal.nextLine()

            except BaseException as e:
                self.terminal.write("[Error] - {}".format(e.message))
                self.terminal.nextLine()
                self.terminal.write("""Expects 1 Argument and a second optional Argument. The 1st argument is the amount of BTC to be converted, the second argument is the currency identifier. If there is no second argument specified then piBlock will resolve the calculation in the default currency.\n
Conditions: None\n
Usage Syntax: 'convertToCurrency <amount> <currency>'\n
Example:
piBlock> convertToCurrency 1.9020\n
Example with specifying a currency:
piBlock> convertToCurrency 1.9020 CAD""")
                self.terminal.nextLine()
                self.terminal.nextLine()


        self.logger.debug("Finished!")

    #-------------------------------------------------------------
    #Command: System - Uptime
    #-------------------------------------------------------------
    def do_uptime(self, *args):
        
        #DOCUMENTATION BLOCK

        """\nDisplays the system uptime.\n===========================\n
Expects No Arguments.\n
Conditions: None\n
Usage Syntax: 'uptime'\n
Example:
piBlock> uptime\n"""

        self.logger.debug("Started...")

        self.terminal.nextLine()
        self.terminal.write("PiBlock has been running for ~ {}".format(self.app.uptime))
        self.terminal.nextLine()

        self.logger.debug("Finished!")

    #-------------------------------------------------------------
    #Command: System - SysStatus
    #-------------------------------------------------------------
    def do_sysStatus(self, *args):
        
        #DOCUMENTATION BLOCK

        """\nDisplays the status state of the system.\n========================================\n
Expects No Arguments.\n
Conditions: None\n
Shortcut: 'stat'
Usage Syntax: 'sysStatus'\n
Example:
piBlock> sysStatus\n"""

        self.logger.debug("Started...")

        self.terminal.nextLine()
        self.terminal.write("PiBlock's Current System Status is '{}'".format(self.app.status))
        self.terminal.nextLine()

        self.logger.debug("Finished!")



    #-------------------------------------------------------------
    #Command: Help
    #-------------------------------------------------------------
    def do_help(self, *args):

        #DOCUMENTATION BLOCK

        """\nDisplays Help.\n==============\n
No Arguments expected but an optional argument can be specified to display additional help of a particular command.
When no arguments specified it displays a list of available commands.\n
Conditions: None\n
Usage Syntax: 'help [<command>]'\n
Shortcut: '?'
Example:
piBlock> help\n
Example when requesting help for a specific command:
piBlock> help sysStatus\n"""

        self.logger.debug("Started...")

        if len(args) != 0:
            # XXX check arg syntax
            try:
                func = getattr(self, 'help_' + args[0])
            except AttributeError:
                try:
                    doc=getattr(self, 'do_' + args[0]).__doc__
                    if doc:
                        self.terminal.write("%s\n"%str(doc))
                        return
                except AttributeError:
                    pass
                self.terminal.write("%s\n"%str(self.nohelp % (args[0],)))
                return
            func()
        else:
            names = self.get_names()
            cmds_doc = []
            cmds_undoc = []
            help = {}
            for name in names:
                if name[:5] == 'help_':
                    help[name[5:]]=1
            names.sort()
            # There can be duplicates if routines overridden
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    cmd=name[3:]
                    if cmd in help:
                        cmds_doc.append(cmd)
                        del help[cmd]
                    elif getattr(self, name).__doc__:
                        cmds_doc.append(cmd)
                    else:
                        cmds_undoc.append(cmd)
            self.terminal.write("%s\n"%str(self.doc_leader))
            self.print_topics(self.doc_header,   cmds_doc,   15,80)
            self.print_topics(self.misc_header,  help.keys(),15,80)
            self.print_topics(self.undoc_header, cmds_undoc, 15,80)

        self.logger.debug("Finished!")

    #-------------------------------------------------------------
    #Commands: Clear
    #-------------------------------------------------------------

    def do_clear(self):

        #DOCUMENTATION BLOCK

        """\nClears the output of this Interactive Terminal.\n===============================================\n
Expects No Arguments.\n
Conditions: None\n
Shortcut: 'cls'
Usage Syntax: 'clear'\n
Example:
piBlock> clear\n"""

        self.logger.debug("Started...")

        self.terminal.reset()

        self.logger.debug("Finished!")

    #-------------------------------------------------------------
    #Commands: Close
    #-------------------------------------------------------------

    def do_close(self):

         #DOCUMENTATION BLOCK

        """\nCloses this Interactive Session with PiBlock.\n=============================================\n
Expects No Arguments.\n
Conditions: None\n
Shortcut: 'q'
Usage Syntax: 'close'\n
Example:
piBlock> close\n"""

        self.logger.debug("Started...")

        self.terminal.write("Quitting... Thanks for using piBlock... Bye bye!")
        self.terminal.nextLine()
        self.terminal.loseConnection()

        self.logger.debug("Finished!")

    #-------------------------------------------------------------
    # Convenience Methods: Canned Text OUTPUT & Other Stuff
    #-------------------------------------------------------------
    def isAppStatusProcessing(self):
        if self.app.status == 'Processing':
            return True
        else:
            return False

    def isAppStatusTendering(self):
        if self.app.status == 'Tendering':
            return True
        else: 
            return False

    def isAppStatusInitialised(self):

        if self.app.status == 'Initialised':
            return True
        else:
            return False

    def isAdminUser(self):

        if self.user.username == 'admin':
            return True
        else:
            return False

    def get_names(self):
        # This method used to pull in base class attributes
        # at a time dir() didn't do it yet.
        return dir(self.__class__)

    def print_topics(self, header, cmds, cmdlen, maxcol):
        if cmds:
            self.terminal.write("%s\n"%str(header))
            if self.ruler:
                self.terminal.write("%s\n"%str(self.ruler * len(header)))
            self.columnize(cmds, maxcol-1)
            self.terminal.write("\n")

    def columnize(self, list, displaywidth=80):
        """Display a list of strings as a compact set of columns.

        Each column is only as wide as necessary.
        Columns are separated by two spaces (one was not legible enough).
        """
        if not list:
            self.terminal.write("<empty>\n")
            return
        nonstrings = [i for i in range(len(list))
                        if not isinstance(list[i], str)]
        if nonstrings:
            raise TypeError, ("list[i] not a string for i in %s" %
                              ", ".join(map(str, nonstrings)))
        size = len(list)
        if size == 1:
            self.terminal.write('%s\n'%str(list[0]))
            return
        # Try every row count from 1 upwards
        for nrows in range(1, len(list)):
            ncols = (size+nrows-1) // nrows
            colwidths = []
            totwidth = -2
            for col in range(ncols):
                colwidth = 0
                for row in range(nrows):
                    i = row + nrows*col
                    if i >= size:
                        break
                    x = list[i]
                    colwidth = max(colwidth, len(x))
                colwidths.append(colwidth)
                totwidth += colwidth + 2
                if totwidth > displaywidth:
                    break
            if totwidth <= displaywidth:
                break
        else:
            nrows = len(list)
            ncols = 1
            colwidths = [0]
        for row in range(nrows):
            texts = []
            for col in range(ncols):
                i = row + nrows*col
                if i >= size:
                    x = ""
                else:
                    x = list[i]
                texts.append(x)
            while texts and not texts[-1]:
                del texts[-1]
            for col in range(len(texts)):
                texts[col] = texts[col].ljust(colwidths[col])
            self.terminal.write("%s\n"%str("  ".join(texts)))

    def outputTitleText(self, titleText):

        self.terminal.nextLine()
        self.terminal.write(titleText.title())
        self.terminal.nextLine()
        self.terminal.write("=" * len(titleText))
        self.terminal.nextLine()


    def outputWelcomeBannerText(self):
        self.terminal.nextLine()
        self.terminal.write(self.app.piBlockEngine.aboutText)
        self.terminal.nextLine()
        self.terminal.write("Loaded the following Configuration from file '{}'...".format(self.app.piBlockEngine.configFileName))
        self.terminal.nextLine()
        self.terminal.write("For more help, issue the 'help' command, (Syntax: 'help' | '?' | 'help <command>')")
        self.terminal.nextLine()
        self.terminal.write("To Quit this interactive seesion, issue the 'close' command.\n")

    def stillToBeImplemented(self, cmdName):

        return "This command, '{}' is not yet implemented. Please check again later. :)\n".format(cmdName)

    #-------------------------------------------------------------
    # Logger
    #-------------------------------------------------------------

    def getPiBlockControlServerLogger(self):
        logger = logging.getLogger(__name__)
        loggingFileHandler = logging.FileHandler('piBlock.log')
        loggingFormatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(funcName)s %(message)s')
        loggingFileHandler.setFormatter(loggingFormatter)
        logger.addHandler(loggingFileHandler)
        logger.setLevel(logging.DEBUG)
        return logger

class PiBlockSSHAvatar(avatar.ConchUser):
    implements(ISession)

    def __init__(self, username, app):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session': session.SSHSession})
        self.app = app

    def openShell(self, protocol):
        serverProtocol = insults.ServerProtocol(PiBlockSSHProtocol, self, self.app)
        serverProtocol.makeConnection(protocol)
        protocol.makeConnection(session.wrapProtocol(serverProtocol))

    def getPty(self, terminal, windowSize, attrs):
        return None

    def execCommand(self, protocol, cmd):
        raise NotImplementedError()

    def closed(self):
        pass

class PiBlockSSHRealm(object):
    implements(portal.IRealm)

    def __init__(self, app):

        self.app = app

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IConchUser in interfaces:
            return interfaces[0], PiBlockSSHAvatar(avatarId, self.app), lambda: None
        else:
            raise NotImplementedError("No supported interfaces found.")

def hash(username, password, passwordHash):
        print("Username: {}".format(username))
        print("Password: {}".format(password))
        print("Hash: {}".format(passwordHash))
        return hashlib.sha256(password).hexdigest()

class PiBlockSSHControlServer(protocol.Factory):

    def __init__(self, app, port):

        try:
            self.app = app

            self.factory = factory.SSHFactory()
            self.factory.portal = portal.Portal(PiBlockSSHRealm(self.app))
            self.factory.portal.registerChecker(checkers.FilePasswordDB("resources/encryptd/encrptdpwd", hash=hash))

            pubKey, privKey = self.getRSAKeys()
            self.factory.publicKeys = {'ssh-rsa': pubKey}
            self.factory.privateKeys = {'ssh-rsa': privKey}

            reactor.listenTCP(int(port), self.factory)

        except Exception as e:

            raise e

    def getRSAKeys(self):

        rsaKeyLocation = self.app.piBlockEngine.getConfigValueForKey("RSAKeyLocation")

        with open(rsaKeyLocation) as privateBlobFile:
            privateBlob = privateBlobFile.read()
            privateKey = keys.Key.fromString(data=privateBlob)
        
        with open(rsaKeyLocation +'.pub') as publicBlobFile:
            publicBlob = publicBlobFile.read()
            publicKey = keys.Key.fromString(data=publicBlob)

        return publicKey, privateKey


        