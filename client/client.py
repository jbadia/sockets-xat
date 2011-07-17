#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Copyright (c) 2009 Jordi Badia
    
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; version 2 of the License.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
import sys, socket, select

BUFSIZ = 1024
port = 7766

class Client(object):
    """Client, es l'objecte que ens permet establir
    connexió amb el servidor i els altres clients, 
    guarda l'informació més important del nostre client"""
    
    def __init__(self, host='127.0.0.1', port=8642):
        """Inicialització per defecte dels clients"""
        self.nom =""
        self.socketServidor = None
        self.socketClients = None
        self.address = host
        self.port = int(port)
        self.lastcmd = ""
        self.estatus = "desconnectat"
        self.expansion = None
    
    # Code gwarrior
    def initClient(self,nom="client", num_clients=5):
        """Inicialització del client, es recomana utilitzar crear
        el client amb aquesta funció, ja que tindrem el client 
        connectat amb el servidor"""
        self.nom = nom
        self.socketServidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) # connexio TCP
        self.socketServidor.connect((self.address,self.port))
        self.estatus = "connectat"
        return self
    
    def startLisseningClients(self):
        """escoltem per a connexions entrants amb els altres clients,
        la interficie utilitzada serà en la que tenim connexió a internet"""
        try:
            self.socketClients = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0) # connexio UDP
            # utilitzem l'interficie principal, ja que 127.0.0.1 dona problemes
            #self.socketClients.bind((socket.gethostbyname(socket.gethostname()),port))
            self.socketClients.bind(('',port))
        except:
            print "\nERR, ja disposes d'un client connectat"
            self.exit()
    
    def autoLog(self):
        """Autolog ens logueja automàticament amb el nom proveït, si 
        s'ha pogut establir la connexió amb el nom especificat, podrem
        enviar missatges, sinò es tancarà l'app i ens farà fora"""
        missatge=""
        while True: # processem cada un dels estats en els que podem estar
            
            if self.lastcmd == "REGISTER":
                if missatge[:3] == "200":
                    print "OK"
                else:
                    print "FAIL"
                    print "\nERR nom en us, prova un altre nom"
                    self.exit()
                return 
            
            if self.estatus == "connectat" and self.lastcmd == "":
                print " identificant ..."
                self.socketServidor.send("HELO\n")
                self.lastcmd = "HELO"
            
            if self.lastcmd == "HELO" and missatge[:3] == "200":
                print " registrant...",
                self.estatus = "identificat"
                self.socketServidor.send("REGISTER " + self.nom + "\n")
                self.lastcmd = "REGISTER"
                
            try:
                sys.stdout.flush()
                inputready, outputready, exceptready = select.select([self.socketServidor], [], [])
                missatge = self.socketServidor.recv(BUFSIZ)
            except: pass
    
    def exit(self):
        """Funció que ens tanca l'aplicació, amb l'alliberament previ
        del sockets"""
        print "\nFinalitzant el client"
        try:
            self.socketServidor.close()
            self.socketClients.close()
        except: pass
        sys.exit()
        
    def exitQuit(self):
        self.socketServidor.send("QUIT\n")
        self.exit()
    
    def askUser(self, name):
        """Mètode que ens permet preguntar la direcció ip al
        servidor donat el seu nom"""
        self.socketServidor.send("QUERY " + name + "\n") 
        # no me mola com esta implementat, en aquest moment el client es quedarà bloquejat
        msg = self.socketServidor.recv(BUFSIZ)
        try:
            msg = msg[:-1]
            codi, direccio = msg.split(' ',1)
            if codi == "200":
                return direccio
        except:
            print "\nERR error en el protocol del servidor"
            self.exit()
        return ""

    def startClient(self, auto = False):
        """Amb aquest mètode es processen les peticions, main"""
        if auto:
            # forcem l'autolog per tenir un nom concret tota l'estona, ja que si deixem 
            # que es pugui canviar, faria falta un metode que verifiques cada instrucció
            # que s'envia al servidor per comprovar el nom, i actualitzar-lo si lautolog 
            # hagues fallat en intentar registrar un nom en us
            self.autoLog()
        self.startLisseningClients() # un cop estem registrats escoltem si ens arriven missatges dels clients
        while True:
            try:
                sys.stdout.flush()
                inputready, outputready, exceptready = select.select([0, self.socketServidor, self.socketClients ], [], [])
                for i in inputready:
                    if i == 0: # gestió de l'entrada per teclat
                        data = sys.stdin.readline().strip()
                        try: # mirem si es un missatge a un altre usuari
                            usuari, missatge = data.split(': ',1)
                            ip = self.askUser(usuari)
                            if ip:
                                self.socketClients.sendto(self.nom + "# " + missatge, (ip, port))
                            else:
                                print u" - l'usuari", usuari ,"no es torba en aquest servidor"
                        except ValueError: # si ha fallat el parsing es una comanda de protocol
                            if data: self.socketServidor.send(data+"\n")    
                    elif i == self.socketServidor: # recollim els missatges del servidor
                        missg = self.socketServidor.recv(BUFSIZ)
                        if missg == "": # si el servidor es queda penjat ens arriba una cadena vuida del
                            self.exit() # servidor constantment
                        print missg
                    elif i == self.socketClients:
                        missg = self.socketClients.recv(BUFSIZ)
                        print missg # mostrem el missatge dels altres clients
                    else: pass
            except KeyboardInterrupt: # es tanca el client amb ctrl + C
                self.exitQuit()

if __name__ == '__main__':
    
    if len(sys.argv) != 3:
        print "Us: ", sys.argv[0], "host nom"
        sys.exit()
        
    host = sys.argv[1]
    nom = sys.argv[2]
    
    usuari = Client(host).initClient(nom) # inicialització del client
    usuari.startClient(True) # amb True forcem a autologuejar-nos amb el nom passat a initClient