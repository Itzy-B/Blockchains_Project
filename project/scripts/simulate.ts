import { network } from "hardhat";
import { formatEther, keccak256, toBytes, type Hash } from "viem";
const { viem } = await network.connect();

const publicClient = await viem.getPublicClient();
const [alice, bob] = await viem.getWalletClients();

// Addresses from deployment
const DIGITAL_IDENTITY = "0x5fbdb2315678afecb367f032d93f642f64180aa3";
const CONSENT_MANAGER = "0xe7f1725e7734ce288f8367e1bb143e90bb3f0512";
const DATA_SHARING = "0x9fe46736679d2d9a65f0992f2272de9f3c7fa6e0";
const REWARD_TOKEN = "0xcf7ed3acca5a467e9e704c703e8d87f634fb0fc9";

console.log("\n=== CREDENTIAL SHARING SIMULATION ===\n");

console.log("Alice:", alice.account.address);
console.log("Bob:  ", bob.account.address);

// Get deployed contracts
const digitalIdentity = await viem.getContractAt(
    "DigitalIdentity",
    DIGITAL_IDENTITY
);
const consentManager = await viem.getContractAt(
    "ConsentManager",
    CONSENT_MANAGER
);
const dataSharing = await viem.getContractAt(
    "DataSharing",
    DATA_SHARING
);
const rewardToken = await viem.getContractAt(
    "RewardToken",
    REWARD_TOKEN
);

async function confirmAndShowCost(label: string, transaction: Promise<Hash>) {
    const hash = await transaction;
    const receipt = await publicClient.waitForTransactionReceipt({ hash });
    const feeWei = receipt.gasUsed * receipt.effectiveGasPrice;
    console.log(`   ${label} gas used: ${receipt.gasUsed.toString()}`);
    console.log(`   ${label} network fee: ${formatEther(feeWei)} ETH (${feeWei.toString()} wei)`);
    return receipt;
}

// 1. Alice registers her identity
const identityHash = keccak256(
    toBytes("alice_identity.json")
);

console.log("\n1. Alice registers her identity...");

await confirmAndShowCost(
    "Registration",
    digitalIdentity.write.registerUser([identityHash], { account: alice.account })
);

console.log("   Identity registered.");

// 2. Alice registers her degree credential
const credentialHash = keccak256(
    toBytes("alice_degree.json")
);

console.log("\n2. Alice registers her degree credential...");

await confirmAndShowCost(
    "Credential registration",
    digitalIdentity.write.addCredential([credentialHash], { account: alice.account })
);

console.log("   Credential registered.");

// 3. Alice grants Bob access for 30 days
console.log("\n3. Alice grants Bob access for 30 days...");

await confirmAndShowCost(
    "Consent grant",
    consentManager.write.grantConsent(
        [bob.account.address, credentialHash, 30n],
        { account: alice.account }
    )
);

console.log("   Consent granted.");

// 4. Check Alices access reward
const reward = await rewardToken.read.balanceOf([
    alice.account.address
]);

const decimals = await rewardToken.read.decimals();

const readableReward =
    Number(reward) / 10 ** Number(decimals);

console.log(
    "\n4. Alice reward balance:",
    readableReward,
    "ACCESS"
);

// 5. Bob accesses Alices credential
console.log("\n5. Bob attempts to access Alice's credential...");

await confirmAndShowCost(
    "Granted access",
    dataSharing.write.accessData([alice.account.address, credentialHash], {
        account: bob.account,
    })
);

console.log("   Access attempt completed.");
console.log("   Expected result: GRANTED");

// 6. Alice revokes consent #0
console.log("\n6. Alice revokes Bob's consent...");

await confirmAndShowCost(
    "Consent revocation",
    consentManager.write.revokeConsent([0n], { account: alice.account })
);

console.log("   Consent revoked.");

// 7. Bob attempts access again
console.log("\n7. Bob attempts access after revocation...");

await confirmAndShowCost(
    "Denied access",
    dataSharing.write.accessData([alice.account.address, credentialHash], {
        account: bob.account,
    })
);

console.log("   Access attempt completed.");
console.log("   Expected result: DENIED");

console.log("\n=== SIMULATION COMPLETE ===\n");
