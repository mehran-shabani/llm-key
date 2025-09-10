# API_DOCS

<!-- BEGIN: AUTH -->
<!-- END: AUTH -->

<!-- BEGIN: ADMIN -->
<!-- END: ADMIN -->

<!-- BEGIN: SYSTEM -->
<!-- END: SYSTEM -->

<!-- BEGIN: WORKSPACES -->
<!-- END: WORKSPACES -->

<!-- BEGIN: CHATS -->
<!-- END: CHATS -->

<!-- BEGIN: DOCUMENTS -->
<!-- END: DOCUMENTS -->

<!-- BEGIN: FILES -->
<!-- END: FILES -->

<!-- BEGIN: LLM -->
<!-- END: LLM -->

<!-- BEGIN: EMBEDDING -->
<!-- END: EMBEDDING -->

<!-- BEGIN: IMAGE -->
<!-- END: IMAGE -->

<!-- BEGIN: STT -->
<!-- END: STT -->

<!-- BEGIN: TTS -->
<!-- END: TTS -->

<!-- BEGIN: CONVERSATION -->
<!-- END: CONVERSATION -->

<!-- BEGIN: SCHEMA -->
## API Schema & Documentation

The API schema is automatically generated using DRF Spectacular and provides comprehensive documentation for all available endpoints.

### Available Endpoints

- **OpenAPI Schema**: `/api/schema/` - Raw OpenAPI 3.0 specification
- **Swagger UI**: `/api/docs/` - Interactive API documentation with testing capabilities
- **ReDoc**: `/api/redoc/` - Alternative documentation interface

### Features

- **Interactive Testing**: Test API endpoints directly from the documentation
- **Authentication Support**: Built-in support for Bearer token authentication
- **Dark Theme**: Optional dark mode for better viewing experience
- **Responsive Design**: Mobile-friendly documentation interface
- **Auto-generated**: Schema is automatically updated when API changes

### Usage

1. Navigate to `/api/docs/` for the main Swagger UI interface
2. Use the "Authorize" button to set your API token
3. Explore endpoints by category (Authentication, Admin, System, etc.)
4. Test endpoints directly from the interface

### Schema Configuration

The schema is configured in `apps/api/schema/schema.py` with:
- Common response schemas for authentication errors
- Reusable decorators for authenticated endpoints
- Standardized parameter definitions
- Consistent error response formats

<!-- END: SCHEMA -->

<!-- BEGIN: JOBS -->
<!-- END: JOBS -->
