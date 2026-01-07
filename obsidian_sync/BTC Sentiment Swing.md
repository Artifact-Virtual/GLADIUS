//@version=6
indicator(" Sentiment Swing Master", overlay=true, max_bars_back=500, max_lines_count=500, max_labels_count=500)

// ═══════════════════════════════════════════════════════════════════
// 🎯 ADVANCED INPUTS
// ═══════════════════════════════════════════════════════════════════

// Multi-Timeframe Trend System
htfTrend1 = input.timeframe("W", "Major Trend (Weekly)", group="📊 Multi-Timeframe Structure")
htfTrend2 = input.timeframe("D", "Intermediate Trend (Daily)", group="📊 Multi-Timeframe Structure")
htfTrend3 = input.timeframe("240", "Swing Trend (4H)", group="📊 Multi-Timeframe Structure")

// Advanced Trend Detection
ema8 = input.int(8, "Fast EMA", group="📈 Trend System")
ema21 = input.int(21, "Medium EMA", group="📈 Trend System")
ema55 = input.int(55, "Slow EMA", group="📈 Trend System")
ema200 = input.int(200, "Macro Trend EMA", group="📈 Trend System")

// Momentum & Oscillators
rsiLength = input.int(14, "RSI Length", group="💪 Momentum")
rsiOB = input.float(75, "RSI Extreme Overbought", group="💪 Momentum")
rsiOS = input.float(25, "RSI Extreme Oversold", group="💪 Momentum")
stochLength = input.int(14, "Stochastic Length", group="💪 Momentum")
stochSmooth = input.int(3, "Stochastic Smooth", group="💪 Momentum")

// Volume Analysis
volSmaLength = input.int(20, "Volume SMA Length", group="📊 Volume Profile")
volSpikeMulti = input.float(2.0, "Volume Spike Multiplier", group="📊 Volume Profile")
volClimaxMulti = input.float(3.0, "Volume Climax Multiplier", group="📊 Volume Profile")

// Volatility & ATR
atrLength = input.int(14, "ATR Length", group="💥 Volatility")
atrMulti = input.float(2.5, "ATR Stop Multiplier", group="💥 Volatility")
bbLength = input.int(20, "Bollinger Length", group="💥 Volatility")
bbStdDev = input.float(2.0, "Bollinger StdDev", group="💥 Volatility")

// Market Structure
swingLength = input.int(10, "Swing Detection Length", group="🎯 Structure")
structureLength = input.int(50, "Structure Break Length", group="🎯 Structure")

// Funding Rate Proxy (Using price action)
fundingProxyLength = input.int(8, "Funding Proxy Length", group="🧠 Speculation Metrics")

// Display Options
showAllSignals = input.bool(true, "Show All Signals", group="🎨 Display")
showMajorOnly = input.bool(false, "Major Signals Only", group="🎨 Display")
showStructure = input.bool(true, "Show Market Structure", group="🎨 Display")
showZones = input.bool(true, "Show Key Zones", group="🎨 Display")
showDashboard = input.bool(true, "Show Dashboard", group="🎨 Display")

// ═══════════════════════════════════════════════════════════════════
// 📊 MULTI-TIMEFRAME TREND ANALYSIS
// ═══════════════════════════════════════════════════════════════════

// EMAs for current timeframe
ema8Val = ta.ema(close, ema8)
ema21Val = ta.ema(close, ema21)
ema55Val = ta.ema(close, ema55)
ema200Val = ta.ema(close, ema200)

// Higher Timeframe Trends
htf1_ema21 = request.security(syminfo.tickerid, htfTrend1, ta.ema(close, 21), lookahead=barmerge.lookahead_off)
htf1_ema55 = request.security(syminfo.tickerid, htfTrend1, ta.ema(close, 55), lookahead=barmerge.lookahead_off)
htf1Bull = htf1_ema21 > htf1_ema55

