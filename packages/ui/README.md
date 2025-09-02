# spending-monitor UI

Modern React frontend application built with Vite and TanStack Router.

## Features

- **React 19** - Latest React with concurrent features
- **TypeScript** - Full type safety and modern JavaScript features
- **Vite** - Lightning fast development and build tool
- **TanStack Router** - Type-safe routing with automatic code splitting
- **Tailwind CSS** - Utility-first CSS framework for rapid styling
- **Storybook** - Component development and documentation
- **Authentication** - OIDC integration with development bypass
- **API Integration** - Ready-to-use API service layer
- **Development** - Hot module replacement for instant feedback
- **Production** - Optimized builds with tree shaking and minification

## Quick Start

### Prerequisites

- Node.js 18+
- pnpm 9+

### Development

1. **Install dependencies**:

```bash
pnpm install
```

2. **Start development server**:

```bash
pnpm dev
```

The application will be available at http://localhost:3000

## Authentication Configuration

The UI supports both development and production authentication modes:

### Development Mode (Default)
Authentication is automatically bypassed for faster development:

```bash
# .env (optional - these are defaults)
VITE_ENVIRONMENT=development
VITE_BYPASS_AUTH=true
```

Features in development mode:
- 🔓 **No login required** - automatic authentication as dev user
- 🚀 **Instant access** - no OIDC flow needed
- 👤 **Mock user data** - consistent dev user for testing
- 🎯 **Visual indicators** - UI shows "Dev Mode" badges

### Production Mode
Full OIDC authentication with Keycloak:

```bash
# .env
VITE_ENVIRONMENT=production
VITE_BYPASS_AUTH=false
VITE_KEYCLOAK_URL=http://localhost:8080/realms/spending-monitor
VITE_KEYCLOAK_CLIENT_ID=spending-monitor
```

### Force Production Auth in Development
To test authentication flow in development:

```bash
# .env
VITE_ENVIRONMENT=development
VITE_BYPASS_AUTH=false  # Explicit override
VITE_KEYCLOAK_URL=http://localhost:8080/realms/spending-monitor
```

## Available Scripts

```bash
# Development
pnpm dev                # Start development server with hot reload
pnpm preview            # Preview production build locally

# Building
pnpm build              # Build for production
pnpm type-check         # Run TypeScript type checking

# Code Quality
pnpm lint               # Run ESLint
pnpm lint:fix           # Fix ESLint issues automatically
pnpm format             # Format code with Prettier
pnpm format:check       # Check code formatting

# Testing
pnpm test               # Run test suite (when implemented)

# Storybook
pnpm storybook          # Start Storybook development server
pnpm build-storybook    # Build Storybook for production
```

## Project Structure

```
src/
├── main.tsx                    # Application entry point
├── components/                 # Reusable UI components
│   ├── Card.tsx               # Basic card component
├── routes/                    # Application routes
│   ├── __root.tsx            # Root layout component
│   ├── index.tsx             # Home page
├── services/                  # External service integrations
│   └── api.ts                # API client configuration
└── styles/
    └── globals.css           # Global styles and Tailwind imports
```

## Routing

This application uses TanStack Router for type-safe routing:

Routes are automatically code-split for optimal loading performance.

## API Integration

The `src/services/api.ts` file provides a configured API client:

```typescript
import { api } from './services/api';

// Example usage
const health = await api.get('/health');
```

The API base URL is automatically configured to work with the backend API.

## Styling

### Tailwind CSS

This project uses Tailwind CSS for styling. Key features:

- Utility-first approach for rapid development
- Responsive design utilities
- Dark mode support (when implemented)
- Custom component classes

### Component Development

- Use TypeScript interfaces for component props
- Follow React best practices for state management
- Implement responsive design from mobile-first
- Use semantic HTML elements for accessibility

## Development Tips

1. **Type Safety**: All routes are type-safe with TanStack Router
2. **Hot Reload**: Changes are instantly reflected in the browser
3. **Component Dev**: Use React DevTools for debugging
4. **Performance**: Vite provides built-in performance optimizations

## Building for Production

```bash
pnpm build
```

This creates an optimized production build in the `dist/` directory with:

- Minified JavaScript and CSS
- Tree-shaken dependencies
- Gzipped assets
- Automatic code splitting

## Deployment

The `dist/` folder can be deployed to any static hosting service:

- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages

For SPA routing, ensure your hosting service redirects all routes to `index.html`.

---

Generated with [AI Kickstart CLI](https://github.com/your-org/ai-kickstart)
