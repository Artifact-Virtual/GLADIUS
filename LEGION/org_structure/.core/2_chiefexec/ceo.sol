```rust
#![cfg_attr(not(feature = "std"), no_std)]

#[ink::contract]
mod chief_executive_officer {
    use ink::prelude::string::String;
    use ink::prelude::vec::Vec;
    use ink::storage::Lazy;

    /// Defines the possible equilibrium states of the supercomputer system.
    #[derive(scale::Encode, scale::Decode, Debug, PartialEq, Eq, Copy, Clone)]
    #[cfg_attr(feature = "ink-generate-abi", derive(ink::generate_abi::TypeInfo))]
    pub enum SystemState {
        Optimized,
        Stable,
        Warning,
        Critical,
    }

    impl Default for SystemState {
        fn default() -> Self {
            SystemState::Stable
        }
    }

    /// Represents a macro resource allocation policy.
    /// Priorities should sum to 1000 (scaled integer for smart contract).
    #[derive(scale::Encode, scale::Decode, Debug, PartialEq, Eq, Copy, Clone)]
    #[cfg_attr(feature = "ink-generate-abi", derive(ink::generate_abi::TypeInfo))]
    pub struct ResourceAllocationPolicy {
        pub compute_priority: u32, // Scaled, e.g., 300 for 30%
        pub memory_priority: u32,  // Scaled
        pub network_priority: u32, // Scaled
        pub storage_priority: u32, // Scaled
                                  // Sum should be 1000
    }

    /// Represents system-wide performance targets.
    /// Latency in milliseconds, Error Rate scaled (e.g., 10 for 0.1%).
    #[derive(scale::Encode, scale::Decode, Debug, PartialEq, Eq, Copy, Clone)]
    #[cfg_attr(feature = "ink-generate-abi", derive(ink::generate_abi::TypeInfo))]
    pub struct PerformanceTargets {
        pub min_global_throughput: u32, // Tasks completed per second
        pub max_task_latency: u32,      // Maximum allowed latency (ms)
        pub max_error_rate_scaled: u32, // Maximum allowed system error rate (scaled, e.g., 10 for 0.1%)
    }

    /// Represents aggregate system metrics.
    /// Utilization and congestion scaled (e.g., 900 for 90%).
    #[derive(scale::Encode, scale::Decode, Debug, PartialEq, Eq, Copy, Clone)]
    #[cfg_attr(feature = "ink-generate-abi", derive(ink::generate_abi::TypeInfo))]
    pub struct GlobalSystemMetrics {
        pub aggregate_cpu_utilization_scaled: u32,    // Scaled, e.g., 850 for 85%
        pub aggregate_memory_utilization_scaled: u32, // Scaled
        pub network_congestion_index_scaled: u32,   // Scaled
        pub active_task_count: u32,                   // Total tasks running
        pub failed_task_count_last_cycle: u32,        // Tasks failed in the last cycle
    }

    /// Defines the storage of the contract.
    #[ink(storage)]
    pub struct ChiefExecutiveOfficerArtifact {
        system_state: SystemState,
        current_policy: Option<ResourceAllocationPolicy>,
        current_targets: Option<PerformanceTargets>,
        recalibration_needed: bool, // Flag indicating recalibration sequence should be initiated externally
    }

    /// Contract events.
    #[ink(event)]
    pub struct RecalibrationInitiated {
        #[ink(topic)]
        from_state: SystemState,
        #[ink(topic)]
        reason: String, // e.g., "Warning State", "Critical State"
    }

    #[ink(event)]
    pub struct PolicyUpdated {
        policy: ResourceAllocationPolicy,
    }

    #[ink(event)]
    pub struct TargetsUpdated {
        targets: PerformanceTargets,
    }

    #[ink(event)]
    pub struct StateEvaluated {
        new_state: SystemState,
        metrics: GlobalSystemMetrics,
    }


    /// Custom error type for the contract.
    #[derive(scale::Encode, scale::Decode, Debug, PartialEq, Eq)]
    #[cfg_attr(feature = "ink-generate-abi", derive(ink::generate_abi::TypeInfo))]
    pub enum Error {
        PolicyPrioritiesInvalid,
        TargetsMathematicallyUnachievable,
        PolicyOrTargetsNotSet,
        RecalibrationNotNeeded,
        MetricsValidationError, // For future validation of input metrics
    }

    impl ChiefExecutiveOfficerArtifact {
        /// Constructor: Initializes the contract with default state.
        #[ink(constructor)]
        pub fn new() -> Self {
            // Initialize with default or last known safe state
            let default_policy = ResourceAllocationPolicy {
                compute_priority: 300, // 30%
                memory_priority: 300,  // 30%
                network_priority: 200, // 20%
                storage_priority: 200, // 20%
            };
            let default_targets = PerformanceTargets {
                min_global_throughput: 1000,
                max_task_latency: 50,
                max_error_rate_scaled: 10, // 0.1%
            };

            Self {
                system_state: SystemState::Stable,
                current_policy: Some(default_policy),
                current_targets: Some(default_targets),
                recalibration_needed: false,
            }
        }

        /// Hardcoded task 1: Sets and validates system-wide performance targets.
        /// Targets must be mathematically consistent and achievable within perceived system limits.
        /// This acts as a synchronous control signal for performance management across all units.
        #[ink(message)]
        pub fn set_performance_targets(
            &mut self,
            new_targets: PerformanceTargets,
        ) -> Result<(), Error> {
            // Synchronous validation: Check logical/mathematical feasibility based on known max capacity
            // These limits are hardcoded for MVP, in a real system they would be dynamic/oracle-fed
            const MAX_THEORETICAL_THROUGHPUT: u32 = 5000;
            const MIN_THEORETICAL_LATENCY: u32 = 5;
            const MIN_THEORETICAL_ERROR_RATE_SCALED: u32 = 1; // 0.01%

            if new_targets.min_global_throughput > MAX_THEORETICAL_THROUGHPUT
                || new_targets.max_task_latency < MIN_THEORETICAL_LATENCY
                || new_targets.max_error_rate_scaled < MIN_THEORETICAL_ERROR_RATE_SCALED
            {
                return Err(Error::TargetsMathematicallyUnachievable);
            }

            // Assume successful validation and 'synchronous' assignment (atomic state update)
            self.current_targets = Some(new_targets);
            self.env().emit_event(TargetsUpdated {
                targets: new_targets,
            });

            // Note: In a real system, updating targets might trigger an immediate state evaluation
            // or require propagation to dependent components off-chain.
            // For this MVP, we just update the state and emit an event.
            // A subsequent call to evaluate_system_state is needed to update the system_state.

            Ok(())
        }

        /// Hardcoded task 2: Distributes a macro resource allocation policy across the system.
        /// The policy dictates how resources should be prioritized at a high level.
        /// This distribution is conceptually synchronous; all relevant subsystems should receive
        /// and acknowledge the policy consistently (represented by atomic state update).
        #[ink(message)]
        pub fn distribute_resource_policy(
            &mut self,
            policy: ResourceAllocationPolicy,
        ) -> Result<(), Error> {
            // Synchronous validation check: Ensure sum of priorities equals 1000
            let sum_priorities = policy.compute_priority
                + policy.memory_priority
                + policy.network_priority
                + policy.storage_priority;
            if sum_priorities != 1000 {
                return Err(Error::PolicyPrioritiesInvalid);
            }

            // Simulate synchronous distribution requiring consistent state update
            // In a blockchain, this is achieved via the atomic transaction.
            self.current_policy = Some(policy);
            self.env().emit_event(PolicyUpdated { policy });

            // Note: Similar to targets, policy update might trigger subsequent actions off-chain.
            // For this MVP, we just update state and emit event.

            Ok(())
        }

        /// Hardcoded task 3: Evaluates global system metrics against targets and policy to determine equilibrium state.
        /// Requires synchronously collected metrics to provide a consistent snapshot.
        /// In a real system, metrics would likely come from an oracle.
        #[ink(message)]
        pub fn evaluate_system_state(
            &mut self,
            metrics: GlobalSystemMetrics,
        ) -> Result<SystemState, Error> {
            let targets = self.current_targets.ok_or(Error::PolicyOrTargetsNotSet)?;
            let policy = self.current_policy.ok_or(Error::PolicyOrTargetsNotSet)?;

            // Assume metrics provided are from a synchronous collection point (e.g., oracle)
            let GlobalSystemMetrics {
                aggregate_cpu_utilization_scaled,
                aggregate_memory_utilization_scaled,
                network_congestion_index_scaled,
                active_task_count,
                failed_task_count_last_cycle,
            } = metrics;
            let PerformanceTargets {
                min_global_throughput,
                max_task_latency,
                max_error_rate_scaled,
            } = targets;
            let ResourceAllocationPolicy {
                compute_priority,
                memory_priority,
                network_priority,
                storage_priority,
            } = policy; // Unused in this simple example, but available for complex logic

            // Mathematical/Logical checks for equilibrium based on targets (examples)
            let mut new_state = SystemState::Stable;

            // Check task failure ratio against target error rate
            // Avoid division by zero if no tasks are active
            let task_failure_ratio_scaled = if active_task_count > 0 {
                (failed_task_count_last_cycle as u64 * 10000) // Scale to 10000 for precision
                    .checked_div(active_task_count as u64)
                    .unwrap_or(0) as u32 // Handle potential overflow/division error defensively
            } else {
                0
            };

            // max_error_rate_scaled is expected in parts per 100 (e.g. 10 for 0.1%), so scale it to match task_failure_ratio_scaled
            // If task_failure_ratio_scaled (parts per 10000) > max_error_rate_scaled (parts per 100) * 100
            if task_failure_ratio_scaled > max_error_rate_scaled * 100 {
                ink::env::debug_println!(
                    "Warning: High task failure ratio (scaled {}), exceeds target (scaled {})",
                    task_failure_ratio_scaled,
                    max_error_rate_scaled * 100
                );
                if new_state != SystemState::Critical {
                    new_state = SystemState::Warning;
                }
            }

            // Check resource utilization against thresholds (simplified, not directly using policy)
            // Thresholds are example values (scaled to 1000)
            const CRITICAL_UTIL_THRESHOLD: u32 = 950; // 95%
            const WARNING_UTIL_THRESHOLD: u32 = 900;  // 90%
            const CRITICAL_CONGESTION_THRESHOLD: u32 = 900; // 90%
            const WARNING_CONGESTION_THRESHOLD: u32 = 700; // 70%

            if aggregate_cpu_utilization_scaled >= CRITICAL_UTIL_THRESHOLD
                || aggregate_memory_utilization_scaled >= CRITICAL_UTIL_THRESHOLD
                || network_congestion_index_scaled >= CRITICAL_CONGESTION_THRESHOLD
            {
                ink::env::debug_println!("Critical: Extreme resource saturation detected.");
                new_state = SystemState::Critical;
            } else if aggregate_cpu_utilization_scaled >= WARNING_UTIL_THRESHOLD
                || aggregate_memory_utilization_scaled >= WARNING_UTIL_THRESHOLD
                || network_congestion_index_scaled >= WARNING_CONGESTION_THRESHOLD
            {
                 ink::env::debug_println!("Warning: High resource utilization or congestion detected.");
                if new_state != SystemState::Critical {
                    new_state = SystemState::Warning;
                }
            }

            // Determine Optimized state (example: low load, zero failures, positive active tasks)
            const OPTIMIZED_UTIL_THRESHOLD: u32 = 500; // 50%
            const OPTIMIZED_CONGESTION_THRESHOLD: u32 = 300; // 30%
            if failed_task_count_last_cycle == 0
                && active_task_count > 0
                && aggregate_cpu_utilization_scaled < OPTIMIZED_UTIL_THRESHOLD
                && aggregate_memory_utilization_scaled < OPTIMIZED_UTIL_THRESHOLD
                && network_congestion_index_scaled < OPTIMIZED_CONGESTION_THRESHOLD
            {
                 ink::env::debug_println!("System state evaluated as Optimized.");
                 new_state = SystemState::Optimized;
            } else {
                ink::env::debug_println!("System state not Optimized based on criteria.");
            }


            // If state is Critical or Warning, set recalibration flag
            if new_state == SystemState::Critical || new_state == SystemState::Warning {
                self.recalibration_needed = true;
            } else {
                self.recalibration_needed = false; // Recalibration is not indicated if state is stable/optimized
            }

            // Atomically update the system state
            self.system_state = new_state;

            self.env().emit_event(StateEvaluated {
                new_state: self.system_state,
                metrics,
            });

            Ok(self.system_state)
        }

        /// Initiates a system-wide recalibration based on current state.
        /// This action itself requires complex coordination across many subsystems off-chain.
        /// The smart contract *indicates* the need for recalibration via state and event,
        /// but the actual complex recalibration sequence must be handled by off-chain agents.
        #[ink(message)]
        pub fn initiate_system_recalibration(&mut self) -> Result<(), Error> {
            if self.system_state == SystemState::Critical || self.system_state == SystemState::Warning {
                if self.recalibration_needed {
                     ink::env::debug_println!("Initiating system recalibration via flag/event.");
                    // Signal off-chain listeners that recalibration is needed
                    let reason = match self.system_state {
                        SystemState::Warning => String::from("Warning State"),
                        SystemState::Critical => String::from("Critical State"),
                        _ => String::from("Unknown"), // Should not happen based on condition
                    };
                     self.env().emit_event(RecalibrationInitiated {
                         from_state: self.system_state,
                         reason,
                     });

                    // Reset the internal flag, assuming off-chain system will handle it
                    self.recalibration_needed = false;

                    // Optionally set state to something like 'Recalibrating' if such a state existed
                    // For MVP, we might optimistically set to Stable, or leave as is until new metrics arrive.
                    // Leaving as is is safer for MVP.

                    Ok(())
                } else {
                    // State is Warning/Critical, but recalibration was already initiated and flag reset
                    // Off-chain system should still be working, or there's an issue.
                    // Don't re-emit event if flag is false.
                    ink::env::debug_println!("Recalibration already indicated/in progress.");
                    Ok(()) // Indicate the call was processed, even if no new action taken
                }
            } else {
                 ink::env::debug_println!("System state is stable or optimized. No recalibration needed.");
                Err(Error::RecalibrationNotNeeded)
            }
        }


        /// Getter for the current equilibrium state.
        #[ink(message)]
        pub fn get_equilibrium_state(&self) -> SystemState {
            self.system_state
        }

        /// Getter for the current targets.
        #[ink(message)]
        pub fn get_current_targets(&self) -> Option<PerformanceTargets> {
            self.current_targets
        }

        /// Getter for the current policy.
        #[ink(message)]
        pub fn get_current_policy(&self) -> Option<ResourceAllocationPolicy> {
            self.current_policy
        }

         /// Getter for the recalibration needed flag.
        #[ink(message)]
        pub fn is_recalibration_needed(&self) -> bool {
            self.recalibration_needed
        }
    }

    /// Unit tests in Rust.
    #[cfg(test)]
    mod tests {
        /// Imports all the definitions from the outer scope so we can use them in tests.
        use super::*;

        /// Imports `ink_lang::test`.
        #[ink::test]
        fn it_works() {
            let mut ceo = ChiefExecutiveOfficerArtifact::new();
            assert_eq!(ceo.get_equilibrium_state(), SystemState::Stable);
            assert!(ceo.get_current_policy().is_some());
            assert!(ceo.get_current_targets().is_some());
        }

        #[ink::test]
        fn set_targets_valid() {
            let mut ceo = ChiefExecutiveOfficerArtifact::new();
            let initial_targets = ceo.get_current_targets().unwrap();
            let new_targets = PerformanceTargets {
                min_global_throughput: 1200,
                max_task_latency: 40,
                max_error_rate_scaled: 5, // 0.05%
            };
            let result = ceo.set_performance_targets(new_targets);
            assert!(result.is_ok());
            assert_eq!(ceo.get_current_targets().unwrap(), new_targets);
            // State should still be stable until evaluate_system_state is called
            assert_eq!(ceo.get_equilibrium_state(), SystemState::Stable);
        }

        #[ink::test]
        fn set_targets_invalid() {
            let mut ceo = ChiefExecutiveOfficerArtifact::new();
            // Target below theoretical minimum latency
            let new_targets_invalid_latency = PerformanceTargets {
                min_global_throughput: 1200,
                max_task_latency: 3, // Invalid: < 5
                max_error_rate_scaled: 5,
            };
             let result_latency = ceo.set_performance_targets(new_targets_invalid_latency);
            assert_eq!(result_latency, Err(Error::TargetsMathematicallyUnachievable));

            // Target above theoretical maximum throughput
             let new_targets_invalid_throughput = PerformanceTargets {
                min_global_throughput: 6000, // Invalid: > 5000
                max_task_latency: 40,
                max_error_rate_scaled: 5,
            };
             let result_throughput = ceo.set_performance_targets(new_targets_invalid_throughput);
            assert_eq!(result_throughput, Err(Error::TargetsMathematicallyUnachievable));

            // State should remain stable as set failed
            assert_eq!(ceo.get_equilibrium_state(), SystemState::Stable);
        }

        #[ink::test]
        fn distribute_policy_valid() {
             let mut ceo = ChiefExecutiveOfficerArtifact::new();
             let initial_policy = ceo.get_current_policy().unwrap();
             let new_policy = ResourceAllocationPolicy {
                 compute_priority: 400,
                 memory_priority: 200,
                 network_priority: 300,
                 storage_priority: 100,
             }; // Sum = 1000
             let result = ceo.distribute_resource_policy(new_policy);
             assert!(result.is_ok());
             assert_eq!(ceo.get_current_policy().unwrap(), new_policy);
             // State should still be stable until evaluate_system_state is called
             assert_eq!(ceo.get_equilibrium_state(), SystemState::Stable);
        }

         #[ink::test]
        fn distribute_policy_invalid() {
             let mut ceo = ChiefExecutiveOfficerArtifact::new();
             let new_policy_invalid = ResourceAllocationPolicy {
                 compute_priority: 400,
                 memory_priority: 200,
                 network_priority: 300,
                 storage_priority: 200, // Sum = 1100 (Invalid)
             };
             let result = ceo.distribute_resource_policy(new_policy_invalid);
             assert_eq!(result, Err(Error::PolicyPrioritiesInvalid));

             // State should remain stable as distribution failed
             assert_eq!(ceo.get_equilibrium_state(), SystemState::Stable);
             // Policy should be the initial one
              assert_eq!(ceo.get_current_policy().unwrap().compute_priority, 300);
        }

        #[ink::test]
        fn evaluate_state_stable() {
            let mut ceo = ChiefExecutiveOfficerArtifact::new();
            let metrics = GlobalSystemMetrics {
                 aggregate_cpu_utilization_scaled: 400, // 40%
                 aggregate_memory_utilization_scaled: 450, // 45%
                 network_congestion_index_scaled: 200, // 20%
                 active_task_count: 1000,
                 failed_task_count_last_cycle: 5, // 0.5% failure, target is 0.1% (10 scaled)
            };
            // Current target max_error_rate_scaled: 10 (0.1%)
            // Current failure ratio: 5/1000 = 0.005 (scaled: 50)
            // 50 > 10 * 100 -> False (50 > 1000 False). Error rate check passes.

            let result_state = ceo.evaluate_system_state(metrics);
            assert!(result_state.is_ok());
            assert_eq!(result_state.unwrap(), SystemState::Stable); // Should be Stable based on these metrics and default targets/policy
            assert_eq!(ceo.get_equilibrium_state(), SystemState::Stable);
             assert!(!ceo.is_recalibration_needed());
        }

         #[ink::test]
        fn evaluate_state_warning_high_failure() {
            let mut ceo = ChiefExecutiveOfficerArtifact::new();
             // Set a slightly higher error rate target for this test to make the next metrics trigger Warning
             let higher_error_target = PerformanceTargets {
                min_global_throughput: 1000,
                max_task_latency: 50,
                max_error_rate_scaled: 0, // Target 0% errors
            };
            let _ = ceo.set_performance_targets(higher_error_target);


            let metrics = GlobalSystemMetrics {
                 aggregate_cpu_utilization_scaled: 400, // 40%
                 aggregate_memory_utilization_scaled: 450, // 45%
                 network_congestion_index_scaled: 200, // 20%
                 active_task_count: 1000,
                 failed_task_count_last_cycle: 5, // 0.5% failure
            };
            // Current target max_error_rate_scaled: 0 (0%)
            // Current failure ratio: 5/1000 = 0.005 (scaled: 50)
            // 50 > 0 * 100 -> True (50 > 0 True). Error rate check fails.

            let result_state = ceo.evaluate_system_state(metrics);
            assert!(result_state.is_ok());
            assert_eq!(result_state.unwrap(), SystemState::Warning); // Should be Warning
            assert_eq!(ceo.get_equilibrium_state(), SystemState::Warning);
            assert!(ceo.is_recalibration_needed()); // Should flag recalibration
        }

         #[ink::test]
        fn evaluate_state_critical_saturation() {
            let mut ceo = ChiefExecutiveOfficerArtifact::new();
            let metrics = GlobalSystemMetrics {
                 aggregate_cpu_utilization_scaled: 960, // 96% - Critical
                 aggregate_memory_utilization_scaled: 800, // 80%
                 network_congestion_index_scaled: 750, // 75%
                 active_task_count: 2000,
                 failed_task_count_last_cycle: 10, // 0.5% failure
            };
             // Failure ratio: 10/2000 = 0.005 (scaled: 50). Default target 0.1% (10 scaled).
             // 50 > 10 * 100 -> False (50 > 1000 False). Error rate check passes.
             // BUT, CPU utilization is critical.

            let result_state = ceo.evaluate_system_state(metrics);
            assert!(result_state.is_ok());
            assert_eq!(result_state.unwrap(), SystemState::Critical); // Should be Critical
            assert_eq!(ceo.get_equilibrium_state(), SystemState::Critical);
             assert!(ceo.is_recalibration_needed()); // Should flag recalibration
        }

        #[ink::test]
        fn evaluate_state_optimized() {
             let mut ceo = ChiefExecutiveOfficerArtifact::new();
             let metrics = GlobalSystemMetrics {
                 aggregate_cpu_utilization_scaled: 300, // 30%
                 aggregate_memory_utilization_scaled: 250, // 25%
                 network_congestion_index_scaled: 150, // 15%
                 active_task_count: 500, // Active tasks > 0
                 failed_task_count_last_cycle: 0, // Zero failures
             };
             // Low utilization, low congestion, zero failures, active tasks > 0

             let result_state = ceo.evaluate_system_state(metrics);
             assert!(result_state.is_ok());
             assert_eq!(result_state.unwrap(), SystemState::Optimized); // Should be Optimized
             assert_eq!(ceo.get_equilibrium_state(), SystemState::Optimized);
             assert!(!ceo.is_recalibration_needed()); // Should NOT flag recalibration
        }


         #[ink::test]
         fn initiate_recalibration_critical() {
            let mut ceo = ChiefExecutiveOfficerArtifact::new();
             // Manually set state to Critical and flag needed
             ceo.system_state = SystemState::Critical;
             ceo.recalibration_needed = true; // Assume evaluation already set this

            let result = ceo.initiate_system_recalibration();
            assert!(result.is_ok());
            // Flag should be reset after initiation
            assert!(!ceo.is_recalibration_needed());
            // State remains Critical until new metrics change it
            assert_eq!(ceo.get_equilibrium_state(), SystemState::Critical);
            // Need to test event emission if possible in ink! tests, but current framework limits direct event assertion.
            // Logic check confirms event should be emitted.
         }

        #[ink::test]
         fn initiate_recalibration_not_needed() {
            let mut ceo = ChiefExecutiveOfficerArtifact::new();
             // State is Stable by default, flag is false
             assert_eq!(ceo.get_equilibrium_state(), SystemState::Stable);
             assert!(!ceo.is_recalibration_needed());

            let result = ceo.initiate_system_recalibration();
            assert_eq!(result, Err(Error::RecalibrationNotNeeded));
             // State and flag should remain unchanged
            assert_eq!(ceo.get_equilibrium_state(), SystemState::Stable);
             assert!(!ceo.is_recalibration_needed());
         }
    }
}
```