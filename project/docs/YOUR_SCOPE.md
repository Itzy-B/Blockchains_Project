# Your completed project responsibility

## 1. Identity and data

- Define identity and academic credential fields.
- Document which values are on-chain, off-chain, or hashed.
- Canonicalize and hash off-chain records with SHA-256.
- Store prototype plaintext records as local JSON.
- Implement `DigitalIdentity.sol` for registration and credential hashes.

## 2. Frontend and contract integration

- Identity registration screen.
- Credential registration and listing screen.
- Consent granting, history, expiry status, and revocation screen.
- Requester access screen with granted/denied feedback.
- Immutable access-event table.
- Reward-token balance screen.
- Demo backend for working before other contracts are finished.
- Web3 backend for the final local Hardhat deployment.

## Explicitly not your responsibility

- Implementing `ConsentManager.sol`, `DataSharing.sol`, or `RewardToken.sol`.
- Unit or integration tests owned by the testing teammate.
- Deployment scripts, gas measurements, or scalability experiments.
- Fixing another contract's internal logic when it does not match the agreed ABI.

## What teammates must give you

1. A contract matching `TEAM_INTERFACE.md`.
2. Its Hardhat-generated ABI if it differs from the provided ABI file.
3. Its local deployed address.

After those three items are supplied, put the address in `.env` and replace the
corresponding ABI JSON if necessary. The UI itself should not need to be rewritten.

