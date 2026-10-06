// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ERC4626InflationGuard
 * @notice Abstract security module to protect ERC-4626 Tokenized Vaults against First-Depositor Share Inflation Attacks.
 * @dev Implements virtual offset shares and virtual assets to eliminate the rounding-down exploit where a malicious
 * first depositor donates underlying assets to inflate share price and steal subsequent deposits.
 * 
 * Designed for deployment on Base L2, Ethereum, and Arbitrum.
 */
abstract contract ERC4626InflationGuard {
    error ZeroDepositNotAllowed();
    error InvalidVirtualOffset();

    /// @notice Number of virtual decimals offset added to shares calculation (Standard: 3 = 10^3)
    uint8 public constant VIRTUAL_DECIMALS_OFFSET = 3;
    uint256 internal constant VIRTUAL_SHARES_BASE = 10 ** VIRTUAL_DECIMALS_OFFSET;
    uint256 internal constant VIRTUAL_ASSETS_BASE = 1;

    /**
     * @notice Computes shares minted for a given amount of deposited assets, including virtual offsets.
     * @param assets Amount of assets being deposited
     * @param totalAssets Current total assets held in the vault
     * @param totalSupply Current total shares minted by the vault
     * @return shares Amount of shares to mint
     */
    function _computeGuardedDepositShares(
        uint256 assets,
        uint256 totalAssets,
        uint256 totalSupply
    ) internal pure returns (uint256 shares) {
        if (assets == 0) revert ZeroDepositNotAllowed();

        // Formula: shares = assets * (totalSupply + 10^offset) / (totalAssets + 1)
        uint256 virtualTotalSupply = totalSupply + VIRTUAL_SHARES_BASE;
        uint256 virtualTotalAssets = totalAssets + VIRTUAL_ASSETS_BASE;

        shares = (assets * virtualTotalSupply) / virtualTotalAssets;
        return shares;
    }

    /**
     * @notice Computes assets returned for a given amount of redeemed shares, including virtual offsets.
     * @param shares Amount of shares being redeemed
     * @param totalAssets Current total assets held in the vault
     * @param totalSupply Current total shares minted by the vault
     * @return assets Amount of assets to redeem
     */
    function _computeGuardedRedeemAssets(
        uint256 shares,
        uint256 totalAssets,
        uint256 totalSupply
    ) internal pure returns (uint256 assets) {
        if (shares == 0) return 0;

        // Formula: assets = shares * (totalAssets + 1) / (totalSupply + 10^offset)
        uint256 virtualTotalSupply = totalSupply + VIRTUAL_SHARES_BASE;
        uint256 virtualTotalAssets = totalAssets + VIRTUAL_ASSETS_BASE;

        assets = (shares * virtualTotalAssets) / virtualTotalSupply;
        return assets;
    }
}
