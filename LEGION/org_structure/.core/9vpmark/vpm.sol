```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title VPofMarketingDigitalAndGrowthArtifact
 * @dev This contract simulates the core calculation logic of the
 *      VP of Marketing (Digital & Growth) supercomputer artifact.
 *      It performs synchronous calculations based on snapshot inputs
 *      to suggest resource allocation adjustments and task prioritization,
 *      aiming to contribute to system equilibrium and "growth".
 *      All calculations within a single function call are logically,
 *      mathematically, and code-wise synchronous within the contract's execution context.
 */
contract VPofMarketingDigitalAndGrowthArtifact {

    // --- Data Structures ---

    struct SystemLoadMetric {
        string nodeId; // Use string for simplicity, could be bytes32 for efficiency
        uint256 currentLoad; // E.g., percentage * 1000 or task count
        uint256 maxCapacity; // Corresponding capacity
    }

    struct PendingTask {
        string taskId; // Use string, could be bytes32
        uint256 priorityScore; // Calculated score
        uint256 estimatedDuration; // Time units
        uint256 resourceUnitsRequired;
    }

    struct AllocationAdjustment {
        string nodeId; // Use string, could be bytes32
        int256 adjustmentFactor; // Stored as scaled integer (e.g., 1000 = 1.0, 900 = 0.9, 1100 = 1.1)
    }

    // DataPipelineState and FlowAdjustment are omitted for MVP contract size, focusing on load & task priority.
    // struct DataPipelineState { ... }
    // struct FlowAdjustment { ... }

    // --- State Variables ---

    // Equilibrium threshold for load balancing, scaled by 1000 (e.g., 100 = 0.1)
    uint256 public equilibriumThresholdScaled = 100; // Represents 0.1

    // Note: currentState is primarily an internal state indicator in the TS version.
    // In a contract, state changes are explicit. We won't mirror this state machine directly
    // in this MVP, focusing on the pure calculation functions.

    // --- Constructor ---

    constructor(uint256 _equilibriumThresholdScaled) {
        equilibriumThresholdScaled = _equilibriumThresholdScaled;
    }

    // --- Hardcoded Tasks (Simulated as View Functions) ---

    /**
     * @dev Hardcoded task 1: Synchronously calculates resource allocation adjustments
     *      based on current node loads to promote system equilibrium.
     *      Performs a synchronous calculation based on a snapshot of current states.
     *      This is a view function, meaning it reads state but doesn't modify it.
     * @param currentLoads Array of current load metrics from system nodes.
     * @return An array of suggested allocation adjustments for each node (scaled integer).
     */
    function calculateResourceBalanceAdjustments(SystemLoadMetric[] memory currentLoads)
        public
        view
        returns (AllocationAdjustment[] memory)
    {
        if (currentLoads.length == 0) {
            return new AllocationAdjustment[](0);
        }

        uint256 totalCapacity = 0;
        uint256 totalCurrentLoad = 0;

        // Synchronous calculation of totals
        for (uint i = 0; i < currentLoads.length; i++) {
            totalCapacity += currentLoads[i].maxCapacity;
            totalCurrentLoad += currentLoads[i].currentLoad;
        }

        // Avoid division by zero
        uint256 averageDesiredLoadScaled = (totalCapacity > 0) ? (totalCurrentLoad * 1000 / totalCapacity) : 0; // average utilization * 1000

        AllocationAdjustment[] memory adjustments = new AllocationAdjustment[](currentLoads.length);

        // Synchronously determine adjustments for each node
        for (uint i = 0; i < currentLoads.length; i++) {
            uint256 nodeCurrentLoad = currentLoads[i].currentLoad;
            uint256 nodeMaxCapacity = currentLoads[i].maxCapacity;

            uint256 utilizationScaled = (nodeMaxCapacity > 0) ? (nodeCurrentLoad * 1000 / nodeMaxCapacity) : 0; // node utilization * 1000

            int256 adjustmentFactorScaled = 1000; // Default: 1.0 (no change)

            // Simple proportional adjustment logic (scaled)
            // utilization > averageDesiredLoad * (1 + equilibriumThreshold)
            if (utilizationScaled > averageDesiredLoadScaled + (averageDesiredLoadScaled * equilibriumThresholdScaled / 1000)) {
                // Node is overloaded relative to average, suggest reduction
                // adjustmentFactor = 1.0 - (utilization - averageDesiredLoad) * 0.5; // Example from TS
                // In scaled integers: 1000 - (utilizationScaled - averageDesiredLoadScaled) * 500 / 1000
                adjustmentFactorScaled = 1000 - int256(utilizationScaled - averageDesiredLoadScaled) * 500 / 1000;
                adjustmentFactorScaled = Math.max(500, adjustmentFactorScaled); // Don't reduce below 0.5 (500)
            }
            // utilization < averageDesiredLoad * (1 - equilibriumThreshold)
             else if (utilizationScaled < averageDesiredLoadScaled - (averageDesiredLoadScaled * equilibriumThresholdScaled / 1000) && nodeMaxCapacity > 0) {
                 // Node is underloaded relative to average, suggest increase
                 // adjustmentFactor = 1.0 + (averageDesiredLoad - utilization) * 0.5; // Example from TS
                 // In scaled integers: 1000 + (averageDesiredLoadScaled - utilizationScaled) * 500 / 1000
                 adjustmentFactorScaled = 1000 + int256(averageDesiredLoadScaled - utilizationScaled) * 500 / 1000;
                 adjustmentFactorScaled = Math.min(1500, adjustmentFactorScaled); // Don't increase above 1.5 (1500)
            }
            // else { Within acceptable equilibrium threshold }

            adjustments[i] = AllocationAdjustment({
                nodeId: currentLoads[i].nodeId,
                adjustmentFactor: adjustmentFactorScaled
            });
        }

        return adjustments;
    }

    /**
     * @dev Hardcoded task 2: Synchronously prioritizes pending tasks based on
     *      calculated scores and estimated system capacity to drive "growth".
     *      Ensures tasks are ordered logically for efficient processing.
     *      This is a view function.
     * @param taskList Array of pending tasks.
     * @param estimatedAvailableResourceUnits Estimate of total available processing units.
     * @return Array of task IDs in suggested processing order.
     */
    function prioritizeGrowthTasks(PendingTask[] memory taskList, uint256 estimatedAvailableResourceUnits)
        public
        view
        returns (string[] memory)
    {
        if (taskList.length == 0) {
            return new string[](0);
        }

        // Solidity does not have built-in sort for complex types like structs.
        // A synchronous sort must be implemented manually if needed, or assume pre-sorted input.
        // For this MVP, we'll simulate the sorting logic conceptually and select.
        // A full implementation would require a comparison-based sort or a different data structure pattern.

        // Simple simulation: Iterate and select based on priority/efficiency heuristic up to capacity
        // This iteration and selection is synchronous within the contract call.

        string[] memory prioritizedTaskIds = new string[](taskList.length); // Allocate max possible size
        uint256 resourcesConsumed = 0;
        uint256 count = 0; // Actual count of prioritized tasks

        // Note: This loop doesn't perform the actual sorting. It processes the tasks
        // *as provided* in the taskList array. A true mirror of the TS sort would need
        // a sorting algorithm implemented here, which is complex and gas-intensive in Solidity.
        // This MVP focuses on the synchronous *selection* process based on the provided list.
        // Assume taskList is pre-sorted or handle sorting off-chain or with a different contract pattern.
        // For demonstration, we'll just process them in the order received,
        // applying the resource limit check synchronously.

        for (uint i = 0; i < taskList.length; i++) {
             if (resourcesConsumed + taskList[i].resourceUnitsRequired <= estimatedAvailableResourceUnits) {
                prioritizedTaskIds[count] = taskList[i].taskId;
                resourcesConsumed += taskList[i].resourceUnitsRequired;
                count++;
            } else {
                // Stop adding tasks if resources exceeded
                break;
            }
        }

        // Resize the array to the actual number of prioritized tasks
        string[] memory finalPrioritizedTaskIds = new string[](count);
        for(uint i = 0; i < count; i++) {
            finalPrioritizedTaskIds[i] = prioritizedTaskIds[i];
        }

        return finalPrioritizedTaskIds;
    }

    // Helper functions for scaled integer math (optional, can use inline)
    library Math {
        function max(int256 a, int256 b) internal pure returns (int256) {
            return a >= b ? a : b;
        }
        function min(int256 a, int256 b) internal pure returns (int256) {
            return a < b ? a : b;
        }
    }
}
```