#!/usr/local/bin/python3
# coding=utf-8
import os
import cmd
import time
import readline
import logging

class FileFormatError(Exception):
    pass

class PiBlockConfig():

    #
    # Constructor
    #
    def __init__(self, configFileName):

        self.logger = self.getPiBlockConfigLogger()
        self.logger.debug('Initialising Configuration...')
        self._configDataDictionary = dict()
        self.configFilename = configFileName
        
        try:
            # self.logger.debug('Reading Config File {}...'.format(self.configFilename))
            self.initialiseConfigDataDictionary()
            # self.logger.debug('Reading Config File {}...Done!'.format(self.configFilename))

            # for k, v in d.items():

            #     print '\npiBlockConfigDEBUG-->' + ((k + '=' + v).strip())

            

            #self._configDataDictionary = d

            self.logger.debug('Initialising Configuration...Done!')

        except BaseException as e:
            self.logger.debug('An Exception occured whilst trying to initialise Configuration!')
            print ('An Exception occured whilst trying to initialise Configuration!')
            self.logger.debug(str(e))
            self.logger.debug('Raising this exception!')
            raise



    #-------------------------------------------------------------
    # Getters
    #-------------------------------------------------------------
    @property
    def configFilename(self):
        return self._configFilename

    @configFilename.setter
    def configFilename(self, filename):
        self._configFilename = filename

    def get_configValueForKey(self, k):
        self.logger.debug("Querying Config setting for {}".format(k))
        return self._configDataDictionary.get(k, None)

    #-------------------------------------------------------------     
    #Methods     
    #-------------------------------------------------------------

    def getConfigKeys(self):
        self.logger.debug("Attempting to get all Keys for Config...")

        self.logger.debug("Attempting to get all Keys for Config...Done!")

        return self._configDataDictionary.keys()


    def addKeyValue(self, k, v):
        self.logger.debug('Attempting to Add Config Setting...')        
        
        if k and v: 
            self.logger.debug("Storing '{}' = '{}'".format(k,v))            
            self._configDataDictionary[k] = v
            self.saveConfigToTxtfile()
        
        self.logger.debug('Attempting to Add Config Setting...Done!')   

    def updateKeyValue(self, k, v):
        self.logger.debug('Attempting to Update Config Setting...')

        if k and v:
            self.logger.debug("Storing '{}' = '{}'".format(k,v)) 
            self._configDataDictionary[k] = v
            self.saveConfigToTxtfile()
        
        self.logger.debug('Attempting to Update Config Setting...Done!')

    def getVerboseConfig(self):
        self.logger.debug('Outputting All Config Data...')
        
        line = ''

        for k, v in list(self._configDataDictionary.items()):
            # line = line + '\n' + ((k + '=' + v).strip())
            line = line + "Config Setting for '{}' has value '{}'".format(k, v).strip() + '\n'
        
        self.logger.debug('Outputting All Config Data...Done!')
        
        return line

    def initialiseConfigDataDictionary(self):
        self.logger.debug('Initialising Config Data...')
        
        try:
            for line in self.readConfigFromTxtfile():
                line = line.strip()
                self.logger.debug("Importing line: {}".format(line))
                info = line.split('=')
                # print(info)
                k = info[0].strip()
                v = info[1].strip()
                # print ("k = {}\nv={}".format(k, v))
                #self._configDataDictionary[info[0].strip()] = info[1].strip()
                self._configDataDictionary[k] = v
        except (FileFormatError, IOError, BaseException) as e:
            self.logger.debug('An error has occured!')
            self.logger.debug(str(e))
            self.logger.debug('Raising this exception!')
            raise

        self.logger.debug('Initialising Config Data...Done!')

    def readConfigFromTxtfile(self):
        self.logger.debug('Reading Config File {}...'.format(self.configFilename))
        
        if self.configFilename.endswith('.txt'):
            self.logger.debug('Checked the config file name .txt!')
            if os.path.exists(self.configFilename):
                self.logger.debug('Checked the config file exists!')
                try:
                    self.logger.debug('Attempting to open config file...')
                    readFilehandle = open(self.configFilename, 'r')
                    self.logger.debug('Attempting to open config file...Done!')
                    self.logger.debug('Attempting to read data from the file!')
                    return readFilehandle.readlines()
                except (IOError, BaseException) as e:
                    self.logger.debug('An error has occured!')
                    self.logger.debug(str(e))
                    self.logger.debug('Raising this exception!')
                    raise
            else:
                self.logger.debug('An error has occured, file does not exist!')
                self.logger.debug('Raising this an IOError exception!')
                raise IOError
        else:
            self.logger.debug('An error has occured, file is not a txt format!')
            self.logger.debug('Incorrect File format. Expected pliain text (.txt) file format.')
            self.logger.debug('Raising this exception!')
            raise FileFormatError('Incorrect File format. Expected pliain text (.txt) file format.')
        
        self.logger.debug('Reading Config File {}...Done!'.format(self.configFilename))

    def saveConfigToTxtfile(self):
        self.logger.debug('Overwriting Config File {}...'.format(self.configFilename))
        
        if self.configFilename.endswith('.txt'):
            self.logger.debug('Checked the config file name .txt!')
            try:
                self.flushConfigFile()
                self.logger.debug('Attempting to create a config file...')
                writeFilehandle = open(self.configFilename, 'w')
                self.logger.debug('Attempting to create a config file...Done!')
                self.logger.debug('Attempting to write data to config file...')
                for k, v in list(self._configDataDictionary.items()):
                    #line = line + '\n' + ((k + '=' + v).strip())
                    writeFilehandle.write((k + '=' + v).strip()+'\n')

                writeFilehandle.close()
                self.logger.debug('Attempting to write data to config file...Done!')
            except (IOError, BaseException) as e:
                self.logger.debug('An error has occured!')
                self.logger.debug(str(e))
                self.logger.debug('Raising this exception!')
                raise 
        else:
            self.logger.debug('An error has occured, file is not a txt format!')
            self.logger.debug('Incorrect File format. Expected pliain text (.txt) file format.')
            self.logger.debug('Raising this exception!')
            raise FileFormatError('Incorrect File format. Expected plain text (.txt) file format.')

        self.logger.debug('Overwriting Config File {}...Done!'.format(self.configFilename))

    def flushConfigFile(self):
        self.logger.debug('Flushing Config File {}...'.format(self.configFilename))
        
        if os.path.exists(self.configFilename):
            os.remove(self.configFilename)

        self.logger.debug('Flushing Config File {}...Done!'.format(self.configFilename))

    #-------------------------------------------------------------
    # Logger
    #-------------------------------------------------------------
    
    def getPiBlockConfigLogger(self):
        logger = logging.getLogger(__name__)
        loggingFileHandler = logging.FileHandler('piBlock.log')
        loggingFormatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        loggingFileHandler.setFormatter(loggingFormatter)
        logger.addHandler(loggingFileHandler)
        logger.setLevel(logging.DEBUG)
        return logger
