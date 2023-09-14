from enlace import *
from enlaceRx import *
import time
import numpy as np

#   python -m serial.tools.list_ports

serialName = "COM7"

def dps_do_h(pedacos, eop, com1):
    i = 0
    while i < len(pedacos):

        # montando head
        n = i.to_bytes(1, byteorder='little')
        print(f"----------------- n: {n} -----------------")
        tamanho = len(pedacos).to_bytes(1, byteorder='big')
        print(f"----------------- tamanho: {tamanho} -----------------")

        head = n + tamanho + b'\x00'*10

        # montando txBuffer
        print(f"HEAD = {head}")
        txBuffer = head + pedacos[i] + eop
        com1.sendData(np.asarray(txBuffer))
        time.sleep(1)
         
        comeco = time.time()
        while time.time()-comeco < 5:
            if com1.rx.getIsEmpty() == False:
                # combinado com o servidor: se nao recebeu o pacote, manda b'\xff', se sim: b'\x00'
                rxBuffer, _ = com1.getData(12 + 1 + 3)
                if rxBuffer[12] == b'\x00':
                    i += 1

def main():
    try:
        print("Iniciou o main")

        com1 = enlace(serialName)

        print("Abriu a comunicação")

        # abrindo e fragmentando a imagem
        img = open('img.png', 'rb').read()
        img = np.frombuffer(img, dtype=np.uint8)
        pedacos = np.array_split(img, len(img) // 50)

        # Montagem do datagrama de handshake
        tamanho = len(pedacos).to_bytes(1, byteorder='big', signed=False)
        head = b'\x00' + tamanho + b'\x00'*10
        eop = b'\xff\xee\xff'
        size_head = np.asarray(head).nbytes
        size_eop = np.asarray(eop).nbytes

        # Handshake: manda 00, recebe 01 (txBuffer = h_dg)
        h_payload = b'\x00'
        h_dg = head + h_payload + eop

        print(f"DATAGRAMA DO HANDSHAKE = {h_dg}")
        print(f"meu array de bytes tem tamanho {len(h_dg)}")   
        
        com1.sendData(np.asarray(h_dg))
        time.sleep(0.1)

        txSize = com1.tx.getStatus()
        print('enviou = {} bytes' .format(txSize))

        # receber quantidade de comandos recebida pelo server
        comeco = time.time()
        while time.time()-comeco < 5:
            if com1.rx.getIsEmpty() == False:
                rxBuffer, _ = com1.getData(size_head + 1 + size_eop) # 16 = 12 + 1 + 3
                if rxBuffer[12] == b'\x01':
                    print('*'*100)
                    print('Handshake completo')
                    print(f"Servidor devolveu o byte {rxBuffer}")
                    print('*'*100)
                    dps_do_h(com1)

                    print("-------------------------")
                    print("Comunicação encerrada")
                    print("-------------------------")
                    com1.disable()

        dnv = input("Servidor inativo. Tentar novamente? S/N \n")
        if dnv == 'S' or dnv == 's':
            com1.disable()
            main()
        else:
            com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        
if __name__ == "__main__":
    main()