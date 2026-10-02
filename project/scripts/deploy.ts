import { network } from "hardhat";
import { formatEther, type Hash } from "viem";

const { viem } = await network.connect();
const publicClient = await viem.getPublicClient();

console.log("Deploying contracts...\n");

async function deployWithCost(name: string, args: unknown[] = []) {
    // Gas is paid automatically by the deployment wallet. The receipt gives
    // the final, exact fee after the contract has been created.
    const deployment = await viem.sendDeploymentTransaction(name, args);
    const receipt = await publicClient.waitForTransactionReceipt({
        hash: deployment.deploymentTransaction.hash as Hash,
    });
    const feeWei = receipt.gasUsed * receipt.effectiveGasPrice;

    console.log(`${name}:`, deployment.contract.address);
    console.log(`  Gas used: ${receipt.gasUsed.toString()}`);
    console.log(`  Deployment fee: ${formatEther(feeWei)} ETH (${feeWei.toString()} wei)`);
    return deployment.contract;
}

// 1. Deploy DigitalIdentity
const digitalIdentity = await deployWithCost("DigitalIdentity");

// 2. Deploy ConsentManager
const consentManager = await deployWithCost("ConsentManager");

// 3. Deploy DataSharing and connect it to ConsentManager
const dataSharing = await deployWithCost(
    "DataSharing",
    [consentManager.address]
);

// 4. Deploy RewardToken and connect it to ConsentManager
const rewardToken = await deployWithCost(
    "RewardToken",
    [consentManager.address]
);

console.log("\nDeployment complete.");
