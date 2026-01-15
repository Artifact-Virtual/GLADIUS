```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/*
--- Frontmatter ---
Title: 'Supercomputer Equilibrium Monitor Contract'
Role: 'Marketing Manager (Tech & Growth) - Smart Contract Representation'
Version: 1.0.0-MVP
Date: 2025-06-16
Description: An MVP smart contract representing the core logic of the Marketing Manager (Tech & Growth) for monitoring and assessing supercomputer system equilibrium based on provided metrics and job data.
--- End Frontmatter ---
*/

// --- Header: System Context & Core Purpose ---
// This smart contract processes system-level metrics and job completion data to assess
// the overall equilibrium and operational health of the supercomputer system.
// It is designed to receive data inputs from off-chain components and perform synchronous
// calculations to derive a consistent view of the system state within a blockchain transaction.
// All calculations and state updates within this contract are designed for logical,
// mathematical, and code-wise synchronicity within the confines of a single block execution.

/**
 * @dev Enum representing the equilibrium status of the supercomputer system.
 * Balanced: System operating within expected parameters.
 * HighLoad: System experiencing high resource utilization, potentially nearing capacity.
 * Imbalanced: System showing signs of inefficiency or non-uniform load/synchronization issues.
 * Degraded: System potentially experiencing significant issues or data inconsistencies.
 */
enum SystemEquilibriumStatus {
    Balanced,
    HighLoad,
    Imbalanced,
    Degraded
}

/**
 * @dev Struct representing a job record for completion analysis.
 * startTime and endTime are Unix timestamps in seconds.
 */
struct JobRecord {
    uint256 startTime; // Unix timestamp in seconds
    uint256 endTime;   // Unix timestamp in seconds, 0 if not completed
    bool completed;    // True if job completed successfully
}

/**
 * @dev Struct for reporting aggregated system growth and equilibrium status.
 * Scaled integers are used for percentages (e.g., 8500 for 85.00%).
 * Durations in seconds.
 */
struct GrowthReport {
    uint256 timestamp;            // Block timestamp when report was generated
    uint256 totalCpuUsageScaled;  // Aggregate CPU usage percentage scaled by 100 (0-10000 * numUnits)
    uint256 averageMemoryUsageScaled; // Average memory usage percentage scaled by 100 (0-10000)
    uint256 totalActiveJobs;      // Total count of active jobs
    uint256 jobCompletionRateScaled; // Percentage of jobs completed scaled by 100 (0-10000)
    uint256 averageDuration;      // Average job duration in seconds
    uint256 durationVarianceScaled; // Job duration variance scaled by 100 (seconds^2 * 100)
    SystemEquilibriumStatus systemEquilibriumStatus;
}

contract MarketingManagerArtifact {

    // State variable storing the current assessed equilibrium status
    SystemEquilibriumStatus public currentEquilibriumStatus = SystemEquilibriumStatus.Balanced;

    // State variable storing the latest generated report
    GrowthReport public latestGrowthReport;

    // Assuming a fixed number of monitored units for equilibrium thresholds in this MVP
    uint256 private constant NUM_MONITORED_UNITS = 4;

    // Percentage thresholds scaled by 100 (e.g., 8000 for 80%)
    uint256 private constant HIGH_CPU_THRESHOLD_PER_UNIT_SCALED = 8000; // 80%
    uint256 private constant HIGH_MEMORY_THRESHOLD_SCALED = 8500; // 85%
    uint256 private constant LOW_CPU_THRESHOLD_PER_UNIT_SCALED = 1000; // 10%
    uint256 private constant MIN_COMPLETION_RATE_SCALED = 9000; // 90%

    // Variance threshold as a factor of average duration (scaled by 100 for comparison)
    // e.g., variance > averageDuration * 0.5 => variance * 100 > averageDuration * 50
    uint256 private constant DURATION_VARIANCE_FACTOR_SCALED = 50; // 0.5 factor scaled by 100

    event GrowthReportGenerated(GrowthReport report);
    event EquilibriumStatusUpdated(SystemEquilibriumStatus newStatus, SystemEquilibriumStatus oldStatus);

    /**
     * @dev Updates the system's equilibrium status based on provided metrics and job data.
     * This function combines the logic of collecting/aggregating (via input) and analyzing data.
     * All calculations are performed synchronously within the transaction.
     * @param totalCpuUsageScaled Aggregate CPU usage percentage scaled by 100 (sum across units).
     * @param averageMemoryUsageScaled Average memory usage percentage scaled by 100.
     * @param totalActiveJobs Total count of active jobs.
     * @param recentJobs Array of recent JobRecord structs for completion analysis.
     */
    function updateSystemStatus(
        uint256 totalCpuUsageScaled,
        uint256 averageMemoryUsageScaled,
        uint256 totalActiveJobs,
        JobRecord[] calldata recentJobs // Use calldata for external calls reading arrays
    ) external {
        SystemEquilibriumStatus newStatus = SystemEquilibriumStatus.Balanced;

        // --- Task 1 & 3 (part): Metric-based Equilibrium Assessment ---
        // Check for High Load based on aggregated metrics
        if (totalCpuUsageScaled > (NUM_MONITORED_UNITS * HIGH_CPU_THRESHOLD_PER_UNIT_SCALED) ||
            averageMemoryUsageScaled > HIGH_MEMORY_THRESHOLD_SCALED)
        {
            newStatus = SystemEquilibriumStatus.HighLoad;
        }
        // Check for Imbalance (Low Utilization)
        else if (totalCpuUsageScaled < (NUM_MONITORED_UNITS * LOW_CPU_THRESHOLD_PER_UNIT_SCALED) &&
                 totalActiveJobs == 0)
        {
             // Low utilization indicates imbalance/inefficiency, but HighLoad takes precedence
            if (newStatus == SystemEquilibriumStatus.Balanced) {
                 newStatus = SystemEquilibriumStatus.Imbalanced;
            }
        }


        // --- Task 2 & 3 (part): Job Completion Synchronicity Analysis ---
        uint256 completedJobCount = 0;
        uint256 totalDuration = 0;
        uint256[] memory durations = new uint256[](recentJobs.length); // Temporary storage

        for (uint i = 0; i < recentJobs.length; i++) {
            if (recentJobs[i].completed && recentJobs[i].endTime > recentJobs[i].startTime) {
                completedJobCount++;
                uint256 duration = recentJobs[i].endTime - recentJobs[i].startTime;
                durations[completedJobCount - 1] = duration; // Store valid duration
                totalDuration += duration;
            }
        }

        uint256 completionRateScaled = 0;
        uint256 averageDuration = 0;
        uint256 durationVarianceScaled = 0; // variance * 100

        if (recentJobs.length > 0) {
            completionRateScaled = (completedJobCount * 10000) / recentJobs.length; // Scaled percentage
        }

        if (completedJobCount > 0) {
            averageDuration = totalDuration / completedJobCount;

            uint256 totalSquaredDifference = 0;
             // Recalculate durations array to only include completed job durations
            uint256[] memory completedDurations = new uint256[](completedJobCount);
            uint k = 0;
            for(uint i = 0; i < recentJobs.length; i++) {
                 if(recentJobs[i].completed && recentJobs[i].endTime > recentJobs[i].startTime) {
                     completedDurations[k] = recentJobs[i].endTime - recentJobs[i].startTime;
                     k++;
                 }
            }

            for (uint i = 0; i < completedJobCount; i++) {
                uint256 diff = completedDurations[i] > averageDuration ? completedDurations[i] - averageDuration : averageDuration - completedDurations[i];
                totalSquaredDifference += diff * diff;
            }
            // Calculate variance (scaled by 100 to keep precision for comparison)
            // variance = totalSquaredDifference / completedJobCount
            // variance * 100 = (totalSquaredDifference * 100) / completedJobCount
            durationVarianceScaled = (totalSquaredDifference * 100) / completedJobCount;
        }


        // Check for Imbalance based on job synchronicity (completion rate or variance)
        // Variance check: durationVarianceScaled > averageDuration * DURATION_VARIANCE_FACTOR_SCALED / 100
        // => durationVarianceScaled * 100 > averageDuration * DURATION_VARIANCE_FACTOR_SCALED
        if (completionRateScaled < MIN_COMPLETION_RATE_SCALED ||
            (completedJobCount > 1 && durationVarianceScaled * 100 > averageDuration * DURATION_VARIANCE_FACTOR_SCALED)) // Need at least 2 completed jobs for variance
        {
            // Job sync issues indicate imbalance, override Low Utilization if currently Balanced
            if (newStatus == SystemEquilibriumStatus.Balanced || newStatus == SystemEquilibriumStatus.Imbalanced) {
                 newStatus = SystemEquilibriumStatus.Imbalanced;
            }
        }


        // --- Final Equilibrium Status Update ---
        // Degraded status would typically be set by external monitoring alerting to critical failure,
        // or potentially internal contract checks if, for example, input data is clearly invalid.
        // For this MVP, we assume valid input and determine status from metrics/jobs.

        SystemEquilibriumStatus oldStatus = currentEquilibriumStatus;
        currentEquilibriumStatus = newStatus;

        // --- Task 3 (part): Generate & Store Report ---
        latestGrowthReport = GrowthReport({
            timestamp: block.timestamp,
            totalCpuUsageScaled: totalCpuUsageScaled,
            averageMemoryUsageScaled: averageMemoryUsageScaled,
            totalActiveJobs: totalActiveJobs,
            jobCompletionRateScaled: completionRateScaled,
            averageDuration: averageDuration,
            durationVarianceScaled: durationVarianceScaled,
            systemEquilibriumStatus: newStatus
        });

        // Emit events for transparency and off-chain monitoring
        emit EquilibriumStatusUpdated(newStatus, oldStatus);
        emit GrowthReportGenerated(latestGrowthReport);
    }

    /**
     * @dev Returns the current assessed equilibrium status.
     */
    function getEquilibriumStatus() public view returns (SystemEquilibriumStatus) {
        return currentEquilibriumStatus;
    }

     /**
     * @dev Returns the latest generated growth report.
     */
    function getLatestGrowthReport() public view returns (GrowthReport memory) {
        return latestGrowthReport;
    }

    // Any supporting internal/private functions or interfaces can be added here.
    // E.g., function to validate input ranges if necessary.
}

// --- Footer: System Integration Notes & Potential Issues (MVP) ---
/*
This MVP smart contract provides a core calculation and state update logic for system equilibrium.
Below are potential issues and considerations for its interaction within a broader, potentially off-chain, supercomputer monitoring system:

**Potential Integration Issues & Considerations:**
- Issue 1: The smart contract relies entirely on off-chain systems to collect, aggregate, and submit accurate and time-synchronized metrics and job data. Data providers must ensure the integrity and freshness of the data before submitting to the contract.
- Resolution/Mitigation 1: Implement robust off-chain data collection agents with timestamping and validation. Use secure oracles (e.g., Chainlink) or decentralized data feeds to provide data to the contract. Consider signed data payloads to verify the source.
- Issue 2: Gas costs associated with processing potentially large arrays of `recentJobs` or complex calculations within a single transaction could become prohibitive under high load or for detailed analysis.
- Resolution/Mitigation 2: Limit the size of input arrays. Offload complex calculations (like variance for very large job sets) off-chain, and only submit aggregated results for verification if feasible. Restructure the contract to process data in smaller batches across multiple transactions if necessary, though this complicates synchronous state assessment.
- Issue 3: The "synchronicity" within the smart contract is limited to the atomic execution of a single transaction. It cannot enforce or verify the real-world distributed synchronicity of metric collection or job execution across the supercomputer nodes.
- Resolution/Mitigation 3: The contract's assessment of equilibrium reflects the state presented by the input data *at the time of the transaction*. Real-world synchronicity must be ensured by the off-chain data collection and submission processes. The contract provides a trust anchor for this processing logic but not the data source itself.
- Issue 4: Defining and translating complex supercomputer equilibrium states and thresholds into simple, deterministic contract logic and fixed thresholds may oversimplify the system's true state.
- Resolution/Mitigation 4: Refine equilibrium definitions based on deeper analysis and simulation. Consider making thresholds configurable via governance or authorized entities. Explore more advanced on-chain mathematical libraries if necessary and gas-permitting.
- Issue 5: Lack of historical data within the contract makes trend analysis or detection of slow drifts in equilibrium impossible without off-chain storage and analysis.
- Resolution/Mitigation 5: Store summary data points periodically (e.g., daily aggregates, trend indicators) on-chain if gas costs allow. Alternatively, use off-chain indexing solutions (e.g., The Graph) to build historical views from emitted events.
*/
```