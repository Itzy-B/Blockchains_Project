// Author / component owner: Ilgaz Mehmetoglu (i6385148)
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import {ConsentManager} from "../contracts/ConsentManager.sol";

// Hardhat's Solidity test runner supplies these test-only controls.
interface Vm {
    function prank(address) external;
    function warp(uint256) external;
    function expectRevert(bytes4) external;
    function expectRevert(bytes calldata) external;
}

contract ConsentManagerTest {
    Vm constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));
    ConsentManager manager;
    address constant OWNER = address(0xA11CE);
    address constant REQUESTER = address(0xB0B);
    bytes32 constant HASH = keccak256("synthetic.degree");

    function setUp() public { manager = new ConsentManager(); }
    function grant(uint256 days_) internal returns (uint256) {
        vm.prank(OWNER);
        return manager.grantConsent(REQUESTER, HASH, days_);
    }
    function valid() internal view returns (bool) {
        return manager.hasValidConsent(OWNER, REQUESTER, HASH);
    }

    // This is the exact permission lifecycle needed by the access component.
    function testGrantAccessRevokeDeny() public {
        require(!valid());
        uint256 id = grant(1);
        require(valid());
        vm.prank(OWNER);
        manager.revokeConsent(id);
        require(!valid());
    }
    // Permission ends at the exact expiry second, with no cleanup transaction.
    function testExpiryBoundary() public {
        uint256 end = block.timestamp + 1 days;
        grant(1);
        vm.warp(end - 1);
        require(valid());
        vm.warp(end);
        require(!valid());
    }
    // A caller cannot withdraw a record belonging to another owner.
    function testUnauthorizedRevocation() public {
        uint256 id = grant(1);
        vm.expectRevert(ConsentManager.NotConsentOwner.selector);
        vm.prank(REQUESTER);
        manager.revokeConsent(id);
        require(valid());
    }
    // Changing any tuple field must not inherit access.
    function testTupleIsolation() public {
        grant(1);
        require(!manager.hasValidConsent(REQUESTER, REQUESTER, HASH));
        require(!manager.hasValidConsent(OWNER, OWNER, HASH));
        require(!manager.hasValidConsent(OWNER, REQUESTER, bytes32(uint256(1))));
    }
    // IDs are stable; the six returned fields match the UI's tuple order.
    function testHistoryAndIndependentDuplicates() public {
        uint256 first = grant(1);
        uint256 second = grant(365);
        vm.prank(OWNER);
        manager.revokeConsent(first);
        require(valid());
        uint256[] memory ids = manager.getOwnerConsentIds(OWNER);
        require(ids.length == 2 && ids[0] == first && ids[1] == second);
        (address owner, address requester, bytes32 hash, uint256 start, uint256 end, bool revoked) = manager.getConsent(first);
        require(owner == OWNER && requester == REQUESTER && hash == HASH);
        require(start == block.timestamp && end == start + 1 days && revoked);
        vm.prank(OWNER);
        manager.revokeConsent(second);
        require(!valid());
    }
    // Reject durations immediately outside the allowed inclusive range.
    function testInvalidDurations() public {
        vm.expectRevert(ConsentManager.InvalidDuration.selector);
        grant(0);
        vm.expectRevert(ConsentManager.InvalidDuration.selector);
        grant(366);
    }
    // Invalid identifiers cannot become usable permissions.
    function testInvalidInputs() public {
        vm.expectRevert(ConsentManager.InvalidRequester.selector);
        manager.grantConsent(address(0), HASH, 1);
        vm.expectRevert(ConsentManager.InvalidCredentialHash.selector);
        manager.grantConsent(REQUESTER, bytes32(0), 1);
    }
    // Unknown IDs and repeated revocation fail rather than silently succeeding.
    function testMissingAndRepeatedRevocation() public {
        vm.expectRevert(abi.encodeWithSelector(ConsentManager.ConsentNotFound.selector, uint256(0)));
        manager.revokeConsent(0);
        vm.expectRevert(abi.encodeWithSelector(ConsentManager.ConsentNotFound.selector, uint256(0)));
        manager.getConsent(0);
        uint256 id = grant(1);
        vm.prank(OWNER);
        manager.revokeConsent(id);
        vm.expectRevert(ConsentManager.AlreadyRevoked.selector);
        vm.prank(OWNER);
        manager.revokeConsent(id);
    }
}
