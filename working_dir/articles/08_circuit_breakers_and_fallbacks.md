# Circuit Breakers and Fallbacks for Trading Agents

## Introduction: When Autonomy Meets Reality

Trading systems operate in unforgiving environments where milliseconds matter and errors compound rapidly. An autonomous trading agent executing a flawed strategy can accumulate catastrophic losses before human intervention is possible. A malfunctioning risk calculation propagating through multiple systems can trigger cascading failures. A dependency on an external market data feed that becomes unavailable can leave agents operating blind.

The financial services industry learned these lessons through painful experience: the 2010 Flash Crash, the 2012 Knight Capital trading glitch that lost $440 million in 45 minutes, and countless smaller incidents where automated systems amplified rather than contained problems. These events share a common characteristic: systems continued operating autonomously even after conditions indicated they should halt or degrade gracefully.

Circuit breakers and fallback mechanisms—borrowed from electrical engineering and adapted for software systems—provide the defensive infrastructure that makes autonomous trading agents deployable in production. This guide explores how to implement these protective patterns, when to trigger them, and how to design fallback behaviors that maintain business continuity while preventing catastrophic failures.

## Understanding Circuit Breakers

### The Electrical Analogy

In electrical systems, circuit breakers detect overcurrent conditions and interrupt power flow to prevent equipment damage or fire. Key characteristics:

**Automatic Detection:** Breakers sense current levels and trip automatically when thresholds are exceeded.

**Immediate Action:** Interruption occurs in milliseconds, preventing damage.

**Manual Reset:** After tripping, breakers must be manually reset, forcing investigation before restoration.

**Graceful Failure:** Power interruption is preferable to equipment destruction or fire.

### Software Circuit Breakers

In software systems, circuit breakers monitor dependencies (external APIs, databases, microservices) and prevent cascading failures.

**States:**

**Closed (Normal Operation):** Requests flow through to dependency. System monitors failure rates and latency.

**Open (Broken):** Circuit has tripped. Requests immediately fail without attempting to reach dependency. This prevents wasting resources on operations likely to fail and gives failing dependency time to recover.

**Half-Open (Testing Recovery):** After timeout period, circuit allows limited test requests to determine if dependency has recovered. If successful, circuit closes. If failures continue, circuit reopens.

**Key Metrics:**

- **Failure Rate:** Percentage of requests failing (errors, timeouts, exceptions)
- **Latency:** Response time distribution (slow responses may indicate degradation)
- **Volume:** Request rate (to distinguish transient issues from systemic problems)

### Implementation: Basic Circuit Breaker

```python
from enum import Enum
from datetime import datetime, timedelta
from collections import deque

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(
        self,
        name,
        failure_threshold=0.5,  # 50% failure rate
        success_threshold=0.8,  # 80% success to close
        timeout_seconds=60,     # Time before testing recovery
        window_size=100         # Number of recent requests to evaluate
    ):
        self.name = name
        self.state = CircuitState.CLOSED
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timedelta(seconds=timeout_seconds)
        self.window_size = window_size
        
        self.opened_at = None
        self.recent_results = deque(maxlen=window_size)
        self.half_open_attempts = 0
        self.max_half_open_attempts = 10
    
    def call(self, func, *args, **kwargs):
        """Execute function through circuit breaker"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_recovery():
                self.state = CircuitState.HALF_OPEN
                self.half_open_attempts = 0
            else:
                raise CircuitBreakerOpenError(f"Circuit {self.name} is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        
        except Exception as e:
            self._record_failure()
            raise
    
    def _record_success(self):
        self.recent_results.append(True)
        
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_attempts += 1
            if self._recovery_successful():
                self._close_circuit()
    
    def _record_failure(self):
        self.recent_results.append(False)
        
        if self.state == CircuitState.CLOSED:
            if self._should_trip():
                self._open_circuit()
        
        elif self.state == CircuitState.HALF_OPEN:
            # Failure during recovery testing
            self._open_circuit()
    
    def _should_trip(self):
        if len(self.recent_results) < 10:  # Minimum sample size
            return False
        
        failures = sum(1 for result in self.recent_results if not result)
        failure_rate = failures / len(self.recent_results)
        
        return failure_rate >= self.failure_threshold
    
    def _should_attempt_recovery(self):
        if self.opened_at is None:
            return False
        
        elapsed = datetime.now() - self.opened_at
        return elapsed >= self.timeout
    
    def _recovery_successful(self):
        if self.half_open_attempts < self.max_half_open_attempts:
            return False
        
        successes = sum(1 for result in list(self.recent_results)[-self.max_half_open_attempts:] if result)
        success_rate = successes / self.max_half_open_attempts
        
        return success_rate >= self.success_threshold
    
    def _open_circuit(self):
        self.state = CircuitState.OPEN
        self.opened_at = datetime.now()
        self._trigger_alerts(f"Circuit {self.name} OPENED due to failures")
    
    def _close_circuit(self):
        self.state = CircuitState.CLOSED
        self.opened_at = None
        self._trigger_alerts(f"Circuit {self.name} CLOSED - recovered")
    
    def _trigger_alerts(self, message):
        # Integration with monitoring/alerting system
        print(f"ALERT: {message}")
```

