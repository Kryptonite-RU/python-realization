import numpy as np
import math
import argparse
import json

from gfsr import rand_bits, gen_perm
from helpers import *


# k = 1448
# n = 2*k
# d = 137
# w = 318
# nlog = math.ceil(math.log(n,2))


# buf = []
# fname = "../GFSR/H-prime"
# with open(fname, "r") as f:
#     words = f.read().split()
#     for word in words:
#         for bit in bin(int(word, base=16))[2:].rjust(32, '0'):
#             buf.append(int(bit))
# H = np.array(buf, dtype=int)
# hash_of_file('../GFSR/H-prime_raw', "H-hash.txt")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h-path", required=True)
    parser.add_argument("--message-path", required=True)
    parser.add_argument("--params-path", required=True)
    parser.add_argument("--secret-key-path", required=True)
    parser.add_argument("--sig-path", required=True)
    args = parser.parse_args()

    params = json.load(open(args.params_path))

    k = params["k"]
    n = params["n"]
    nlog = math.ceil(math.log(n,2))

    d = params["d"]

    H = read_matrix_hex(args.h_path, (k, k))

    s = from_hex_file_to_bit_vector(args.secret_key_path)

    sig = b''

    all_u = []
    all_perms = []
    all_perms_binary = []

    f_input = b''
    for j in range(d): #1й внешний цикл, как прописано в стандарте
        #генерируем случайности
        u = rand_bits(j, n)   # u_hex = subprocess.check_output(['../GFSR/a.out'], input = '{} {}'.format(j, n).encode())
        # u = bytes_to_bit_vector(binascii.unhexlify(u_hex))
        # u = u[:n-((n+31)//32)*32] #сокращаем длину, которая из-за генератора кратна 32
        perm = gen_perm(j + d, n)
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

    with open(args.message_path, "rb") as f:
        message = f.read() # b'fedcba9876543210'
    
    f_input = message + f_input
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

    with open(args.sig_path, 'wb') as f: 
        f.write(binascii.hexlify(sig))

if __name__ == "__main__":
    main()
