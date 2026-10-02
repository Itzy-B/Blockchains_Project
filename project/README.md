# Credence

Credence is a local blockchain project for academic identity and credential sharing.

Students can register an identity, add credential hashes, choose who can access a credential, and revoke access later. The actual identity and credential files stay on the computer. Only hashes, consent information, and access events are stored on the blockchain.

This README explains what is in the project and how to run each part.

## Main features

1. Students can register an identity hash.
2. Students can add academic credential hashes.
3. Students can grant a requester access for a chosen number of days.
4. Students can revoke a consent record.
5. Every access attempt is recorded, whether it is allowed or denied.
6. Students receive ACCESS reward tokens for giving consent.
7. The application shows the gas used and network fee for blockchain transactions.

## Folder guide

```text
project/
├── app.py                         Streamlit application entry point
├── contracts/                     Solidity smart contracts
│   ├── DigitalIdentity.sol         Identity and credential hash storage
│   ├── ConsentManager.sol          Consent creation and revocation
│   ├── DataSharing.sol             Access checks and audit events
│   └── RewardToken.sol             ACCESS reward token balance
├── scripts/
│   ├── deploy.ts                   Deploy all contracts locally
│   └── simulate.ts                 Run a full example workflow
├── test/                           Solidity tests
├── abi/                            Contract ABI files used by the application
├── src/identity_platform/
│   ├── gateways/                   Demo mode and blockchain connection code
│   ├── ui/                         Application pages
│   ├── hashing.py                  Hash creation for local records
│   ├── storage.py                  Local JSON record storage
│   └── models.py                   Shared data models, including gas costs
├── data/examples/                  Example data only
└── docs/                           Project notes and contract interface guide
```

## Install the project

Open PowerShell in the `project` folder.

```powershell
npm install
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If PowerShell blocks `npm`, use `npm.cmd` and `npx.cmd` instead.

```powershell
npm.cmd install
```

## Run the application in demo mode

Demo mode does not need a local blockchain. It is useful for checking the application flow.

```powershell
streamlit run app.py
```

Use Alice to register an identity and add a credential. Grant Bob access, switch to Bob, and try to access the credential. Then switch back to Alice, revoke the consent, and try the access again as Bob.

Demo mode does not show a real gas fee because no blockchain transaction is sent.

## Run the local blockchain version

First, copy `.env.example` to a new file named `.env`.

```powershell
Copy-Item .env.example .env
```

Open `.env` and set this value.

```text
APP_MODE=web3
```

Start the local Hardhat blockchain in one PowerShell window.

```powershell
npx hardhat node
```

Open a second PowerShell window in the same `project` folder. Deploy the contracts.

```powershell
npx hardhat run scripts/deploy.ts --network localhost
```

Copy the four contract addresses printed by the deployment script into `.env`.

```text
DIGITAL_IDENTITY_ADDRESS=
CONSENT_MANAGER_ADDRESS=
DATA_SHARING_ADDRESS=
REWARD_TOKEN_ADDRESS=
```

Then start the application.

```powershell
streamlit run app.py
```

The local Hardhat accounts are unlocked for this coursework project. This is fine for local testing only.

## Run the example workflow

Keep the Hardhat node running. Deploy the contracts first, then run this command in a second PowerShell window.

```powershell
npx hardhat run scripts/simulate.ts --network localhost
```

The script registers Alice, adds a credential, grants Bob access, records a successful access attempt, revokes the consent, and records a denied access attempt.

## Gas costs

Ethereum charges gas automatically when a transaction changes blockchain data. This includes registering an identity, adding a credential, granting consent, revoking consent, and attempting credential access.

After a transaction is confirmed, the application reads its receipt and calculates the real network fee.

```text
network fee in wei = gas used × effective gas price
```

The application shows the gas used, gas price, ETH fee, and wei fee after each transaction. The access page also shows the network fee for every entry in the audit log. The deployment and simulation scripts print the same information in PowerShell.

Read only functions do not create a transaction, so they do not cost gas.

## Run the tests

Compile the contracts first.

```powershell
npx hardhat compile
```

Then run the Solidity tests.

```powershell
npx hardhat test solidity
```

## Important notes

Use only fake data for this coursework project. Never put real student details or real credentials on the blockchain.

A hash proves that a record has not changed. It does not hide or encrypt the original record.

The files in `data/` are stored locally for the prototype. The blockchain only stores hashes and permission information.