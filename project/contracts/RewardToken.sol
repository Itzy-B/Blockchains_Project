// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

///@title Reward Token
///@notice Read-only ERC-20 style reward balance for consent sharing.
///@dev Each consent granted by a student represents 10 ACCESS tokens.
/// Rewards are derived from ConsentManager's records. Revoking or expiring
/// consent does not remove an earned reward.
interface IConsentManager {
    function getOwnerConsentIds(
        address owner
    ) external view returns (uint256[] memory);

    function getConsent(
        uint256 consentId
    ) external view returns (
        address owner,
        address requester,
        bytes32 credentialHash,
        uint256 startTime,
        uint256 expiryTime,
        bool revoked
    );
}

contract RewardToken{
    IConsentManager public immutable consentManager;

    ///@notice Thrown when the zero address is provided as the ConsentManager
    error InvalidConsentManager();
    
    uint256 private constant REWARD = 10 ether;

    ///@notice Creates a reward token interface
    constructor(address _consentManager){
        if (_consentManager == address(0)) {
            // Reject the zero address
            revert InvalidConsentManager();
        }

        consentManager = IConsentManager(_consentManager);
    }

    ///@notice Returns the student's earned ACCESS reward balance.
    ///@dev Every consent created by a student is worth 10 ACCESS, granted
    /// once the consent is created.
    function balanceOf(address account) external view returns (uint256) {
        uint256[] memory consentIds = consentManager.getOwnerConsentIds(account);
        return consentIds.length * REWARD;
    }

    ///@notice Returns the number of decimal places used by ACCESS for the UI.
    function decimals() external pure returns(uint8) {
        // Standard precision used by ERC-20 tokens
        return 18;
    }

    ///@notice Returns the token symbol that the UI will display as a label.
    function symbol() external pure returns (string memory) {
        return "ACCESS";
    }
}