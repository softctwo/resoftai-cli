# ResoftAI Enterprise Admin Dashboard

Modern, responsive admin dashboard for ResoftAI Enterprise Edition built with Vue 3, Vite, and Element Plus.

## Features

- **Dashboard**: Overview of system metrics and activity
- **Organization Management**: Manage organizations, teams, and members
- **Plugin Marketplace**: Browse, install, and manage plugins
- **Project Management**: Create and monitor AI-powered projects
- **User Management**: User roles, permissions, and access control
- **Analytics**: Usage statistics and performance metrics

## Tech Stack

- **Vue 3**: Progressive JavaScript framework
- **Vite**: Next-generation frontend tooling
- **Element Plus**: Vue 3 UI library
- **Pinia**: State management
- **Vue Router**: Client-side routing
- **Axios**: HTTP client

## Project Structure

```
frontend/admin/
├── src/
│   ├── assets/          # Static assets (images, fonts, etc.)
│   ├── components/      # Reusable Vue components
│   ├── views/           # Page components
│   ├── stores/          # Pinia stores
│   ├── router/          # Vue Router configuration
│   ├── api/             # API client functions
│   ├── utils/           # Utility functions
│   ├── App.vue          # Root component
│   └── main.js          # Application entry point
├── public/              # Public static files
├── index.html           # HTML entry point
├── vite.config.js       # Vite configuration
└── package.json         # Dependencies and scripts
```

## Development Setup

### Prerequisites

- Node.js 16+ and npm/yarn
- ResoftAI API server running on http://localhost:8000

### Installation

```bash
cd frontend/admin
npm install
```

### Development Server

```bash
npm run dev
```

Open http://localhost:5173 in your browser.

### Production Build

```bash
npm run build
```

Build artifacts will be in the `dist/` directory.

### Linting and Formatting

```bash
# Lint
npm run lint

# Format
npm run format
```

## Environment Variables

Create a `.env.local` file:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=ResoftAI Admin
```

## Key Features

### Dashboard

- Real-time metrics
- Recent activity feed
- Quick actions
- System health status

### Organization Management

- Create and manage organizations
- Team collaboration
- Member invitation and roles
- Subscription tier management

### Plugin Marketplace

- Browse available plugins
- Search and filter
- One-click installation
- Plugin reviews and ratings
- Trending and recommended plugins

### Project Management

- Create AI-powered projects
- Monitor agent activities
- View generated code
- Download project files

### User Management

- User accounts and profiles
- Role-based access control (RBAC)
- Permission management
- Audit log viewer

## API Integration

The admin dashboard communicates with the ResoftAI API using Axios. API client is configured in `src/api/client.js`.

Example:

```javascript
import api from '@/api/client'

// List projects
const projects = await api.get('/api/projects')

// Create organization
const org = await api.post('/api/organizations', {
  name: 'My Organization',
  slug: 'my-org',
  tier: 'professional'
})
```

## Authentication

JWT-based authentication. Token is stored in localStorage and automatically included in API requests.

## Contributing

1. Follow Vue 3 Composition API best practices
2. Use TypeScript for type safety (optional)
3. Write unit tests for components
4. Follow Element Plus design guidelines
5. Ensure responsive design

## License

Enterprise License - See main project LICENSE file
