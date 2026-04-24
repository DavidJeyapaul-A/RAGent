"""
Logger module
"""
# system module import
from datetime import datetime,timezone
import logging as log
from os import path, makedirs
# import coloredlogs


class StreamLogger():
    """
    This is a logger class to setup the custom logger.
    Parameters:
        module_name     : name of the calling module
        save_log        : If True, the store the logs in log file
        log_level       : Log level of logger
    
    Return: returns the instanse of the custum logger
    """
    def __init__(self,module_name,save_log=False,log_level=None):
        """
        Costructor of the logger class
        """
        self.log = log
        self.module_name   = module_name
        self.log_level     = log_level
        self.save_log      = save_log
        self.log_file_path = "logs/"
        if path.exists(self.log_file_path):
            pass
        else:
            makedirs(self.log_file_path)
        self.log_file_path = f"logs/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.log"
        self.save_log    = False
        #return self.logger()


    def logger(self):
        """
        This function is to setup the logger with custom logging_obj format.
        also can configure the logging_obj based on files.
        """

        need_handler    = False
        # logging_obj         = self.log.getLogger(self.module_name)

        if self.log is None or not self.log.Handler:
            logging_obj  = self.log.getLogger(self.module_name)
            need_handler = True
        else:
            logging_obj = self.log.getLogger(self.module_name)
        
        # # logger setup
        # # logging_obj     = self.log.getLogger(self.module_name)
        # # # coloredlogs.install()
        # if not self.log.handlers:
        #     logging_obj     = self.log.getLogger(self.module_name)
        # else:
        #     return self.log.getLogger(self.module_name)
        
        if self.log_level == "DEBUG":
            logging_obj.setLevel(self.log.DEBUG)
        elif self.log_level == "INFO":
            logging_obj.setLevel(self.log.INFO)
        elif self.log_level == "ERROR":
            logging_obj.setLevel(self.log.ERROR)
        elif self.log_level == "WARNING":
            logging_obj.setLevel(self.log.WARNING)
        elif self.log_level == "WARN":
            logging_obj.setLevel(self.log.WARNING)
        elif self.log_level == "CRITICAL":
            logging_obj.setLevel(self.log.CRITICAL)
        elif self.log_level == "FATAL":
            logging_obj.setLevel(self.log.FATAL)
        else:
            logging_obj.setLevel(self.log.NOTSET)

        # Log format configuration
        log_format = self.log.Formatter(\
            "%(asctime)s %(levelname)s [%(name)s]: %(message)s",\
            datefmt="%m-%d-%Y %I:%M:%S")

        logging_obj.setLevel(self.log.DEBUG)

        # Add the stream logger
        if need_handler is True:
            shandler = self.log.StreamHandler()
            shandler.setFormatter(log_format)
            logging_obj.addHandler(shandler)

        # Add the file logger
        if self.save_log is True:
            fhandler  = self.log.FileHandler(self.log_file_path)
            fhandler.setFormatter(log_format)
            logging_obj.addHandler(fhandler)
        return logging_obj
