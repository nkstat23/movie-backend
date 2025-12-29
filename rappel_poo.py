#### Classe chien######

class Chien:
    pass

### Objet (instance de la classe) ###
mon_chien = Chien() # creation d'un objet de la classe chien

type(mon_chien) # <class '__main__.Chien'>

### les attributs ###
class Chien:
    def __init__(self, nom, race): # methodes d'initialisation
        self.nom = nom #  attribut nom
        self.race = race # attribut age

mon_chien = Chien("Rex", "Labradore")    # creation d'un objet de la classe chien

print(mon_chien.nom)  # affiche "Rex"
print(mon_chien.race) # affiche "Labradore"


### les methodes ###
## ce sont des actions que l'objet peut effectuer
class Chien:
    def __init__(self, nom, race):
        self.nom = nom
        self.race = race
    def aboyer(self):  # methode aboyer
        return "Woof!"

rex = Chien("Rex", "Labradore")
print(rex.aboyer())  # affiche "Woof!"

#%%
# on retient quatre elements importants:
# 1. Une classe est un plan de construction pour creer des objets
# 2. Un objet est une instance d'une classe
# 3. Les attributs sont des caracteristiques d'un objet
# 4. Les methodes sont des actions que l'objet peut effectuer
#%%
# mais pourquoi utiliser la POO?
# La POO permet de mieux organiser le code, de le rendre plus reutilisable et plus facile a maintenir.
# Elle est particulirement utile pour les projets complexes ou pour modeliser des objets du monde reel.
# on encapsule les donnees et les comportements dans des objets, ce qui facilite la comprehension et la gestion du code.
# En utilisant la POO, on peut creer des objets qui encapsulent des donnees et des comportements, ce qui facilite la gestion de la complexite.