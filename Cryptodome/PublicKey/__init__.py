# uncompyle6 version 3.7.4
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.0 (v3.6.0:41df79263a11, Dec 23 2016, 08:06:12) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: lib\site-packages\Cryptodome\PublicKey\__init__.py
from Cryptodome.Util.asn1 import DerSequence, DerInteger, DerBitString, DerObjectId, DerNull

def _expand_subject_public_key_info(encoded):
    """Parse a SubjectPublicKeyInfo structure.

    It returns a triple with:
        * OID (string)
        * encoded public key (bytes)
        * Algorithm parameters (bytes or None)
    """
    spki = DerSequence().decode(encoded, nr_elements=2)
    algo = DerSequence().decode((spki[0]), nr_elements=(1, 2))
    algo_oid = DerObjectId().decode(algo[0])
    spk = DerBitString().decode(spki[1]).value
    if len(algo) == 1:
        algo_params = None
    else:
        try:
            DerNull().decode(algo[1])
            algo_params = None
        except:
            algo_params = algo[1]

    return (
     algo_oid.value, spk, algo_params)


def _create_subject_public_key_info(algo_oid, secret_key, params=None):
    if params is None:
        params = DerNull()
    spki = DerSequence([
     DerSequence([
      DerObjectId(algo_oid),
      params]),
     DerBitString(secret_key)])
    return spki.encode()


def _extract_subject_public_key_info(x509_certificate):
    """Extract subjectPublicKeyInfo from a DER X.509 certificate."""
    certificate = DerSequence().decode(x509_certificate, nr_elements=3)
    tbs_certificate = DerSequence().decode((certificate[0]), nr_elements=(range(6, 11)))
    index = 5
    try:
        tbs_certificate[0] + 1
        version = 1
    except TypeError:
        version = DerInteger(explicit=0).decode(tbs_certificate[0]).value
        if version not in (2, 3):
            raise ValueError('Incorrect X.509 certificate version')
        index = 6

    return tbs_certificate[index]