## Circuit Breakers for Trading Systems

### Trading-Specific Triggers

Financial trading requires additional circuit breaker triggers beyond generic failure detection:

**Loss Thresholds:**
```python
class TradingCircuitBreaker(CircuitBreaker):
    def __init__(self, *args, max_loss_per_hour=10000, max_loss_per_day=50000, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_loss_per_hour = max_loss_per_hour
        self.max_loss_per_day = max_loss_per_day
        self.hourly_pnl = deque(maxlen=3600)  # Track last hour
        self.daily_pnl = []
    
    def check_pnl_limits(self, current_pnl):
        """Check if PnL breaches thresholds"""
        self.hourly_pnl.append(current_pnl)
        self.daily_pnl.append(current_pnl)
        
        hourly_loss = sum(p for p in self.hourly_pnl if p < 0)
        daily_loss = sum(p for p in self.daily_pnl if p < 0)
        
        if abs(hourly_loss) >= self.max_loss_per_hour:
            self._open_circuit()
            raise TradingHaltError(f"Hourly loss limit exceeded: {hourly_loss}")
        
        if abs(daily_loss) >= self.max_loss_per_day:
            self._open_circuit()
            raise TradingHaltError(f"Daily loss limit exceeded: {daily_loss}")
```

**Position Limits:**
```python
def check_position_limits(self, position):
    """Halt trading if positions exceed limits"""
    if abs(position) > self.max_position:
        self._open_circuit()
        raise TradingHaltError(f"Position limit exceeded: {position}")
    
    if self.concentration_ratio(position) > self.max_concentration:
        self._open_circuit()
        raise TradingHaltError(f"Portfolio concentration too high")
```

**Market Condition Triggers:**
```python
def check_market_conditions(self, market_data):
    """Halt trading during abnormal market conditions"""
    volatility = calculate_volatility(market_data)
    spread = market_data['ask'] - market_data['bid']
    volume = market_data['volume']
    
    if volatility > self.max_volatility:
        self._open_circuit()
        raise TradingHaltError(f"Excessive volatility: {volatility}")
    
    if spread / market_data['mid'] > self.max_spread_pct:
        self._open_circuit()
        raise TradingHaltError(f"Excessive spread: {spread}")
    
    if volume < self.min_volume:
        self._open_circuit()
        raise TradingHaltError(f"Insufficient liquidity: {volume}")
```

**Data Quality Checks:**
```python
def validate_market_data(self, data):
    """Halt if market data is stale or invalid"""
    data_age = datetime.now() - data['timestamp']
    
    if data_age > timedelta(seconds=5):
        self._open_circuit()
        raise TradingHaltError(f"Stale market data: {data_age.total_seconds()}s old")
    
    if data['ask'] <= data['bid']:
        self._open_circuit()
        raise TradingHaltError("Invalid market data: ask <= bid")
    
    if abs(data['mid'] - data['last_mid']) / data['last_mid'] > 0.1:
        self._open_circuit()
        raise TradingHaltError("Suspicious price move: >10% in single tick")
```

## Fallback Mechanisms

When primary systems fail, fallback mechanisms provide degraded but safe operation.

### Fallback Pattern 1: Degraded Functionality

```python
class TradingAgent:
    def __init__(self):
        self.primary_data_feed = MarketDataAPI()
        self.fallback_data_feed = BackupMarketDataAPI()
        self.circuit_breaker = CircuitBreaker("market_data")
    
    def get_market_data(self, symbol):
        """Get market data with fallback"""
        try:
            return self.circuit_breaker.call(
                self.primary_data_feed.get_quote,
                symbol
            )
        except CircuitBreakerOpenError:
            # Primary feed unavailable, use fallback
            return self.fallback_data_feed.get_quote(symbol)
```

