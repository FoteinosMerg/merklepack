"""
Tests validation of Merkle-proofs
"""

import pytest
import os
import json
from pymerkle.hashing import HASH_TYPES
from pymerkle import MerkleTree, validateProof, getValidationReceipt
from pymerkle.validations.validations import Receipt
from tests.config import ENCODINGS

# Setup

MAX_LENGTH = 4

trees = []
for raw_bytes in (True, False):
    for security in (True, False):
        for length in range(1, MAX_LENGTH + 1):
            for hash_type in HASH_TYPES:
                for encoding in ENCODINGS:
                # for encoding in ('utf-8', 'utf-16', 'utf-32'):
                    trees.append(
                        MerkleTree(
                            *['%d-th record' %i for i in range(length)],
                            hash_type=hash_type,
                            encoding=encoding,
                            security=security
                        )
                    )


# Audit-proof validation

__false_audit_proofs = []
__true_audit_proofs  = []

for tree in trees:

    __false_audit_proofs.extend(
        [
            (
                tree,
                tree.auditProof(-1),                                            # Based upon negative index
            ),
            (
                tree,
                tree.auditProof(tree.length),                                   # Based upon index exceeding current length
            ),
            (
                tree,
                tree.auditProof('anything that has not been recorded')          # Based upon non encrypted record
            )
        ]
    )

    for index in range(0, tree.length):
        __true_audit_proofs.extend(
            [
                (
                    tree,
                    tree.auditProof(index),                                     # Index based proof
                ),
                (
                    tree,
                    tree.auditProof('%d-th record' % index),                    # String based proof
                ),
                (
                    tree,
                    tree.auditProof(
                        bytes(
                            '%d-th record' % index,
                            tree.encoding
                        )
                    )                                                           # Bytes based proof
                )
            ]
        )

@pytest.mark.parametrize("tree, audit_proof", __false_audit_proofs)
def test_false_audit_validateProof(tree, audit_proof):
    assert not validateProof(tree.rootHash, audit_proof)

@pytest.mark.parametrize("tree, audit_proof", __true_audit_proofs)
def test_true_audit_validateProof(tree, audit_proof):
    assert validateProof(tree.rootHash, audit_proof)


# Consistency-proof validation

trees_and_subtrees = []

for tree in trees:
    for sublength in range(1, tree.length + 1):

        trees_and_subtrees.append(
            (
                tree,
                MerkleTree(
                    *['%d-th record' %_ for _ in range(sublength)],
                    hash_type=tree.hash_type,
                    encoding=tree.encoding,
                    raw_bytes=tree.raw_bytes,
                    security=tree.security
                )
            )
        )

__false_consistency_proofs = []
__true_consistency_proofs  = []

for (tree, subtree) in trees_and_subtrees:

        __false_consistency_proofs.extend(
            [
                (
                    tree,
                    tree.consistencyProof(
                        b'anything except for the right hash',
                        subtree.length
                    )                                                           # Based upon wrong target-hash
                ),
                (
                    tree,
                    tree.consistencyProof(
                        subtree.rootHash,
                        subtree.length + 1
                    )                                                           # Based upon wrong sublength
                )
            ]
        )

        __true_consistency_proofs.append(
            (
                tree,
                tree.consistencyProof(
                    subtree.rootHash,
                    subtree.length
                )
            )
        )

@pytest.mark.parametrize("tree, consistency_proof", __false_consistency_proofs)
def test_false_consistency_validateProof(tree, consistency_proof):
    assert not validateProof(tree.rootHash, consistency_proof)

@pytest.mark.parametrize("tree, consistency_proof", __true_consistency_proofs)
def test_true_consistency_validateProof(tree, consistency_proof):
    assert validateProof(tree.rootHash, consistency_proof)