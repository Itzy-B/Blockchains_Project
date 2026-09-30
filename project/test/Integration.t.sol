// Author / component owner: Eirini Papaioannou (i6389716)
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {DigitalIdentity} from "../contracts/DigitalIdentity.sol";
import {ConsentManager} from "../contracts/ConsentManager.sol";
import {DataSharing} from "../contracts/DataSharing.sol";

interface Vm {
    function prank(address) external;
}

contract IntegrationTest {
    Vm constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));
    DigitalIdentity identity;
    ConsentManager consentManager;
    DataSharing dataSharing;

    address constant ALICE = address(0xA11CE);
    address constant BOB = address(0xB0B);

    bytes32 constant IDENTITY_HASH = keccak256("alice.identity");
    bytes32 constant CREDENTIAL_HASH = keccak256("alice.degree");

    function setUp() public {
        // Deploying all the contracts required for the workflow.
        identity = new DigitalIdentity();
        consentManager = new ConsentManager();
        // Connect DataSharing to ConsentManager.
        dataSharing = new DataSharing(address(consentManager));
    }

    function testCompleteCredentialSharingWorkflow() public {
        // 1. Alice registers her identity.
        vm.prank(ALICE);
        identity.registerUser(IDENTITY_HASH);
        require(identity.isRegistered(ALICE));

        // 2. Alice registers her credential (a degree for example).
        vm.prank(ALICE);
        identity.addCredential(CREDENTIAL_HASH);
        require(
            identity.hasCredential(ALICE, CREDENTIAL_HASH)
        );

        // 3. Alice gives Bob access for 30 days.
        vm.prank(ALICE);
        uint256 consentId =
            consentManager.grantConsent(
                BOB,
                CREDENTIAL_HASH,
                30
            );
        require(
            consentManager.hasValidConsent(
                ALICE,
                BOB,
                CREDENTIAL_HASH
            )
        );

        // 4. Bob requests the credential.
        vm.prank(BOB);
        bool granted =
            dataSharing.accessData(
                ALICE,
                CREDENTIAL_HASH
            );
        require(granted);

        // 5. Alice revokes Bobs consent.
        vm.prank(ALICE);
        consentManager.revokeConsent(consentId);
        require(
            !consentManager.hasValidConsent(
                ALICE,
                BOB,
                CREDENTIAL_HASH
            )
        );

        // 6. Bob tries to access it again after revocation.
        vm.prank(BOB);
        bool grantedAfterRevocation =
            dataSharing.accessData(
                ALICE,
                CREDENTIAL_HASH
            );
        require(!grantedAfterRevocation);
    }
}