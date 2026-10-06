// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title SlidingWindowFeeOracle
 * @notice Real-Time Gas Price & Priority Fee Oracle with Sliding Window Median for Base L2.
 * Target Wallet: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20
 */

contract SlidingWindowFeeOracle {
    uint256 public constant WINDOW_SIZE = 10;
    uint256[WINDOW_SIZE] public feeHistory;
    uint256 public headIndex;
    uint256 public count;
    address public immutable owner;

    event FeeSampleRecorded(uint256 feeWei, uint256 calculatedMedian);

    constructor() {
        owner = msg.sender;
    }

    function recordFeeSample(uint256 feeWei) external {
        feeHistory[headIndex] = feeWei;
        headIndex = (headIndex + 1) % WINDOW_SIZE;
        if (count < WINDOW_SIZE) {
            count++;
        }

        emit FeeSampleRecorded(feeWei, getMedianFee());
    }

    function getMedianFee() public view returns (uint256) {
        require(count > 0, "No fee data");
        uint256[] memory sorted = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            sorted[i] = feeHistory[i];
        }

        // Insertion sort for small array
        for (uint256 i = 1; i < count; i++) {
            uint256 key = sorted[i];
            int256 j = int256(i) - 1;
            while (j >= 0 && sorted[uint256(j)] > key) {
                sorted[uint256(j + 1)] = sorted[uint256(j)];
                j--;
            }
            sorted[uint256(j + 1)] = key;
        }

        return sorted[count / 2];
    }
}
