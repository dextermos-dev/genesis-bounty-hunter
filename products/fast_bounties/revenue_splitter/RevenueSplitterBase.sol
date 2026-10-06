// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title RevenueSplitterBase
 * @notice Automated Revenue & Yield Routing Splitter for Base L2.
 * Target Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
 */

interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
}

contract RevenueSplitterBase {
    address public immutable primaryBeneficiary;
    address public immutable secondaryBeneficiary;
    uint256 public immutable primaryShareBps; // Basis points e.g. 8000 = 80%

    event RevenueDistributed(address indexed token, uint256 primaryAmount, uint256 secondaryAmount);

    constructor(address _primary, address _secondary, uint256 _bps) {
        require(_primary != address(0) && _secondary != address(0), "Invalid address");
        require(_bps <= 10000, "Invalid BPS");
        primaryBeneficiary = _primary;
        secondaryBeneficiary = _secondary;
        primaryShareBps = _bps;
    }

    function distributeERC20(address token) external {
        IERC20 erc20 = IERC20(token);
        uint256 balance = erc20.balanceOf(address(this));
        require(balance > 0, "No balance to distribute");

        uint256 primaryAmount = (balance * primaryShareBps) / 10000;
        uint256 secondaryAmount = balance - primaryAmount;

        if (primaryAmount > 0) {
            require(erc20.transfer(primaryBeneficiary, primaryAmount), "Primary transfer failed");
        }
        if (secondaryAmount > 0) {
            require(erc20.transfer(secondaryBeneficiary, secondaryAmount), "Secondary transfer failed");
        }

        emit RevenueDistributed(token, primaryAmount, secondaryAmount);
    }
}
