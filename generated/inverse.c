#include <stdio.h>

int main() {
    int inverse, n, reste;
    printf("Entrez un nombre : \n");
    scanf("%d", &n);
    inverse = 0;
    while ((n > 0)) {
        reste = (n % 10);
        inverse = ((inverse * 10) + reste);
        n = (n / 10);
    }
    printf("Sortie : %d\n", inverse);
    return 0;
}
