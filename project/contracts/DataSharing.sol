// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

///@title IConsentManager
///@notice Interface used to check whether a requester has valid consent
/// to access a specific credential.
interface IConsentManager{
    function hasValidConsent(
        address owner,
        address requester,
        bytes32 credentialHash
    ) external view returns (bool);
}

/// @title Credentials Access Control
///@notice Controls access to credentials based on the recorded consent in ConsentManager.
///@dev The function should every log every access attempt through the AccessAttempt event, 
/// including both granted and denied attempts.
contract DataSharing{
    ///@dev Immutable, since the ConsentManager address is set once during deployment.
    IConsentManager public immutable consentManager;

    ///@notice Thrown when the zero address is provided as the ConsentManager
    error InvalidConsentManager();

    event AccessAttempt(
        address indexed owner,
        address indexed requester,
        bytes32 indexed credentialHash,
        uint256 timestamp,
        bool granted
    );

    ///@notice Sets the ConsentManager contract used by DataSharing.
    constructor(address _consentManager){
        if (_consentManager == address(0)) {
            // Reject the zero address
            revert InvalidConsentManager();
        }

        consentManager = IConsentManager(_consentManager);
    }

    ///@notice Attempts to access a credential.
    ///@dev Once identifying the requester using msg.sender, the function asks
    /// ConsentManager whether the requester has valid consent for the specified credential.
    /// Granted and denied attempts are recorded using the AccessAttempt event. Denied access does 
    /// not revert, allowing the failed attempt to remain in the blockchain event log.
    function accessData(
        address owner, 
        bytes32 credentialHash
    ) external returns (bool granted){

        //Identifying requester from the sender
        address requester = msg.sender;

        //Checking whether the requester has valid consent
        granted = consentManager.hasValidConsent(
            owner,
            requester,
            credentialHash
        );
        
        //Record attempt in the audit trail
        emit AccessAttempt(
            owner,
            requester,
            credentialHash,
            block.timestamp,
            granted
        );

        //If access was granted, returns true (otherwise, returns false)
        return granted;
    }
}