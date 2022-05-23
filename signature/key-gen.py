import argparse
import json

from helpers import *
from gfsr import gen_perm

# k = 1448
# n = 2*k
# d = 137
# w = 318
# nlog = math.ceil(math.log(n,2))

def secret_key_gen(seed, n, w):
    s = [1 for i in range(w)]
    s = s + [0 for i in range(n-w)]
    # local_perm = gen_perm(0xadf85459)
    local_perm = gen_perm(seed, n)
    s = permute(s, local_perm)
    return np.array(s, dtype=int)

# buf = []
# fname = "../GFSR/H-prime"
# with open(fname, "r") as f:
#     words = f.read().split()
#     for word in words:
#         for bit in bin(int(word, base=16))[2:].rjust(32, '0'):
#             buf.append(int(bit))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h-path", required=True)
    parser.add_argument("--params-path", required=True)
    parser.add_argument("--seed", required=True, type=lambda s: int(s, 16))
    parser.add_argument("--secret-key-path", required=True)
    parser.add_argument("--public-key-path", required=True)
    args = parser.parse_args()

    params = json.load(open(args.params_path))

    k = params["k"]
    H = read_matrix_hex(args.h_path, (k, k))

    s = secret_key_gen(args.seed, params["n"], params["w"])
    to_file(s, args.secret_key_path)

    y = mul(H, s)
    to_file(y, args.public_key_path)


if __name__ == "__main__":
    main()
