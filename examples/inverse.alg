Algorithme inverse
Début
Écrire("Entrez un nombre : ")
Lire(n)
inverse <- 0
TantQue (n > 0) Faire
    reste <- n Mod 10
    inverse <- (inverse * 10) + reste
    n <- n Div 10
FinTantQue
Écrire("Sortie : ", inverse)
Fin
