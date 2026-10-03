import { network } from "hardhat";
import { keccak256, toBytes, type Hash } from "viem";

const { viem } = await network.connect();

const publicClient = await viem.getPublicClient();
const wallets = await viem.getWalletClients();

const USER_COUNTS = [1, 5, 10];

async function executeTransaction(
    transaction: Promise<Hash>
): Promise<bigint> {
    const hash = await transaction;

    const receipt = await publicClient.waitForTransactionReceipt({
        hash,
    });

    return receipt.gasUsed;
}

console.log("\n=== SCALABILITY TEST ===\n");

for (const userCount of USER_COUNTS) {

    // Fresh contracts for every test size so we know for sure that each experiment starts from the same state.
    const digitalIdentity =
        await viem.deployContract("DigitalIdentity");

    const consentManager =
        await viem.deployContract("ConsentManager");

    const dataSharing =
        await viem.deployContract("DataSharing", [
            consentManager.address,
        ]);

    let totalGas = 0n;

    const startTime = performance.now();

    for (let i = 0; i < userCount; i++) {

        const owner = wallets[i];
        const requester = wallets[(i + 1) % wallets.length];
        const identityHash = keccak256(
            toBytes(`scale_identity_${userCount}_${i}`)
        );
        const credentialHash = keccak256(
            toBytes(`scale_credential_${userCount}_${i}`)
        );

        // 1. Reg identity
        totalGas += await executeTransaction(
            digitalIdentity.write.registerUser(
                [identityHash],
                { account: owner.account }
            )
        );

        // 2. Reg credential
        totalGas += await executeTransaction(
            digitalIdentity.write.addCredential(
                [credentialHash],
                { account: owner.account }
            )
        );

        // 3. Grant consent
        totalGas += await executeTransaction(
            consentManager.write.grantConsent(
                [
                    requester.account.address,
                    credentialHash,
                    30n,
                ],
                { account: owner.account }
            )
        );

        // 4. Requester accesses credential
        totalGas += await executeTransaction(
            dataSharing.write.accessData(
                [
                    owner.account.address,
                    credentialHash,
                ],
                { account: requester.account }
            )
        );
    }

    const endTime = performance.now();
    const totalTimeSeconds = (endTime - startTime) / 1000;
    const averageGasPerUser = totalGas / BigInt(userCount);
    const averageTimePerUser = totalTimeSeconds / userCount;

    console.log(`--- ${userCount} USER(S) ---`);
    console.log(`Total gas: ${totalGas.toString()}`);
    console.log(`Average gas per user: ${averageGasPerUser.toString()}` );
    console.log( `Total execution time: ${totalTimeSeconds.toFixed(3)} seconds` );
    console.log( `Average time per user: ${averageTimePerUser.toFixed(3)} seconds` );
    console.log("");
}

console.log("=== SCALABILITY TEST COMPLETE ===");