htf2_ema21 = request.security(syminfo.tickerid, htfTrend2, ta.ema(close, 21), lookahead=barmerge.lookahead_off)
htf2_ema55 = request.security(syminfo.tickerid, htfTrend2, ta.ema(close, 55), lookahead=barmerge.lookahead_off)
htf2Bull = htf2_ema21 > htf2_ema55

htf3_ema8 = request.security(syminfo.tickerid, htfTrend3, ta.ema(close, 8), lookahead=barmerge.lookahead_off)
htf3_ema21 = request.security(syminfo.tickerid, htfTrend3, ta.ema(close, 21), lookahead=barmerge.lookahead_off)
htf3Bull = htf3_ema8 > htf3_ema21

// Current Timeframe Trend
trendBull = ema8Val > ema21Val and ema21Val > ema55Val
trendBear = ema8Val < ema21Val and ema21Val < ema55Val
trendNeutral = not trendBull and not trendBear

// Trend Alignment Score (0-4)
trendScore = (close > ema200Val ? 1 : 0) + (htf1Bull ? 1 : 0) + (htf2Bull ? 1 : 0) + (htf3Bull ? 1 : 0)

// ═══════════════════════════════════════════════════════════════════
// 💪 MOMENTUM & OSCILLATORS
// ═══════════════════════════════════════════════════════════════════

// RSI with divergence detection
rsi = ta.rsi(close, rsiLength)
rsiOverbought = rsi > rsiOB
rsiOversold = rsi < rsiOS

// RSI Divergences (pivot detection)
rsiHigh = ta.pivothigh(rsi, 5, 5)
rsiLow = ta.pivotlow(rsi, 5, 5)
priceHigh = ta.pivothigh(high, 5, 5)
priceLow = ta.pivotlow(low, 5, 5)

var float lastRsiHigh = na
var float lastPriceHigh = na
var float lastRsiLow = na
var float lastPriceLow = na

if not na(rsiHigh)
    lastRsiHigh := rsi[5]
    lastPriceHigh := high[5]

if not na(rsiLow)
    lastRsiLow := rsi[5]
    lastPriceLow := low[5]

// Bearish divergence: Price higher high, RSI lower high
bearDiv = not na(priceHigh) and not na(lastPriceHigh) and not na(lastRsiHigh) and 
          priceHigh > lastPriceHigh and rsi[5] < lastRsiHigh and rsi[5] > 50

// Bullish divergence: Price lower low, RSI higher low
bullDiv = not na(priceLow) and not na(lastPriceLow) and not na(lastRsiLow) and 
          priceLow < lastPriceLow and rsi[5] > lastRsiLow and rsi[5] < 50

// Stochastic
stochK = ta.sma(ta.stoch(close, high, low, stochLength), stochSmooth)
stochD = ta.sma(stochK, stochSmooth)
stochOverbought = stochK > 80
stochOversold = stochK < 20
stochBullCross = ta.crossover(stochK, stochD) and stochK < 50
stochBearCross = ta.crossunder(stochK, stochD) and stochK > 50

// ═══════════════════════════════════════════════════════════════════
// 📊 ADVANCED VOLUME ANALYSIS
// ═══════════════════════════════════════════════════════════════════

volSma = ta.sma(volume, volSmaLength)
volSpike = volume > volSma * volSpikeMulti
volClimax = volume > volSma * volClimaxMulti

// Volume character
bullVolume = close > open and volSpike
bearVolume = close < open and volSpike

// Accumulation/Distribution
buyingPressure = close > (high + low) / 2
sellingPressure = close < (high + low) / 2
accumulationBar = buyingPressure and volume > volSma
distributionBar = sellingPressure and volume > volSma

// Volume Momentum
volMomentum = volume / volSma
volTrend = ta.sma(volMomentum, 5)
risingVolume = volTrend > volTrend[1]

// ═══════════════════════════════════════════════════════════════════
// 💥 VOLATILITY ANALYSIS
// ═══════════════════════════════════════════════════════════════════

