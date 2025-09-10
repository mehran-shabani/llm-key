# AnythingLLM Frontend - React Application Architecture

## Purpose
The frontend is a modern React single-page application (SPA) that provides the user interface for AnythingLLM, featuring real-time chat, document management, administrative controls, and multi-language support.

## Technologies Used
- **React 18**: Component-based UI framework with hooks
- **Vite**: Fast build tool and development server
- **React Router**: Client-side routing and navigation
- **Tailwind CSS**: Utility-first CSS framework with custom theming
- **i18next**: Internationalization framework
- **Phosphor Icons**: Modern icon library
- **React Toastify**: Toast notifications
- **React Beautiful DnD**: Drag and drop functionality
- **Tremor**: Data visualization components

## Architecture Overview

### Application Structure
```
frontend/src/
├── App.jsx               # Main app component with routing
├── main.jsx             # Application entry point
├── components/          # Reusable UI components
├── pages/              # Route-specific page components
├── hooks/              # Custom React hooks
├── models/             # API client layer
├── utils/              # Utility functions
├── locales/            # Internationalization files
└── media/              # Static assets
```

## Core Architectural Patterns

### 1. **Context-Driven State Management**
The application uses React Context for global state management:

```javascript
// AuthContext.jsx - Authentication state
export const AuthContext = createContext(null);
export function ContextWrapper(props) {
  const [store, setStore] = useState({
    user: localUser ? JSON.parse(localUser) : null,
    authToken: localAuthToken ? localAuthToken : null,
  });

  const [actions] = useState({
    updateUser: (user, authToken = "") => {
      localStorage.setItem(AUTH_USER, JSON.stringify(user));
      localStorage.setItem(AUTH_TOKEN, authToken);
      setStore({ user, authToken });
    },
    unsetUser: () => {
      localStorage.removeItem(AUTH_USER);
      localStorage.removeItem(AUTH_TOKEN);
      setStore({ user: null, authToken: null });
    },
  });

  return (
    <AuthContext.Provider value={{ store, actions }}>
      {props.children}
    </AuthContext.Provider>
  );
}
```

**Context Providers**:
- **AuthContext**: User authentication and session management
- **ThemeContext**: Light/dark theme switching with CSS variables
- **PfpProvider**: Profile picture management
- **LogoProvider**: Custom branding and logo handling
- **TTSProvider**: Text-to-speech functionality

### 2. **Route-Based Code Splitting**
```javascript
// App.jsx - Lazy loading for performance
const Main = lazy(() => import("@/pages/Main"));
const WorkspaceChat = lazy(() => import("@/pages/WorkspaceChat"));
const AdminUsers = lazy(() => import("@/pages/Admin/Users"));

export default function App() {
  return (
    <Suspense fallback={<FullScreenLoader />}>
      <Routes>
        <Route path="/" element={<PrivateRoute Component={Main} />} />
        <Route path="/workspace/:slug" element={<PrivateRoute Component={WorkspaceChat} />} />
        {/* ... other routes */}
      </Routes>
    </Suspense>
  );
}
```

**Benefits**:
- Reduced initial bundle size
- Faster application startup
- Progressive loading based on user navigation

### 3. **Role-Based Access Control**
```javascript
// PrivateRoute/index.jsx - Authentication guards
export function AdminRoute({ Component }) {
  const { isAuthd, multiUserMode } = useIsAuthenticated();
  const user = userFromStorage();
  
  return isAuthd && (user?.role === "admin" || !multiUserMode) ? (
    <KeyboardShortcutWrapper>
      <UserMenu>
        <Component />
      </UserMenu>
    </KeyboardShortcutWrapper>
  ) : (
    <Navigate to={paths.home()} />
  );
}

export function ManagerRoute({ Component }) {
  // Manager and Admin access
  return isAuthd && (user?.role !== "default" || !multiUserMode) ? (
    <Component />
  ) : (
    <Navigate to={paths.home()} />
  );
}
```

**Access Levels**:
- **PrivateRoute**: Any authenticated user
- **ManagerRoute**: Manager and Admin roles
- **AdminRoute**: Admin role only (bypassed in single-user mode)

## Core Components

### 1. **Authentication System**

