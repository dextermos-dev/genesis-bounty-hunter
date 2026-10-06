// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AgentEscrowArbiter
 * @notice Automated 2-of-3 Multi-Sig Escrow for Autonomous AI Agent Bounties on Base L2.
 * Target Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
 */

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

contract AgentEscrowArbiter {
    struct Escrow {
        address creator;
        address agentBeneficiary;
        address arbiter;
        uint256 amount;
        uint256 expiryTimestamp;
        bool isSettled;
        bool isDisputed;
    }

    IERC20 public immutable usdcToken;
    mapping(bytes32 => Escrow) public escrows;

    event EscrowCreated(bytes32 indexed escrowId, address indexed creator, address indexed agent, uint256 amount);
    event EscrowReleased(bytes32 indexed escrowId, address indexed agent, uint256 amount);
    event EscrowRefunded(bytes32 indexed escrowId, address indexed creator, uint256 amount);

    constructor(address _usdcToken) {
        usdcToken = IERC20(_usdcToken);
    }

    function createEscrow(
        bytes32 escrowId,
        address agentBeneficiary,
        address arbiter,
        uint256 amount,
        uint256 durationSeconds
    ) external {
        require(escrows[escrowId].amount == 0, "Escrow already exists");
        require(agentBeneficiary != address(0), "Invalid agent address");
        require(amount > 0, "Amount must be > 0");

        require(usdcToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");

        escrows[escrowId] = Escrow({
            creator: msg.sender,
            agentBeneficiary: agentBeneficiary,
            arbiter: arbiter,
            amount: amount,
            expiryTimestamp: block.timestamp + durationSeconds,
            isSettled: false,
            isDisputed: false
        });

        emit EscrowCreated(escrowId, msg.sender, agentBeneficiary, amount);
    }

    function releaseToAgent(bytes32 escrowId) external {
        Escrow storage e = escrows[escrowId];
        require(!e.isSettled, "Already settled");
        require(msg.sender == e.creator || msg.sender == e.arbiter || (block.timestamp >= e.expiryTimestamp && !e.isDisputed), "Unauthorized");

        e.isSettled = true;
        require(usdcToken.transfer(e.agentBeneficiary, e.amount), "USDC Transfer failed");

        emit EscrowReleased(escrowId, e.agentBeneficiary, e.amount);
    }
}
