#include<stdio.h>
#include<string.h>
#include<stdint.h>

//#define TEST 1

#ifdef TEST

#define H_SIZE 64// bits (but in reality stores in bytes)
#define S_SIZE 16// bits
#define S_HALF_SIZE  8// bits
#define H_NAME "H-test" 
#define S_NAME "s-test"  
#define Y_NAME "y_bin-test"  
#define Y_PRINT "y-test" 

#else

#define H_SIZE  2096704   //bits (but in reality stores in bytes)
#define S_SIZE  2896      //bits
#define S_HALF_SIZE  1448      //bits
#define H_NAME "H-prime_bin"  
#define S_NAME "s_bin"
#define Y_NAME "y_bin"
#define Y_PRINT "y" 

#endif


const uint8_t Hbuffer[H_SIZE/8];
const uint8_t sbuffer[S_SIZE/8];

int rows = H_SIZE/S_HALF_SIZE;
int cols = S_HALF_SIZE;


int main(){
    FILE *fH = fopen(H_NAME,"r");  
    if (!fH) {
        printf("123");
        return 1;
    }
    FILE *fs = fopen(S_NAME,"r");  
    if (!fs) {
        printf("456");
        return 1;
    }
    fread(Hbuffer, H_SIZE/8, 1, fH);
    fread(sbuffer, S_SIZE/8, 1, fs);

    uint8_t res[rows/8];
    for (int i = 0; i < sizeof(res); ++i){
        res[i] = sbuffer[S_HALF_SIZE/8+i];
    }
    uint8_t short_s[S_HALF_SIZE/8];
    for (int i = 0; i < sizeof(short_s); ++i){
        short_s[i] = sbuffer[i];
    }
    
    int k = 0; 
    for(int i = 0; i < rows; ++i){
        uint8_t local_sum = 0;
        for (int j = 0; j < cols/8; ++j){
            //printf("%02x %02x\n", Hbuffer[i*cols/8 + j], short_s[j]);
            local_sum ^= Hbuffer[i*cols/8 + j] & short_s[j];
        }
        //printf("%02x\n", local_sum);
        uint8_t tmp_vec = 0; 
        tmp_vec = (uint8_t)(((__builtin_popcount(local_sum) % 2)) << (7-k));
        res[i/8] ^= tmp_vec;
        if (k == 7){
            k = 0; 
        } else {
            k++;
        } 
    }

    FILE *f1 = fopen(Y_NAME,"w"); 
    FILE *f2 = fopen(Y_PRINT,"w"); 
    fprintf(f2, "\\texttt{");
    for(int i = 0; i < sizeof(res); ++i){ 
        fprintf(f2, "%02x", res[i]); 
        if ((i+1) % 28 == 0){ 
            fprintf(f2, "} \\\\ \n\\texttt{");
        } else if ((i+1) % 4 == 0) {
            fprintf(f2, "} & \\texttt{");
        }
    } 
    fprintf(f2, "}");
    fclose(f1);
    fclose(f2); 
    return 0;
}