#### Session Management
```javascript
// useIsAuthenticated hook
function useIsAuthenticated() {
  const [isAuthd, setIsAuthed] = useState(null);
  const [multiUserMode, setMultiUserMode] = useState(false);

  useEffect(() => {
    const validateSession = async () => {
      const { MultiUserMode, RequiresAuth, LLMProvider, VectorDB } = await System.keys();
      
      // Onboarding redirect logic
      if (!MultiUserMode && !RequiresAuth && !LLMProvider && !VectorDB) {
        setShouldRedirectToOnboarding(true);
        return;
      }

      // Single user mode bypass
      if (!MultiUserMode && !RequiresAuth) {
        setIsAuthed(true);
        return;
      }

      // Token validation
      const isValid = await validateSessionTokenForUser();
      setIsAuthed(isValid);
    };
    validateSession();
  }, []);

  return { isAuthd, multiUserMode };
}
```

**Features**:
- **Multi-mode support**: Single-user, password-protected, and multi-user modes
- **Token validation**: JWT token verification with backend
- **Automatic onboarding**: Redirects new installations to setup flow
- **Session persistence**: LocalStorage-based session management

### 2. **API Client Layer**

#### Model-Based API Abstraction
```javascript
// models/workspace.js - API client pattern
const Workspace = {
  new: async function (data = {}) {
    const { workspace, message } = await fetch(`${API_BASE}/workspace/new`, {
      method: "POST",
      body: JSON.stringify(data),
      headers: baseHeaders(),
    }).then((res) => res.json());
    
    return { workspace, message };
  },

  // Real-time streaming chat
  streamChat: async function ({ slug, message, sessionId, mode = "chat" }, handleChat) {
    const ctrl = new AbortController();
    
    await fetchEventSource(`${API_BASE}/workspace/${slug}/stream-chat`, {
      method: "POST",
      body: JSON.stringify({ message, sessionId, mode }),
      headers: baseHeaders(),
      signal: ctrl.signal,
      
      onmessage(msg) {
        try {
          const chatResult = JSON.parse(msg.data);
          handleChat(chatResult);
        } catch (error) {
          handleChat({ id: v4(), type: "abort", textResponse: null, close: true });
        }
      },
    });

    return { close: () => ctrl.abort() };
  },
};
```

**API Features**:
- **RESTful endpoints**: Standard CRUD operations
- **Server-Sent Events**: Real-time chat streaming
- **Error handling**: Consistent error response handling
- **Token authentication**: Automatic bearer token inclusion

### 3. **Theme System**

#### CSS Variable-Based Theming
```javascript
// ThemeContext.jsx + Tailwind configuration
const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const themeValue = useTheme(); // Custom hook for theme management
  return (
    <ThemeContext.Provider value={themeValue}>
      {children}
    </ThemeContext.Provider>
  );
}
```

```css
/* Tailwind theme configuration */
theme: {
  extend: {
    colors: {
      // CSS variable-based theme colors
      theme: {
        bg: {
          primary: 'var(--theme-bg-primary)',
          secondary: 'var(--theme-bg-secondary)',
          sidebar: 'var(--theme-bg-sidebar)',
        },
        text: {
          primary: 'var(--theme-text-primary)',
          secondary: 'var(--theme-text-secondary)',
        }
      }
    }
  }
}
```

**Theme Features**:
- **Dynamic theme switching**: Light/dark mode support
- **CSS variable system**: Runtime theme changes without reload
- **Component-specific themes**: Granular theming for different UI areas
- **Custom branding**: Support for custom logos and colors

### 4. **Chat Interface Architecture**

#### Real-Time Chat Component
```javascript
// WorkspaceChat/index.jsx - Main chat interface
export default function WorkspaceChat({ loading, workspace }) {
  const { threadSlug = null } = useParams();
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  useEffect(() => {
    async function getHistory() {
      const chatHistory = threadSlug
        ? await Workspace.threads.chatHistory(workspace.slug, threadSlug)
        : await Workspace.chatHistory(workspace.slug);
      
      setHistory(chatHistory);
      setLoadingHistory(false);
    }
    getHistory();
  }, [workspace, loading]);

  return (
    <TTSProvider>
      <DnDFileUploaderProvider>
        <ChatContainer 
          workspace={workspace} 
          history={history} 
          setHistory={setHistory} 
        />
      </DnDFileUploaderProvider>
    </TTSProvider>
  );
}
```

**Chat Features**:
- **Thread support**: Multiple conversation threads per workspace
- **File uploads**: Drag-and-drop document attachment
- **Real-time streaming**: Server-sent events for live responses
- **Text-to-speech**: Built-in TTS with multiple providers
- **Speech-to-text**: Voice input support
- **Message history**: Persistent chat history with pagination

### 5. **Internationalization (i18n)**

