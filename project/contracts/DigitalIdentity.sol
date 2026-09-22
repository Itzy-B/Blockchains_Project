// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title Digital Identity Registry
/// @notice Stores only identity and credential hashes. Plaintext records remain off-chain.
contract DigitalIdentity {

    // identityHash: a 32-byte fingerprint of their off-chain identity record.
    // registered: whether that Ethereum address has registered.
    struct Identity {
        bytes32 identityHash;
        bool registered;
    }

    // This connects an Ethereum wallet to an identity:
    mapping(address => Identity) private identities;

    // Each student can have multiple credentials:
    mapping(address => bytes32[]) private credentialHashes;

    // Does this exact credential hash already exist for this student?
    mapping(address => mapping(bytes32 => bool)) private credentialExists;

    // This creates a blockchain log/events when someone registers.
    event UserRegistered(address indexed user, bytes32 indexed identityHash);
    event CredentialAdded(address indexed owner, bytes32 indexed credentialHash);

    // | Error                         | Meaning                                                   |
    // | ----------------------------- | --------------------------------------------------------- |
    // | AlreadyRegistered             | The wallet has already registered an identity.            |
    // | NotRegistered                 | The wallet tried adding a credential without an identity. |
    // | EmptyHash                     | An empty bytes32 value was submitted.                     |
    // | CredentialAlreadyRegistered   | The same credential was submitted twice.                  |
    error AlreadyRegistered();
    error NotRegistered();
    error EmptyHash();
    error CredentialAlreadyRegistered();

    /// @notice Register the caller's identity hash once. The student calls this using their Ethereum wallet.
    function registerUser(bytes32 identityHash) external {
        // This prevents a wallet from registering twice.
        if (identities[msg.sender].registered) revert AlreadyRegistered();
        // This prevents an empty identity hash.
        if (identityHash == bytes32(0)) revert EmptyHash();

        // The caller’s wallet becomes connected to the supplied hash.
        identities[msg.sender] = Identity({
            identityHash: identityHash,
            registered: true
        });

        // A permanent blockchain event is created.
        emit UserRegistered(msg.sender, identityHash);
    }

    /// @notice Add a credential hash owned by the caller. A registered student calls this with their credential hash.
    function addCredential(bytes32 credentialHash) external {
        // Only registered identities can add credentials.
        if (!identities[msg.sender].registered) revert NotRegistered();
        // An empty credential cannot be added.
        if (credentialHash == bytes32(0)) revert EmptyHash();
        // The same student cannot register the same credential twice.
        if (credentialExists[msg.sender][credentialHash]) {
            revert CredentialAlreadyRegistered();
        }
        // Marks the credential as existing.
        credentialExists[msg.sender][credentialHash] = true;
        // Adds it to the student’s credential list.
        credentialHashes[msg.sender].push(credentialHash);

        // This creates the registration event.
        emit CredentialAdded(msg.sender, credentialHash);
    }

    // This returns the identity hash and registration status of any address. view means it only reads the blockchain. It does not change anything and does not create a transaction when called locally.
    // The UI uses this to show: Identity: Registered | Identity hash: 0x...
    function getIdentity(address user) external view returns (bytes32 identityHash, bool registered) {
        Identity memory identity = identities[user];
        return (identity.identityHash, identity.registered);
    }

    // This provides a simpler yes or no registration check.
    function isRegistered(address user) external view returns (bool) {
        return identities[user].registered;
    }

    // This returns every credential hash registered by a student. The Python UI uses it to display the student’s credential list.Memory means the returned array is temporarily copied for the function response. It does not modify permanent contract storage.
    function getCredentialHashes(address user) external view returns (bytes32[] memory) {
        return credentialHashes[user];
    }

    // This checks whether a particular credential belongs to a particular wallet. The consent contract could use this before allowing someone to grant consent for a credential.
    function hasCredential(address user, bytes32 credentialHash) external view returns (bool) {
        return credentialExists[user][credentialHash];
    }
}

