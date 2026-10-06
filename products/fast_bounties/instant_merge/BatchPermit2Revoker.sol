// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title BatchPermit2Revoker
 * @notice High-Speed EIP-712 Permit2 & ERC-20 Allowance Revocation on Base L2.
 * Target Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
 */

interface IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
}

interface IPermit2 {
    function lockdown(tuple(address token, address spender)[] calldata approvals) external;
    function invalidateUnorderedNonces(uint256 wordPos, uint256 mask) external;
}

contract BatchPermit2Revoker {
    address public immutable payoutWallet;

    event AllowancesRevoked(address indexed user, uint256 tokensCount);

    constructor() {
        payoutWallet = 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20;
    }

    function batchRevokeERC20(address[] calldata tokens, address[] calldata spenders) external {
        require(tokens.length == spenders.length, "Length mismatch");
        for (uint256 i = 0; i < tokens.length; i++) {
            IERC20(tokens[i]).approve(spenders[i], 0);
        }
        emit AllowancesRevoked(msg.sender, tokens.length);
    }
}
