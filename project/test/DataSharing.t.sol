// Author / component owner: Eirini Papaioannou (i6389716)
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ConsentManager} from "../contracts/ConsentManager.sol";
import {DataSharing} from "../contracts/DataSharing.sol";

interface Vm {
    function prank(address) external;
    function warp(uint256) external;
    function expectRevert(bytes4) external;
    function expectEmit(
        bool checkTopic1,
        bool checkTopic2,
        bool checkTopic3,
        bool checkData
    ) external;
}

contract DataSharingTest {
    Vm constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));
    ConsentManager consentManager;
    DataSharing dataSharing;

    address constant OWNER = address(0xA11CE);
    address constant REQUESTER = address(0xB0B);
    address constant OTHER = address(0xCAFE);

    bytes32 constant CREDENTIAL_HASH = keccak256("alice.degree");

    event AccessAttempt(
        address indexed owner,
        address indexed requester,
        bytes32 indexed credentialHash,
        uint256 timestamp,
        bool granted
    );

    function setUp() public {
        // Consent contract first.
        consentManager = new ConsentManager();
        // DataSharing needs to know which ConsentManager to use.
        dataSharing = new DataSharing(address(consentManager));
    }

    // Without consent access has to be denied.
    function testAccessDeniedWithoutConsent() public {
        vm.prank(REQUESTER);
        bool granted = dataSharing.accessData(OWNER, CREDENTIAL_HASH);
        require(!granted);
    }

    // A requester with valid consent should get access.
    function testAccessGrantedWithValidConsent() public {
        vm.prank(OWNER);
        consentManager.grantConsent(
            REQUESTER,
            CREDENTIAL_HASH,
            30
        );

        vm.prank(REQUESTER);
        bool granted = dataSharing.accessData(OWNER, CREDENTIAL_HASH);
        require(granted);
    }

    // Revoking consent should cause preveously given access to be denied.
    function testAccessDeniedAfterRevocation() public {
        vm.prank(OWNER);
        uint256 consentId =
            consentManager.grantConsent(
                REQUESTER,
                CREDENTIAL_HASH,
                30
            );

        vm.prank(OWNER);
        consentManager.revokeConsent(consentId);

        vm.prank(REQUESTER);
        bool granted = dataSharing.accessData(OWNER, CREDENTIAL_HASH);
        require(!granted);
    }

    // Expired consent cant keep giving access.
    function testAccessIsDeniedAfterExpiryDate() public {
        vm.prank(OWNER);
        consentManager.grantConsent(
            REQUESTER,
            CREDENTIAL_HASH,
            1
        );

        vm.warp(block.timestamp + 1 days);

        vm.prank(REQUESTER);
        bool granted = dataSharing.accessData(OWNER, CREDENTIAL_HASH);
        require(!granted);
    }

    // Consent belongs only to the requester specified by the owner.
    function testDifferentRequesterIsDenied() public {
        vm.prank(OWNER);
        consentManager.grantConsent(
            REQUESTER,
            CREDENTIAL_HASH,
            30
        );

        vm.prank(OTHER);
        bool granted = dataSharing.accessData(OWNER, CREDENTIAL_HASH);
        require(!granted);
    }

    // DataSharing must reject an invalid ConsentManager address.
    function testInvalidConsentManagerAddressFails() public {
        vm.expectRevert(
            DataSharing.InvalidConsentManager.selector
        );
        new DataSharing(address(0));
    }

    // A denied access attempt should still be recorded in the audit history.
    function testDeniedAccessEmitsAuditEvent() public {
        vm.expectEmit(true, true, true, true);
        emit AccessAttempt(
            OWNER,
            REQUESTER,
            CREDENTIAL_HASH,
            block.timestamp,
            false
        );

        vm.prank(REQUESTER);
        bool granted = dataSharing.accessData(OWNER, CREDENTIAL_HASH);
        require(!granted);
    }

    
}