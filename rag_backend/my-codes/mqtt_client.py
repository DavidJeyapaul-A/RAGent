# system module imprt
from time                   import sleep
import json
import sys
import path
import paho.mqtt.client     as mqtt

# logger setup
directory = path.Path(__file__)
PARENT_FOLDER_PATH = str(directory.parent.parent.parent.parent)
sys.path.append(PARENT_FOLDER_PATH)

# local module import
from src.helpers.logger     import StreamLogger


# logger setup
logging = StreamLogger("MQTT",True,"DEBUG").logger()

# MQTT Client class
class MQTTHandler:
    """
    This is a class which handles MQTT connection.
    mqtt_Host       : str
    mqtt_Port       : number
    subcribe_topics : list(string)
    interface_type  : str
    on_msg          : On message function with one message input
    """
    def __init__(self,
                 mqtt_Host,
                 mqtt_Port,
                 subcribe_topics,
                 interface_type,
                 on_msg,
                 username=None,
                 password=None,
                 caCert=None,
                 clientCert=None,
                 privateKey=None,
                 keepAlive=60):
        """
        This is constructor of the class
        """
        self.mqtt_host          = mqtt_Host
        self.mqtt_port          = mqtt_Port
        self.on_msg             = on_msg
        self.username           = username
        self.password           = password
        self.ca_cert            = caCert
        self.client_cert        = clientCert
        self.private_key         = privateKey
        self.keep_alive          = keepAlive
        self.interface_type     = interface_type
        self.subcribe_topics    = subcribe_topics
        self.mqtt_client         = None
        self.mqtt_connected      = False
        self.mqtt_init           = True

    def update_config(self,topics):
        """
        This function to update the subcribed topic list if any differenece

        Parameters:
            topics  : new topic list

        return: None
        """
        if set(topics) != set(self.subcribe_topics):
            if self.mqtt_connected:
                for topic in self.subcribe_topics:
                    self.mqtt_client.unsubscribe(topic)
                for topic in topics:
                    self.mqtt_client.subscribe(topic,qos=1)

    #The callback for when the client receives a CONNACK response from the server.
    def on_connect(self,mqttClient, userdata, flags, rc):
        """
        This is a MQTT callback connect function
        """
        logging.debug(f"MQTT Client connected with result code : {rc}")
        self.mqtt_connected = True
        for topic in self.subcribe_topics:
            mqttClient.subscribe(topic,qos=1)
            logging.info(f'MQTT Clinet subcribed to the topic: {topic}')

    def on_disconnect(self,mqttClient,userdata, rc):
        """
        This is a MQTT call back disconnect function
        """
        for topic in self.subcribe_topics:
            mqttClient.unsubscribe(topic)
        logging.info(f'MQTT Client disconnected with rc: {rc}')
        # mqttClient.loop_stop()
        self.mqtt_connected = False

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self,mqttClient,userdata, msg):
        """
        This is a MQTT callback for when a PUBLISH message is received from
          the server.
        """
        self.on_msg(str(msg.payload.decode()))


    # connect
    def mqtt_connect(self):
        """
        This funtion is to connect the MQTT client to MQTT broker

        Return: returns the status of the MQTT connetion
        """
        try:
            if self.mqtt_connected:
                return {
                    "response": f"MQTT is already connecected \
                        with {self.mqtt_host}:{self.mqtt_port}",
                    "status_code": 200
                }

            logging.info('Started mqtt connection')
            if self.mqtt_init:
                logging.debug("Creating mqtt client")
                self.mqtt_client                  = mqtt.Client()
                self.mqtt_client.on_connect       = self.on_connect
                self.mqtt_client.on_disconnect    = self.on_disconnect
                self.mqtt_client.on_message       = self.on_message
                self.mqtt_client.username_pw_set(username= self.username,\
                                                password= self.password)
                self.mqtt_client.connect(self.mqtt_host, self.mqtt_port,\
                                        self.keep_alive)
                self.mqtt_client.loop_start()
                sleep(0.5)      # Safe sleep
                if self.mqtt_connected:
                    return {
                        "response": f"MQTT is connected with \
                            {self.mqtt_host}:{self.mqtt_port}",
                        "status_code": 200
                    }
                else:
                    return {
                        "response": "MQTT connection not established",
                        "status_code": 400
                    }
            else:
                return {
                        "response": "MQTT client not initialized",
                        "status_code": 400
                    }
        except Exception as err:
            logging.error(f"Error in MQTT connect: {err}")
            return {
                        "response": f"Error in MQTT connect: {err}",
                        "status_code": 400
                    }

    # disconnect
    def mqtt_disconnect(self):
        """
        This function is to disconnect the MQTT client from the MQTT broker.

        Return: returns the status of the MQTT connetion
        """
        try:
            if self.mqtt_connected and (self.mqtt_client is not None):
                rc = self.mqtt_client.disconnect()
                sleep(0.3)      # Safe sleep
                if rc == 0:
                    return {
                        "response" : "MQTT clinet is disconnected",
                        "status_code" : 200
                    }
                else:
                    return {
                        "response" : "Error disconnecting MQTT client",
                        "status_code" : 400
                    }
            else:
                return {
                    "response" : "MQTT clinet is already disconnected",
                    "status_code" : 200
                }
        except Exception as expt:
            logging.error(f"Error Disconnectig MQTT Clinet: {expt}")
            return {
                "response" : f"Error Disconnectig MQTT Clinet: {expt}",
                "status_code" : 400
            }

    # pubish
    def mqtt_pub(self,topic,msg):
        """
        This function is to publish the data to connected MQTT broker. 

        Parameters:
            topic : Topic to publish the message
            msg   : Message to publish

        Return: returns the status of the publish operation
        """
        try:
            if self.mqtt_connected and (self.mqtt_client is not None):
                (rc , mid) = self.mqtt_client.publish(topic,json.dumps(msg), qos = 1)
                if rc == 0:
                    return {
                        "response" : f"MQTT message published success: \
                            {msg}.Topic: {topic}",
                        "status_code" : 200
                    }
                else:
                    return {
                        "response" : f"Failed to send MQTT message.\
                              Error code : {rc}, MID : {mid}",
                        "status_code" : 400
                    }

            else:
                return {
                    "response" : "MQTT clinet disconnected",
                    "status_code" : 400
                }
        except Exception as expt:
            logging.error(f"Error publishing MQTT message: {expt}")
            return {
                "response" : f"Error publishing MQTT message: {expt}",
                "status_code" : 400
            }