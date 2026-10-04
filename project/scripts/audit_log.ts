
import { network } from "hardhat";

const { viem } = await network.connect();

const publicClient = await viem.getPublicClient();

// Address from your existing simulation
const DATA_SHARING =
    "0x9fe46736679d2d9a65f0992f2272de9f3c7fa6e0";

// Connect to the deployed contract
const dataSharing = await viem.getContractAt(
    "DataSharing",
    DATA_SHARING
);

// Retrieve all AccessAttempt events
const logs = await publicClient.getContractEvents({
    address: dataSharing.address,
    abi: dataSharing.abi,
    eventName: "AccessAttempt",
    fromBlock: 0n,
    toBlock: "latest",
});

console.log("\nAUDIT LOG HISTORY\n");

if (logs.length === 0) {
    console.log("No access attempts found.");
}

for (const [index, log] of logs.entries()) {
    const { owner, requester, credentialHash, timestamp, granted } =
        log.args;

    console.log(`Access Attempt #${index + 1}`);
    console.log(`Owner: ${owner}`);
    console.log(`Requester: ${requester}`);
    console.log(`Credential: ${credentialHash}`);

    console.log(
        `Time: ${new Date(Number(timestamp) * 1000).toLocaleString()}`
    );

    console.log(`Result: ${granted ? "GRANTED" : "DENIED"}`);
    console.log(`Transaction: ${log.transactionHash}`);
    console.log("----------------------------------");
}

console.log(`\nTotal access attempts: ${logs.length}`);