atr = ta.atr(atrLength)
atrPercent = (atr / close) * 100

// Bollinger Bands
bbBasis = ta.sma(close, bbLength)
bbDev = ta.stdev(close, bbLength) * bbStdDev
bbUpper = bbBasis + bbDev
bbLower = bbBasis - bbDev
bbWidth = ((bbUpper - bbLower) / bbBasis) * 100

// Volatility States
volCompression = bbWidth < ta.sma(bbWidth, 50) * 0.7
volExpansion = bbWidth > ta.sma(bbWidth, 50) * 1.3
bbSqueeze = volCompression and atr < ta.sma(atr, 50) * 0.8

// Price position in BB
bbPosition = (close - bbLower) / (bbUpper - bbLower)
atUpperBB = bbPosition > 0.95
atLowerBB = bbPosition < 0.05

// ═══════════════════════════════════════════════════════════════════
// 🎯 MARKET STRUCTURE & LEVELS
// ═══════════════════════════════════════════════════════════════════

// Swing Points
swingHigh = ta.highest(high, swingLength)
swingLow = ta.lowest(low, swingLength)
isSwingHigh = high == swingHigh
isSwingLow = low == swingLow

// Higher Highs / Higher Lows (Bullish Structure)
higherHigh = high > ta.highest(high[1], structureLength) and trendScore >= 2
higherLow = low > ta.lowest(low[1], structureLength) and trendScore >= 2

// Lower Highs / Lower Lows (Bearish Structure)
lowerHigh = high < ta.highest(high[1], structureLength) and trendScore <= 2
lowerLow = low < ta.lowest(low[1], structureLength) and trendScore <= 2

// Structure Breaks
bullStructureBreak = close > ta.highest(high[1], structureLength) and trendScore >= 2
bearStructureBreak = close < ta.lowest(low[1], structureLength) and trendScore <= 2

// Support/Resistance Zones
var float keyResistance = na
var float keySupport = na
var int resistanceStrength = 0
var int supportStrength = 0

if isSwingHigh
    keyResistance := high
    resistanceStrength := 0

if isSwingLow
    keySupport := low
    supportStrength := 0

if not na(keyResistance) and high >= keyResistance * 0.995 and high <= keyResistance * 1.005
    resistanceStrength += 1

if not na(keySupport) and low <= keySupport * 1.005 and low >= keySupport * 0.995
    supportStrength += 1

// ═══════════════════════════════════════════════════════════════════
// 🧠 BTC-SPECIFIC: SPECULATION PROXY INDICATORS
// ═══════════════════════════════════════════════════════════════════

// Funding Rate Proxy (Perp vs Spot premium simulation)
// Using momentum and volume as proxy for leverage
leverageProxy = (ta.roc(close, fundingProxyLength) / atrPercent) * (volMomentum - 1)
extremeLeverage = math.abs(leverageProxy) > 2
longLeverage = leverageProxy > 2
shortLeverage = leverageProxy < -2

// Momentum Exhaustion
momentumExhaustion = (rsiOverbought and stochOverbought and bearDiv) or 
                     (rsiOversold and stochOversold and bullDiv)

// Retail FOMO Detection (rapid price move + volume climax + overbought)
retailFOMO = ta.roc(close, 5) > 5 and volClimax and rsiOverbought
smartMoneyExit = retailFOMO and distributionBar

// Capitulation Detection (panic selling)
capitulation = ta.roc(close, 5) < -8 and volClimax and rsiOversold and stochOversold
smartMoneyEntry = capitulation and accumulationBar

// ═══════════════════════════════════════════════════════════════════
// 🚨 SIGNAL GENERATION - ADVANCED LOGIC
// ═══════════════════════════════════════════════════════════════════

