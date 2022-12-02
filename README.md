# TIA_SMA

## Résumé

Agent (Thread)

- Connaissances
  - Grilles
  - les autres pièces
  - Etat courant
  - Etat terminal  
  
- Comportement
  - Run() : boucle de contrôle, condition d'arrêt Etat courant = Etat final
    - Observer
    - Rechercher
    - Appliquer les mouvements
  
Message

- Emetteur
- Recepteur
- Performatif (demande un mouvement)
- Contenu
  - Action (bouger)
  - Paramètre (quelle est la case à quitter)

## Frameworks

[Lien récap](https://cedric-buron.medium.com/un-rapide-retour-sur-les-frameworks-python-pour-les-syst%C3%A8mes-multi-agents-183986474019)
Potentiellement Pade pour l'envoie de message entre agents
Pour les threads le module Threading qui marche comme pthreads en C++

