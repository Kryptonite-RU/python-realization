#from functools import reduce
#from os import RTLD_LAZY
#import random
import numpy as np
import _pystribog
import binascii
import math
import subprocess
 
from helpers import *
 

#np.random.seed(4)
#random.seed(3)

k = 1448  
n = 2*k
d = 137  
nlog = math.ceil(math.log(n,2))

#m_test = np.random.randint(0, 2, 15)

def rand_num(seed, size):
    rand_num_hex = subprocess.check_output(['../GFSR/a.out'], input = '{} {}'.format(seed, 32 * size).encode())
    b = binascii.unhexlify(rand_num_hex)
    return np.array([bytes_to_int(b[4*i:4*i+4]) for i in range(size)], dtype=np.int64)

def shuffle(seed, vec):
    rand_nums = rand_num(seed, len(vec) - 2)
    for i in range(len(vec)-2): 
        r = rand_nums[i] * (len(vec) - i) // 2**32
        j = i + r
        tmp = vec[i]
        vec[i] = vec[j]
        vec[j] = tmp
    return vec   

def gen_perm(seed):
    perm = list(range(n))
    shuffle(seed, perm) 
    return np.array(perm, dtype=int)

def secret_key_gen(): 
    s = [1 for i in range(d)]
    s = s + [0 for i in range(n-d)]
    local_perm = gen_perm(0xadf85459)
    s = permute(s, local_perm) 
    return np.array(s, dtype=int) 

buf = []
fname = "../GFSR/H-prime"
with open(fname, "r") as f:
    words = f.read().split()
    for word in words:
        for bit in bin(int(word, base=16))[2:].rjust(32, '0'):
            buf.append(int(bit))
H = np.array(buf, dtype=int)
hash_of_file('../GFSR/H-prime_raw', "H-hash.txt")


sig = b''

s = secret_key_gen()
to_file(s, 'secret-key.txt') 

y = mul(H, s) 
to_file(y, 'public-key.txt')
 

all_u = []
all_perms = []
all_perms_binary = []

f_input = b''
for j in range(d): #1й внешний цикл, как прописано в стандарте

    #генерируем случайности 
    #u = np.random.randint(0, 2, n)
    u_hex = subprocess.check_output(['../GFSR/a.out'], input = '{} {}'.format(j, n).encode())
    u = bytes_to_bit_vector(binascii.unhexlify(u_hex)) 
    u = u[:n-((n+31)//32)*32] #сокращаем длину, которая из-за генератора кратна 32
    perm = gen_perm(j+d)
    all_u.append(u)
    all_perms.append(perm)
    all_perms_binary.append([bin(perm[i])[2:].rjust(nlog, '0') for i in range(n)])    

    s_u = permute(u, perm) 
    u_plus_s = [u[i] ^ s[i] for i in range(n)] 
    s_uplus_s = permute(u_plus_s, perm)
 
    #вычисляем произведение Hu^T 
    Hu = mul(H, u)  
    assert len(Hu) % 8 == 0

    #генерируем аргументы хэш-функции
    prec0 = permutation_to_bytes(perm, nlog) + bit_vector_to_bytes(Hu) 
    prec1 = bit_vector_to_bytes(s_u)  
    prec2 = bit_vector_to_bytes(s_uplus_s)  

    #вычисляем три хэш-значения 
    c0 = h_512(prec0)    
    c1 = h_512(prec1)  
    c2 = h_512(prec2) 
    f_input = f_input + c0 + c1 + c2  
    sig = sig + c0 + c1 + c2  


m_test = b'fedcba9876543210' 
f_input = m_test + f_input  
f = F(f_input, d)  


for fj, u, perm in zip(f, all_u, all_perms):
    if fj == '0':   
        str_u = bit_vector_to_bytes(u) 
        str_sigma = permutation_to_bytes(perm, nlog)   
        sig = sig + str_sigma + str_u  
    if fj == '1': 
        us = u ^ s 
        str_us = bit_vector_to_bytes(us)  
        str_sigma = permutation_to_bytes(perm, nlog)  
        sig = sig + str_sigma + str_us 
    if fj == '2': 
        s_u = permute(u, perm)
        str_u = bit_vector_to_bytes(s_u) 
        s_s = permute(s, perm)  
        str_s = bit_vector_to_bytes(s_s)  
        sig = sig + str_u + str_s  
 

f = open('signature.txt', 'wb') 
f.write(binascii.hexlify(sig))
f.close()
# hash_of_file('signature.txt', 'sig-hash.txt')
