// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AgentSessionKeyManager
 * @notice Modular Session Key Validator for Autonomous AI Agents on Base L2 (ERC-7579 / ERC-4337).
 * Target Settlement: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
 */

contract AgentSessionKeyManager {
    struct SessionPermission {
        address agentKey;
        address targetContract;
        uint256 dailySpendLimit;
        uint256 currentDaySpent;
        uint256 lastResetTimestamp;
        uint256 expiryTimestamp;
        bool isActive;
    }

    mapping(address => mapping(bytes32 => SessionPermission)) public userSessions;

    event SessionCreated(address indexed user, bytes32 indexed sessionId, address indexed agentKey, uint256 limit, uint256 expiry);
    event SessionExecuted(address indexed user, bytes32 indexed sessionId, uint256 amount);
    event SessionRevoked(address indexed user, bytes32 indexed sessionId);

    function createSession(
        bytes32 sessionId,
        address agentKey,
        address targetContract,
        uint256 dailySpendLimit,
        uint256 durationSeconds
    ) external {
        require(agentKey != address(0), "Invalid agent key");
        require(dailySpendLimit > 0, "Invalid limit");

        userSessions[msg.sender][sessionId] = SessionPermission({
            agentKey: agentKey,
            targetContract: targetContract,
            dailySpendLimit: dailySpendLimit,
            currentDaySpent: 0,
            lastResetTimestamp: block.timestamp,
            expiryTimestamp: block.timestamp + durationSeconds,
            isActive: true
        });

        emit SessionCreated(msg.sender, sessionId, agentKey, dailySpendLimit, block.timestamp + durationSeconds);
    }

    function validateAndCharge(
        address user,
        bytes32 sessionId,
        uint256 amount
    ) external returns (bool) {
        SessionPermission storage session = userSessions[user][sessionId];
        require(session.isActive, "Session inactive");
        require(msg.sender == session.agentKey, "Unauthorized agent");
        require(block.timestamp <= session.expiryTimestamp, "Session expired");

        // 24-hour daily spend reset
        if (block.timestamp >= session.lastResetTimestamp + 1 days) {
            session.currentDaySpent = 0;
            session.lastResetTimestamp = block.timestamp;
        }

        require(session.currentDaySpent + amount <= session.dailySpendLimit, "Daily spend limit exceeded");
        session.currentDaySpent += amount;

        emit SessionExecuted(user, sessionId, amount);
        return true;
    }
}
