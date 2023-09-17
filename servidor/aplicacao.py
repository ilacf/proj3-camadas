from enlace import *
import time
import base64

serialName = "COM8"

def main():
    try:
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()
        print("Abriu a comunicação")
        print("esperando 1 byte de sacrifício")
        _, _ = com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(1)

        h_head = b'\x00\x00' + (1).to_bytes(1, byteorder="big") + b'\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa\xaa'
        eop = b'\xff\xee\xff'
        
        # handshake
        head_receb_h , _ = com1.getData(12)
        pl_receb_h, _ = com1.getData(head_receb_h[2])
        eop_receb_h, _ = com1.getData(3)

        if pl_receb_h == b'\x00' and eop_receb_h == eop:
            com1.sendData(h_head + b'\x01' + eop)
            time.sleep(0.1)
        
        recebido = b''
        pacote_anterior = 0
        i = 0
        while i < head_receb_h[1]:
            comeco = time.time()
            mandou = False
            while time.time()-comeco < 5:
                if com1.rx.getIsEmpty() == False:
                    # pegando head do pacote
                    mandou = True
                    head_receb, _ = com1.getData(12)
                    pl_receb, _ = com1.getData(head_receb[2])
                    eop_receb, _ = com1.getData(3)

                    pacote_atual = head_receb[0]
                    print(f"pacote atual: {pacote_atual}")
                    qntd_pacotes = head_receb[1].to_bytes(1, byteorder='big')
                    n_pacote = i.to_bytes(1, byteorder='big')
                    # pl de confirmacao de recebimento do pacote
                    pl_correto = b'\xcc'
                    pl_errado = b'\xbb'

                    # confirmacao de recebimento do pacote
                    if eop_receb == eop and pacote_atual == (pacote_anterior + 1):
                        pacote_anterior = pacote_atual
                        i += 1
                        recebido += pl_receb
                        # head de confirmacao de recebimento do pacote
                        head_a = n_pacote + qntd_pacotes + (1).to_bytes(1, byteorder="big") + b'\xaa'*9
                        com1.sendData(head_a + pl_correto + eop)
                        time.sleep(0.1)
                    else:
                        # avisar cliente que nao recebeu pacote
                        head_a = n_pacote + qntd_pacotes + (1).to_bytes(1, byteorder="big") + b'\xaa'*9
                        com1.sendData(head_a + pl_errado + eop)
                        time.sleep(0.1)
            if mandou == False:
                print("Cliente parou de mandar pacotes antes da quantidade total. Parar recepção")
                com1.disable()
                break

        if i == head_receb_h[1]-1:
            # combinado com o cliente: quando o servidor terminar de receber tudo, envia um b'\xAA'
            head_termino = n_pacote + qntd_pacotes + (1).to_bytes(1, byteorder="big") + b'\xaa'*9
            com1.sendData(head_termino + b'\xAA' + eop)
            time.sleep(0.1)

            with open('output.png', 'wb') as image_file:
                image_file.write(recebido)

            print("Imagem recebida salva")

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
