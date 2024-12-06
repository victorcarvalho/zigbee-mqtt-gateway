import unittest
import struct
from main import XbeeMQTTGateway, XBeeConfig, MQTTConfig

class TestXbeeMQTTGateway(unittest.TestCase):

    def setUp(self):
        self.xbee_config = XBeeConfig(serial_port="/dev/ttyS0", baud_rate=9600, target_address=None)
        self.mqtt_config = MQTTConfig(broker="localhost", port=1883, topic="xbee/data")
        self.gateway = XbeeMQTTGateway(self.xbee_config, self.mqtt_config)

    def test_mqtt_config_initialization(self):
        broker = "localhost"
        port = 1883
        topic = "xbee/data"
        mqtt_config = MQTTConfig(broker, port, topic)
        
        self.assertEqual(mqtt_config.broker, broker)
        self.assertEqual(mqtt_config.port, port)
        self.assertEqual(mqtt_config.topic, topic)

    def test_connect_mqtt(self):
        # Test the connection to the MQTT broker
        self.gateway.connect_mqtt()
        self.assertTrue(self.gateway.mqtt_client.is_connected())

    def test_publish_sensor_data(self):
        # Setup for publishing test
        self.gateway.connect_mqtt()
        self.assertTrue(self.gateway.mqtt_client.is_connected())
        # Simulate sensor data publishing
        temperature = 25.5
        humidity = 60.0
        sender_address = "00:13:A2:00:41:52:74:21"
        self.gateway._publish_sensor_data(temperature, humidity, sender_address)

    def test_xbee_config_initialization(self):
        serial_port = "/dev/ttyS0"
        baud_rate = 9600
        target_address = None
        xbee_config = XBeeConfig(serial_port, baud_rate, target_address)
        
        self.assertEqual(xbee_config.serial_port, serial_port)
        self.assertEqual(xbee_config.baud_rate, baud_rate)
        self.assertEqual(xbee_config.target_address, target_address)

    def test_unpack_sensor_data_valid(self):
        data = struct.pack('ff', 25.0, 60.0)
        temperature, humidity = self.gateway._unpack_sensor_data(data)
        self.assertEqual(temperature, 25.0)
        self.assertEqual(humidity, 60.0)

    def test_unpack_sensor_data_invalid_length(self):
        invalid_data = b"\x00\x00\x00\x00"  # Incorrect length
        with self.assertRaises(ValueError):
            self.gateway._unpack_sensor_data(invalid_data)


if __name__ == '__main__':
    unittest.main()
