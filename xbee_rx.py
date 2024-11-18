import struct
import time
import logging
import paho.mqtt.client as mqtt
from digi.xbee.devices import XBeeDevice
from digi.xbee.exception import InvalidPacketException, TimeoutException
from digi.xbee.models.address import XBee64BitAddress


class XBeeMQTTBridge:
    def __init__(self, serial_port, baud_rate, mqtt_broker, mqtt_port, mqtt_topic):
        self.device = XBeeDevice(serial_port, baud_rate)
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        # create console handler
        c_handler = logging.StreamHandler()
        c_format = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
        c_handler.setFormatter(c_format)
        self.logger.addHandler(c_handler)

        # create file handler
        f_handler = logging.FileHandler('app.log')
        f_handler.setFormatter(c_format)
        self.logger.addHandler(f_handler)

        # target_address = None
        # self.target_address = XBee64BitAddress.from_hex_string(target_address)


    def connect_mqtt(self):
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port)

    def xbee_data_receive_callback(self, xbee_message):
        try:
            temperature, humidity = self._unpack_data(xbee_message.data)
            self.mqtt_publish_data(temperature, humidity)

            # self._unpack_temperature(xbee_message.data)
            # self.mqtt_publish_data(temperature)
        except (InvalidPacketException, TimeoutException) as e:
            self.logger.error(f"Error processing packet: {e}")
        except UnicodeDecodeError:
            self.logger.error("Decoding error while reading data.")

    def _unpack_temperature(self, data):
        """Unpack the received data into a float."""
        return struct.unpack('f', data)[0]
    
    def _unpack_data(self, data):
        """Unpack the received data into a float."""
        # return struct.unpack('ff', data)[0]
        return struct.unpack('ff', data)

    def mqtt_publish_data(self, temperature, humidity):
        """Publish the temperature and humidity."""
        self.logger.info("Data published")
        # self.logger.info(temperature, humidity)
        self.logger.info(f'{temperature}, {humidity}')
        self.mqtt_client.publish(self.mqtt_topic + '/temperature', temperature)
        self.mqtt_client.publish(self.mqtt_topic + '/humidity', humidity)

    def mqtt_publish_temperature(self, temperature):
        """Publish the temperature and humidity."""
        self.logger.info("Data published")
        self.logger.info(temperature)
        self.mqtt_client.publish(self.mqtt_topic + '/temperature', temperature)

    def xbee_ask_temperature(self):
        """Send command to XBee to request temperature."""
        try:
            # self.device.send_data_broadcast("0")
            self.device.send_data_broadcast("GET_TEMP")
            # self.device.send_data(self.device.get_remote_device(target_address), bytes([0]))
            self.logger.info("Requested temperature from XBee")
        except Exception as e:
            self.logger.error(f"Failed to request temperature: {e}")

        
    def xbee_ask_humidity(self):
        pass

    def start(self):
        try:
            self.device.open()
            self.logger.debug("Conexão XBee estabelecida. Aguardando pacotes (modo API 1)")
            self.device.add_data_received_callback(self.xbee_data_receive_callback)
            self.logger.info("Gateway iniciado com sucesso")

            # input("Press Enter to exit...\n")

            while True:
                self.xbee_ask_temperature()
                time.sleep(10)

        except Exception as e:
            self.logger.error(f"Erro de leitura: {str(e)}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Close the XBee device connection."""
        if self.device.is_open():
            self.device.close()
            self.logger.info("Connection with XBee closed")

if __name__ == "__main__":
    # Configuration
    SERIAL_PORT = "/dev/ttyS0"
    BAUD_RATE = 9600
    MQTT_BROKER = "localhost"  # or remote MQTT broker IP
    MQTT_PORT = 1883            # MQTT broker port
    MQTT_TOPIC = "xbee/data"

    # Create and start the XBee-MQTT bridge
    bridge = XBeeMQTTBridge(SERIAL_PORT, BAUD_RATE, MQTT_BROKER, MQTT_PORT, MQTT_TOPIC)
    bridge.connect_mqtt()
    bridge.start()