#include <stdio.h>

int main() {
    int n;
    printf("Entrez un entier : \n");
    scanf("%d", &n);
    if (((n % 2) == 0)) {
        if ((n >= 0)) {
            printf("Pair et Positif\n");
        } else {
            printf("Pair et Négatif\n");
        }
    } else {
        if ((n >= 0)) {
            printf("Impair et Positif\n");
        } else {
            printf("Impair et Négatif\n");
        }
    }
    return 0;
}
