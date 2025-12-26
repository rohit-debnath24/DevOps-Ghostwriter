# Authentication API Documentation

## Overview

The Ghostwriter application uses JWT-based session management with OAuth support for GitHub and Google.

## Session Management

### Session Cookie
- **Name**: `session`
- **Type**: JWT token (httpOnly)
- **Expiration**: 7 days (configurable)
- **Payload**:
  ```typescript
  {
    sessionId: string    // UUID v4
    userId: string       // nanoid(16)
    email: string
    name?: string
    provider: 'local' | 'github' | 'google'
  }
  ```

## API Endpoints

### 1. User Registration (Local)

**POST** `/api/auth/register`

Register a new user with email and password.

**Request Body:**
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Operator profile successfully initialized.",
  "user": {
    "userId": "abc123def456ghi7",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "name": "John Doe"
  }
}
```

**Sets Cookies:**
- `session`: JWT token with user session

---

### 2. User Login (Local)

**POST** `/api/auth/login`

Authenticate with email and password.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Authentication successful. Access granted.",
  "user": {
    "userId": "abc123def456ghi7",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "name": "John Doe"
  }
}
```

**Sets Cookies:**
- `session`: JWT token with user session

---

### 3. GitHub OAuth - Initiate

**GET** `/api/auth/github`

Redirects user to GitHub OAuth authorization page.

**Response:**
- Redirects to GitHub with OAuth parameters
- Sets `oauth_state` cookie for CSRF protection

---

### 4. GitHub OAuth - Callback

**GET** `/api/auth/github/callback?code=xxx&state=xxx`

Handles GitHub OAuth callback and creates user session.

**Query Parameters:**
- `code`: Authorization code from GitHub
- `state`: CSRF protection state

**Response:**
- Redirects to `/dashboard/{userId}` on success
- Redirects to `/login?error=xxx` on failure

**Sets Cookies:**
- `session`: JWT token with user session
- `github_token`: GitHub access token (for API access)

---

### 5. Google OAuth - Initiate

**GET** `/api/auth/google`

Redirects user to Google OAuth authorization page.

**Response:**
- Redirects to Google with OAuth parameters
- Sets `oauth_state` cookie for CSRF protection

---

### 6. Google OAuth - Callback

**GET** `/api/auth/google/callback?code=xxx&state=xxx`

Handles Google OAuth callback and creates user session.

**Query Parameters:**
- `code`: Authorization code from Google
- `state`: CSRF protection state

**Response:**
- Redirects to `/dashboard/{userId}` on success
- Redirects to `/login?error=xxx` on failure

**Sets Cookies:**
- `session`: JWT token with user session
- `google_token`: Google access token (for API access)

---

### 7. Check Session

**GET** `/api/auth/session`

Validate current user session.

**Response (200):**
```json
{
  "authenticated": true,
  "user": {
    "userId": "abc123def456ghi7",
    "email": "john@example.com",
    "name": "John Doe",
    "provider": "local"
  }
}
```

**Response (401) - Not authenticated:**
```json
{
  "authenticated": false,
  "user": null
}
```

---

### 8. Logout

**POST** `/api/auth/logout`  
**GET** `/api/auth/logout`

Terminate user session and clear cookies.

**Response (200):**
```json
{
  "success": true,
  "message": "Session terminated successfully."
}
```

**Clears Cookies:**
- `session`

---

### 9. Get GitHub Repositories

**GET** `/api/github/repos`

Fetch user's GitHub repositories (requires GitHub authentication).

**Headers:**
- Cookie: `github_token` must be present

**Response (200):**
```json
[
  {
    "id": 123456789,
    "name": "my-repo",
    "description": "Repository description",
    "language": "TypeScript",
    "topics": ["nextjs", "react"],
    "url": "https://github.com/user/my-repo",
    "stars": 42,
    "forks": 7
  }
]
```

**Response (401) - Not authenticated:**
```json
{
  "error": "Not authenticated. Please connect your GitHub account first."
}
```

---

## Error Responses

### Registration Errors

**400 - Bad Request:**
```json
{
  "success": false,
  "message": "All fields are required for operator registration."
}
```

**409 - Conflict:**
```json
{
  "success": false,
  "message": "Identity already registered. Please authenticate via login terminal."
}
```

### Login Errors

**401 - Unauthorized:**
```json
{
  "success": false,
  "message": "No operator profile found. Please register to initialize access."
}
```

```json
{
  "success": false,
  "message": "Invalid credentials. Access denied."
}
```

```json
{
  "success": false,
  "message": "This account uses github authentication. Please sign in with github."
}
```

### OAuth Errors

OAuth errors redirect to `/login?error={error_code}`:

- `oauth_failed` - OAuth handshake failed
- `local_account_exists` - Email already used by local account
- `no_account` - No account found (deprecated)

---

## Client-Side Usage Examples

### Register New User

```typescript
const response = await fetch('/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    firstName: 'John',
    lastName: 'Doe',
    email: 'john@example.com',
    password: 'SecurePass123!'
  })
})

const data = await response.json()
if (data.success) {
  window.location.href = `/dashboard/${data.user.userId}`
}
```

### Login with Email/Password

```typescript
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'john@example.com',
    password: 'SecurePass123!'
  })
})

const data = await response.json()
if (data.success) {
  window.location.href = `/dashboard/${data.user.userId}`
}
```

### Login with GitHub

```typescript
// Simply redirect to GitHub OAuth
window.location.href = '/api/auth/github'
```

### Login with Google

```typescript
// Simply redirect to Google OAuth
window.location.href = '/api/auth/google'
```

### Check Current Session

```typescript
const response = await fetch('/api/auth/session')
const data = await response.json()

if (data.authenticated) {
  console.log('User:', data.user)
} else {
  // Redirect to login
  window.location.href = '/login'
}
```

### Logout

```typescript
await fetch('/api/auth/logout', { method: 'POST' })
window.location.href = '/login'
```

### Fetch GitHub Repos

```typescript
const response = await fetch('/api/github/repos')
const data = await response.json()

if (response.ok) {
  console.log('Repositories:', data)
} else {
  console.error('Error:', data.error)
}
```

---

## Security Considerations

1. **Password Storage**: Passwords are hashed using SHA-256 (consider upgrading to bcrypt for production)
2. **Session Security**: Sessions use httpOnly cookies to prevent XSS attacks
3. **CSRF Protection**: OAuth flows use state parameter for CSRF protection
4. **Token Expiration**: JWT tokens expire after 7 days
5. **Secure Cookies**: Cookies are marked secure in production (HTTPS only)

## Production Recommendations

1. **Use a real database** instead of in-memory storage
2. **Upgrade password hashing** to bcrypt or argon2
3. **Add rate limiting** to prevent brute force attacks
4. **Implement refresh tokens** for longer sessions
5. **Add email verification** for new registrations
6. **Set up proper monitoring** for auth failures
7. **Use environment-specific secrets** (never commit .env files)
