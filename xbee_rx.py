from digi.xbee.devices import XBeeDevice
from digi.xbee.exception import InvalidPacketException, TimeoutException

# Configuração da porta serial e taxa de transmissão
device = XBeeDevice("/dev/ttyS0", 9600)

try:
    # Abre a conexão com o XBee
    device.open()
    print("Esperando pacotes do XBee no modo API 1")

    def data_receive_callback(xbee_message):
        try:
            sender = xbee_message.remote_device.get_64bit_addr()
            data = xbee_message.data.decode('utf-8')  # Decodifica os dados recebidos
            print(f"Dados recebidos do endereço {sender}: {data}")
        except (InvalidPacketException, TimeoutException) as e:
            print(f"Erro ao processar o pacote: {e}")
        except UnicodeDecodeError:
            print("Erro de decodificação ao tentar ler dados.")
    
    # Configura o callback para dados recebidos
    device.add_data_received_callback(data_receive_callback)

    input("Pressione Enter para encerrar...\n")

except Exception as e:
    print(f"Erro na leitura: {e}")

finally:
    if device.is_open():
        device.close()
        print("Conexão com o XBee encerrada.")