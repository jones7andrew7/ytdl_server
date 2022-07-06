from configparser import ConfigParser
#import logging #NOTE: Because the config is loaded BEFORE logging starts I will not be loading logging in this module
import os, io

#REF: https://docs.python.org/3/library/configparser.html
class YTDLServerConfig():

    def __init__(self):
        self._cfg_file = 'ytdl-server-DEV.ini' #This is just a quick and dirty default for dev
        #Formally, the config file will be loaded from ENV vars; which are easier to integrate with docker
        #I'm splitting between the two just to jog my memory on how to use each option.
        #Ideally a project of this size would be better off just picking one method and sticking with it.
        if 'YTDL_CFG_FILE' in os.environ:
            self._cfg_file = os.environ['YTDL_CFG_FILE']
        # Write a default config file if no file is present at the configured path
        if not os.path.isfile(self._cfg_file):
            self.write_default_config_file()
        self._config = self.load_config_file()

        # Set variables from the config file
        self.host = self._config['server']['host']
        self.port = self._config['server']['port']
        self.working_dir = None #If not provided in the file, let the main module handle setting this to the dev default
        if 'working_dir' in self._config['server']:
            self.working_dir = self._config['server']['working_dir']

        #Read the path of the log file from environment variable
        #Default to setting ing this to None, which will result in the logging going to console instead of a file.
        self.log_file = None
        if 'YTDL_LOG_FILE' in os.environ:
            log_file_dir = os.path.dirname(os.environ['YTDL_LOG_FILE'])
            #print(f"DEBUG: log_file_dir: '{log_file_dir}'")
            #Check that the directory path is at least valid before trusting the ENV var
            #If the path given was JUST a filename (no dir or './' which will make log_file_dir == '') then that will also work
            if log_file_dir == '' or os.path.isdir(log_file_dir):
                self.log_file = os.environ['YTDL_LOG_FILE']

    def write_default_config_file(self):
        print(f'DEBUG: No config file found at name: {self._cfg_file}; Creating default.')
        config = ConfigParser()
        config['server'] = {'host': '0.0.0.0',
                            'port': 8443,
                            'working_dir': '/opt/ytdl_server/'}
        with open(self._cfg_file, 'w') as cfgfile:
            config.write(cfgfile)

    def load_config_file(self):
        config = ConfigParser()
        config.read(self._cfg_file)
        return config
