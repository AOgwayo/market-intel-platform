#!/bin/bash
set -e

echo "🔄 Generating TypeScript types from OpenAPI specification"

# Check if backend server is running
if ! curl -f http://localhost:8000/health &> /dev/null; then
    echo "❌ Backend API is not running. Please start it first with 'make api'"
    exit 1
fi

# Create output directory
mkdir -p frontend/src/types/generated

# Generate OpenAPI specification
echo "📄 Fetching OpenAPI specification..."
curl -s http://localhost:8000/openapi.json > frontend/src/types/generated/openapi.json

# Check if openapi-typescript is installed globally
if ! command -v openapi-typescript &> /dev/null; then
    echo "📦 Installing openapi-typescript..."
    npm install -g openapi-typescript
fi

# Generate TypeScript types
echo "⚙️  Generating TypeScript types..."
cd frontend
npx openapi-typescript src/types/generated/openapi.json --output src/types/generated/api.ts

# Create index file for easy imports
cat > src/types/generated/index.ts << 'EOF'
/**
 * Generated API types from OpenAPI specification
 * 
 * This file is auto-generated. Do not edit manually.
 * Run 'make generate-types' to regenerate.
 */

export * from './api';

// Re-export commonly used types with friendly names
export type { components } from './api';

// Define commonly used API response types
export type ApiResponse<T = any> = {
  data?: T;
  message?: string;
  error?: string;
  success?: boolean;
};

// Define signal types for easier use
export type Signal = components['schemas']['Signal'];
export type MarketBar = components['schemas']['MarketBar'];
export type Order = components['schemas']['Order'];
export type Position = components['schemas']['Position'];

// API endpoint types
export type GetSignalsResponse = {
  signals: Signal[];
  count: number;
};

export type GetMarketBarsResponse = {
  symbol: string;
  timeframe: string;
  bars: MarketBar[];
  count: number;
};

export type BacktestResponse = {
  final_pnl: number;
  final_capital: number;
  total_return_pct: number;
  trades: any[];
  total_trades: number;
  avg_daily_pnl: number;
  strategy_name: string;
  symbol: string;
};
EOF

cd ..

echo "✅ TypeScript types generated successfully!"
echo ""
echo "Generated files:"
echo "  - frontend/src/types/generated/openapi.json"
echo "  - frontend/src/types/generated/api.ts"
echo "  - frontend/src/types/generated/index.ts"
echo ""
echo "Import types in your components:"
echo "  import { Signal, GetSignalsResponse } from '@/types/generated';"
echo ""