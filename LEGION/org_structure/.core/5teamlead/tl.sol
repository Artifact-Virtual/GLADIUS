```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/*
--- Frontmatter ---
Title: System Ops Report Processor
Role: Team Lead (System Ops)
Version: 1.0.0-MVP
Date: 2025-06-16
Description: An MVP smart contract for processing subsystem status reports and checking system equilibrium,
             emulating the core function of the Team Lead (System Ops) artifact within a blockchain paradigm.
--- End Frontmatter ---
*/

// --- Header: System Context & Core Purpose ---
// This contract receives aggregated status reports from off-chain supercomputer subsystems
// and verifies their consistency and contribution to the overall system equilibrium state.
// The processing of a batch of reports within a single transaction emulates synchronous
// collection and validation from the perspective of the blockchain state update.
// Equilibrium checks are performed on the aggregated data.

contract SystemOpsReportProcessor {

    // Define enums for clarity and state representation
    enum SystemState { Operational, Degraded, Critical }
    enum SubsystemState { Operational, Degraded, Offline }
    enum LogSeverity { ERROR, CRITICAL, ALERT }

    // Struct to hold subsystem status details
    struct SubsystemStatus {
        SubsystemState state;
        // Simplified metrics mapping for MVP. In reality, this might be more complex.
        // Using a simple array or fixed set of metrics is often better for gas.
        // Let's use a fixed array for a couple of example metrics (e.g., Load, Memory).
        // Metrics are represented as scaled integers (e.g., 0-1000).
        uint256[] metrics;
        uint256 timestamp; // Block timestamp when reported to the contract
    }

    // State variables
    SystemState public overallState;
    uint256 public lastEquilibriumCheckTimestamp;

    // Mapping to store the latest status reported by each subsystem
    mapping(bytes32 => SubsystemStatus) public subsystemStatuses;

    // Mapping to track last heartbeats for critical units (simplified from TS version)
    // Key: unitId (bytes32), Value: block.timestamp of last report
    mapping(bytes32 => uint256) public criticalUnitsHeartbeats;

    // Constants related to equilibrium checks and heartbeats
    uint256 private constant EXPECTED_METRIC_COUNT = 2; // Number of expected metrics in the metrics array for each subsystem
    // Example threshold for an aggregate metric sum (sum of all metric[0] across reporting systems)
    uint256 private constant AGGREGATE_METRIC_0_THRESHOLD = 800;
     // Example threshold for average of metric[1] across reporting systems (scaled integer, e.g., 900 for 90%)
    uint256 private constant AGGREGATE_METRIC_1_AVG_THRESHOLD = 900;
    // Example timeout in blocks for critical units heartbeat
    uint256 private constant CRITICAL_HEARTBEAT_TIMEOUT_BLOCKS = 100;

    // Role-based access control (simple owner-based for MVP)
    address private owner;
    // In a production system, use roles or access control lists (ACL)
    // mapping(address => bool) public isAuthorizedReporter;
    // mapping(bytes32 => address) public criticalUnitReporters; // Map unit ID to authorized reporter address

    // Events to signal state changes and critical occurrences off-chain
    event SystemStateUpdated(SystemState newState, uint256 timestamp);
    event EquilibriumCheckStatus(bool passed, SystemState currentSystemState, uint256 timestamp);
    event CriticalUnitHeartbeatMissed(bytes32 unitId, uint256 lastTimestamp, uint256 currentTimestamp);
    event CriticalEventLogged(LogSeverity severity, string message, bytes32 sourceId, uint256 timestamp);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    // Add modifiers for authorized reporters/units if implementing granular access control
    // modifier onlyAuthorizedReporter() {
    //     require(isAuthorizedReporter[msg.sender], "Caller is not an authorized reporter");
    //     _;
    // }
    // modifier onlyCriticalUnitReporter(bytes32 unitId) {
    //     require(criticalUnitReporters[unitId] == msg.sender, "Caller is not authorized for this unit");
    //     _;
    // }


    constructor() {
        owner = msg.sender;
        overallState = SystemState.Operational;
        lastEquilibriumCheckTimestamp = block.timestamp;
         // Set up initial authorized reporters/units in a real system
    }

    // Function to set authorized reporters/units (MVP: only owner)
    // function setAuthorizedReporter(address reporter, bool authorized) public onlyOwner {
    //     isAuthorizedReporter[reporter] = authorized;
    // }
    // function setCriticalUnitReporter(bytes32 unitId, address reporter) public onlyOwner {
    //     criticalUnitReporters[unitId] = reporter;
    // }


    /**
     * @notice Receives and processes a batch of subsystem status reports.
     * This function represents the core 'synchronous' collection and validation task
     * from the TypeScript artifact within the atomic execution context of a transaction.
     * Ensures logical and mathematical consistency checks on the provided data batch
     * before updating the contract's state representing overall system equilibrium.
     * @param subsystemIds Array of subsystem IDs (bytes32).
     * @param states Array of subsystem states (enum). Must match subsystemIds length.
     * @param metricsData Aggregated metrics data (e.g., flattened array). Expects
     *                    metricsData[i * EXPECTED_METRIC_COUNT + j] is the j-th metric for subsystem i.
     * @param timestamps Array of off-chain timestamps. Used for basic recency check but block.timestamp is canonical.
     */
    function reportSubsystemStatuses(
        bytes32[] memory subsystemIds,
        SubsystemState[] memory states,
        uint256[] memory metricsData,
        uint256[] memory timestamps // Off-chain timestamp - useful metadata, but not for on-chain sync logic
    ) public onlyOwner { // Using onlyOwner for MVP. Should be specific reporter role/modifier.
        require(
            subsystemIds.length > 0, // Require at least one report
            "No status reports provided"
        );
         require(
            subsystemIds.length == states.length &&
            subsystemIds.length == timestamps.length &&
            metricsData.length == subsystemIds.length * EXPECTED_METRIC_COUNT,
            "Input array lengths mismatch or metrics format incorrect"
        );

        // Process reports atomically in this transaction, ensuring data consistency for this batch
        uint256 operationalCount = 0;
        uint256 degradedCount = 0;
        uint256 criticalCount = 0; // Including Offline

        // Aggregate metrics for mathematical equilibrium check
        uint256[] memory aggregatedMetricsSum = new uint256[](EXPECTED_METRIC_COUNT);
        uint256 totalSubsystemsReportingMetrics = 0;

        // Off-chain timestamp consistency check (basic) - Ensure reports are from roughly the same time window
        // In a real system, this might involve comparing std deviation or requiring timestamps within a few seconds
        uint256 firstTimestamp = timestamps[0];
        for (uint256 i = 0; i < subsystemIds.length; i++) {
             // Check if timestamp is reasonably close to the first one in the batch (within 5 seconds)
             require(timestamps[i] >= firstTimestamp && timestamps[i] - firstTimestamp < 5, "Timestamp variance in reports too high (over 5s)");
        }


        for (uint256 i = 0; i < subsystemIds.length; i++) {
            bytes32 subId = subsystemIds[i];
            SubsystemState subState = states[i];
            // uint256 offchainTimestamp = timestamps[i]; // Off-chain timestamp stored in struct if needed

            // Extract metrics for this subsystem from the flattened array
            uint256[] memory currentMetrics = new uint256[](EXPECTED_METRIC_COUNT);
            for(uint256 j = 0; j < EXPECTED_METRIC_COUNT; j++) {
                 currentMetrics[j] = metricsData[i * EXPECTED_METRIC_COUNT + j];
                 aggregatedMetricsSum[j] += currentMetrics[j]; // Aggregate sum
            }
             if (EXPECTED_METRIC_COUNT > 0) totalSubsystemsReportingMetrics++; // Count systems providing metrics


            // Store latest status (using block.timestamp for on-chain canonical time)
            subsystemStatuses[subId] = SubsystemStatus(
                subState,
                currentMetrics,
                block.timestamp // Record the block timestamp when this report batch was processed
            );

            // Count states (logical consistency check within the batch)
            if (subState == SubsystemState.Operational) {
                operationalCount++;
            } else if (subState == SubsystemState.Degraded) {
                degradedCount++;
            } else { // Critical or Offline
                criticalCount++;
            }

             // Basic on-chain timestamp recency check
             // require(block.timestamp >= timestamps[i] && block.timestamp - timestamps[i] < 300, "Report timestamp too far in the future or too old (>5mins)"); // Example: report within 5 mins of block time
        }

        // Calculate overall state based on counts (logical equilibrium check)
        SystemState previousState = overallState;
        if (criticalCount > 0 || degradedCount * 2 > subsystemIds.length) { // If any critical or majority degraded
            overallState = SystemState.Critical;
        } else if (degradedCount > 0 || operationalCount * 10 < subsystemIds.length * 8) { // If some degraded or less than 80% operational
            overallState = SystemState.Degraded;
        } else { // All or almost all operational
            overallState = SystemState.Operational;
        }

        // Perform mathematical equilibrium check on aggregated metrics
        bool equilibriumCheckPassed = true;
        if (totalSubsystemsReportingMetrics > 0) {
             // Example check 1: sum of all reported metric[0] should be below threshold
            if (aggregatedMetricsSum[0] > AGGREGATE_METRIC_0_THRESHOLD) {
                 equilibriumCheckPassed = false;
                 // In a real system, this would trigger more specific alerts or state degradation
            }
             // Example check 2: average of all reported metric[1] should be below threshold
             if (EXPECTED_METRIC_COUNT > 1) {
                  uint256 aggregateMetric1Avg = aggregatedMetricsSum[1] / totalSubsystemsReportingMetrics;
                  if (aggregateMetric1Avg > AGGREGATE_METRIC_1_AVG_THRESHOLD) {
                      equilibriumCheckPassed = false;
                  }
             }
            // Add more complex mathematical checks here as needed, within gas limits.
        } else if (EXPECTED_METRIC_COUNT > 0 && subsystemIds.length > 0) {
            // Expected metrics but none reported? Indicate failure.
             equilibriumCheckPassed = false;
        }


        lastEquilibriumCheckTimestamp = block.timestamp;

        // Emit events signalling the result of this synchronous processing batch
        if (previousState != overallState) {
            emit SystemStateUpdated(overallState, block.timestamp);
        }
        emit EquilibriumCheckStatus(equilibriumCheckPassed, overallState, block.timestamp);

        // Optional: Automatically degrade state if mathematical checks fail, even if state counts look OK
        if (!equilibriumCheckPassed && overallState == SystemState.Operational) {
             overallState = SystemState.Degraded;
             // Re-emit state updated if it changed
             if (previousState != overallState) {
                 emit SystemStateUpdated(overallState, block.timestamp);
             }
        }
    }

    /**
     * @notice Records a heartbeat for a critical unit by updating its last reported timestamp.
     * Off-chain units call this function. This doesn't simulate a synchronous *check* initiated
     * by the contract, but rather records the fact that a unit is alive within the blockchain state.
     * @param unitId The ID of the critical unit (bytes32).
     */
    function reportHeartbeat(bytes32 unitId) public { // Should have access control for specific unit/proxy, e.g., onlyCriticalUnitReporter(unitId)
        require(unitId != bytes32(0), "Invalid unit ID");
        criticalUnitsHeartbeats[unitId] = block.timestamp;
        // Could emit an event here: event HeartbeatReceived(bytes32 unitId, uint256 timestamp);
    }

    /**
     * @notice Checks if any configured critical unit has missed its heartbeat deadline based on blockchain blocks.
     * This is a query function (`view`) and does not simulate synchronous waiting or external interaction.
     * It checks the recorded state against the current block timestamp.
     * @param criticalUnitIds Array of unit IDs to check.
     * @return An array of unit IDs that have potentially missed their heartbeat based on CRITICAL_HEARTBEAT_TIMEOUT_BLOCKS.
     */
    function checkCriticalUnitsHeartbeats(bytes32[] memory criticalUnitIds) public view returns (bytes32[] memory) {
        bytes32[] memory missedHeartbeats = new bytes32[](criticalUnitIds.length);
        uint256 missedCount = 0;

        for (uint256 i = 0; i < criticalUnitIds.length; i++) {
            bytes32 unitId = criticalUnitIds[i];
            uint256 lastTimestamp = criticalUnitsHeartbeats[unitId];

            // If unit never reported (lastTimestamp == 0) or last report is too old
            // Using block.timestamp for the check relative to CRITICAL_HEARTBEAT_TIMEOUT_BLOCKS
            // Ensure no underflow if block.timestamp < lastTimestamp (unlikely with reliable nodes, but defensive check)
            if (lastTimestamp == 0 || (block.timestamp > lastTimestamp && block.timestamp - lastTimestamp > CRITICAL_HEARTBEAT_TIMEOUT_BLOCKS)) {
                 missedHeartbeats[missedCount] = unitId;
                 missedCount++;
            }
        }

        // Resize the result array to the actual number of missed heartbeats
        bytes32[] memory result = new bytes32[](missedCount);
        for(uint256 i = 0; i < missedCount; i++) {
            result[i] = missedHeartbeats[i];
        }
        return result;
    }


    /**
     * @notice Logs a critical event by emitting a blockchain event.
     * This replaces the synchronous external logging described in the TypeScript artifact.
     * External monitoring systems must listen for these events to capture log entries.
     * Emitting the event is an atomic, synchronous action within the transaction.
     * @param severity The severity of the event.
     * @param message The event message.
     * @param sourceId The source of the event (bytes32).
     */
    function logCriticalEvent(LogSeverity severity, string memory message, bytes32 sourceId) public onlyOwner { // Owner or authorized logging entity
        require(sourceId != bytes32(0), "Invalid source ID");
        // In Solidity, logging is done by emitting an event.
        // It's an atomic action within the transaction that gets recorded on the blockchain.
        // It does *not* guarantee synchronous delivery or processing by off-chain systems.
        emit CriticalEventLogged(severity, message, sourceId, block.timestamp);

        // Optionally update the overall system state based on critical log severity
        if (severity == LogSeverity.CRITICAL || severity == LogSeverity.ALERT) { // Assuming ALERT is also critical
             if (overallState != SystemState.Critical) {
                 overallState = SystemState.Critical;
                 emit SystemStateUpdated(overallState, block.timestamp);
             }
        }
    }

    /**
     * @notice Get the current overall system equilibrium state as determined by the latest report processing.
     */
    function getOverallState() public view returns (SystemState) {
        return overallState;
    }

    /**
     * @notice Get the timestamp (block.timestamp) of the last equilibrium check (based on report batch processing).
     */
    function getLastEquilibriumCheckTimestamp() public view returns (uint256) {
        return lastEquilibriumCheckTimestamp;
    }

     // Helper functions to convert enum to string for off-chain readability (optional)
    function systemStateToString(SystemState state) public pure returns (string memory) {
        if (state == SystemState.Operational) return "Operational";
        if (state == SystemState.Degraded) return "Degraded";
        if (state == SystemState.Critical) return "Critical";
        return "Unknown"; // Should not happen
    }

    function subsystemStateToString(SubsystemState state) public pure returns (string memory) {
        if (state == SubsystemState.Operational) return "Operational";
        if (state == SubsystemState.Degraded) return "Degraded";
        if (state == SubsystemState.Offline) return "Offline"; // Mapping Offline to Critical in report processing, but enum exists
        return "Unknown"; // Should not happen
    }

     function logSeverityToString(LogSeverity severity) public pure returns (string memory) {
        if (severity == LogSeverity.ERROR) return "ERROR";
        if (severity == LogSeverity.CRITICAL) return "CRITICAL";
        if (severity == LogSeverity.ALERT) return "ALERT";
        return "Unknown"; // Should not happen
    }

     // Function to retrieve the status of a specific subsystem
     function getSubsystemStatus(bytes32 subsystemId) public view returns (SubsystemState state, uint256[] memory metrics, uint256 timestamp) {
        SubsystemStatus storage status = subsystemStatuses[subsystemId];
        // Note: Returning the metrics array requires creating a new array in memory for return
        uint256[] memory currentMetrics = new uint256[](status.metrics.length);
        for(uint256 i = 0; i < status.metrics.length; i++) {
            currentMetrics[i] = status.metrics[i];
        }
        return (status.state, currentMetrics, status.timestamp);
     }

     // Function to retrieve the last heartbeat timestamp for a critical unit
     function getCriticalUnitHeartbeat(bytes32 unitId) public view returns (uint256 lastTimestamp) {
         return criticalUnitsHeartbeats[unitId];
     }
}

// --- Footer: System Integration Notes & Potential Issues (MVP) ---
/*
This MVP smart contract serves as an on-chain state representation and validation layer
for off-chain supercomputer monitoring. It is designed for integration with external systems
that collect data and interact with the contract.

**Potential Integration Issues & Considerations in a Blockchain Context:**
- [Issue 1]: **Data Delivery Reliability and Cost:** Submitting status reports and heartbeats requires sending transactions, incurring gas costs and depending on blockchain network availability and transaction confirmation times. Delayed or failed transactions mean the on-chain state is stale relative to the off-chain system.
- [Resolution/Mitigation 1]: Off-chain systems must implement robust transaction management (retries, gas price optimization) and potentially use a dedicated relayer network or meta-transactions for cost abstraction. Batched reports (as in `reportSubsystemStatuses`) help amortize gas costs.
- [Issue 2]: **Off-chain Data Integrity and Trust:** The contract trusts the data submitted by the designated reporters/units (currently `onlyOwner` for MVP simplicity). There's no inherent way for the contract to verify the truthfulness or accuracy of the off-chain subsystem states or metrics without external oracles or proofs.
- [Resolution/Mitigation 2]: Implement strong access control for reporting functions (e.g., specific addresses per subsystem/unit). Consider using cryptographic proofs (e.g., zero-knowledge proofs) to verify aspects of the off-chain state before reporting, or a multi-signature/DAO scheme for critical state updates.
- [Issue 3]: **Timing Model Mismatch:** Smart contract time (`block.timestamp`, block number) is not wall-clock time. Synchronous operations and precise real-time timeouts as implemented in the TypeScript artifact are not possible. The heartbeat check is based on block height/timestamp differences, which can be variable and potentially manipulated (e.g., miner timestamp manipulation within limits).
- [Resolution/Mitigation 3]: Design off-chain systems to be resilient to blockchain timing variations. Rely on blockchain time only for relative ordering and approximate intervals. Off-chain components must handle precise real-time synchronization and reaction. The smart contract provides an auditable record and state validation, but not real-time control.
- [Issue 4]: **State Staleness:** The contract's view of the system state is only updated when a transaction is successfully processed. It is always potentially slightly behind the true real-time state of the off-chain supercomputer.
- [Resolution/Mitigation 4]: Implement off-chain monitoring systems that consume blockchain events (`SystemStateUpdated`, `CriticalUnitHeartbeatMissed`, `CriticalEventLogged`, etc.) to get near real-time updates on the *on-chain* validated state. Use off-chain systems for immediate real-time reactions and the smart contract for auditable state, policy enforcement, and dispute resolution layer.
- [Issue 5]: **Complexity of On-Chain Calculations:** Complex mathematical or statistical analysis on metrics for equilibrium checks can be computationally expensive and hit gas limits. Storing large amounts of historical metric data on-chain is prohibitively expensive.
- [Resolution/Mitigation 5]: Keep on-chain equilibrium checks mathematically simple (e.g., checks against static thresholds or basic averages/sums within a single report batch). Offload complex analysis, anomaly detection, and historical trend monitoring to off-chain systems. The contract can store aggregated snapshots or summary statistics rather than raw data.
*/
```