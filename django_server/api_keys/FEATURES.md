# API Keys App

## Purpose and Scope
The api_keys app manages API authentication, browser extension keys, and invitation-based user registration. It provides secure token generation, validation, and management for various authentication scenarios including developer APIs and user onboarding.

## Key Models

### APIKey
- Developer API keys for programmatic access
- SHA-256 hashed storage
- One-time display of raw keys
- Creator tracking

### BrowserExtensionAPIKey
- Keys for browser extension authentication
- User-specific tokens
- Direct storage (not hashed)
- One key per user limit

### Invite
- Invitation codes for user registration
- Status tracking (pending/claimed/expired)
- Workspace assignment capability
- Creator attribution

## Key APIs

### API Key Management
- `GET /api/keys/api-keys/` - List API keys (admin only)
- `POST /api/keys/api-keys/generate/` - Generate new API key
- `POST /api/keys/api-keys/verify/` - Verify API key validity
- `DELETE /api/keys/api-keys/{id}/` - Revoke API key

### Browser Extension Keys
- `GET /api/keys/browser-extension-keys/` - List user's keys
- `POST /api/keys/browser-extension-keys/generate/` - Generate new key
- `DELETE /api/keys/browser-extension-keys/{id}/` - Delete key

### Invitation System
- `GET /api/keys/invites/` - List invitations (admin only)
- `POST /api/keys/invites/generate/` - Create invitation
- `POST /api/keys/invites/claim/` - Claim invitation (public)
- `POST /api/keys/invites/{code}/revoke/` - Revoke invitation

## Technologies/Libraries Used
- **secrets**: Cryptographically secure token generation
- **hashlib**: SHA-256 hashing for API keys
- **uuid**: Unique identifier generation
- **Django permissions**: Role-based access control

## Architectural Patterns

### API Key Security
- **One-Way Hashing**: Keys hashed before storage
- **Secure Generation**: 32-byte random tokens
- **One-Time Display**: Raw key shown only at creation
- **No Recovery**: Lost keys must be regenerated
- **Verification**: Hash comparison for validation

### Browser Extension Authentication
- **User-Bound Keys**: One key per user
- **Auto-Replacement**: New key deletes old one
- **Direct Storage**: Keys stored unhashed for retrieval
- **Simplified Management**: Easy key rotation

### Invitation Workflow
1. **Generation**: Admin creates invite with optional workspace assignment
2. **Distribution**: Invite code shared with user
3. **Claiming**: User creates account with invite code
4. **Assignment**: Automatic workspace access granted
5. **Tracking**: Full audit trail of invite usage

### Token Formats
- **API Keys**: URL-safe base64, 32 bytes
- **Browser Keys**: URL-safe base64, 32 bytes
- **Invite Codes**: URL-safe base64, 16 bytes

## Security Features

### API Key Security
- **Hashed Storage**: Prevents key theft from database
- **No Plaintext**: Keys never stored in readable form
- **Secure Random**: Cryptographically secure generation
- **Admin Only**: Only admins can generate API keys
- **Audit Logging**: All key operations logged

### Invitation Security
- **Single Use**: Invites can only be claimed once
- **Status Tracking**: Prevent reuse of claimed codes
- **Expiration**: Can be marked as expired
- **Workspace Scoping**: Limit access to specific workspaces
- **Creator Tracking**: Know who created each invite

### Browser Extension Security
- **User Isolation**: Keys tied to specific users
- **Rotation Support**: Easy key replacement
- **Access Control**: Users manage own keys only
- **Event Logging**: Track key generation/deletion

## Integration Points
- **Authentication app**: User creation via invites
- **Workspaces app**: Automatic workspace assignment
- **System Settings**: Event logging for audit
- **External APIs**: Developer access to platform
- **Browser Extensions**: Secure browser integration

## Use Cases

### Developer API Access
- Programmatic workspace management
- Automated document upload
- Chat API integration
- Bulk operations
- CI/CD integration

### Browser Extension
- Capture web content
- Quick chat access
- Document clipping
- Cross-site integration
- User convenience features

### User Onboarding
- Controlled registration
- Team invitations
- Workspace pre-assignment
- Beta access control
- Partner organization access

## API Key Lifecycle
1. **Generation**: Admin creates key
2. **Distribution**: Key shared with developer
3. **Usage**: Key used in API requests
4. **Monitoring**: Usage tracked via logs
5. **Rotation**: Periodic key replacement
6. **Revocation**: Key deleted when no longer needed

## Invitation Lifecycle
1. **Creation**: Admin generates invite
2. **Configuration**: Set workspace access
3. **Sharing**: Code sent to invitee
4. **Claiming**: User registers with code
5. **Activation**: Account created and configured
6. **Completion**: Invite marked as claimed

## Best Practices
- **Key Rotation**: Regular API key replacement
- **Minimal Scope**: Only necessary workspace access
- **Secure Storage**: Store keys in environment variables
- **HTTPS Only**: Always use encrypted connections
- **Rate Limiting**: Implement request throttling
- **Monitoring**: Track unusual API usage patterns

## Event Tracking
- api_key_generated
- api_key_deleted
- browser_extension_key_generated
- browser_extension_key_deleted
- invite_generated
- invite_claimed
- invite_revoked