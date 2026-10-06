// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title BountycasterBaseTipper
 * @notice Contrato inteligente de micro-propinas y micropagos instantáneos en USDC sobre Base.
 * @dev Optimizado para bajo consumo de gas y liquidación instantánea para bounties de Farcaster.
 */

interface IERC20 {
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function transfer(address recipient, uint256 amount) external returns (bool);
}

contract BountycasterBaseTipper {
    address public owner;
    IERC20 public immutable usdcToken;

    event BountyTipSent(address indexed sender, address indexed recipient, uint256 amount, string castHash);

    modifier onlyOwner() {
        require(msg.sender == owner, "Unauthorized");
        _;
    }

    constructor(address _usdcToken) {
        owner = msg.sender;
        usdcToken = IERC20(_usdcToken);
    }

    function tipBountySolver(address recipient, uint256 amount, string calldata castHash) external {
        require(recipient != address(0), "Invalid recipient");
        require(amount > 0, "Amount must be > 0");

        bool success = usdcToken.transferFrom(msg.sender, recipient, amount);
        require(success, "USDC transfer failed");

        emit BountyTipSent(msg.sender, recipient, amount, castHash);
    }

    function batchTipSolvers(address[] calldata recipients, uint256[] calldata amounts, string[] calldata castHashes) external {
        require(recipients.length == amounts.length && amounts.length == castHashes.length, "Length mismatch");
        for (uint256 i = 0; i < recipients.length; i++) {
            require(recipients[i] != address(0), "Invalid recipient");
            require(amounts[i] > 0, "Amount must be > 0");
            bool success = usdcToken.transferFrom(msg.sender, recipients[i], amounts[i]);
            require(success, "USDC transfer failed");
            emit BountyTipSent(msg.sender, recipients[i], amounts[i], castHashes[i]);
        }
    }
}
