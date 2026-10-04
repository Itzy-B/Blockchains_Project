// Author / component owner: Ilgaz Mehmetoglu (i6385148)
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title Consent & Permission component for the team's credential-sharing UI
/// @author Ilgaz Mehmetoglu (i6385148)
/// @notice Minimal consent lifecycle matching the frontend interface.
contract ConsentManager {
    // Field order matches the six values consumed by Web3Gateway.owner_consents.
    // Only wallet addresses, hashes and timestamps belong on chain, never records.
    struct Consent {
        address owner;
        address requester;
        bytes32 credentialHash;
        uint256 startTime;
        uint256 expiryTime;
        bool revoked;
    }

    // Array positions are consent IDs, starting at zero like the demo backend.
    // Keep old entries for history; revocation must not delete or renumber them.
    Consent[] private consents;
    mapping(address => uint256[]) private ownerConsentIds;

    // Index only matching grants so checks do not scan unrelated owners' history.
    mapping(address => mapping(address => mapping(bytes32 => uint256[]))) private matchingIds;

    error InvalidRequester();
    error InvalidCredentialHash();
    error InvalidDuration();
    error NotConsentOwner();
    error AlreadyRevoked();
    event ConsentGranted(uint256 indexed consentId, address indexed owner, address indexed requester, bytes32 credentialHash, uint256 expiryTime);
    event ConsentRevoked(uint256 indexed consentId, address indexed owner);
    error ConsentNotFound(uint256 consentId);

    /// @notice Grant access to one credential for 1–365 whole days.
    /// @dev The signing wallet is the owner. Repeated grants have independent IDs,
    /// matching the demo backend. This method does not mint rewards.
    function grantConsent(
        address requester,
        bytes32 credentialHash,
        uint256 durationDays
    ) external returns (uint256 consentId) {
        if (requester == address(0)) revert InvalidRequester();
        if (credentialHash == bytes32(0)) revert InvalidCredentialHash();
        if (durationDays < 1 || durationDays > 365) revert InvalidDuration();
        consentId = consents.length;
        uint256 expiryTime = block.timestamp + durationDays * 1 days;
        consents.push(Consent(msg.sender, requester, credentialHash, block.timestamp, expiryTime, false));
        ownerConsentIds[msg.sender].push(consentId);
        matchingIds[msg.sender][requester][credentialHash].push(consentId);
        emit ConsentGranted(consentId, msg.sender, requester, credentialHash, expiryTime);
    }

    /// @notice Withdraw this specific grant; its history remains available.
    /// @dev Only its owner can revoke it. Other active grants remain valid.
    function revokeConsent(uint256 consentId) external {
        if (consentId >= consents.length) revert ConsentNotFound(consentId);
        Consent storage consent = consents[consentId];
        if (consent.owner != msg.sender) revert NotConsentOwner();
        if (consent.revoked) revert AlreadyRevoked();
        consent.revoked = true;
        emit ConsentRevoked(consentId, msg.sender);
    }

    /// @notice True if any matching grant is unrevoked and strictly before expiry.
    /// @dev this is called from DataSharing using the authenticated requester.
    /// This read does not log access or release files. DataSharing must log both
    /// outcomes without reverting denied attempts. The matching history scan is
    /// sufficient for the local prototype; it is not bounded for production use.
    function hasValidConsent(
        address owner,
        address requester,
        bytes32 credentialHash
    ) external view returns (bool) {
        uint256[] storage ids = matchingIds[owner][requester][credentialHash];
        for (uint256 i = ids.length; i > 0; i--) {
            Consent storage consent = consents[ids[i - 1]];
            if (!consent.revoked && block.timestamp < consent.expiryTime) return true;
        }
        return false;
    }

    /// @notice Returns IDs for the owner's consent-history screen.
    function getOwnerConsentIds(address owner) external view returns (uint256[] memory) {
        return ownerConsentIds[owner];
    }

    /// @notice Reads one historical record in the exact frontend ABI field order.
    function getConsent(uint256 consentId) external view returns (
        address owner,
        address requester,
        bytes32 credentialHash,
        uint256 startTime,
        uint256 expiryTime,
        bool revoked
    ) {
        if (consentId >= consents.length) revert ConsentNotFound(consentId);
        Consent storage consent = consents[consentId];
        return (
            consent.owner, consent.requester, consent.credentialHash,
            consent.startTime, consent.expiryTime, consent.revoked
        );
    }
}
