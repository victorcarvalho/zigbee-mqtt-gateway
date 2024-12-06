#include <SoftwareSerial.h>
#include "DHT.h"
#include "config.h"
#include "xbee_radio.h"

// Define destination addresses here if needed
const uint8_t destinyAddress64[8] = {0x00, 0x13, 0xA2, 0x00, 0x41, 0xD8, 0xCF, 0x47};

// Sensor and communication objects
DHT dht(DHTPIN, DHT11);
SoftwareSerial xbeeSerial(RX_PIN, TX_PIN);

// Temperature and humidity variables
float humidity;
float temperature;

void setup() {
    Serial.begin(9600);
    xbeeSerial.begin(9600);
    dht.begin();
}

void loop() {
    // Read sensor data
    humidity = dht.readHumidity();
    temperature = dht.readTemperature();
    // humidity = 4.5;
    // temperature = 4.5;

    if (isnan(temperature) || isnan(humidity)) {
        Serial.println("Failed to read from DHT");
    } else {
        Serial.println("Sucessfull read from DHT");
        Serial.print("Humidity: ");
        Serial.print(humidity);
        Serial.print("%, Temperature: ");
        Serial.print(temperature);
        Serial.println(" °C");
    }

    handleReceivedCommand();  // Handle Zigbee commands
    delay(SAMPLING_PERIOD);
}
