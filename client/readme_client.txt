El codi font d'aquesta solució és en python per tant no fa falta compilar-lo.
El codi s'ha provat sobre l'interpret de python 2.5, segurament funciona amb
versions anteriors, però no s'ha comprovat.

Per executar-lo:

	./client.py ip_host nom_usuari

ip_host és la direcció ip de la màquina en la que s'executa el servidor.

nom_usuari és el nom amb el que ens registrem al servidor, i amb el que s'adreça
la gent a nosaltres

Pot ser que no es tinguin permisos d'execució de l'aplicació, per a fer-ho:

	chmod +x client.py

un cop donats els permisos ja podrem executar-lo

Per aturar-lo es pot fer amb ^C (Control + c)

