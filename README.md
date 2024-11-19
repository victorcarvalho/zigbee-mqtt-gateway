# XBee MQTT Gateway

Este projeto implementa um gateway para comunicação entre sensores XBee e um broker MQTT. Ele coleta dados de temperatura e umidade a partir de sensores conectados a dispositivos XBee e os transmite para um servidor MQTT, permitindo o monitoramento remoto desses parâmetros.

![Visão geral da arquitetura do sistema]("iot-architecture.png")

## Arquitetura do sistema

O sistema é composto pelos seguintes dispositivos e componentes:

- DHT-11: Sensor utilizado para coletar dados de temperatura e humidade. Ele está conectado a um NodeMCU que, por sua vez, transmite os dados via comunicação serial para o XBee.

- XBee S2C: Utilizado para comunicação Zigbee entre os dispositivos da rede de sensores sem fios.

- NodeMCU (ESP8266): Módulo baseado no ESP8266 que conecta o sensor DHT-11 ao gateway, transmitindo os dados de temperatura e umidade via XBee.

- Raspberry Pi 3: Dispositivo que atua como gateway entre o XBee e o broker MQTT. Ele recebe os dados do XBee e publica as informações no servidor MQTT para monitoramento. Além disso, executa o servidor MQTT (Mosquitto) e o NodeRED.

- Broker MQTT: Servidor que recebe e gerencia as mensagens publicadas pelos dispositivos. Ele permite que os dados de temperatura e umidade sejam acessados por outros sistemas ou aplicações.

- NodeRED: Ferramenta de integração IoT que consome e apresenta os dados dos sensores em interface gráfica web.

## Requisitos de hardware
- XBee S2C: Um dispositivo que implementa o protocolo ZigBee configurado corretamente e conectado via porta serial.

- DHT-11: Um sensor conectado ao XBee via NodeMCU que envia dados de temperatura e umidade.

- NodeMCU: um módulo baseado no ESP8266 que se recebe os dados do DHT-11 e envia via Xbee para o gateway.

- Raspberry Pi 3: Um SoC que implementa um gateway de ZigBee para MQTT.

## Requisitos de software

### Dependências

Este projeto requer Python 3.6 ou superior, além de várias bibliotecas para implementar a comunicação com o XBee e o broker MQTT. As dependências podem ser instaladas usando o arquivo requirements.txt

Para instalar as dependências, basta executar o seguinte comando:

```bash
pip install -r requirements.txt
```

## Estrutura do projeto

A estrutura do projeto é a seguinte:
```bash
XBee-MQTT-Gateway/
│
├── config.yaml                # Arquivo de configuração YAML
├── xbee_mqtt_gateway.py       # Código principal do gateway
├── requirements.txt           # Arquivo de dependências
└── README.md                  # Este arquivo
```


## Conexões entre Raspberry Pi 3 e NodeMCU (ESP8266)

Abaixo está a tabela que descreve como o Raspberry Pi 3 e o NodeMCU (ESP8266) estão fisicamente conectados.


| **Pin XBee S2C** | **Pin Raspberry Pi 3 (Model B)** | **Descrição**                                  |
|------------------|---------------------------|------------------------------------------------|
| **VCC**          | **3V3**                    | Alimentação de 3,3V para o XBee (alimentado pela placa NodeMCU)  |
| **GND**          | **GND**                    | Terra (GND) para ambos os dispositivos         |
| **TX**           | **TXD (GPIO 15)**                | Comunicação serial: TX do XBee para TX do Raspberry PI (transmissão de dados) |
| **RX**           | **RXD (GPIO 16)**                | Comunicação serial: RX do XBee para RX do Raspberry PI (recepção de dados) |




## Conexões entre XBee e NodeMCU (ESP8266)

Abaixo está a tabela que descreve como o XBee S2C e o NodeMCU (ESP8266) estão fisicamente conectados para permitir a comunicação entre o sensor DHT-11 e o gateway.

| **Pin XBee S2C** | **Pin NodeMCU (ESP8266)** | **Descrição**                                  |
|------------------|---------------------------|------------------------------------------------|
| **VCC**          | **3V3**                    | Alimentação de 3,3V para o XBee (alimentado pela placa NodeMCU)  |
| **GND**          | **GND**                    | Terra (GND) para ambos os dispositivos         |
| **TX**           | **RX (D7)**                | Comunicação serial: TX do XBee para RX do NodeMCU (transmissão de dados) |
| **RX**           | **TX (D6)**                | Comunicação serial: RX do XBee para TX do NodeMCU (recepção de dados) |