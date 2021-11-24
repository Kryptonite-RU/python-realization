#include <stdio.h>
#include <stdint.h>

#define P 521
#define Q1 86
#define Q2 197
#define Q3 447
#define W 32
/* Q1 < Q2 < Q3 */
/* W должно быть степенью 2 */
static uint32_t state[P] ;
static int state_i; 
void init_gfsr5(uint32_t s)
{
    int i, j, k;
    static uint32_t x[P];
    s &= 0xffffffffUL; 

    for (i=0 ; i<P ; i++) {
        x[i] = s >> 31 ;
        s = 1664525UL * s + 1UL ;
        s &= 0xffffffffUL;
    }
    for (k=0, i=0 ; i < P ; i++) {
        state[i] = 0UL ;
        for (j=0 ; j < W ; j++) {
            state[i] <<= 1 ;
            state[i] |= x [k ];
            x[k] ^= x[(k+Q1) %P] ^ x[(k+Q2) %P] ^ x[ (k+Q3) % P];
            k++;
            if (k==P) k = 0;
        }
    }
    state_i = 0;
}

uint32_t gfsr5(void)
{
    int i ;
    uint32_t *p0, *p1, *p2, *p3;

    if (state_i >= P) {
        state_i = 0;
        p0 = state;
        p1 = state + Q1;
        p2 = state + Q2;
        p3 = state + Q3;
        for (i=0 ; i<(P-Q3); i++)
            *p0++ ^= *p1++ ^ *p2++ ^ *p3++;
        p3 = state;
        for (; i<(P-Q2); i++)
            *p0++ ^= *p1++ ^ *p2++ ^ *p3++;
        p2 = state;
        for (; i<(P-Q1); i++)
            *p0++ ^= *p1++ ^ *p2++ ^ *p3++;
        p1 = state;
        for (; i<P ; i++)
            *p0++ ^= *p1++ ^ *p2++ ^ *p3++;
    }
    return state[state_i++];
} 

void form_mat(uint32_t s){
    init_gfsr5(s);
    FILE *f = fopen("H-prime","w");
    FILE *f_bin = fopen("H-prime_bin","w"); 
    FILE *f_raw = fopen("H-prime_raw","w"); 
    for (int i = 0; i < 65522; i++){
        uint32_t x = gfsr5();
        fprintf(f_raw, "%08x", x);
        fwrite(&x, sizeof(x), 1, f_bin);
        if ((i+1) % 8 == 0){ 
            fprintf(f, "\n");
        } else {
            fprintf(f, " ");
        }
    }
    fclose(f);
    fclose(f_bin);
    fclose(f_raw);
}

void form_key(uint32_t s){
    init_gfsr5(s);
    FILE *f = fopen("s","w");
    FILE *f_bin = fopen("s_bin","w"); 
    FILE *f_raw = fopen("s_raw","w"); 
    int my_max = 91;
    for (int i = 0; i < my_max; i++){
        uint32_t x = gfsr5();
        fprintf(f, "\\texttt{%08x}", x);
        if (i == my_max - 1){
            x >>= 16; 
            // ВНИМАНИЕ!!! при других параметрах константа изменится!
            // она соответствует лишнему числу бит, полученному в результате генерации 32-битных последовательностей
            fprintf(f_raw, "%04x", x);
            fwrite(&x, 16, 1, f_bin); 
            // ВНИМАНИЕ!!! тоже обратить внимание на константу
        }
        else{
            fprintf(f_raw, "%08x", x);
            fwrite(&x, sizeof(x), 1, f_bin);
        }
        if ((i+1) % 7 == 0){ 
            fprintf(f, " \\\\ \n");
        } else {
            fprintf(f, " & ");
        }
    }
    fclose(f);
    fclose(f_bin);
    fclose(f_raw);
}

int div_up(int x, int y)
{
    return (x + y - 1) / y;
}

int main()
{
    //uint32_t s = 0xc90fdaa2; 
    //form_mat(s);
    ////uint32_t s = 0xaaaaaaaa; 
    ////form_key(s);
    uint32_t s;
    int n;
    scanf("%d %d", &s, &n);
    init_gfsr5(s); 
    int end = div_up(n,32);
    for (int i = 0; i < end; i++){
        uint32_t x = gfsr5();
        printf("%08x", x); 
    } 
    return 0;
}