# Contract interface required by the frontend

The frontend depends on these public functions and events. Teammates may implement the
internal logic however they choose, but names, argument order, and return types should
match the ABI files in `abi/`.

## DigitalIdentity (your component)

- `registerUser(bytes32 identityHash)`
- `addCredential(bytes32 credentialHash)`
- `getIdentity(address) returns (bytes32, bool)`
- `isRegistered(address) returns (bool)`
- `getCredentialHashes(address) returns (bytes32[])`

## ConsentManager

- `grantConsent(address requester, bytes32 credentialHash, uint256 durationDays)`
- `revokeConsent(uint256 consentId)`
- `hasValidConsent(address owner, address requester, bytes32 credentialHash)`
- `getOwnerConsentIds(address owner) returns (uint256[])`
- `getConsent(uint256 consentId) returns (address, address, bytes32, uint256, uint256, bool)`

Duration is expressed in days. The contract is responsible for enforcing 1–365 days.
The last two read functions are required to display consent history in the UI.

## DataSharing

- `accessData(address owner, bytes32 credentialHash) returns (bool granted)`
- Emits `AccessAttempt(owner, requester, credentialHash, timestamp, granted)` for both
  successful and failed access attempts.

Important: denied access must not revert. A reverted transaction removes its event, so
the project could not keep the required immutable log of failed attempts.

## RewardToken

- `balanceOf(address) returns (uint256)`
- `decimals() returns (uint8)`
- `symbol() returns (string)`

This is the standard read-only ERC-20 interface needed by the UI.

