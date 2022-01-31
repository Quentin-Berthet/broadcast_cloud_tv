# TP1 Broadcast Algorithm

## Branches
* Le code Go se trouve sur la branche [go](https://gitedu.hesge.ch/baptiste.coudray/tp1_broadcast_algorithm/-/tree/go).
* Le code Python se trouve sur la branche [python](https://gitedu.hesge.ch/baptiste.coudray/tp1_broadcast_algorithm/-/tree/python).

## Executer le projet
* ouvrir 10 terminals au niveau du projet
* pour lancer les programme il suffit de faire 
	* python3 ClientServer.py (num du fichier neighbour) port
* de ce fait on aura pour chaque instance respectivement:
	* python3 ClientServer.py 1 1331
	* python3 ClientServer.py 2 1332
	* python3 ClientServer.py 3 1333
	* (...)
			
	* python3 ClientServer.py 10 1340

* Une fois toute les machine lancées 
	appuyer sur 1 pour créer une transaction

* une fois la premiere transaction effectuée vous pouvez maintenat effectuer un vote afin de savoir si tout vos voisins ont bien reçu la transaction
	appuyer sur 2 puis choisissez une transaction, copier coller 	la valeur auquel correcpond cette transaction dans le 	terminal et ensuite vous verrez apparaître une valeur en 	pourcente représentant le bon déroulement de l'envoie d une 	transaction à ses voisins. 

* pour modifier les voisins de chaque noeuds utilisez les fichiers neighbour-X.txt en restectant la nomenclature suivante:
* 127.0.0.1:n°port

## Auteurs
* Baptiste Coudray
* Quentin Berthet
