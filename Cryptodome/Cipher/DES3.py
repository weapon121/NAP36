# uncompyle6 version 3.7.4
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.0 (v3.6.0:41df79263a11, Dec 23 2016, 08:06:12) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: lib\site-packages\Cryptodome\Cipher\DES3.py
"""
Module's constants for the modes of operation supported with Triple DES:

:var MODE_ECB: :ref:`Electronic Code Book (ECB) <ecb_mode>`
:var MODE_CBC: :ref:`Cipher-Block Chaining (CBC) <cbc_mode>`
:var MODE_CFB: :ref:`Cipher FeedBack (CFB) <cfb_mode>`
:var MODE_OFB: :ref:`Output FeedBack (OFB) <ofb_mode>`
:var MODE_CTR: :ref:`CounTer Mode (CTR) <ctr_mode>`
:var MODE_OPENPGP:  :ref:`OpenPGP Mode <openpgp_mode>`
:var MODE_EAX: :ref:`EAX Mode <eax_mode>`
"""
import sys
from Cryptodome.Cipher import _create_cipher
from Cryptodome.Util.py3compat import byte_string, bchr, bord, bstr
from Cryptodome.Util._raw_api import load_pycryptodome_raw_lib, VoidPointer, SmartPointer, c_size_t
_raw_des3_lib = load_pycryptodome_raw_lib('Cryptodome.Cipher._raw_des3', '\n                    int DES3_start_operation(const uint8_t key[],\n                                             size_t key_len,\n                                             void **pResult);\n                    int DES3_encrypt(const void *state,\n                                     const uint8_t *in,\n                                     uint8_t *out,\n                                     size_t data_len);\n                    int DES3_decrypt(const void *state,\n                                     const uint8_t *in,\n                                     uint8_t *out,\n                                     size_t data_len);\n                    int DES3_stop_operation(void *state);\n                    ')

def adjust_key_parity(key_in):
    """Set the parity bits in a TDES key.

    :param key_in: the TDES key whose bits need to be adjusted
    :type key_in: byte string

    :returns: a copy of ``key_in``, with the parity bits correctly set
    :rtype: byte string

    :raises ValueError: if the TDES key is not 16 or 24 bytes long
    :raises ValueError: if the TDES key degenerates into Single DES
    """

    def parity_byte(key_byte):
        parity = 1
        for i in range(1, 8):
            parity ^= key_byte >> i & 1

        return key_byte & 254 | parity

    if len(key_in) not in key_size:
        raise ValueError('Not a valid TDES key')
    key_out = (b'').join([bchr(parity_byte(bord(x))) for x in key_in])
    if key_out[:8] == key_out[8:16] or key_out[-16:-8] == key_out[-8:]:
        raise ValueError('Triple DES key degenerates to single DES')
    return key_out


def _create_base_cipher(dict_parameters):
    """This method instantiates and returns a handle to a low-level base cipher.
    It will absorb named parameters in the process."""
    try:
        key_in = dict_parameters.pop('key')
    except KeyError:
        raise TypeError("Missing 'key' parameter")

    key = adjust_key_parity(bstr(key_in))
    start_operation = _raw_des3_lib.DES3_start_operation
    stop_operation = _raw_des3_lib.DES3_stop_operation
    cipher = VoidPointer()
    result = start_operation(key, c_size_t(len(key)), cipher.address_of())
    if result:
        raise ValueError('Error %X while instantiating the TDES cipher' % result)
    return SmartPointer(cipher.get(), stop_operation)


def new(key, mode, *args, **kwargs):
    """Create a new Triple DES cipher.

    :param key:
        The secret key to use in the symmetric cipher.
        It must be 8 byte long. The parity bits will be ignored.
    :type key: bytes/bytearray/memoryview

    :param mode:
        The chaining mode to use for encryption or decryption.
    :type mode: One of the supported ``MODE_*`` constants

    :Keyword Arguments:
        *   **iv** (*bytes*, *bytearray*, *memoryview*) --
            (Only applicable for ``MODE_CBC``, ``MODE_CFB``, ``MODE_OFB``,
            and ``MODE_OPENPGP`` modes).

            The initialization vector to use for encryption or decryption.

            For ``MODE_CBC``, ``MODE_CFB``, and ``MODE_OFB`` it must be 8 bytes long.

            For ``MODE_OPENPGP`` mode only,
            it must be 8 bytes long for encryption
            and 10 bytes for decryption (in the latter case, it is
            actually the *encrypted* IV which was prefixed to the ciphertext).

            If not provided, a random byte string is generated (you must then
            read its value with the :attr:`iv` attribute).

        *   **nonce** (*bytes*, *bytearray*, *memoryview*) --
            (Only applicable for ``MODE_EAX`` and ``MODE_CTR``).

            A value that must never be reused for any other encryption done
            with this key.

            For ``MODE_EAX`` there are no
            restrictions on its length (recommended: **16** bytes).

            For ``MODE_CTR``, its length must be in the range **[0..7]**.

            If not provided for ``MODE_EAX``, a random byte string is generated (you
            can read it back via the ``nonce`` attribute).

        *   **segment_size** (*integer*) --
            (Only ``MODE_CFB``).The number of **bits** the plaintext and ciphertext
            are segmented in. It must be a multiple of 8.
            If not specified, it will be assumed to be 8.

        *   **mac_len** : (*integer*) --
            (Only ``MODE_EAX``)
            Length of the authentication tag, in bytes.
            It must be no longer than 8 (default).

        *   **initial_value** : (*integer*) --
            (Only ``MODE_CTR``). The initial value for the counter within
            the counter block. By default it is **0**.

    :Return: a Triple DES object, of the applicable mode.
    """
    return _create_cipher(sys.modules[__name__], key, mode, *args, **kwargs)


MODE_ECB = 1
MODE_CBC = 2
MODE_CFB = 3
MODE_OFB = 5
MODE_CTR = 6
MODE_OPENPGP = 7
MODE_EAX = 9
block_size = 8
key_size = (16, 24)