// === LONG ENTRY CONDITIONS ===
longTrendAlign = trendScore >= 3 and trendBull
longMomentum = (rsi > 40 and rsi < 65) or bullDiv or stochBullCross
longVolume = bullVolume or accumulationBar
longStructure = (close > ema21Val and low > swingLow * 0.995) or bullStructureBreak
longNotOverextended = not rsiOverbought and not atUpperBB

longSetup = longTrendAlign and longMomentum and longStructure and longNotOverextended
longConfirmed = longSetup and longVolume

// === STRONG LONG (Major Setup) ===
strongLong = longConfirmed and (smartMoneyEntry or (bullDiv and volSpike)) and 
             htf1Bull and htf2Bull

// === SHORT ENTRY CONDITIONS ===
shortTrendAlign = trendScore <= 1 and trendBear
shortMomentum = (rsi < 60 and rsi > 35) or bearDiv or stochBearCross
shortVolume = bearVolume or distributionBar
shortStructure = (close < ema21Val and high < swingHigh * 1.005) or bearStructureBreak
shortNotOverextended = not rsiOversold and not atLowerBB

shortSetup = shortTrendAlign and shortMomentum and shortStructure and shortNotOverextended
shortConfirmed = shortSetup and shortVolume

// === STRONG SHORT (Major Setup) ===
strongShort = shortConfirmed and (smartMoneyExit or (bearDiv and volSpike)) and 
              not htf1Bull and not htf2Bull

// === SCALP OPPORTUNITIES (Counter-Trend) ===
scalpLong = rsiOversold and stochOversold and bullVolume and close > ema8Val and bbSqueeze
scalpShort = rsiOverbought and stochOverbought and bearVolume and close < ema8Val and bbSqueeze

// === HEDGE SIGNALS ===
hedgeLong = (rsiOverbought or extremeLeverage) and distributionBar and resistanceStrength >= 2
hedgeShort = (rsiOversold or extremeLeverage) and accumulationBar and supportStrength >= 2

// === BREAKOUT SIGNALS ===
bullBreakout = bbSqueeze[1] and volExpansion and bullVolume and close > bbUpper
bearBreakout = bbSqueeze[1] and volExpansion and bearVolume and close < bbLower

// ═══════════════════════════════════════════════════════════════════
// ✨ VISUAL RENDERING - ADVANCED
// ═══════════════════════════════════════════════════════════════════

// Background - Multi-layer trend glow
bgcolor(htf1Bull ? color.new(color.rgb(0,255,136), 97) : color.new(color.rgb(255,51,102), 97), title="Major Trend Glow")
bgcolor(htf2Bull ? color.new(color.rgb(0,255,136), 95) : color.new(color.rgb(255,51,102), 95), title="Intermediate Trend Glow")
bgcolor(trendBull ? color.new(color.rgb(0,255,136), 93) : trendBear ? color.new(color.rgb(255,51,102), 93) : na, title="Current Trend")

// EMA Cloud
ema21Plot = plot(ema21Val, "EMA 21", color.new(color.rgb(0,255,255), 0), 2)
ema55Plot = plot(ema55Val, "EMA 55", color.new(color.rgb(255,0,255), 0), 2)
fill(ema21Plot, ema55Plot, color=trendBull ? color.new(color.rgb(0,255,136), 90) : color.new(color.rgb(255,51,102), 90), title="EMA Cloud")

plot(ema8Val, "EMA 8", color.new(color.rgb(255,255,0), 0), 2)
plot(ema200Val, "EMA 200", color.new(color.rgb(255,255,255), 50), 3)

// Bollinger Bands
plot(bbUpper, "BB Upper", color.new(color.rgb(255,0,102), 70), 1, plot.style_circles)
plot(bbLower, "BB Lower", color.new(color.rgb(0,255,102), 70), 1, plot.style_circles)
bbUpperPlot = plot(bbSqueeze ? bbUpper : na, display=display.none)
bbLowerPlot = plot(bbSqueeze ? bbLower : na, display=display.none)
fill(bbUpperPlot, bbLowerPlot, color.new(color.rgb(255,170,0), 85), title="Squeeze Zone")

