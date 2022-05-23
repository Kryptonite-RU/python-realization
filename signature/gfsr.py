import pathlib
import subprocess
import tempfile
import os
import shutil
import binascii
import numpy as np

from helpers import bytes_to_bit_vector, bytes_to_int


CUR_DIR = pathlib.Path(__file__).parent.resolve()
GFSR_PATH = CUR_DIR.parent / 'GFSR' / 'GFSR'


def _rand_hex(seed, size):
    try:
        tmp_dir = tempfile.mkdtemp()
        tmp_f_name = pathlib.Path(tmp_dir) / 'output'
        subprocess.check_output([GFSR_PATH, hex(seed)[2:], str(size), "hex", tmp_f_name])
        with open(tmp_f_name) as f:
            return f.read()
    finally:
        shutil.rmtree(tmp_dir)


def rand_num(seed, size):
    rand_num_hex = _rand_hex(seed, 32 * size)
    b = binascii.unhexlify(rand_num_hex)
    return np.array([bytes_to_int(b[4*i:4*i+4]) for i in range(size)], dtype=np.int64)


def rand_bits(seed, size):
    rand_num_hex = _rand_hex(seed, size)
    u = bytes_to_bit_vector(binascii.unhexlify(rand_num_hex))
    assert len(u) == size
    return u


def shuffle(seed, vec):
    rand_nums = rand_num(seed, len(vec) - 2)
    for i in range(len(vec)-2):
        r = rand_nums[i] * (len(vec) - i) // 2**32
        j = i + r
        tmp = vec[i]
        vec[i] = vec[j]
        vec[j] = tmp
    return vec


def gen_perm(seed, n):
    perm = list(range(n))
    shuffle(seed, perm)
    return np.array(perm, dtype=int)
        