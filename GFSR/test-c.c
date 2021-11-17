#include<stdio.h>
#include <stdint.h>

int main(){
    uint32_t s = 0xc90fdaa2; 
    s >>= 16;
    printf("%04x\n", s);
    return 0;
}