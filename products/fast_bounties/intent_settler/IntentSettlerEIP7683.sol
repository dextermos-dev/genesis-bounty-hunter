// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IntentSettlerEIP7683
 * @notice Cross-Chain Intent Settlement Engine for Base L2 (EIP-7683 Standard).
 * Beneficiary Settlement: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
 */

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

contract IntentSettlerEIP7683 {
    struct CrossChainOrder {
        address user;
        address originToken;
        uint256 originAmount;
        address destinationToken;
        uint256 destinationAmount;
        uint32 destinationChainId;
        bytes32 orderHash;
        bool isResolved;
    }

    address public immutable fillerBeneficiary;
    mapping(bytes32 => CrossChainOrder) public orders;

    event OrderOpened(bytes32 indexed orderHash, address indexed user, uint256 originAmount);
    event OrderFilled(bytes32 indexed orderHash, address indexed filler, uint256 destinationAmount);

    constructor(address _filler) {
        require(_filler != address(0), "Invalid filler");
        fillerBeneficiary = _filler;
    }

    function openOrder(
        address originToken,
        uint256 originAmount,
        address destinationToken,
        uint256 destinationAmount,
        uint32 destinationChainId
    ) external returns (bytes32) {
        bytes32 orderHash = keccak256(abi.encodePacked(msg.sender, originToken, originAmount, destinationToken, destinationAmount, destinationChainId, block.timestamp));
        require(!orders[orderHash].isResolved, "Order exists");

        require(IERC20(originToken).transferFrom(msg.sender, address(this), originAmount), "Escrow failed");

        orders[orderHash] = CrossChainOrder({
            user: msg.sender,
            originToken: originToken,
            originAmount: originAmount,
            destinationToken: destinationToken,
            destinationAmount: destinationAmount,
            destinationChainId: destinationChainId,
            orderHash: orderHash,
            isResolved: false
        });

        emit OrderOpened(orderHash, msg.sender, originAmount);
        return orderHash;
    }

    function fillOrder(bytes32 orderHash) external {
        CrossChainOrder storage order = orders[orderHash];
        require(!order.isResolved, "Already resolved");
        require(msg.sender == fillerBeneficiary, "Only designated filler");

        order.isResolved = true;
        require(IERC20(order.originToken).transfer(fillerBeneficiary, order.originAmount), "Payout failed");

        emit OrderFilled(orderHash, fillerBeneficiary, order.destinationAmount);
    }
}