### Fallback Pattern 2: Cached Data

```python
class DataService:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = timedelta(minutes=5)
    
    def get_data(self, key):
        try:
            data = self.circuit_breaker.call(self.fetch_from_api, key)
            self.cache[key] = {
                'data': data,
                'timestamp': datetime.now()
            }
            return data
        
        except CircuitBreakerOpenError:
            # API unavailable, use cached data if available
            if key in self.cache:
                cached = self.cache[key]
                age = datetime.now() - cached['timestamp']
                
                if age < self.cache_ttl:
                    return cached['data']  # Cache still valid
                else:
                    raise DataUnavailableError("API down and cache expired")
            else:
                raise DataUnavailableError("API down and no cached data")
```

### Fallback Pattern 3: Conservative Defaults

```python
class RiskManager:
    def calculate_position_size(self, signal_strength, volatility):
        """Calculate position size with fallbacks"""
        try:
            # Sophisticated risk model
            return self.circuit_breaker.call(
                self.advanced_risk_model,
                signal_strength,
                volatility
            )
        except CircuitBreakerOpenError:
            # Risk model unavailable, use conservative defaults
            base_size = 100
            volatility_adjustment = max(0.5, 1.0 - volatility)
            return int(base_size * volatility_adjustment * 0.5)  # Half normal size
```

### Fallback Pattern 4: Human Escalation

```python
class TradeExecutor:
    def execute_trade(self, trade_request):
        """Execute trade with human escalation fallback"""
        # Check automated execution conditions
        if not self.can_execute_automatically(trade_request):
            # Fallback to human approval
            return self.queue_for_human_review(trade_request)
        
        try:
            return self.circuit_breaker.call(
                self.execute_automated,
                trade_request
            )
        except CircuitBreakerOpenError:
            # Automated execution unavailable
            if trade_request['urgency'] == 'high':
                # Escalate to manual execution
                return self.queue_for_immediate_human_execution(trade_request)
            else:
                # Can wait for system recovery
                return self.queue_for_later_execution(trade_request)
```

## Comprehensive Trading Agent Protection

```python
class ProtectedTradingAgent:
    def __init__(self):
        # Circuit breakers for dependencies
        self.market_data_breaker = CircuitBreaker("market_data")
        self.execution_breaker = CircuitBreaker("execution")
        self.risk_breaker = CircuitBreaker("risk_calculation")
        
        # Trading-specific breakers
        self.pnl_breaker = TradingCircuitBreaker(
            "pnl_limits",
            max_loss_per_hour=10000,
            max_loss_per_day=50000
        )
        
        # State tracking
        self.current_position = 0
        self.current_pnl = 0
        self.trades_today = []
    
    def trading_loop(self):
        """Main trading loop with comprehensive protection"""
        while True:
            try:
                # Check PnL limits
                self.pnl_breaker.check_pnl_limits(self.current_pnl)
                
                # Get market data (with circuit breaker)
                market_data = self.market_data_breaker.call(
                    self.get_market_data
                )
                
                # Validate data quality
                self.validate_data_quality(market_data)
                
                # Calculate signal (with circuit breaker)
                signal = self.risk_breaker.call(
                    self.calculate_signal,
                    market_data
                )
                
                # Generate trade if signal strong enough
                if abs(signal) > self.signal_threshold:
                    trade = self.generate_trade(signal, market_data)
                    
                    # Execute (with circuit breaker)
                    result = self.execution_breaker.call(
                        self.execute_trade,
                        trade
                    )
                    
                    self.update_position(result)
                    self.update_pnl(result)
                
                time.sleep(1)  # Trading frequency control
            
            except CircuitBreakerOpenError as e:
                # Circuit breaker tripped - enter safe mode
                self.enter_safe_mode(str(e))
                time.sleep(60)  # Wait before retry
            
            except TradingHaltError as e:
                # Trading limits exceeded - full halt
                self.halt_trading(str(e))
                self.notify_operators(str(e))
                break
            
            except Exception as e:
                # Unexpected error
                self.log_error(e)
                self.enter_safe_mode(f"Unexpected error: {e}")
                time.sleep(60)
    
    def enter_safe_mode(self, reason):
        """Safe mode: close positions, halt new trades"""
        print(f"Entering safe mode: {reason}")
        
        try:
            # Attempt to close open positions
            if self.current_position != 0:
                self.close_all_positions()
        except Exception as e:
            print(f"Failed to close positions in safe mode: {e}")
            self.notify_operators(f"URGENT: Manual intervention required")
    
    def halt_trading(self, reason):
        """Full trading halt"""
        print(f"TRADING HALTED: {reason}")
        
        # Disable all trading
        self.trading_enabled = False
        
        # Generate incident report
        self.generate_incident_report(reason)
        
        # Notify all stakeholders
        self.notify_operators(f"TRADING HALTED: {reason}")
```

