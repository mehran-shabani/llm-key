# Authentication App

## Purpose and Scope
The authentication app handles all user authentication, authorization, and account management functionality for AnythingLLM. It provides a complete user management system with JWT-based authentication, role-based access control, and various security features.

## Key Models

### User
- Custom user model extending Django's AbstractBaseUser
- Fields: username, email, role (admin/manager/default), daily message limit, bio, profile picture
- Supports suspension and recovery codes for 2FA

### RecoveryCode
- Stores recovery codes for two-factor authentication
- Hashed codes for security

### PasswordResetToken
- Temporary tokens for password reset functionality
- Expiration-based validation

### TemporaryAuthToken
- Short-lived tokens for special authentication scenarios
- Used for mobile app connections and temporary access

### DesktopMobileDevice
- Manages connections between desktop and mobile applications
- Token-based authentication with approval workflow

## Key APIs

### Authentication Endpoints
- `POST /api/auth/login/` - JWT token authentication
- `POST /api/auth/refresh/` - Refresh JWT tokens
- `POST /api/users/logout/` - User logout

### User Management
- `GET /api/users/` - List users (admin only)
- `POST /api/users/` - Create new user
- `GET /api/users/me/` - Get current user info
- `PATCH /api/users/{id}/` - Update user profile
- `POST /api/users/change_password/` - Change password
- `POST /api/users/request_password_reset/` - Request password reset
- `POST /api/users/reset_password/` - Reset password with token
- `POST /api/users/generate_recovery_codes/` - Generate 2FA recovery codes

### Device Management
- `GET /api/devices/` - List user's connected devices
- `POST /api/devices/` - Register new device
- `POST /api/devices/{id}/approve/` - Approve device connection
- `POST /api/devices/{id}/revoke/` - Revoke device access

## Technologies/Libraries Used
- **djangorestframework-simplejwt**: JWT authentication
- **bcrypt**: Password hashing
- **secrets**: Secure token generation
- **Django permissions**: Role-based access control

## Architectural Patterns

### JWT Authentication
- Access tokens with 60-minute lifetime
- Refresh tokens with 7-day lifetime
- Token blacklisting after rotation
- Custom claims including user role and username

### Role-Based Access Control
- Three user roles: admin, manager, default
- Custom permission classes for role validation
- Flexible role checking middleware

### Security Features
- Password validation using Django validators
- Recovery codes for account recovery
- Token-based password reset with expiration
- Device approval workflow for mobile connections
- Event logging for all authentication events
- Daily message limits for rate limiting

### Multi-User Mode Support
- Configurable multi-user vs single-user modes
- Workspace-based user access control
- User suspension capability
- Invite-based user registration (via api_keys app)

## Integration Points
- Integrates with system_settings for event logging
- Works with workspaces for user access control
- Provides authentication for all other apps
- WebSocket authentication via channels