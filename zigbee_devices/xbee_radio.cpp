#include "config.h"
#include "xbee_radio.h"
#include <Arduino.h>

// Zigbee frame start delimiter
const uint8_t START_DELIMITER = 0x7E;
// "GET_DATA" in ASCII
const char *COMMAND = "GET_DATA";

// Function to calculate the checksum
uint8_t calculateChecksum(const uint8_t *data, uint16_t length) {
    uint8_t checksum = 0;
    for (uint16_t i = 0; i < length; i++) {
        checksum += data[i];
    }
    return 0xFF - checksum;
}

// Function to send a Transmit Request with any payload
void sendTransmitRequest(const uint8_t *destAddress64, const uint8_t *data, uint16_t dataLength) {
    uint16_t packetLength = 14 + dataLength;  // 14 bytes fixed + payload length
    uint8_t packet[packetLength + 4];         // +4 for Start Delimiter and length
    int index = 0;

    packet[index++] = START_DELIMITER;
    packet[index++] = (packetLength >> 8) & 0xFF;
    packet[index++] = packetLength & 0xFF;
    packet[index++] = 0x10;  // Frame Type
    packet[index++] = 0x01;  // Frame ID

    memcpy(packet + index, destAddress64, 8);
    index += 8;
    packet[index++] = 0xFF;
    packet[index++] = 0xFE;
    packet[index++] = 0x00;
    packet[index++] = 0x00;

    memcpy(packet + index, data, dataLength);
    index += dataLength;
    packet[index++] = calculateChecksum(packet + 3, packetLength);

    xbeeSerial.write(packet, index);
    Serial.println("Transmit Request sent.");
}

// Send a Transmit Request with a float
void sendTransmitRequestFloat(const uint8_t *destAddress64, float data) {
    uint8_t floatBytes[sizeof(float)];
    memcpy(floatBytes, &data, sizeof(float));
    sendTransmitRequest(destAddress64, floatBytes, sizeof(float));
}

// Send combined temperature and humidity
void sendTransmitRequestTemperatureAndHumidity(const uint8_t *destAddress64, float temperature, float humidity) {
    uint8_t payload[sizeof(float) * 2];
    memcpy(payload, &temperature, sizeof(float));
    memcpy(payload + sizeof(float), &humidity, sizeof(float));
    sendTransmitRequest(destAddress64, payload, sizeof(payload));
}

// Handle command received via Zigbee
void handleReceivedCommand() {
    if (xbeeSerial.available()) {
        if (xbeeSerial.read() == START_DELIMITER) {
            delay(50);

            uint16_t length = (xbeeSerial.read() << 8) | xbeeSerial.read();
            Serial.print("Length: ");
            Serial.println(length);

            uint8_t frameType = xbeeSerial.read();

            if (frameType == 0x91) {
                Serial.println("Explicit RX Indicator (0x91) received");

                uint8_t sourceAddress[8];
                xbeeSerial.readBytes(sourceAddress, sizeof(sourceAddress));

                uint8_t networkAddress[2] = {xbeeSerial.read(), xbeeSerial.read()};
                uint8_t sourceEndpoint = xbeeSerial.read();
                uint8_t destinationEndpoint = xbeeSerial.read();
                uint8_t clusterID[2] = {xbeeSerial.read(), xbeeSerial.read()};
                uint8_t profileID[2] = {xbeeSerial.read(), xbeeSerial.read()};
                uint8_t receiveOptions = xbeeSerial.read();

                uint16_t rfDataLength = length - 18;
                uint8_t rfData[rfDataLength];
                xbeeSerial.readBytes(rfData, rfDataLength);

                Serial.print("rfData: ");
                for (int i = 0; i < sizeof(rfData); i++) {
                    Serial.print(rfData[i]);
                    Serial.print(" ");
                }
                Serial.println();
                
                Serial.print("Command expected: ");
                for (int i = 0; i < sizeof(COMMAND); i++) {
                    Serial.print(COMMAND[i]);
                    Serial.print(" ");
                }
                Serial.println();

                if (memcmp(rfData, COMMAND, sizeof(COMMAND)) == 0) {
                    Serial.println("Request for temperature and humidity");
                    sendTransmitRequestTemperatureAndHumidity(sourceAddress, temperature, humidity);
                }
                
                Serial.println();

                uint8_t checksum = xbeeSerial.read();
                uint8_t computedChecksum = calculateChecksum(&frameType, length + 1);
                if (checksum != computedChecksum) {
                    Serial.println("Invalid checksum");
                }
            } else {
                Serial.print("Unknown frame type: ");
                Serial.println(frameType, HEX);
            }
        }
    }
}
