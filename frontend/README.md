# Ship-Shape Quality Profiling UI

React/TypeScript/PatternFly frontend for the Ship-Shape quality profiling system.

## Prerequisites

- Node.js 18+
- npm or yarn

## Installation

```bash
npm install
```

## Development

```bash
# Start development server
npm run dev

# Run linting
npm run lint
npm run lint:fix

# Format code
npm run format

# Run unit tests
npm test
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

## API Client Generation

To generate the TypeScript API client from the OpenAPI specification:

```bash
npm run generate-api
```

This will create type-safe API client code in `src/generated/api/` based on the OpenAPI spec at `../specs/003-quality-profiling-ui/contracts/openapi.yaml`.

**Note**: The API client generation requires `@openapitools/openapi-generator-cli` which is included in devDependencies. On first run, it may take a moment to download the generator binary.

## Project Structure

```
frontend/
├── src/
│   ├── components/     # React components
│   ├── pages/          # Page components
│   ├── services/       # API services and utilities
│   ├── types/          # TypeScript type definitions
│   ├── generated/      # Generated API client (do not edit manually)
│   ├── App.tsx         # Root application component
│   └── main.tsx        # Application entry point
├── tests/
│   ├── components/     # Component unit tests
│   └── e2e/            # End-to-end tests
└── public/             # Static assets
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_ENABLE_BENCHMARK=true
VITE_ENABLE_EXPORT=true
VITE_ENABLE_COMPARISON=true
VITE_RADAR_DIMENSIONS=8
```

### Development Server

The Vite dev server runs on port 5173 by default with API proxy configured to forward `/api/*` requests to `http://localhost:8000`.

## Building for Production

```bash
npm run build
```

The build output will be in the `dist/` directory.

## Preview Production Build

```bash
npm run preview
```

## Technologies

- **React 18** - UI framework
- **TypeScript 5** - Type-safe JavaScript
- **Vite 5** - Build tool and dev server
- **PatternFly 5** - Enterprise UI components
- **Vitest** - Unit testing
- **Playwright** - E2E testing
- **React Router** - Client-side routing
- **Axios** - HTTP client