// Market Structure Lines
if showStructure
    if isSwingHigh
        line.new(bar_index, high, bar_index + 20, high, color=color.new(color.rgb(255,0,0), 60), width=2, style=line.style_dashed)
    if isSwingLow
        line.new(bar_index, low, bar_index + 20, low, color=color.new(color.rgb(0,255,0), 60), width=2, style=line.style_dashed)

// Structure Breaks with glow
bgcolor(bullStructureBreak ? color.new(color.rgb(0,255,0), 80) : na, title="Bull Structure Break")
bgcolor(bearStructureBreak ? color.new(color.rgb(255,0,0), 80) : na, title="Bear Structure Break")

// ═══════════════════════════════════════════════════════════════════
// 🎯 SIGNAL LABELS
// ═══════════════════════════════════════════════════════════════════

// STRONG LONG
if strongLong and showAllSignals
    label.new(bar_index, low, "⚡ STRONG LONG ⚡\n🚀", 
              color=color.new(color.rgb(0,255,0), 0), 
              style=label.style_label_up, 
              textcolor=color.white, 
              size=size.large)
    box.new(bar_index - 2, low * 0.997, bar_index + 2, low * 1.003,
            border_color=color.new(color.rgb(0,255,0), 30), bgcolor=color.new(color.rgb(0,255,0), 85))

// LONG
if longConfirmed and not strongLong and showAllSignals
    label.new(bar_index, low, "LONG\n🟢", 
              color=color.new(color.rgb(0,255,136), 0), 
              style=label.style_label_up, 
              textcolor=color.white, 
              size=size.normal)

// STRONG SHORT
if strongShort and showAllSignals
    label.new(bar_index, high, "⚡ STRONG SHORT ⚡\n🔻", 
              color=color.new(color.rgb(255,0,0), 0), 
              style=label.style_label_down, 
              textcolor=color.white, 
              size=size.large)
    box.new(bar_index - 2, high * 0.997, bar_index + 2, high * 1.003,
            border_color=color.new(color.rgb(255,0,0), 30), bgcolor=color.new(color.rgb(255,0,0), 85))

// SHORT
if shortConfirmed and not strongShort and showAllSignals
    label.new(bar_index, high, "SHORT\n🔴", 
              color=color.new(color.rgb(255,51,102), 0), 
              style=label.style_label_down, 
              textcolor=color.white, 
              size=size.normal)

// SCALP SIGNALS
if scalpLong and showAllSignals and not showMajorOnly
    label.new(bar_index, low, "SCALP↗", 
              color=color.new(color.rgb(0,255,255), 20), 
              style=label.style_label_up, 
              textcolor=color.black, 
              size=size.small)

if scalpShort and showAllSignals and not showMajorOnly
    label.new(bar_index, high, "SCALP↘", 
              color=color.new(color.rgb(255,0,255), 20), 
              style=label.style_label_down, 
              textcolor=color.black, 
              size=size.small)

// HEDGE WARNINGS
if hedgeLong and showAllSignals
    label.new(bar_index, high, "⚠️ HEDGE LONG", 
              color=color.new(color.rgb(255,170,0), 0), 
              style=label.style_xcross, 
              textcolor=color.black, 
              size=size.normal)

if hedgeShort and showAllSignals
    label.new(bar_index, low, "⚠️ HEDGE SHORT", 
              color=color.new(color.rgb(255,170,0), 0), 
              style=label.style_xcross, 
              textcolor=color.black, 
              size=size.normal)

// BREAKOUTS
if bullBreakout and showAllSignals
    label.new(bar_index, high, "💥 BREAKOUT 💥", 
              color=color.new(color.rgb(153,0,255), 0), 
              style=label.style_diamond, 
              textcolor=color.white, 
              size=size.large)

