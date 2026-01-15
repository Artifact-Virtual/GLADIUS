# UniXchange - Live Market Charts

A professional market charts and trading interface with real-time data, built with React, TypeScript, and TradingView-style components.

## Features

- **Real-time Market Data**: Live price updates via WebSocket connections
- **Professional Charts**: Candlestick and line charts with technical indicators
- **Order Book**: Live bid/ask data with depth visualization
- **Trade History**: Recent trades with buy/sell indicators
- **Market Overview**: Comprehensive market statistics
- **Responsive Layout**: Drag-and-drop workspace with customizable panels
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Multiple Timeframes**: 1m, 5m, 15m, 1h, 4h, 1D, 1W intervals

## Technology Stack

- **Frontend**: React 18, TypeScript
- **Charts**: Lightweight Charts (TradingView library)
- **Styling**: Tailwind CSS
- **Layout**: React Grid Layout
- **Icons**: Lucide React
- **Data**: Binance API (demo), WebSocket streams
- **Build Tool**: Vite

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Modern web browser with WebSocket support

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
src/
├── components/          # React components
│   ├── Charts/         # Chart-related components
│   ├── Layout/         # Layout components (Header, Sidebar)
│   ├── Trading/        # Trading components (OrderBook, TradeHistory)
│   ├── TradingWorkspace/ # Main workspace
│   └── UI/             # Reusable UI components
├── contexts/           # React contexts for state management
├── services/           # API and WebSocket services
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
└── index.css          # Global styles
```

## Key Components

### TradingWorkspace
- Main container with drag-and-drop grid layout
- Customizable panel arrangement
- Layout persistence and controls

### PriceChart
- Professional candlestick/line charts
- Multiple timeframe support
- Real-time price updates
- Technical indicators integration

### OrderBook
- Live bid/ask data
- Depth visualization
- Spread calculation
- Real-time updates

### Market Data Context
- Centralized state management
- WebSocket connection handling
- Real-time data distribution
- Error handling and reconnection

## Configuration

### API Endpoints
The app uses Binance API for demonstration. To use your own data source:

1. Update `src/services/MarketDataService.ts`
2. Modify `src/services/WebSocketService.ts`
3. Adjust data format mapping in contexts

### Styling
- Tailwind configuration: `tailwind.config.js`
- Custom CSS: `src/index.css`
- Dark theme optimized for trading

## Features in Detail

### Real-time Data
- WebSocket connections for live updates
- Automatic reconnection on connection loss
- Efficient data streaming and caching

### Professional Interface
- TradingView-inspired design
- Dark theme optimized for extended use
- Responsive design for all screen sizes

### Customizable Workspace
- Drag-and-drop panel arrangement
- Resizable components
- Layout saving and restoration
- Multiple workspace configurations

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - TypeScript type checking

### Adding New Features

1. **New Chart Indicators**: Add to `TechnicalIndicators.tsx`
2. **Additional Markets**: Extend `MarketDataService.ts`
3. **Custom Layouts**: Modify `TradingWorkspace.tsx`
4. **New Data Sources**: Update service layer

## Production Deployment

### Environment Variables
- `VITE_API_BASE_URL` - API base URL
- `VITE_WS_URL` - WebSocket endpoint
- `VITE_API_KEY` - API key (if required)

### Performance Optimizations
- Code splitting implemented
- Bundle size optimization
- WebSocket connection pooling
- Efficient re-rendering strategies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Disclaimer

This is a demonstration application. Real trading involves financial risk. Always use proper risk management and consult financial professionals before making investment decisions.
