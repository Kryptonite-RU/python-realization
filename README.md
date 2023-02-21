# Шиповник (Shipovnik, Rose hip) python realization

## Installation prerequisites

1. `Python 3.8`, `gcc 8.3` or higher, `git 2.22` or higher for Windows, Linux and macOS;

2. `WSL 2` for Windows. 

## Build

  1. To build GFSR, go to `GFSR` directory and execute
```
gcc -O3 GFSR.c -o GFSR
```
2. To build [pystribog library](https://github.com/ddulesov/pystribog/) follow the instructions for that repository.
  

## Execution

There are several scripts for all the necessary tasks including generating and verifying signatures, they are described below. 
**NOTE:** all generated files contain data in hex format.

### Matrix generation 

The matrix $H'$ is generated with GFSR algorithm. Execute the following command 
```
./GFSR/GFSR c90fdaa2 2096704 hex data/H-prime.hex
```

### Key generation

To generate the key, execute the following command:
```
python3 signature/key-gen.py --h-path data/H-prime.hex --params-path signature/params.json --seed 64ea04bf --secret-key-path data/secret-key.hex --public-key-path data/public-key.hex
```
The secret and public keys will be written to specified files.
Feel free to use your own seed.

### Signature generation

To generate the signature, save your message in file `data/message.txt` (or just leave the default) and execute the following command:
```
python3 signature/sig-gen.py --h-path data/H-prime.hex --params-path signature/params.json --secret-key-path data/secret-key.hex --message-path data/message.txt --sig-path data/sig.hex
```

### Signature verification

To check the signature, execute the following command:
```
python3 signature/sig-ver.py --h-path data/H-prime.hex --params-path signature/params.json --public-key-path data/public-key.hex --message-path data/message.txt --sig-path data/sig.hex
```

If the signature for the message is correst, one can see the line "The signature does work!" on the standard output. Otherwise the programm throws an exception and writes clarifying message about the first error that occurred.

All the algorithms rely on the function library contained in the file `helpers.py`.

### Computing a hash

We are using pystribog [library](https://github.com/ddulesov/pystribog/) for computing the Stribog hash function.
To compute the hash, execute the following command:
```
python3 signature/hash.py --path data/H-prime.hex --type 512 --hash-path data/H-prime.hash
```

**NOTE:** the contents of a file are expected to be in hex format.

### Moving to tex-format

To make latex table items of form `& \texttt{smth}, & ` execute the folowing command with your options: 

```
python3 signature/to_tex.py --in-file .\data\u_d-1.txt --out-file .\data\u_d-1.tex --groups-in-row 7
```
 