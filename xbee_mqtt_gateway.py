import struct
import time
import logging
from typing import Tuple, Optional
import paho.mqtt.client as mqtt
from digi.xbee.devices import XBeeDevice
from digi.xbee.exception import InvalidPacketException, TimeoutException, XBeeException
from digi.xbee.models.address import XBee64BitAddress
import yaml


class MQTTConfig:
    def __init__(self, broker: str, port: int, topic: str):
        self.broker = broker
        self.port = port
        self.topic = topic


class XBeeConfig:
    def __init__(self, serial_port: str, baud_rate: int, target_address: Optional[str] = None):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.target_address = target_address


class LoggerSetup:
    @staticmethod
    def setup_logger(name: str = __name__) -> logging.Logger:
        logger = logging.getLogger(name)
        if logger.hasHandlers():
            return logger

        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%d-%m-%Y %H:%M:%S'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        file_handler = logging.FileHandler('app.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger


class XbeeMQTTGateway:
    TEMPERATURE_TOPIC = 'temperature'
    HUMIDITY_TOPIC = 'humidity'
    POLLING_INTERVAL = 10  # seconds

    def __init__(self, xbee_config: XBeeConfig, mqtt_config: MQTTConfig):
        self.xbee_config = xbee_config
        self.mqtt_config = mqtt_config
        self.logger = LoggerSetup.setup_logger()
        
        self.device = self._initialize_xbee()
        self.mqtt_client = self._initialize_mqtt()
        
        if xbee_config.target_address:
            self.target_address = XBee64BitAddress.from_hex_string(xbee_config.target_address)
        else:
            self.target_address = None

    def _initialize_xbee(self) -> XBeeDevice:
        """Initialize XBee device with configured parameters."""
        return XBeeDevice(
            self.xbee_config.serial_port,
            self.xbee_config.baud_rate
        )

    def _initialize_mqtt(self) -> mqtt.Client:
        """Initialize MQTT client with configured parameters."""
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = self._on_mqtt_connect
        client.on_disconnect = self._on_mqtt_disconnect
        return client

    def _on_mqtt_connect(self, client, userdata, flags, rc, properties=None):
        """Callback for when the client receives a CONNACK response from the server."""
        self.logger.info(f"Connected to MQTT broker with result code: {rc}")

    def _on_mqtt_disconnect(self, *args):
        """Flexible callback for when the client disconnects from the server."""
        rc = args[-1]  # Last argument is typically the result code
        self.logger.warning(f"Disconnected from MQTT broker with result code: {rc}")

    def connect_mqtt(self):
        """Establish connection to MQTT broker."""
        try:
            self.mqtt_client.connect(self.mqtt_config.broker, self.mqtt_config.port)
            self.mqtt_client.loop_start()
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    def _unpack_sensor_data(self, data: bytes) -> Tuple[float, float]:
        """Unpack the received sensor data into temperature and humidity values."""
        try:
            return struct.unpack('ff', data)
        except struct.error as e:
            self.logger.error(f"Failed to unpack sensor data: {e}")
            raise

    def _publish_sensor_data(self, temperature: float, humidity: float):
        """Publish sensor data to MQTT broker."""
        try:
            self.mqtt_client.publish(
                f"{self.mqtt_config.topic}/{self.TEMPERATURE_TOPIC}",
                temperature
            )
            self.mqtt_client.publish(
                f"{self.mqtt_config.topic}/{self.HUMIDITY_TOPIC}",
                humidity
            )
            self.logger.info(f"Published sensor data - Temperature: {temperature}, Humidity: {humidity}")
        except Exception as e:
            self.logger.error(f"Failed to publish sensor data: {e}")

    def xbee_data_receive_callback(self, xbee_message):
        """Handle incoming XBee messages."""
        try:
            temperature, humidity = self._unpack_sensor_data(xbee_message.data)
            self._publish_sensor_data(temperature, humidity)
        except (InvalidPacketException, TimeoutException, struct.error) as e:
            self.logger.error(f"Error processing XBee message: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in XBee callback: {e}")

    def request_sensor_data(self):
        """Send command to XBee to request sensor data."""
        try:
            self.device.send_data_broadcast("GET_TEMP")
            self.logger.debug("Requested sensor data from XBee")
        except XBeeException as e:
            self.logger.error(f"Failed to request sensor data: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error requesting sensor data: {e}")

    def start(self):
        """Start the XBee-MQTT gateway operation."""
        try:
            self.device.open()
            self.logger.info(f"XBee connection established (API mode 1). Polling sensors each {self.POLLING_INTERVAL} s")
            self.device.add_data_received_callback(self.xbee_data_receive_callback)
            self.logger.info("Gateway started successfully")

            while True:
                self.request_sensor_data()
                time.sleep(self.POLLING_INTERVAL)

        except KeyboardInterrupt:
            self.logger.info("Shutting down gateway...")
        except Exception as e:
            self.logger.error(f"Fatal error in gateway operation: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources and connections."""
        try:
            if self.device and self.device.is_open():
                self.device.close()
                self.logger.info("XBee connection closed")
            
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
                self.logger.info("MQTT connection closed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def load_config(config_file: str) -> Tuple[XBeeConfig, MQTTConfig]:
    """Carregar configurações do arquivo YAML."""
    with open(config_file, 'r') as file:
        config_data = yaml.safe_load(file)

    # Carregar configurações do XBee
    xbee_config = XBeeConfig(
        serial_port=config_data['xbee']['serial_port'],
        baud_rate=config_data['xbee']['baud_rate'],
        target_address=config_data['xbee'].get('target_address')
    )

    # Carregar configurações do MQTT
    mqtt_config = MQTTConfig(
        broker=config_data['mqtt']['broker'],
        port=config_data['mqtt']['port'],
        topic=config_data['mqtt']['topic']
    )

    return xbee_config, mqtt_config


if __name__ == "__main__":
    # Carregar as configurações do arquivo YAML
    xbee_config, mqtt_config = load_config('config.yaml')

    # Criar e iniciar o gateway XBee-MQTT
    gateway = XbeeMQTTGateway(xbee_config, mqtt_config)
    gateway.connect_mqtt()
    gateway.start()