## Testing Circuit Breakers

### Test 1: Failure Threshold Triggering

```python
def test_circuit_breaker_opens_on_failures():
    breaker = CircuitBreaker("test", failure_threshold=0.5, window_size=10)
    
    def failing_function():
        raise Exception("Simulated failure")
    
    # Execute 6 failures out of 10 attempts (60% failure rate)
    for i in range(10):
        try:
            if i < 6:
                breaker.call(failing_function)
            else:
                breaker.call(lambda: "success")
        except Exception:
            pass
    
    # Circuit should be open
    assert breaker.state == CircuitState.OPEN
    
    # Subsequent calls should fail fast
    with pytest.raises(CircuitBreakerOpenError):
        breaker.call(lambda: "test")
```

### Test 2: Recovery Testing

```python
def test_circuit_breaker_recovery():
    breaker = CircuitBreaker("test", timeout_seconds=1)
    
    # Trip circuit
    for _ in range(10):
        try:
            breaker.call(lambda: exec('raise Exception()'))
        except:
            pass
    
    assert breaker.state == CircuitState.OPEN
    
    # Wait for timeout
    time.sleep(2)
    
    # Next successful call should enter half-open
    breaker.call(lambda: "success")
    assert breaker.state == CircuitState.HALF_OPEN
    
    # Sustained success should close circuit
    for _ in range(10):
        breaker.call(lambda: "success")
    
    assert breaker.state == CircuitState.CLOSED
```

### Test 3: Trading Limits

```python
def test_pnl_circuit_breaker():
    breaker = TradingCircuitBreaker("test", max_loss_per_hour=1000)
    
    # Accumulate losses
    for loss in [-100, -200, -300, -400]:  # Total: -1000
        breaker.check_pnl_limits(loss)
    
    # Next loss should trip circuit
    with pytest.raises(TradingHaltError):
        breaker.check_pnl_limits(-100)
    
    assert breaker.state == CircuitState.OPEN
```

## Operational Considerations

### Alert Configuration

Circuit breaker state changes should trigger immediate alerts:

```python
def _trigger_alerts(self, message):
    severity = "CRITICAL" if self.state == CircuitState.OPEN else "WARNING"
    
    alert_service.send(
        severity=severity,
        title=f"Circuit Breaker: {self.name}",
        message=message,
        metadata={
            'circuit_name': self.name,
            'state': self.state.value,
            'failure_rate': self.get_failure_rate(),
            'timestamp': datetime.now().isoformat()
        },
        notify_channels=['pagerduty', 'slack', 'email']
    )
```

### Monitoring Dashboards

Track circuit breaker states in real-time dashboards:

- Circuit state (closed/open/half-open)
- Failure rates and trends
- Time in current state
- Historical trip events
- Recovery attempt outcomes

### Manual Override Capabilities

Provide operators manual control:

```python
def force_open(self, reason):
    """Manually trip circuit"""
    self._open_circuit()
    self._log_manual_intervention("forced_open", reason)

def force_close(self, reason):
    """Manually close circuit (use with caution)"""
    self._close_circuit()
    self._log_manual_intervention("forced_close", reason)
```

## Conclusion

Circuit breakers and fallbacks are not optional for production trading agents—they are foundational safety mechanisms that prevent autonomous systems from amplifying failures into disasters. The financial industry's painful history of algorithmic trading incidents demonstrates what happens when systems lack appropriate safeguards.

Implementing comprehensive circuit breakers requires understanding both general software resilience patterns and domain-specific trading constraints. Loss limits, position controls, market condition monitoring, and data quality checks must be built into every autonomous trading system from inception, not retrofitted after incidents occur.

Organizations that deploy trading agents protected by well-designed circuit breakers and fallback mechanisms will operate with confidence. Those that neglect these safeguards will discover—likely expensively—why defensive architecture matters in financial systems. The question is not whether circuit breakers are needed, but how comprehensively they are implemented and how rigorously they are tested.

The stakes are too high for anything less than comprehensive protection.
