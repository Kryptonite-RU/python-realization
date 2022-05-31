from functools import reduce
import random
import numpy as np
import _pystribog
import binascii
import math

h_512_obj = _pystribog.StribogHash( _pystribog.Hash512 )
h_256_obj = _pystribog.StribogHash( _pystribog.Hash256 )

def h_512(s):
    assert isinstance(s, bytes)
    h_512_obj.clear()
    h_512_obj.update(s)
    return h_512_obj.digest()

def h_256(s):
    assert isinstance(s, bytes)
    h_256_obj.clear()
    h_256_obj.update(s)
    return h_256_obj.digest()


def permute(x, perm):
    n = len(perm)
    res = [0 for i in range(n)]
    for i in range(n):
        t = perm[i] 
        res[i] = x[t] 
    return res


def print_s_to_pdf(s, n):
    str_s =''.join(str(e) for e in s)
    hex_str_s = ''
    count = 0
    hex_str_s += '\\texttt{'
    for i in range(n//4): 
        hex_str_s += hex(int(str_s[4*i: 4*i+4],2))[2:]
        if (count+1) % 56 == 0:
            hex_str_s += '} \\\\ \n\\texttt{' 
        elif (count+1) % 8 == 0:
            hex_str_s += '} & \\texttt{' 
        count += 1
    hex_str_s += '} \\\\'
    print(hex_str_s)

def string_to_bytes(s,b): 
    if b == 16:
        assert len(s) % 2 == 0
        return bytes.fromhex(s) 
    else:
        return int(s, b).to_bytes(len(s) // 8, byteorder='big')

def bin_to_hex_string(str_s): 
    hex_str_s = '' 
    n = len(str_s)
    for i in range(n//4): 
        hex_str_s += hex(int(str_s[4*i: 4*i+4],2))[2:] 
    return hex_str_s  

def print_s_to_byte_file(s):
    str_s =''.join(str(e) for e in s)
    hex_str_s = bin_to_hex_string(str_s, len(str_s))
    with open('s_bin', 'wb') as output:
        output.write(bytearray(int(i, 16) for i in hex_str_s)) 

def bit_vector_to_bytes(v):
    """
        np.array([1,0,0,0,0,0,0,0]) -> b'\x80'
    """
    assert len(v) % 8 == 0
    packed = np.packbits(v, bitorder='big')
    return bytes(packed.tolist())


def bytes_to_bit_vector(v):
    """
        b'\x80' -> np.array([1,0,0,0,0,0,0,0]) 
    """
    return np.unpackbits(np.frombuffer(v, dtype=np.uint8), bitorder='big').astype(int)


def read_matrix_hex(fname, shape):
    with open(fname, "r") as f:
        hex_str = f.read()
    bytes_ = string_to_bytes(hex_str, 16)
    vec = bytes_to_bit_vector(bytes_)
    return np.reshape(vec, shape)

 
def permutation_to_bytes(perm, nlog):
    """
        [3,2,1,0] -> np.array([1,1|1,0|0,1|0,0]) -> b'\xe4'
    """
    perm_bin = np.array([
        [int(i) for i in bin(x)[2:].rjust(nlog, '0')]
        for x in perm
    ], dtype=int)
    return bit_vector_to_bytes(perm_bin.flatten(order='C'))

def bit_vector_to_permutation(vec, nlog):
    """
        [1,1|1,0|0,1|0,0] -> [[1,1],[1,0],[0,1],[0,0]] @ [2,1] -> [3,2,1,0]
    """
    assert len(vec) % nlog == 0
    M = vec.reshape((-1, nlog), order="C").astype(int)
    powers = 2**np.arange(nlog-1,-1,-1) # [2**(nlog-1), ..., 1]
    return M @ powers

def mul(mat, x):
    k = len(x) // 2
    # H = mat.reshape(k,k)
    x_left = x[:k]
    x_right = x[k:]
    res = np.dot(mat, x_left) + x_right 
    bin_res = list([res[i] % 2 for i in range(len(res))]) 
    return bin_res

def invert_notation(x): 
    if x < 3:
        return str(x) 
    return str(x % 3) + invert_notation(x // 3)
 
def to_ternary(x):
    return invert_notation(x)[::-1]

def to_file(x, file_name):
    with open(file_name, "wb") as f: 
        f.write(binascii.hexlify(bit_vector_to_bytes(x))) 

def from_hex_file_to_bytes(filename):
    with open(filename, "rb") as f:
        return binascii.unhexlify(f.read()) 

def from_hex_file_to_bit_vector(filename):
    res = from_hex_file_to_bytes(filename)
    return bytes_to_bit_vector(res)   

def bytes_to_int(byte_vec):
    res = 0
    for i in range(len(byte_vec)):
        res += byte_vec[i] * 256**i
    return res

def F(f_input, d):
    f = h_512(f_input)
    f = int(binascii.hexlify(f), 16)*3**d  
    f = f >> 512 
    f = to_ternary(f).rjust(d,'0')
    return f

def hash_of_file(filename_in, filename_out, type="512"):
    with open(filename_in, "rb") as f_in:
        message_hex = f_in.read()
        message = binascii.unhexlify(message_hex)
    with open(filename_out, "wb") as f_out:
        if type == "256":
            h_fun = h_256
        elif type == "512":
            h_fun = h_512
        else:
            assert False, "Expected \"256\" or \"512\""
        h = h_fun(message)        
        f_out.write(binascii.hexlify(h))


def perm_to_file(perm, file_name):
    with open(file_name, "w") as f:
        for i in range(len(perm)): 
            f.write('\\texttt{')
            f.write(str(perm[i]))
            f.write('}, ')
