# Шиповник (Shipovnik, Rose hip) python realization

Currently signature is formed for a test message *m_test*, that is hard-coded in both _sig-gen.py_ and _sig-ver.py_.

**Key generation algorithm**

Is currently implemented in _sig-gen.py_.
Secret key is generated with function _secret_key_gen()_.
Public key is generated with function _mul(H, s)_, where *s* is the secret key and *H* is a public parameter, generated with *gfsr5()* function from GOST R ISO 28640-2012.
The output is saved in files _secret-key.txt_ and _public-key.txt_, respectively.

**Signature generation algorithm**

Is implemented in _sig-gen.py_. The signature for the test message is saved in the file _signature.txt_.

**Signature verification algorithm**

Is implemented in _sig-ver.py_. If the signature for the test message is correst, one can see line 
> The signature does work!

on the standard output. Otherwise the programm throws an exception and writes clarifying message about the first error that occurred.

Both algorithms rely on the function library contained in the file _"helpers.py"_.

We are using pystribog [library](https://github.com/ddulesov/pystribog/).


**Additional information**

*  All generated files contain data in hex-format.
*  Public parameter *H'* generation is possible with function *form_mat()* that can be found in *GFSR.c*. 
*  As a subprogram *GFSR.c* given *seed* and number *n* outputs *x* random bits, where *x* is minimum multiple of 32 that is at least n.
*  To calculate the hash value of one of the generated files one can use function *hash_of_file()* from *helpers.py*.
