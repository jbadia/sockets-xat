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
port = 8642

class InetNode(object):
    """Aquest un tipus de node de xarxa,esta pensat
    per a que pugui emmagatzemar informació de clients
    com informació de servidors"""
    
    def __init__(self, address='127.0.0.1'):
        """Paràmetres per defecte d'un client"""
        self.nom = ""
        self.socket = None
        self.address = address
        self.port = socket.htons(port)
        self.estatus = "desconnectat"
        self.expansion = None

    def setServidor(self,address=socket.gethostname(),num_clients=10):
        """Configuració d'un client de tipus servidor"""
        self.nom = "server"
        self.address = socket.gethostbyname(address)
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM,0)
            self.socket.bind((self.address, port))
            self.socket.listen(num_clients)
        except:
            print "port" , port , "no disponible"
            sys.exit()
        self.status = "servidor"
    
    def setClient(self,socket,address='127.0.0.1',puerto=port):
        """Configuració d'un client de tipus client"""
        self.socket = socket
        self.address = address
        self.port = puerto
        self.status = "connectat"

    def printClient(self):
        """Funció per a veure l'estat d'un client concret"""
        print "nom: ", self.nom
        print "socket: ", self.socket
        print "ip: ", self.address
        print "port: ", self.port
        print "estat: ",self.status
        
    def sendMissatge(self, text):
        """Funció per enviar missatges de text"""
        self.socket.send(text)
    
    def sendOK(self,text="OK"):
        """Funció per enviar missatges de confirmació, es pot canviar la
        part final del missatge"""
        self.sendMissatge("200 " + text + "\n")
        
    def sendERROR(self, text="PAIN IN THE ASS"):
        """Funció per enviar missatges d'error, equivalent a sendOk però per 
        a errors"""
        self.sendMissatge("400 " + text + "\n")
    
    def sendREGERR(self, text="USER ALREADY REGISTERED"):
        self.sendMissatge("401 " + text + "\n")
    
    def reciveMissatge(self):
        """Funció per a rebre missatges"""
        return self.socket.recv(BUFSIZ)    


        
class Servidor(object):
    """Aquesta classe és la que ens farà la gestió dels missatges i 
    dels clients que te connectats"""
    
    def __init__(self,host,num_clients=10):
        self.clients = []
        self.maxClients = num_clients
        
        ##socket servidor
        self.clients.append(InetNode())
        self.clients[0].setServidor(host,self.maxClients)
      
    def totsSockets(self):
        """Funció que retorna una llista amb tots els sockets de l'aplicació"""
        llistaSockets = []
        for client in self.clients:
            llistaSockets.append(client.socket)
        return llistaSockets
      
    def socketsClient(self):
        """Funció que retorna tots els sockets clients que estan connectats
        en aquest servidor"""
        llistaSockets = totsSockets()
        return llistaSockets[1:]

    def printTotsClients(self):
        """Funció que mostra l'estatus de tots els nodes connectats al servidor,
        el servidor també hi apareix, de la forma que esta fet ara"""
        for client in self.clients:
            client.printClient()
        
    def posicioClient(self, socket):
        """Funció que ens retorna la posició del socket sobre la llista
        de sockets"""
        for pos,clie in enumerate(self.clients):
            if socket==clie.socket : return pos
    
    def closeClient(self, posicio):
        """Funció que gestiona la ordre QUIT del protocol"""
        self.clients[posicio].sendOK()
        self.clients[posicio].socket.close()
        self.clients[posicio].status = "desconnectat"
        del self.clients[posicio]
    
    def closeErrClient(self, posicio):
        """Funció que tanca sockets de clients, a diferencia de
        close clients està pensada per tancar sockets morts"""
        self.clients[posicio].socket.close()
        self.clients[posicio].status = "desconnectat"
        del self.clients[posicio]
        
    def indentificar(self, posicio, missatge):
        """Funció que gestiona la ordre HELLO del protocol"""
        if missatge == "HELO\n":
            self.clients[posicio].sendOK()
            self.clients[posicio].status = "identificat"
        else:
            self.clients[posicio].sendERROR()
    
    def registrar(self, posicio, missatge):
        """Funció que gestiona la ordre REGISTER del protocol"""
        try:
            comanda, nom = missatge.split(' ')
            nom=nom[:-1]
        except:
            self.clients[posicio].sendERROR()
            return
        
        if comanda != "REGISTER":
            self.clients[posicio].sendERROR()
            return
        
        for client in self.clients:
            if client.nom == nom:
                self.clients[posicio].sendREGERR()
                return
        
        self.clients[posicio].nom = nom
        self.clients[posicio].sendOK()
        self.clients[posicio].status = "registrat"
    
    def query(self, posicio, missatge):
        """Funció que gestiona la ordre QUERY del protocol"""
        try:
            comanda, nom = missatge.split(' ')
            nom=nom[:-1]
        except:
            self.clients[posicio].sendERROR()
            return
        
        if comanda != "QUERY":
            self.clients[posicio].sendERROR()
            return
        
        for client in self.clients:
            if client.nom == nom:
                self.clients[posicio].sendOK(client.address)
                return
            
        self.clients[posicio].sendERROR("USER NOT FOUND")
        
    def start(self):
        """Funció que inicia el servidor per a gestionar peticions"""
        print "port d'escolta: ", port
        print "ip host: ", self.clients[0].address
        while True:
            try:

                inputready, outputready, exceptready = select.select(self.totsSockets(), [], [])

                for input in inputready:
                    #mirem si ha sigut el servidor
                    if input == self.clients[0].socket:
                        
                        sock, address = self.clients[0].socket.accept()
                        if len(self.clients) < self.maxClients+1:
                            
                            client = InetNode()
                            client.setClient(sock, address[0], address[1])
                            
                            self.clients.append(client)
                        else:
                            sock.close()
                        
                    else:
                        accio_efectuada = False
                        #aquest else tracta tots els clients
                        data = input.recv(BUFSIZ)
                        posicio_client = self.posicioClient(input)
                        if data == "" : self.closeErrClient(posicio_client)
                        
                        #comprovem si vol marxar
                        if data == "QUIT\n" and not accio_efectuada:
                            print "surt", posicio_client
                            self.closeClient(posicio_client)
                            accio_efectuada = True
                        
                        if self.clients[posicio_client].status == "connectat" and not accio_efectuada:
                            print "identifica", posicio_client
                            self.indentificar(posicio_client, data)
                            accio_efectuada = True
                            
                        if self.clients[posicio_client].status == "identificat" and not accio_efectuada:
                            print "registrant", posicio_client
                            self.registrar(posicio_client, data)
                            accio_efectuada = True
                            
                        if self.clients[posicio_client].status == "registrat" and not accio_efectuada:
                            self.query(posicio_client, data)
                            accio_efectuada = True
                            
            except KeyboardInterrupt:
                self.clients[0].socket.close()
                sys.exit()
                
            except: pass

if __name__ == '__main__':
    host = socket.gethostname()
    if len(sys.argv) > 1:
        host = sys.argv[1]
    Servidor(host).start()