// Author / component owner: Eirini Papaioannou (i6389716)
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {DigitalIdentity} from "../contracts/DigitalIdentity.sol";

// Hardhat's Solidity test runner supplies these test-only controls.
interface Vm {
    function prank(address) external;
    function expectRevert(bytes4) external;
}

contract DigitalIdentityTest {
    Vm constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));
    DigitalIdentity identity;

    address constant ALICE = address(0xA11CE);
    address constant BOB = address(0xB0B);

    bytes32 constant IDENTITY_HASH = keccak256("alice.identity");
    bytes32 constant CREDENTIAL_HASH = keccak256("alice.degree");

    function setUp() public {
        identity = new DigitalIdentity();
    }

    // A wallet should be able to register an identity and retrieve it afterwards.
    function testRegisterIdentity() public {
        vm.prank(ALICE);
        identity.registerUser(IDENTITY_HASH);
        require(identity.isRegistered(ALICE));

        (bytes32 storedHash, bool registered) = identity.getIdentity(ALICE);

        require(registered);
        require(storedHash == IDENTITY_HASH);
    }

    // That same wallet shouldnt be able to register a second identity.
    function testDuplicateRegistrationFails() public {
        vm.prank(ALICE);
        identity.registerUser(IDENTITY_HASH);
        vm.expectRevert(DigitalIdentity.AlreadyRegistered.selector);
        vm.prank(ALICE);
        identity.registerUser(keccak256("another.identity"));
    }

    // An empty identity hash cant be allowed to register.
    function testEmptyIdentityHashFails() public {
        vm.expectRevert(DigitalIdentity.EmptyHash.selector);
        vm.prank(ALICE);
        identity.registerUser(bytes32(0));
    }

    // A already registered student must be able to register a credential.
    function testAddCredential() public {
        vm.prank(ALICE);
        identity.registerUser(IDENTITY_HASH);

        vm.prank(ALICE);
        identity.addCredential(CREDENTIAL_HASH);

        require(identity.hasCredential(ALICE, CREDENTIAL_HASH));

        bytes32[] memory credentials = identity.getCredentialHashes(ALICE);

        require(credentials.length == 1);
        require(credentials[0] == CREDENTIAL_HASH);
    }

    // An unregistered wallet isnt allowed to add a credential.
    function testUnregisteredUserCantAddCredential() public {
        vm.expectRevert(DigitalIdentity.NotRegistered.selector);
        vm.prank(BOB);
        identity.addCredential(CREDENTIAL_HASH);
    }

    // Empty credential hashes are rejected.
    function testEmptyCredentialHashFails() public {
        vm.prank(ALICE);
        identity.registerUser(IDENTITY_HASH);
        vm.expectRevert(DigitalIdentity.EmptyHash.selector);
        vm.prank(ALICE);
        identity.addCredential(bytes32(0));
    }

    // That same credential cant be registered twice by one student.
    function testDuplicateCredentialFails() public {
        vm.prank(ALICE);
        identity.registerUser(IDENTITY_HASH);

        vm.prank(ALICE);
        identity.addCredential(CREDENTIAL_HASH);

        vm.expectRevert(
            DigitalIdentity.CredentialAlreadyRegistered.selector
        );
        vm.prank(ALICE);
        identity.addCredential(CREDENTIAL_HASH);
    }

    // Credential ownership should be isolated between different wallets.
    function testCredentialOwnershipIsolation() public {
        vm.prank(ALICE);
        identity.registerUser(IDENTITY_HASH);

        vm.prank(ALICE);
        identity.addCredential(CREDENTIAL_HASH);

        require(identity.hasCredential(ALICE, CREDENTIAL_HASH));
        require(!identity.hasCredential(BOB, CREDENTIAL_HASH));
    }
}