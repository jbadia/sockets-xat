El codi font d'aquesta solució és en python per tant no fa falta compilar-lo.
El codi s'ha provat sobre l'interpret de python 2.5, segurament funciona amb
versions anteriors, però no s'ha comprovat.

Per executar-lo:

	./servidor.py [host]

host és la direcció ip de la màquina en la que s'esta executant. Si no s'especifica 
el paràmetre, en principi, utilitza la direcció ip de la interficia del sistema
operatiu. Si no és així utilitzaria la ip local.

Pot ser que no es tinguin permisos d'execució de l'aplicació, per a fer-ho:

	chmod +x servidor.py

un cop donats els permisos ja podrem executar-lo

Per aturar-lo es pot fer amb ^C (Control + c)

Quan s'executa es mostra el port i la IP sobre el que esta treballant