#### Multi-Language Support
```javascript
// i18n.js - i18next configuration
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: "en",
    debug: false,
    resources: {
      en: { translation: require("./locales/en/common.json") },
      es: { translation: require("./locales/es/common.json") },
      fr: { translation: require("./locales/fr/common.json") },
      // ... 20+ languages
    },
  });
```

**Supported Languages**:
- English, Spanish, French, German, Italian
- Japanese, Korean, Chinese (Simplified/Traditional)
- Arabic, Hebrew, Russian, Polish, Dutch
- Portuguese, Romanian, Turkish, Vietnamese
- Danish, Estonian, Latvian

### 6. **Component Architecture**

#### Reusable Component Pattern
```javascript
// components/Sidebar/index.jsx - Modular component design
export default function Sidebar() {
  const { logo } = useLogoContext();
  const user = userFromStorage();
  const [workspaces, setWorkspaces] = useState([]);

  return (
    <div className="transition-all duration-500 relative m-[16px] mr-0 rounded-[16px] bg-theme-bg-sidebar border-2 border-theme-sidebar-border min-w-[250px] p-[18px]">
      <div className="flex flex-col h-full justify-between">
        
        {/* Logo Section */}
        <div className="flex flex-col h-full justify-between">
          <div className="flex flex-col gap-y-4 pb-8 overflow-y-scroll no-scroll">
            <div className="flex gap-x-2 items-center justify-between">
              {logo ? (
                <img src={logo} alt="Logo" className="block mx-auto h-6 w-auto" />
              ) : (
                <AnythingLLMLogo />
              )}
            </div>

            {/* Workspace List */}
            <WorkspacesList 
              workspaces={workspaces} 
              setWorkspaces={setWorkspaces} 
            />
          </div>

          {/* Footer */}
          <Footer user={user} />
        </div>
      </div>
    </div>
  );
}
```

**Component Design Principles**:
- **Single Responsibility**: Each component has a focused purpose
- **Composition over Inheritance**: Components compose together
- **Props Interface**: Clear prop definitions and PropTypes
- **Accessibility**: ARIA labels and keyboard navigation support

## Build and Development Configuration

### Vite Configuration
```javascript
// vite.config.js - Modern build tooling
export default defineConfig({
  // WebAssembly support for Piper TTS
  assetsInclude: [
    './public/piper/ort-wasm-simd-threaded.wasm',
    './public/piper/piper_phonemize.wasm',
  ],
  
  // Development server
  server: {
    port: 3000,
    host: "localhost"
  },

  // Build optimizations
  build: {
    rollupOptions: {
      output: {
        // Consistent file naming for SSR
        entryFileNames: 'index.js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name === 'index.css') return `index.css`;
          return assetInfo.name;
        },
      },
    },
  },

  // Path aliases
  resolve: {
    alias: [
      { find: "@", replacement: fileURLToPath(new URL("./src", import.meta.url)) }
    ]
  }
});
```

## Notable Technical Decisions

### 1. **Micro-Frontend Architecture**
```javascript
// Modular page structure
const pages = {
  admin: lazy(() => import("@/pages/Admin")),
  workspace: lazy(() => import("@/pages/WorkspaceChat")),
  settings: lazy(() => import("@/pages/GeneralSettings"))
};
```
**Rationale**: Enables independent development and deployment of different application areas

### 2. **CSS-in-JS Alternative**
```css
/* Tailwind + CSS Variables approach */
.bg-theme-bg-primary { background-color: var(--theme-bg-primary); }
.text-theme-text-primary { color: var(--theme-text-primary); }
```
**Rationale**: Better performance than CSS-in-JS while maintaining dynamic theming capabilities

### 3. **Progressive Web App Features**
- **Service Worker**: Offline capability and caching
- **Responsive Design**: Mobile-first responsive layout
- **Touch Support**: Mobile gesture and touch interactions

### 4. **Performance Optimizations**
```javascript
// Bundle analysis and optimization
plugins: [
  visualizer({
    template: "treemap",
    filename: "bundleinspector.html"
  })
],

// Tree shaking optimization
build: {
  rollupOptions: {
    external: [
      // Exclude unused icon variants
      /@phosphor-icons\/react\/dist\/ssr/,
    ]
  }
}
```

### 5. **Accessibility Features**
- **Keyboard Navigation**: Full keyboard accessibility
- **ARIA Labels**: Screen reader support
- **Color Contrast**: WCAG compliant color schemes
- **Focus Management**: Proper focus handling in modals and forms

This frontend architecture enables AnythingLLM to provide a modern, responsive, and accessible user experience while supporting complex features like real-time chat, multi-language support, and extensive customization options.