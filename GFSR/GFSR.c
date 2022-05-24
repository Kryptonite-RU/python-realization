#include <stdio.h>
#include <stdint.h>
#include <string.h>

enum Format {
    FormatTex,
    FormatBinary,
    FormatHex
};

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

void generate(uint32_t seed, int n_bytes, enum Format format, FILE* f) {
    init_gfsr5(seed);
    int n_words = (n_bytes + 3) / 4;
    int leftover_bytes = n_bytes % 4;
    for (int i = 0; i < n_words; i++){
        uint32_t x = gfsr5();
        int cur_bytes;
        if (i == n_words - 1 && leftover_bytes != 0) {
            cur_bytes = leftover_bytes;
            x >>= (32 - 8 * leftover_bytes);
        } else {
            cur_bytes = 4;
        }
        switch (format) {
            case FormatBinary:
                fwrite(&x, cur_bytes, 1, f);
                break;
            case FormatHex:
                fprintf(f, "%0*x", cur_bytes * 2, x);
                break;
            case FormatTex:
                fprintf(f, "\\texttt{%0*x}", cur_bytes * 2, x);
                if ((i+1) % 7 == 0){
                    fprintf(f, " \\\\ \n");
                } else {
                    fprintf(f, " & ");
                }
                break;
        }
    }
}

int main(int argc, char** argv)
{
    if (argc != 5) {
        fprintf(stderr, "USAGE: %s <seed in hex> <num of rand bits> <format> <out-file>\n", argv[0]);
        return 1;
    }

    uint32_t seed;
    sscanf(argv[1], "%x", &seed);

    int n_bits;
    sscanf(argv[2], "%d", &n_bits);
    if (n_bits % 8 != 0) {
        fprintf(stderr, "Number of bits must be a multiple of 8, got %d\n", n_bits);
        return 1;
    }

    int n_bytes = n_bits / 8;

    enum Format format;
    const char* format_str = argv[3];
    if (strcmp(format_str, "tex") == 0) {
        format = FormatTex;
    } else if (strcmp(format_str, "binary") == 0) {
        format = FormatBinary;
    } else if (strcmp(format_str, "hex") == 0) {
        format = FormatHex;
    } else {
        fprintf(stderr, "Format must be one of \"tex\", \"binary\" or \"hex\", got \"%s\"\n", format_str);
        return 1;
    }

    FILE* f = fopen(argv[4], "w");
    if (!f) {
        fprintf(stderr, "Cannot open %s for writing", argv[4]);
        return 1;
    }
    generate(seed, n_bytes, format, f);

    //uint32_t s = 0xc90fdaa2;
    //form_mat(s);
    //uint32_t s = 0xaaaaaaaa;
    //form_key(s);
    //
    //uint32_t s;
    //int n;
    //scanf("%d %d", &s, &n);
    //init_gfsr5(s);
    //int end = div_up(n,32);
    //for (int i = 0; i < end; i++){
    //    uint32_t x = gfsr5();
    //    printf("%08x", x);
    //}
    return 0;
}
