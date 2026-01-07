import os
import time
import datetime
import schedule
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import mplfinance as mpf
import google.generativeai as genai
from colorama import Fore, Style, init

# ==========================================
# CONFIGURATION
# ==========================================
# 1. API KEY
# REPLACE THIS WITH YOUR ACTUAL GEMINI API KEY
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY" 

# 2. TARGET FILE LOCATION (Updated for Android/Termux)
# This points to Internal Storage > Documents > Worxpace > Personal
PREFERRED_PATH = "/storage/emulated/0/Documents/Worxpace/ Personal/Dashboard (Gold).md"

# 3. ASSETS
ASSETS = {
    'GOLD': 'GC=F',       
    'SILVER': 'SI=F',     
    'DXY': 'DX-Y.NYB',    
    'YIELD_10Y': '^TNX',  
    'GLD_ETF': 'GLD',     
    'SLV_ETF': 'SLV'      
}

# AI Configuration
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro-latest') 

init(autoreset=True)

# ==========================================
# MODULE 0: PATH LOGIC
# ==========================================
def setup_paths():
    """Determines where to save files based on directory existence."""
    preferred_dir = os.path.dirname(PREFERRED_PATH)
    
    # Check if the user's specific path exists
    if os.path.exists(preferred_dir):
        print(f"{Fore.GREEN}[SYSTEM] Custom path detected: {preferred_dir}")
        output_file = PREFERRED_PATH
        # Save charts in a subfolder inside that custom directory
        charts_dir = os.path.join(preferred_dir, "charts")
        # For the markdown link, we want the relative path from the MD file
        chart_rel_path = "charts" 
    else:
        print(f"{Fore.YELLOW}[SYSTEM] Custom path not found at: {preferred_dir}")
        print(f"{Fore.YELLOW}[SYSTEM] Falling back to local folder.")
        output_file = "Dashboard (Gold).md"
        charts_dir = "charts"
        chart_rel_path = "charts"

    # Create charts directory if it doesn't exist
    os.makedirs(charts_dir, exist_ok=True)
    
    return output_file, charts_dir, chart_rel_path

# ==========================================
# MODULE 1: THE SENSES (Data Gathering)
# ==========================================
class MarketData:
    def __init__(self, charts_dir):
        self.data = {}
        self.news = []
        self.charts_dir = charts_dir

    def fetch_ohlcv(self, ticker, period="1y", interval="1d"):
        try:
            # Added multi_level_index=False to fix recent yfinance update format issues
            df = yf.download(ticker, period=period, interval=interval, progress=False, multi_level_index=False)
            if df.empty: return None
            
            # Technicals
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['SMA_50'] = ta.sma(df['Close'], length=50)
            df['SMA_200'] = ta.sma(df['Close'], length=200)
            return df
        except Exception as e:
            print(f"{Fore.RED}Error fetching {ticker}: {e}")
            return None

    def get_live_snapshot(self):
        print(f"{Fore.CYAN}[SCANNING] Gathering Global Market Data...")
        snapshot = {}
        
        for name, ticker in ASSETS.items():
            df = self.fetch_ohlcv(ticker)
            if df is not None:
                current_price = df['Close'].iloc[-1]
                prev_price = df['Close'].iloc[-2]
                change_pct = ((current_price - prev_price) / prev_price) * 100
                
                snapshot[name] = {
                    "price": round(float(current_price), 2),
                    "change_pct": round(float(change_pct), 2),
                    "rsi": round(float(df['RSI'].iloc[-1]), 2),
                    "trend": "BULLISH" if df['Close'].iloc[-1] > df['SMA_200'].iloc[-1] else "BEARISH"
                }
                
                # Fetch News
                try:
                    tick = yf.Ticker(ticker)
                    news_items = tick.news[:2]
                    for n in news_items:
                        self.news.append(f"{name}: {n['title']}")
                except: pass

                # Generate Chart
                self.generate_chart(name, df)
        
        return snapshot

    def generate_chart(self, name, df):
        try:
            chart_df = df.tail(100)
            style = mpf.make_mpf_style(base_mpf_style='nightclouds', rc={'font.size': 8})
            
            # Save to the dynamic charts directory
            filename = os.path.join(self.charts_dir, f"{name}.png")
            
            mpf.plot(
                chart_df, type='candle', mav=(20, 50), volume=True, 
                style=style, title=f"{name} - Automated",
                savefig=filename
            )
        except Exception as e:
            print(f"{Fore.RED}Chart Error {name}: {e}")

