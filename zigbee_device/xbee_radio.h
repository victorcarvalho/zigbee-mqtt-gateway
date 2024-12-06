#ifndef XBEE_RADIO_H
#define XBEE_RADIO_H

#include <SoftwareSerial.h>
#include <stdint.h>

extern SoftwareSerial xbeeSerial;  // Reference to xbeeSerial defined in main file
extern const uint8_t destinyAddress64[8];
extern float temperature;
extern float humidity;

// Function declarations for transmission and reception
void sendTransmitRequest(const uint8_t *destAddress64, const uint8_t *data, uint16_t dataLength);
void sendTransmitRequestFloat(const uint8_t *destAddress64, float data);
void sendTransmitRequestTemperatureAndHumidity(const uint8_t *destAddress64, float temperature, float humidity);
void handleReceivedCommand();

#endif  // XBEE_RADIO_H
