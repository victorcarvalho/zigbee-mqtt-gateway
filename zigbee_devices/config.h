#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// Sampling period in milliseconds
const uint16_t SAMPLING_PERIOD = 500;

// Pins for DHT and SoftwareSerial
const uint8_t DHTPIN = D2;
const uint8_t RX_PIN = D6;
const uint8_t TX_PIN = D7;

#endif  // CONFIG_H