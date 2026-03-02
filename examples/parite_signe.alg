Algorithme Parite_Signe
Début
Écrire("Entrez un entier : ")
Lire(n)
Si (n Mod 2 = 0) Alors
    Si (n >= 0) Alors
        Écrire("Pair et Positif")
    Sinon
        Écrire("Pair et Négatif")
    FinSi
Sinon
    Si (n >= 0) Alors
        Écrire("Impair et Positif")
    Sinon
        Écrire("Impair et Négatif")
    FinSi
FinSi
Fin