if bearBreakout and showAllSignals
    label.new(bar_index, low, "💥 BREAKDOWN 💥", 
              color=color.new(color.rgb(153,0,255), 0), 
              style=label.style_diamond, 
              textcolor=color.white, 
              size=size.large)

// Special Events
if smartMoneyEntry
    label.new(bar_index, low, "🐋 CAPITULATION BUY", 
              color=color.new(color.rgb(0,255,255), 0), 
              style=label.style_flag, 
              textcolor=color.black, 
              size=size.normal)

if smartMoneyExit
    label.new(bar_index, high, "🐋 TOP SIGNAL", 
              color=color.new(color.rgb(255,0,255), 0), 
              style=label.style_flag, 
              textcolor=color.black, 
              size=size.normal)

// Volume bars
barcolor(volClimax and bullVolume ? color.new(color.rgb(0,255,0), 0) : 
         volClimax and bearVolume ? color.new(color.rgb(255,0,0), 0) :
         bullVolume ? color.new(color.rgb(0,255,136), 40) : 
         bearVolume ? color.new(color.rgb(255,51,102), 40) : na)

// ═══════════════════════════════════════════════════════════════════
// 📊 ADVANCED DASHBOARD
// ═══════════════════════════════════════════════════════════════════

if showDashboard and barstate.islast
    var table dashboard = table.new(position.top_right, 2, 12, 
                                     bgcolor=color.new(color.rgb(0,0,0), 5), 
                                     frame_color=color.new(color.rgb(0,255,255), 40), 
                                     frame_width=3)
    
    // Header (merge across columns 0..1)
    table.cell(dashboard, 0, 0, "⚡ BTC ULTIMATE SYSTEM ⚡", 
               text_color=color.white, bgcolor=color.new(color.rgb(0,102,255), 20), text_size=size.normal)
    table.merge_cells(dashboard, 0, 0, 0, 1)
    
    // Trend Alignment
    trendText = trendScore == 4 ? "🟢🟢🟢🟢 PERFECT" : 
                trendScore == 3 ? "🟢🟢🟢 STRONG" :
                trendScore == 2 ? "🟡🟡 NEUTRAL" :
                trendScore == 1 ? "🔴 WEAK BULL" : "🔴🔴 BEARISH"
    table.cell(dashboard, 0, 1, "Trend Align:", text_color=color.gray)
    table.cell(dashboard, 1, 1, trendText, text_color=color.white, 
               bgcolor=trendScore >= 3 ? color.new(color.rgb(0,255,0), 80) : trendScore == 2 ? color.new(color.rgb(255,170,0), 80) : color.new(color.rgb(255,0,0), 80))
    
    // RSI
    table.cell(dashboard, 0, 2, "RSI:", text_color=color.gray)
    table.cell(dashboard, 1, 2, str.tostring(math.round(rsi, 1)), 
               text_color=color.white,
               bgcolor=rsi > 70 ? color.new(color.rgb(255,0,0), 70) : rsi < 30 ? color.new(color.rgb(0,255,0), 70) : color.new(color.rgb(102,102,102), 70))
    
    // Volume
    volText = volClimax ? "🔥🔥 CLIMAX" : volSpike ? "🔥 SPIKE" : "😴 Normal"
    table.cell(dashboard, 0, 3, "Volume:", text_color=color.gray)
    table.cell(dashboard, 1, 3, volText, text_color=color.white,
               bgcolor=volClimax ? color.new(color.rgb(255,102,0), 60) : volSpike ? color.new(color.rgb(255,102,0), 80) : color.new(color.rgb(102,102,102), 80))
    
    // Volatility
    volText2 = bbSqueeze ? "💤 SQUEEZE" : volExpansion ? "💥 EXPANSION" : "➡️ Normal"
    table.cell(dashboard, 0, 4, "Volatility:", text_color=color.gray)
    table.cell(dashboard, 1, 4, volText2, text_color=color.white,
               bgcolor=bbSqueeze ? color.new(color.rgb(255,170,0), 70) : volExpansion ? color.new(color.rgb(255,0,0), 70) : color.new(color.rgb(102,102,102), 80))
    
    // Structure
    structText = bullStructureBreak ? "🚀 BULL BREAK" : bearStructureBreak ? "💥 BEAR BREAK" : 
                 higherHigh ? "📈 HH" : lowerLow ? "📉 LL" : "➡️ Range"
    table.cell(dashboard, 0, 5, "Structure:", text_color=color.gray)
    table.cell(dashboard, 1, 5, structText, text_color=color.white,
               bgcolor=bullStructureBreak ? color.new(color.rgb(0,255,0), 70) : bearStructureBreak ? color.new(color.rgb(255,0,0), 70) : color.new(color.rgb(102,102,102), 80))
    
    // Divergence
    divText = bullDiv ? "🟢 BULL DIV" : bearDiv ? "🔴 BEAR DIV" : "➖ None"
    table.cell(dashboard, 0, 6, "Divergence:", text_color=color.gray)
    table.cell(dashboard, 1, 6, divText, text_color=color.white,
               bgcolor=bullDiv ? color.new(color.rgb(0,255,0), 70) : bearDiv ? color.new(color.rgb(255,0,0), 70) : color.new(color.rgb(102,102,102), 80))
    
    // Leverage Proxy
    levText = longLeverage ? "🔴 LONG OI HIGH" : shortLeverage ? "🟢 SHORT OI HIGH" : "➖ Balanced"
    table.cell(dashboard, 0, 7, "Leverage:", text_color=color.gray)
    table.cell(dashboard, 1, 7, levText, text_color=color.white,
               bgcolor=extremeLeverage ? color.new(color.rgb(255,170,0), 70) : color.new(color.rgb(102,102,102), 80))
    
    // Signal
    signalText = strongLong ? "⚡ STRONG LONG ⚡" :
                 strongShort ? "⚡ STRONG SHORT ⚡" :
                 longConfirmed ? "🟢 LONG SETUP" :
                 shortConfirmed ? "🔴 SHORT SETUP" :
                 (hedgeLong or hedgeShort) ? "⚠️ HEDGE ZONE" :
                 "⏳ WAIT"
    signalBg = (strongLong or longConfirmed) ? color.new(color.rgb(0,255,0), 60) :
               (strongShort or shortConfirmed) ? color.new(color.rgb(255,0,0), 60) :
               (hedgeLong or hedgeShort) ? color.new(color.rgb(255,170,0), 60) :
               color.new(color.rgb(102,102,102), 80)
    table.cell(dashboard, 0, 8, "SIGNAL:", text_color=color.gray)
    table.cell(dashboard, 1, 8, signalText, text_color=color.white, bgcolor=signalBg)
    
    // Smart Money
    smartText = smartMoneyEntry ? "🐋 BUYING" : smartMoneyExit ? "🐋 SELLING" : "➖ Neutral"
    table.cell(dashboard, 0, 9, "Smart Money:", text_color=color.gray)
    table.cell(dashboard, 1, 9, smartText, text_color=color.white,
               bgcolor=smartMoneyEntry ? color.new(color.rgb(0,255,255), 70) : smartMoneyExit ? color.new(color.rgb(255,0,255), 70) : color.new(color.rgb(102,102,102), 80))
    
    // Metrics / Extras (empty placeholders for expansion)
    table.cell(dashboard, 0, 10, "Info:", text_color=color.gray)
    table.cell(dashboard, 1, 10, "v2", text_color=color.white, bgcolor=color.new(color.rgb(102,102,102), 80))
    
    table.cell(dashboard, 0, 11, "Updated:", text_color=color.gray)
    table.cell(dashboard, 1, 11, str.tostring(time, "yyyy-MM-dd HH:mm"), text_color=color.white, bgcolor=color.new(color.rgb(102,102,102), 80))

// End of script