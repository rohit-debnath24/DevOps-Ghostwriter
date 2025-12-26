# OAuth Setup Guide - Ghostwriter

This guide will help you set up Google and GitHub OAuth for the Ghostwriter application.

## Prerequisites

- A GitHub account
- A Google account
- Your application running locally (default: http://localhost:3000)

## Environment Variables

First, copy the `.env.local.example` file to `.env.local`:

```bash
cp .env.local.example .env.local
```

## 1. GitHub OAuth Setup

### Step 1: Create a GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **"New OAuth App"**
3. Fill in the details:
   - **Application name**: Ghostwriter (or your preferred name)
   - **Homepage URL**: `http://localhost:3000`
   - **Authorization callback URL**: `http://localhost:3000/api/auth/github/callback`
4. Click **"Register application"**

### Step 2: Get Your Credentials

1. After creating the app, you'll see your **Client ID**
2. Click **"Generate a new client secret"** to get your **Client Secret**
3. Copy both values

### Step 3: Update .env.local

```env
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
GITHUB_CALLBACK_URL=http://localhost:3000/api/auth/github/callback
```

## 2. Google OAuth Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project name (e.g., "Ghostwriter") and click **"Create"**

### Step 2: Enable Google+ API

1. In your project dashboard, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google+ API"** and enable it
3. Also enable **"Google OAuth2 API"**

### Step 3: Create OAuth Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. If prompted, configure the OAuth consent screen:
   - User Type: **External**
   - App name: **Ghostwriter**
   - User support email: Your email
   - Developer contact: Your email
   - Add scopes: `userinfo.email` and `userinfo.profile`
   - Add test users (your email)
   - Save and continue
4. Back in Credentials, click **"Create Credentials"** → **"OAuth client ID"**
5. Choose **"Web application"**
6. Fill in:
   - **Name**: Ghostwriter Web Client
   - **Authorized JavaScript origins**: `http://localhost:3000`
   - **Authorized redirect URIs**: `http://localhost:3000/api/auth/google/callback`
7. Click **"Create"**

### Step 4: Get Your Credentials

1. Copy the **Client ID** and **Client Secret**

### Step 5: Update .env.local

```env
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_CALLBACK_URL=http://localhost:3000/api/auth/google/callback
```

## 3. JWT Configuration

Generate a secure random string for JWT_SECRET:

```bash
# On Linux/Mac:
openssl rand -base64 32

# On Windows PowerShell:
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

Update in `.env.local`:

```env
JWT_SECRET=your_generated_secret_here
JWT_EXPIRES_IN=7d
```

## 4. Final .env.local Example

Your complete `.env.local` should look like:

```env
# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRES_IN=7d

# GitHub OAuth
GITHUB_CLIENT_ID=Ov23abc123def456
GITHUB_CLIENT_SECRET=abc123def456ghi789jkl012mno345pqr678stu901
GITHUB_CALLBACK_URL=http://localhost:3000/api/auth/github/callback

# Google OAuth
GOOGLE_CLIENT_ID=123456789012-abc123def456ghi789jkl012mno345pq.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abc123def456ghi789jkl012
GOOGLE_CALLBACK_URL=http://localhost:3000/api/auth/google/callback

# Application URL
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## 5. Testing

1. Start your development server:
   ```bash
   pnpm dev
   ```

2. Navigate to:
   - Sign up: `http://localhost:3000/sign-up`
   - Login: `http://localhost:3000/login`

3. Try the OAuth buttons:
   - Click **"Google"** to sign in with Google
   - Click **"GitHub"** to sign in with GitHub

## Production Deployment

When deploying to production:

1. Update all URLs in your OAuth apps:
   - GitHub: Update Homepage URL and Callback URL to your production domain
   - Google: Update Authorized origins and redirect URIs

2. Update `.env` variables:
   ```env
   NEXT_PUBLIC_APP_URL=https://your-domain.com
   GITHUB_CALLBACK_URL=https://your-domain.com/api/auth/github/callback
   GOOGLE_CALLBACK_URL=https://your-domain.com/api/auth/google/callback
   ```

3. Generate a new, strong JWT_SECRET for production

4. For Google OAuth in production, submit your app for verification if needed

## Features Implemented

✅ **JWT Session Management**
- Sessions stored as httpOnly cookies
- UUID v4 for session IDs
- nanoid for user IDs
- 7-day expiration (configurable)

✅ **OAuth Providers**
- GitHub OAuth with repository access
- Google OAuth with profile access

✅ **Authentication Routes**
- `/api/auth/login` - Email/password login
- `/api/auth/register` - User registration
- `/api/auth/logout` - Session termination
- `/api/auth/session` - Session validation
- `/api/auth/github` - GitHub OAuth initiation
- `/api/auth/github/callback` - GitHub callback
- `/api/auth/google` - Google OAuth initiation
- `/api/auth/google/callback` - Google callback

✅ **Security Features**
- Password hashing with SHA-256
- CSRF protection with state parameter
- httpOnly cookies
- Secure cookies in production
- Session validation

## Troubleshooting

### "OAuth not configured" error
- Check that all environment variables are set in `.env.local`
- Restart your development server after changing `.env.local`

### "Redirect URI mismatch" error
- Verify callback URLs match exactly in OAuth app settings
- Include `http://` or `https://` in URLs
- Check for trailing slashes

### "Invalid state" error
- Clear your browser cookies
- This is CSRF protection - ensure cookies are enabled

### Session not persisting
- Check that cookies are enabled in your browser
- Verify the domain matches your application URL
- Check browser console for cookie errors

## Database Migration (Future)

Currently using in-memory storage. To migrate to a database:

1. Replace `lib/db.ts` with your database ORM (Prisma, Drizzle, etc.)
2. Implement the same interface:
   - `createUser()`
   - `findUserByEmail()`
   - `findUserByGitHubId()`
   - `findUserByGoogleId()`
   - `updateUser()`
3. Keep the same user ID generation (nanoid) and password hashing

## Support

For issues or questions, please open an issue on the GitHub repository.