# ==========================================
# MODULE 2: THE BRAIN (AI Analysis)
# ==========================================
class AIAnalyst:
    def __init__(self, market_data, news_data):
        self.market_data = market_data
        self.news_data = news_data

    def generate_journal(self):
        print(f"{Fore.YELLOW}[THINKING] Analyzing data and formulating thesis...")
        
        data_str = "\n".join([f"{k}: ${v['price']} ({v['change_pct']}%) | RSI: {v['rsi']} | Trend: {v['trend']}" for k, v in self.market_data.items()])
        news_str = "\n".join(self.news_data[:8])
        date_str = datetime.datetime.now().strftime("%A, %d %B %Y")

        prompt = f"""
        Act as a Hedge Fund Macro Strategist. Today is {date_str}.
        
        ### MARKET DATA:
        {data_str}
        
        ### NEWS HEADLINES:
        {news_str}
        
        ### INSTRUCTIONS:
        Write a high-precision trading journal using this EXACT structure.
        
        # {date_str} - Live Analysis

        ## 1. Market Context
        *   **Macro:** (Analyze DXY & Yields effect on Gold)
        *   **News:** (Synthesize key headlines)

        ## 2. Asset Analysis (Gold/Silver)
        *   **Price Action:** (Analyze trend vs SMAs)
        *   **RSI Check:** (Is it overbought/oversold?)

        ## 3. Thesis for the Day
        *   **Bias:** (BULLISH / BEARISH / NEUTRAL)
        *   **Logic:** (Why?)

        ## 4. Setup Scan
        *   **Entry Zone:** (Specific price range)
        *   **Stop Loss:** (Technical invalidation level)
        *   **Target:** (Upside objective)

        ## 5. Scenario Matrix
        | Scenario | Probability | Price Range |
        |---|---|---|
        | Bull Case | % | $ - $ |
        | Base Case | % | $ - $ |
        | Bear Case | % | $ - $ |
        """

        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI Generation Failed: {e}"

# ==========================================
# MODULE 3: ORCHESTRATOR
# ==========================================
def run_cycle():
    print(f"\n{Fore.MAGENTA}>>> CYCLE START: {datetime.datetime.now()}")
    
    # 1. Determine Paths
    output_file, charts_dir, chart_rel_path = setup_paths()

    # 2. Gather Data
    bot = MarketData(charts_dir)
    snapshot = bot.get_live_snapshot()
    
    # 3. Analyze
    analyst = AIAnalyst(snapshot, bot.news)
    journal_entry = analyst.generate_journal()

    # 4. Save
    with open(output_file, "w", encoding='utf-8') as f:
        f.write(journal_entry)
        f.write("\n\n---\n")
        f.write("## Live Charts\n")
        # Use relative paths so Markdown viewer finds them easily
        f.write(f"![Gold]({chart_rel_path}/GOLD.png)\n")
        f.write(f"![Silver]({chart_rel_path}/SILVER.png)\n")
        f.write(f"\n*Last Updated: {datetime.datetime.now().strftime('%H:%M:%S')}*")

    print(f"{Fore.GREEN}[DONE] Journal updated at: {output_file}")

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    print(f"{Fore.GREEN}SYSTEM ONLINE.")
    run_cycle() # Run once on start
    schedule.every(1).hours.do(run_cycle) # Update every hour

    while True:
        schedule.run_pending()
        time.sleep(60)