// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title InstantPermit2Validator
 * @notice Gas-Optimized ERC-20 Permit2 Signature Validator for Base L2.
 * Target Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
 */

interface IERC20Permit {
    function permit(
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external;
}

contract InstantPermit2Validator {
    address public immutable payoutWallet;

    event PermitExecuted(address indexed token, address indexed owner, address indexed spender, uint256 value);

    constructor() {
        payoutWallet = 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20;
    }

    function executePermitAndVerify(
        address token,
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external returns (bool) {
        require(block.timestamp <= deadline, "Permit expired");
        IERC20Permit(token).permit(owner, spender, value, deadline, v, r, s);
        emit PermitExecuted(token, owner, spender, value);
        return true;
    }
}
