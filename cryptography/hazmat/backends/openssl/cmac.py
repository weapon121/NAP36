# uncompyle6 version 3.7.4
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.0 (v3.6.0:41df79263a11, Dec 23 2016, 08:06:12) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: lib\site-packages\cryptography\hazmat\backends\openssl\cmac.py
from __future__ import absolute_import, division, print_function
from cryptography import utils
from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm, _Reasons
from cryptography.hazmat.primitives import constant_time, mac
from cryptography.hazmat.primitives.ciphers.modes import CBC

@utils.register_interface(mac.MACContext)
class _CMACContext(object):

    def __init__(self, backend, algorithm, ctx=None):
        if not backend.cmac_algorithm_supported(algorithm):
            raise UnsupportedAlgorithm('This backend does not support CMAC.', _Reasons.UNSUPPORTED_CIPHER)
        self._backend = backend
        self._key = algorithm.key
        self._algorithm = algorithm
        self._output_length = algorithm.block_size // 8
        if ctx is None:
            registry = self._backend._cipher_registry
            adapter = registry[(type(algorithm), CBC)]
            evp_cipher = adapter(self._backend, algorithm, CBC)
            ctx = self._backend._lib.CMAC_CTX_new()
            self._backend.openssl_assert(ctx != self._backend._ffi.NULL)
            ctx = self._backend._ffi.gc(ctx, self._backend._lib.CMAC_CTX_free)
            key_ptr = self._backend._ffi.from_buffer(self._key)
            res = self._backend._lib.CMAC_Init(ctx, key_ptr, len(self._key), evp_cipher, self._backend._ffi.NULL)
            self._backend.openssl_assert(res == 1)
        self._ctx = ctx

    algorithm = utils.read_only_property('_algorithm')

    def update(self, data):
        res = self._backend._lib.CMAC_Update(self._ctx, data, len(data))
        self._backend.openssl_assert(res == 1)

    def finalize(self):
        buf = self._backend._ffi.new('unsigned char[]', self._output_length)
        length = self._backend._ffi.new('size_t *', self._output_length)
        res = self._backend._lib.CMAC_Final(self._ctx, buf, length)
        self._backend.openssl_assert(res == 1)
        self._ctx = None
        return self._backend._ffi.buffer(buf)[:]

    def copy(self):
        copied_ctx = self._backend._lib.CMAC_CTX_new()
        copied_ctx = self._backend._ffi.gc(copied_ctx, self._backend._lib.CMAC_CTX_free)
        res = self._backend._lib.CMAC_CTX_copy(copied_ctx, self._ctx)
        self._backend.openssl_assert(res == 1)
        return _CMACContext((self._backend),
          (self._algorithm), ctx=copied_ctx)

    def verify(self, signature):
        digest = self.finalize()
        if not constant_time.bytes_eq(digest, signature):
            raise InvalidSignature('Signature did not match digest.')