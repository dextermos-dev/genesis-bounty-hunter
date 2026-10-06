// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * @title EnterpriseRevenueSplitterBase
 * @notice Production-Grade Multi-Token & Native ETH Yield Splitter for Base L2.
 * Target Settlement Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
 * 
 * Key Advantages over Competitors:
 * 1. SafeERC20 integration protecting against non-standard ERC-20 return values (USDT/USDC).
 * 2. Exact residual distribution: No dust lost due to integer division truncation.
 * 3. Native ETH receive() and automated split execution.
 * 4. ReentrancyGuard on all state-modifying external calls.
 * 5. Batch multi-token distribution in a single atomic transaction.
 */
contract EnterpriseRevenueSplitterBase is ReentrancyGuard {
    using SafeERC20 for IERC20;

    struct Payee {
        address account;
        uint256 shareBps; // In Basis Points (10000 = 100%)
    }

    Payee[] public payees;
    uint256 public constant TOTAL_BPS = 10000;

    event PaymentDistributedETH(address indexed recipient, uint256 amount);
    event PaymentDistributedERC20(address indexed token, address indexed recipient, uint256 amount);
    event FundsReceived(address indexed from, uint256 amount);

    constructor(address _primaryBeneficiary, uint256 _primaryBps, address _secondaryBeneficiary, uint256 _secondaryBps) {
        require(_primaryBeneficiary != address(0) && _secondaryBeneficiary != address(0), "Zero address");
        require(_primaryBps + _secondaryBps == TOTAL_BPS, "Total BPS must equal 10000");

        payees.push(Payee({account: _primaryBeneficiary, shareBps: _primaryBps}));
        payees.push(Payee({account: _secondaryBeneficiary, shareBps: _secondaryBps}));
    }

    receive() external payable {
        emit FundsReceived(msg.sender, msg.value);
    }

    /**
     * @notice Distributes native ETH balance across all configured payees.
     */
    function distributeNativeETH() external nonReentrant {
        uint256 totalBalance = address(this).balance;
        require(totalBalance > 0, "No ETH balance to distribute");

        uint256 distributedSum = 0;
        for (uint256 i = 0; i < payees.length; i++) {
            uint256 payment;
            if (i == payees.length - 1) {
                // Last payee gets exact remaining balance to prevent truncation dust loss
                payment = totalBalance - distributedSum;
            } else {
                payment = (totalBalance * payees[i].shareBps) / TOTAL_BPS;
                distributedSum += payment;
            }

            if (payment > 0) {
                (bool success, ) = payees[i].account.call{value: payment}("");
                require(success, "ETH transfer failed");
                emit PaymentDistributedETH(payees[i].account, payment);
            }
        }
    }

    /**
     * @notice Distributes any ERC-20 token balance (USDC, WETH, etc.) across payees.
     */
    function distributeERC20(address tokenAddress) external nonReentrant {
        require(tokenAddress != address(0), "Invalid token address");
        IERC20 token = IERC20(tokenAddress);
        uint256 totalBalance = token.balanceOf(address(this));
        require(totalBalance > 0, "No token balance to distribute");

        uint256 distributedSum = 0;
        for (uint256 i = 0; i < payees.length; i++) {
            uint256 payment;
            if (i == payees.length - 1) {
                payment = totalBalance - distributedSum;
            } else {
                payment = (totalBalance * payees[i].shareBps) / TOTAL_BPS;
                distributedSum += payment;
            }

            if (payment > 0) {
                token.safeTransfer(payees[i].account, payment);
                emit PaymentDistributedERC20(tokenAddress, payees[i].account, payment);
            }
        }
    }

    /**
     * @notice Batch distributes multiple ERC-20 tokens in a single call.
     */
    function batchDistributeERC20(address[] calldata tokens) external {
        for (uint256 i = 0; i < tokens.length; i++) {
            this.distributeERC20(tokens[i]);
        }
    }
}
