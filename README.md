# pymerkle: Merkle-tree cryptographic library for generation and validation of Proofs

[![Build Status](https://travis-ci.com/FoteinosMerg/pymerkle.svg?branch=master)](https://travis-ci.com/FoteinosMerg/pymerkle)
[![codecov](https://codecov.io/gh/FoteinosMerg/pymerkle/branch/master/graph/badge.svg)](https://codecov.io/gh/FoteinosMerg/pymerkle)
[![Docs Status](https://readthedocs.org/projects/pymerkle/badge/?version=latest)](http://pymerkle.readthedocs.org)
[![PyPI version](https://badge.fury.io/py/pymerkle.svg)](https://pypi.org/project/pymerkle/)
![Python >= 3.6](https://img.shields.io/badge/python-%3E%3D%203.6-blue.svg)

**Complete documentation found at [pymerkle.readthedocs.org](http://pymerkle.readthedocs.org/)**

_Pymerkle_ provides a class for binary balanced Merkle-trees (with possibly
odd number of leaves), capable of generating Merkle-proofs (audit-proofs
and consistency-proofs) and performing inclusion-tests. It supports almost all
combinations of hash functions (including SHA3 variations) and encoding
types, with defense against second-preimage attack by default enabled.
It further provides flexible validation mechanisms, allowing for direct
verification of existence and integrity of encrypted data.

It is a zero dependency library (with the inessential exception of `tqdm`
for displaying progress bars).

## Installation [Work in progress]

**WARNING: The present version has not yet been published to the Python index.
For the moment, the following command will only install the pre-release of the
last published version (No backwards compatibility)**

```bash
pip3 install pymerkle --pre
```

## Usage

**See [_Usage_](USAGE.md)**

## Security

Enhanced security of the present implementation relies on the
tree's topology as well as the standard refinement
of the encoding procedure.

### Defense against second-preimage attack

Defense against second-preimage attack consists in the following security measures:

- Before computing the hash of a leaf, prepend the corresponding record with
the null hexadecimal `0x00`

- Before computing the hash of any interior node, prepend both of its parents'
hashes with the unit hexadecimal `0x01`

Refer to
[`tests/test_security.py`](https://github.com/FoteinosMerg/pymerkle/blob/master/tests/test_security.py)
to see how to perform second-preimage attacks
against the present implementation. In order to disable defense (say, for testing purposes),
set ``security`` equal to ``False`` at construction.

### Deviation from bitcoin specification

In contrast to the
[bitcoin](https://en.bitcoin.it/wiki/Protocol_documentation#Merkle_Trees)
specification for Merkle-trees, lonely leaves are not duplicated in order for
the tree to remain binary. Instead, creating bifurcation nodes at the
rightmost branch allows the tree to remain both binary and balanced upon any update
(see _Tree structure_ below). As a consequence, the present implementation is
structurally invulnerable to _denial-of-service attacks_ exploiting the
vulnerability described
[here](https://github.com/bitcoin/bitcoin/blob/bccb4d29a8080bf1ecda1fc235415a11d903a680/src/consensus/merkle.cpp)
(reported as [CVE-2012-2459](https://nvd.nist.gov/vuln/detail/CVE-2012-2459)).

## Tree structure

Contrary to other implementations, the present Merkle-tree remains always
binary balanced, with all nodes except for the exterior ones (leaves) having
two parents. This is attained as follows: upon appending a block of new leaves,
instead of promoting a lonely leaf to the next level or duplicating it, a
*bifurcation* node is created _so that trees with the same number of leaves
have identical structure independently of their growing strategy_.
This standardization is further crucial for:

- fast generation of consistency-proofs (based on additive decompositions in
  decreasing powers of 2)
- fast recalculation of the root-hash after appending a new leaf, since only
  the hashes at the tree's right-most branch need be recalculated
- memory efficiency, since the height as well as total number of nodes with respect
  to the tree's length is constrained to the minimum.

The topology turns out to be identical with that of a binary _Sekura tree_,
depicted in Section 5.4 of [this](https://keccak.team/files/Sakura.pdf) paper.
Follow the straightforward algorithm of the
[`.update`](https://pymerkle.readthedocs.io/en/latest/_modules/pymerkle/tree/tree.html#MerkleTree.update)
method for further insight.

_Note_: Due to the binary balanced structure of the present implementation,
the consistency-proof algorithm significantly deviates from that exposed
in [RFC 6912](https://tools.ietf.org/html/rfc6962#section-2.1.2)


## Validation

Validation of a Merkle-proof presupposes correct configuration of the client’s
hashing machinery, so that the latter coincides with that of the server. In the
nomenclature of the present implementation, this amounts to knowledge of the
tree’s hash algorithm, encoding type, raw-bytes mode and security mode, which
are inscribed in the header of any proof. The client’s machinery is
automatically configured from these parameters by just feeding the proof into
any of the available validation mechanisms.

Proof validation is agnostic of whether a Merkle-proof has been
the result of an audit or a consistency proof request.
Audit-proofs and consistency-proofs share identical structure,
so that both kinds are instances of the same class.

## Development

### Tests

You need to have installed ``pytest``.

```shell
pip install -r dev-requirements.txt
```

From inside the project's root directory type

```shell
./runtests
```

to run all tests against the limited set of encoding types UTF-8, UTF-16 and
UTF-32 (108 combinations in total). To run tests against all possible hash
types, encoding types, raw-bytes modes and security modes (3240 combinations
in total), run

```shell
./runtests --extended
```

### Benchmarks

```shell
python benchmarks
```
from inside the project's root directory.

### Documentation

Run

```shell
./dev/build-docs
```

from inside the projects root dir to build Sphinx docs for the project.
Provide `-h/--help` for more options.
