"""
Notification helper module
"""

# system module import
import sys
import json
from datetime                     import timezone,datetime
from path                         import Path

# path setup
directory = Path(__file__)
# PARENT_FOLDER_PATH = str(directory.parent.parent.parent)
PARENT_FOLDER_PATH = str(directory.parent.parent.parent.parent)
sys.path.append(PARENT_FOLDER_PATH)

# local module import
from src.helpers.load_config      import fetch_json_config
from src.helpers                  import mqtt_client
from src.helpers.logger           import StreamLogger
from db_lib.db_lib                import tConfig


from src.helpers                        import validate_input_params

from src.template.interface_template import ProtocolInterface
from src.template.client_template    import BaseClient



# logger setup
logging = StreamLogger("Notification-service",True,"DEBUG").logger()

# db instanse creations
tConfig_notification_object  = tConfig()


class NotificationClient(BaseClient):
    """
    This ModbusInterface class is equiped with connect, disconnect, stop, get 
    and set bit and registers. It object is instatiated with some mandatory 
    parameters such as ip, port, unit and mapping of device registers
    
    Parameters:
        ip         : IP address of the modbus device
        port       : Port of the modbus device
        unit       : Unit ID of the modbus device
        devRegs    : The address of which registers need to be captured and 
                        updated via periodic loop

    Return: 
        returns the instance of ModbusInterface class specific to modbus ip and 
        port
    """

    interface_name = "notification"

    def __init__(self, **kwargs):
        """
        This is constructor of the class
        """
        super(BaseClient, self).__init__()

        self.instance_id            = NotificationClient.get_instance_id(**kwargs)
        self.mqtt_host              = None
        self.mqtt_port              = None
        self.subcribe_topics        = None
        self.publish_topic          = None
        self.username               = None
        self.password               = None
        self.caCert                 = None
        self.clientCert             = None
        self.privateKey             = None
        self.keepAlive              = None
        # self.will_topic             = None
        # self.will_message           = None
        
        self.interface_config       = None
        self.app_config             = None

        self.client                 = None
        self.connected              = False
        self.stopped                = False
        self.triggered_by           = "unknown"
        self.origin_id              = None
        self.request_id             = None
        self.update_db_rejected     = False
        self.nt_send_url            = None

        self.temp_msg_list          = []
        
        if "mqttHost"           in kwargs and "mqttPort"     in kwargs \
            and "userName"      in kwargs and "password"     in kwargs \
            and "caCert"        in kwargs and "clientCert"   in kwargs \
            and "mqttPubTopic"  in kwargs and "mqttSubTopic" in kwargs \
            and "privateKey"    in kwargs and "keepAlive"    in kwargs:

            self.mqtt_host              = kwargs["mqttHost"]
            self.mqtt_port              = kwargs["mqttPort"]
            self.subcribe_topics        = kwargs["mqttSubTopic"]
            self.publish_topic          = kwargs["mqttPubTopic"]
            self.username               = kwargs["userName"]
            self.password               = kwargs["password"]
            self.ca_cert                = kwargs["caCert"]
            self.client_cert            = kwargs["clientCert"]
            self.private_key            = kwargs["privateKey"]
            self.keep_alive             = kwargs["keepAlive"]
            # self.will_topic             = kwargs["will_topic"]
            # self.will_message           = kwargs["will_message"]
        
        if "interfaceConfig" in kwargs:
            self.interface_config = kwargs["interfaceConfig"]

        if "appConfig" in kwargs:
            self.app_config       = kwargs["appConfig"]
            self.nt_send_url      = f"http://{self.app_config['APP_HOST']}:{self.app_config['APP_PORT']}/notification/send"

        if "interfaceObj" in kwargs:
            self.interface_obj = kwargs["interfaceObj"]


            
    
     # get instance id to map with perticular parameter based on module
    
    @staticmethod
    def get_instance_id(**params):
        if "mqttHost" in params and "mqttPort" in params:
            if validate_input_params.validate_ip(str(params["mqttHost"])) is False:
                return None

            if validate_input_params.validate_port(str(params["mqttPort"])) is False:
                return None

            instance_id = NotificationClient.interface_name + "-" + str(params["mqttHost"]) + ":" + str(params["mqttPort"])
            return instance_id
        else:
            return None

    
    # Notification connect
    def connect(self):
        """
        This function is to connect the notification client to the MQTT broker.

        Return:
            returns the connection status
        """
        if self.mqtt_host is not None and self.mqtt_port is not None \
            and self.connected is False and self.stopped is False:
            self.client = mqtt_client.MQTTHandler(
                                    mqtt_Host           = self.mqtt_host,
                                    mqtt_Port           = self.mqtt_port,
                                    subcribe_topics     = self.subcribe_topics,
                                    interface_type      = NotificationClient.interface_name,
                                    on_msg              = self.message_handler,
                                    username            = self.username,
                                    password            = self.password,
                                    caCert              = self.ca_cert,
                                    clientCert          = self.client_cert,
                                    privateKey          = self.private_key,
                                    keepAlive           = self.keep_alive
                                )
            resp = self.client.mqtt_connect()
            config_data_dict = self.create_config_payload()
            if resp['status_code'] == 200:
                self.connected     = True
                config_data_dict["IsActive"] = 1
                config_data_dict["Status"]   = "Connected"
                logging.info(f"Updating the Notification config to db: {json.dumps(config_data_dict)}")
                tconfig_response = tConfig_notification_object.set(config_data_dict)
                logging.info(f"Data updated to the config table: {tconfig_response}")
            else:
                MQTT_CLIENT_DISCONNECT     = False
                config_data_dict["IsActive"] = 0
                config_data_dict["Status"]   = "Failed to Connect"
                logging.info(f"Updating the Notification config to db: {json.dumps(config_data_dict)}")
                tconfig_response = tConfig_notification_object.set(config_data_dict)
                logging.info(f"Data updated to the config table: {tconfig_response}")

            return {
                    "response" : f"{NotificationClient.interface_name} - {resp['response']}",
                    "status_code" : resp["status_code"]
                }
        else:
            if self.connected is True:
                return {
                    "response" : f"{NotificationClient.interface_name} is already connected",
                    "status_code" : 208
                }

            if self.stopped is True:
                return {
                    "response" : f"{NotificationClient.interface_name} is stopped",
                    "status_code": 400
                }


    # disconnect MQTT module
    def disconnect(self):
        """
        This function is to disconnect the notification client from the MQTT broker.

        Return:
            returns the connection status
        """
        if self.client is not None:
            resp = self.client.mqtt_disconnect()
            if resp['status_code'] == 200:
                self.connected = False
                self.client    = None
            return resp
        
    # connection status
    def status(self):
        """
        This function is to check the connectivity between notification client and
        the MQTT broker.

        Return:
            returns the connection status
        """
        if self.client is not None:
            if self.client.mqtt_connected:
                return {
                        "response": "MQTT client connected",
                        "status_code": 200
                        }
            else:
                return {
                    "response": "MQTT client disconnected",
                    "status_code": 412
                    }
        else:
            return {
                    "response": "MQTT client not created",
                    "status_code": 400
                    }

    # send notification
    def send(self,**params):
        """
        This function is to publish the notification to the MQTT broker.

        Parameters:
            payload     : Message to be published.

        Return:
            returns the notification publish status
        """
        try:
            if "service_type"  in params and "message"  in params and \
                "hash_id"      in params and "priority" in params:
                service_type    = params["service_type"]
                message         = params["message"]
                hash_id         = params["hash_id"]
                priority        = params["priority"]
            else:
                return {
                    "response" : f"Invalid input: {dict(params.items())}",
                    "status_code" : 400
                }
            

            if self.stopped is True:
                return {
                    "response" : f"{NotificationClient.interface_name} is stopped",
                    "status_code": 400
                }

            if self.connected is False:
                self.connect()


            if self.client is not None:
                if self.connected is True:
                    if(service_type == "mqtt" and type(message) is dict):
                        message.update({"RTC":str(datetime.now(timezone.utc))})
                        resp = self.client.mqtt_pub(self.publish_topic.format(deviceID=hash_id),message)
                        return resp
                    else:
                        return {
                                "response": "Unknown service type or message is not JSON",
                                "status_code": 400
                                }
                else:
                    return {
                        "response" : "MQTT Client is not connected",
                        "status_code" : 400
                    }
            else:
                return {
                    "response" : "MQTT Client is not created",
                    "status_code" : 400
                }
        except Exception as err:
            logging.error(f"Error in Notification send: {err}")
            return {
                "response" : f"Error in Notification send: {err}",
                "status_code" : 400
            }

    # Call back function for MQTT
    def message_handler(self,**kwargs):
        """
        This is a MQTT callback fucntion for notification. When there is a message on
        subcribed topic, this will log the message in the console.

        Parameters:
            mqtt_message         : The actual message 
        """
        if "mqttmessage" in kwargs:
            mqtt_message = kwargs["mqttmessage"]
            
        logging.info(f"Notification Message: {mqtt_message}")

    def stop(self):
        self.disconnect()
        self.stopped = True
        return {
            "response" : f"{NotificationClient.interface_name} is stopped successfully",
            "status_code" : 200
        }
    
    def start(self):
        self.stopped = False
        self.connect()
        return {
            "response" : f"{NotificationClient.interface_name} is started successfully",
            "status_code" : 200
        }

    # create config dict
    def create_config_payload(self):
        """
        This funciton is to create the config dict

        Parameters:
            _payload        : The input payload for notification module.

        Return:
            returns the config dict
        """
        config_data_dict = tConfig_notification_object.payload_tconfig
        config_data_dict["Id"] = self.instance_id
        config_data_dict["InterfaceType"] = NotificationClient.interface_name
        config_data_dict["Configuration"] = {
                                        "mqttHost"     : self.mqtt_host,       
                                        "mqttPort"     : self.mqtt_port,      
                                        "mqttSubTopic" : self.subcribe_topics,
                                        "mqttPubTopic" : self.publish_topic,
                                        "userName"     : self.username,         
                                        "password"     : self.password,         
                                        "caCert"       : self.ca_cert,          
                                        "clientCert"   : self.client_cert,       
                                        "privateKey"   : self.private_key,      
                                        "keepAlive"    : self.keep_alive  
                                    }
        config_data_dict["Description"] = "Notification config update description"
        config_data_dict["ModifiedOn"]  = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        return config_data_dict
    
    def details(self,**kwargs):
        pass
    
    def get_properties(self,**kwargs):
        pass
    
    def set_property(self,**kwargs):
        pass
    
    def devices(self,**kwargs):
        pass

    def update_to_db(self,**kwargs):
        if len(self.temp_msg_list) > 0:
            for item in self.temp_msg_list:
                self.send(**item)
            self.temp_msg_list = []
        
        self.update_now = False

    
    def delete_device(self,**kwargs):
        pass

    def add_device(self, **kwargs):
        return {
            "status_code" : 422,
            "response"  : f"Functionality is not supported for {NotificationClient.interface_name} interface yet"
        }
    
    def get_live_data(self, **kwargs):
        return {
            "status_code" : 422,
            "response"  : f"Functionality is not supported for {NotificationClient.interface_name} interface yet"
        }
        
class NotificationMqttInterface(ProtocolInterface):
    def __init__(self, **kwargs):
      super().__init__(**kwargs)


    def send(self,**params):

        nt_obj_list = self.instances
        if len(nt_obj_list) <= 0:
            return {"response":f"Any notification interface is not created yet!", "status_code": 400}

        for obj in nt_obj_list:
            client_obj = obj["obj"]
            
            if len(client_obj.temp_msg_list) >= client_obj.interface_config["messeageBufferSize"]:
                client_obj.temp_msg_list.pop(0)
            client_obj.temp_msg_list.append(params)
            client_obj.update_now = True
        self.fetch_now = True

        return {
            "response"      : "Notification messege is in queue",
            "status_code"   : 200
        }

        
# Notification mqtt interface object
# Note: Please keep the object name "interface_obj"
interface_obj = NotificationMqttInterface(client=NotificationClient)
