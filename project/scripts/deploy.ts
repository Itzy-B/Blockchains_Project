import { network } from "hardhat";

const { viem } = await network.connect();

console.log("Deploying contracts...\n");

// 1. Deploy DigitalIdentity
const digitalIdentity = await viem.deployContract("DigitalIdentity");
console.log(
    "DigitalIdentity:",
    digitalIdentity.address
);

// 2. Deploy ConsentManager
const consentManager = await viem.deployContract("ConsentManager");
console.log(
    "ConsentManager:",
    consentManager.address
);

// 3. Deploy DataSharing and connect it to ConsentManager
const dataSharing = await viem.deployContract(
    "DataSharing",
    [consentManager.address]
);
console.log(
    "DataSharing:",
    dataSharing.address
);

// 4. Deploy RewardToken and connect it to ConsentManager
const rewardToken = await viem.deployContract(
    "RewardToken",
    [consentManager.address]
);
console.log(
    "RewardToken:",
    rewardToken.address
);

console.log("\nDeployment complete.");