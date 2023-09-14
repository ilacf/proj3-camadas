from enlace import *
import enlaceRx
import time
import numpy as np

serialName = "COM5"

def main():
    try:
        print("Iniciou o main")
        com1 = enlace(serialName)

        com1.enable()

        head = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        eop = b'\xff\xee\xff'
        
        # handshake
        byte_h , _ = com1.getData(16) # 16 = tamanho do datagrama do handshake
        print(byte_h)

        qntdd_pacotes = byte_h[1]

        if byte_h[12] == b'\x00':
            com1.sendData(head + b'\x01' + eop)
            time.sleep(1)

        time.sleep(0.1)
        print(rxBuffer)

        recebido = []
        i = 0
        while i <= qntdd_pacotes:
            if com1.rx.getIsEmpty() == False:
                pacote = com1.getData(65)
                if pacote[-3:-1] == eop:
                    i += 1
                    recebido.append(pacote[12:61])
                    head_a = int.to_bytes(i, byteorder='little') + b'\x00'*11
                    com1.sendData(head_a + b'\x00' + eop)
                    time.sleep(1)
                else:
                    # avisar cliente que nao recebeu pacote
                    head_a = int.to_bytes(i, byteorder='little') + b'\x00'*11
                    com1.sendData(head_a + b'\xff' + eop)
                    time.sleep(1)

        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        
if __name__ == "__main__":
    main()
