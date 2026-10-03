import { network } from "hardhat";
import { keccak256, toBytes, type Hash } from "viem";

const { viem } = await network.connect();
const publicClient = await viem.getPublicClient();
const wallets = await viem.getWalletClients();

// 10 runs for now
const RUNS = 10;

// Creating new contracts for the benchmark
console.log("\nCreating fresh contracts for gas benchmark...");

const digitalIdentity = await viem.deployContract("DigitalIdentity");
const consentManager = await viem.deployContract("ConsentManager");

const dataSharing = await viem.deployContract("DataSharing", [
    consentManager.address,
]);

console.log("Contracts deployed!!");
console.log(`Running each benchmark ${RUNS} times...\n`);

const results: Record<string, bigint[]> = {
    registration: [],
    credentialRegistration: [],
    consentGrant: [],
    grantedAccess: [],
    consentRevocation: [],
    deniedAccess: [],
};

async function gasUsed(transaction: Promise<Hash>): Promise<bigint> {
    const hash = await transaction;
    const receipt = await publicClient.waitForTransactionReceipt({ hash });
    return receipt.gasUsed;
}

for (let i = 0; i < RUNS; i++) {
    // Going through the Hardhat accounts.
    const owner = wallets[i % wallets.length];
    const requester = wallets[(i + 1) % wallets.length];

    const identityHash = keccak256(
        toBytes(`benchmark_identity_${i}`)
    );

    const credentialHash = keccak256(
        toBytes(`benchmark_credential_${i}`)
    );

    // Reg identithy
    results.registration.push(
        await gasUsed(
            digitalIdentity.write.registerUser(
                [identityHash],
                { account: owner.account }
            )
        )
    );

    // Credential reg
    results.credentialRegistration.push(
        await gasUsed(
            digitalIdentity.write.addCredential(
                [credentialHash],
                { account: owner.account }
            )
        )
    );

    // Grant consent
    results.consentGrant.push(
        await gasUsed(
            consentManager.write.grantConsent(
                [requester.account.address, credentialHash, 30n],
                { account: owner.account }
            )
        )
    );

    // Determine the consent id that was just created
    const consentIds =
        await consentManager.read.getOwnerConsentIds([
            owner.account.address,
        ]);

    const consentId = consentIds[consentIds.length - 1];

    // Granted access
    results.grantedAccess.push(
        await gasUsed(
            dataSharing.write.accessData(
                [owner.account.address, credentialHash],
                { account: requester.account }
            )
        )
    );

    // Revoke consent
    results.consentRevocation.push(
        await gasUsed(
            consentManager.write.revokeConsent(
                [consentId],
                { account: owner.account }
            )
        )
    );

    // Denied access after revoking
    results.deniedAccess.push(
        await gasUsed(
            dataSharing.write.accessData(
                [owner.account.address, credentialHash],
                { account: requester.account }
            )
        )
    );

    console.log(`Run ${i + 1}/${RUNS} complete`);
}

function average(values: bigint[]): bigint {
    return values.reduce((sum, value) => sum + value, 0n)
        / BigInt(values.length);
}

console.log("\n=== AVERAGE GAS RESULTS ===\n");

console.log(
    "Identity registration:",
    average(results.registration).toString()
);

console.log(
    "Credential registration:",
    average(results.credentialRegistration).toString()
);

console.log(
    "Consent grant:",
    average(results.consentGrant).toString()
);

console.log(
    "Granted access:",
    average(results.grantedAccess).toString()
);

console.log(
    "Consent revocation:",
    average(results.consentRevocation).toString()
);

console.log(
    "Denied access:",
    average(results.deniedAccess).toString()
);

console.log("\n=== BENCHMARK COMPLETE ===");