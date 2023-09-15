from enlace import *
from enlaceRx import *
import time
import numpy as np

#   python -m serial.tools.list_ports

serialName = "COM3"

def dps_do_h(pedacos, eop, com1):
    i = 0
    while i < len(pedacos):
        print(f"cheguei: {i}")
        # montando head
        n = (i+1).to_bytes(1, byteorder='big')
        tamanho = len(pedacos).to_bytes(1, byteorder='big')
        len_pl = len(pedacos[i]).to_bytes(1, byteorder='big')

        head = n + tamanho + len_pl + b'\xaa'*9

        com1.sendData(np.asarray(head + pedacos[i] + eop))
        time.sleep(0.1)
         
        comeco = time.time()
        while time.time()-comeco < 5:
            if com1.rx.getIsEmpty() == False:
                print("recebeu direito")
                # combinado com o servidor: se nao recebeu o pacote, manda b'\xbb', se sim: b'\xcc'
                head_confirm, _ = com1.getData(12)
                time.sleep(0.1)
                pl_confirm, _ = com1.getData(head_confirm[2])
                time.sleep(0.1)
                print(pl_confirm)
                eop_confirm, _ = com1.getData(3)
                if pl_confirm == b'\xcc' and eop_confirm == eop:
                    i += 1

def main():
    try:
        print("Iniciou o main")

        com1 = enlace(serialName)
        com1.enable()

        # byte de sacrificio
        time.sleep(.2)
        com1.sendData(b'00')
        time.sleep(0.1)

        print("Abriu a comunicação")

        # abrindo e fragmentando a imagem
        pedacos = []
        img = open('img.png', 'rb').read()
        x = len(img) / 50
        for pedaco in range(round(x)):
            pedacos.append(img[pedaco:pedaco+50])

        # Montagem do datagrama de handshake
        qntd_pacotes = len(pedacos).to_bytes(1, byteorder='big', signed=False)
        # tamanho do payload:
        len_pl = (1).to_bytes(1, byteorder="big") # payload do handshake eh 1
        h_head = b'\x00' + qntd_pacotes + len_pl + b'\xaa'*9
        print(f"qntd_pacotes = {qntd_pacotes}")
        # Handshake: manda 00, recebe 01 (txBuffer = h_dg)
        h_payload = b'\x00'
        h_eop = b'\xff\xee\xff'

        com1.sendData(np.asarray(h_head + h_payload + h_eop))
        time.sleep(0.1)
        txSize = com1.tx.getStatus()
        print('enviou = {} bytes' .format(txSize))

        # receber quantidade de comandos recebida pelo server
        comeco = time.time()
        while time.time()-comeco < 5:
            if com1.rx.getIsEmpty() == False:
                head_receb, _ = com1.getData(12)
                time.sleep(0.1)
                pl_receb, _ = com1.getData(head_receb[2])
                time.sleep(0.1)
                eop_receb, _ = com1.getData(3)
                if pl_receb == b'\x01' and eop_receb == b'\xff\xee\xff':
                    print('*'*50)
                    print('Handshake completo')
                    print(f"Servidor devolveu o byte {pl_receb}")
                    print('*'*50)
                    dps_do_h(pedacos, h_eop, com1)

                    print("-------------------------")
                    print("Comunicação encerrada")
                    print("-------------------------")
                    com1.disable()

        dnv = input("Servidor inativo. Tentar novamente? S/N \n")
        if dnv == 'S' or dnv == 's':
            main()
        else:
            com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        
if __name__ == "__main__":
    main()