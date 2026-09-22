# Data model and storage decisions

| Attribute | On-chain | Off-chain | Hashed |
|---|---:|---:|---:|
| Ethereum address | Yes | Referenced | No |
| Student name | No | Yes | Yes, inside identity hash |
| Email | No | Yes | Yes, inside identity hash |
| Student ID | No | Yes | Yes, inside both record hashes |
| University | No | Yes | Yes |
| Degree / programme | No | Yes | Yes |
| Complete credential record | No | Yes | Yes |
| Identity hash | Yes | Stored with local record | Already hashed |
| Credential hash | Yes | Stored with local record | Already hashed |
| Consent information | Yes | No | No |
| Access audit events | Yes | No | No |

## Hashing strategy

The Python application converts selected record fields to canonical JSON (sorted keys,
compact separators, UTF-8), then calculates SHA-256. The result is a 32-byte value and
is passed to Solidity as `bytes32`. Storage metadata such as `created_at` is excluded so
moving or re-saving an unchanged academic record does not change its hash.

This prototype uses local JSON files for off-chain storage, as permitted by the project
plan. The `JsonRecordStore` class isolates that decision so it can later be replaced by
IPFS or a database without changing UI pages or smart-contract calls.

## Ownership rule

The `DigitalIdentity` contract always uses `msg.sender` as the owner. A caller cannot
register an identity or credential for another address, and each credential hash is
accepted only once per owner.

