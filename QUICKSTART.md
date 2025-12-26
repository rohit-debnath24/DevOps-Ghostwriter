# 🚀 Quick Start Guide - OAuth Authentication

## Prerequisites
- Node.js installed
- pnpm installed
- GitHub account
- Google account

## 1️⃣ Install Dependencies (Already Done ✅)

```bash
pnpm install
```

## 2️⃣ Set Up Environment Variables

### Create `.env.local` file:

```bash
# Copy the example file
cp .env.local.example .env.local
```

### Generate JWT Secret:

**Windows PowerShell:**
```powershell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

**Linux/Mac:**
```bash
openssl rand -base64 32
```

### Edit `.env.local` and add:

```env
# JWT (Use your generated secret)
JWT_SECRET=your-generated-secret-here
JWT_EXPIRES_IN=7d

# GitHub OAuth (Get from GitHub)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_CALLBACK_URL=http://localhost:3000/api/auth/github/callback

# Google OAuth (Get from Google Cloud)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_CALLBACK_URL=http://localhost:3000/api/auth/google/callback

# App URL
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## 3️⃣ Set Up GitHub OAuth

1. Go to: https://github.com/settings/developers
2. Click **"New OAuth App"**
3. Fill in:
   - **Application name**: Ghostwriter
   - **Homepage URL**: `http://localhost:3000`
   - **Callback URL**: `http://localhost:3000/api/auth/github/callback`
4. Click **"Register application"**
5. Copy **Client ID** and generate **Client Secret**
6. Paste into `.env.local`

## 4️⃣ Set Up Google OAuth

1. Go to: https://console.cloud.google.com/
2. Create new project: **"Ghostwriter"**
3. Enable APIs:
   - Go to **"APIs & Services"** → **"Library"**
   - Enable **"Google+ API"**
4. Create OAuth Credentials:
   - Go to **"APIs & Services"** → **"Credentials"**
   - Click **"Create Credentials"** → **"OAuth client ID"**
   - Configure consent screen if needed (External, add your email)
   - Choose **"Web application"**
   - Add authorized redirect URI: `http://localhost:3000/api/auth/google/callback`
5. Copy **Client ID** and **Client Secret**
6. Paste into `.env.local`

## 5️⃣ Start Development Server

```bash
pnpm dev
```

## 6️⃣ Test Authentication

### Test Local Registration
1. Visit: http://localhost:3000/sign-up
2. Fill in the form
3. Click **"Register"**
4. Should redirect to `/dashboard/{userId}`

### Test Local Login
1. Visit: http://localhost:3000/login
2. Enter email and password
3. Click **"Submit"**
4. Should redirect to `/dashboard/{userId}`

### Test GitHub OAuth
1. Visit: http://localhost:3000/login
2. Click **"GitHub"** button
3. Authorize the app
4. Should redirect to `/dashboard/{userId}`

### Test Google OAuth
1. Visit: http://localhost:3000/login
2. Click **"Google"** button
3. Choose Google account
4. Should redirect to `/dashboard/{userId}`

### Test GitHub Repo Fetch
1. Login with GitHub OAuth
2. Go to `/dashboard/{userId}`
3. Click the GitHub icon in the input field
4. Should see a toast with number of repos loaded

## 7️⃣ Verify Session

Open browser console and run:

```javascript
fetch('/api/auth/session')
  .then(r => r.json())
  .then(d => console.log(d))
```

Should see:
```json
{
  "authenticated": true,
  "user": {
    "userId": "...",
    "email": "...",
    "name": "...",
    "provider": "local|github|google"
  }
}
```

## 8️⃣ Test Logout

```javascript
fetch('/api/auth/logout', { method: 'POST' })
  .then(() => window.location.href = '/login')
```

## 🎯 What's Working

✅ **User Registration** - Email/password with validation
✅ **User Login** - Email/password authentication  
✅ **GitHub OAuth** - Full GitHub integration
✅ **Google OAuth** - Full Google integration
✅ **Session Management** - JWT tokens in cookies
✅ **Session Validation** - Check if user is logged in
✅ **Logout** - Clear session
✅ **GitHub API** - Fetch repos after GitHub OAuth
✅ **User IDs** - nanoid(16) for unique IDs
✅ **Session IDs** - UUID v4 for session tracking
✅ **Security** - httpOnly cookies, CSRF protection, password hashing

## 🔍 Debugging Tips

### Check Environment Variables
```bash
# In PowerShell
Get-Content .env.local
```

### Check Cookies in Browser
1. Open DevTools (F12)
2. Go to Application → Cookies
3. Look for: `session`, `github_token`, `google_token`

### Check Server Logs
Look for console outputs:
- `[Ghostwriter] New operator registered:`
- `[Ghostwriter] Operator authenticated:`
- `GitHub Token from cookies:`

### Common Issues

**"OAuth not configured"**
- Make sure `.env.local` exists and has all variables
- Restart dev server after changing `.env.local`

**"Redirect URI mismatch"**
- Check callback URLs match exactly in OAuth apps
- Must include `http://` and full path

**"Invalid state"**
- Clear browser cookies
- This is CSRF protection working correctly

**Session not working**
- Check browser allows cookies
- Check cookie domain matches your URL
- Look for errors in browser console

## 📁 Project Structure

```
app/
  api/
    auth/
      login/route.ts          # Email/password login
      register/route.ts       # User registration
      logout/route.ts         # Session termination
      session/route.ts        # Session validation
      github/
        route.ts              # GitHub OAuth start
        callback/route.ts     # GitHub OAuth callback
      google/
        route.ts              # Google OAuth start
        callback/route.ts     # Google OAuth callback
    github/
      repos/route.ts          # Fetch GitHub repos
lib/
  jwt.ts                      # JWT utilities
  db.ts                       # User model & storage
components/
  login-form.tsx              # Login UI
  signup-form.tsx             # Registration UI
```

## 🔗 Useful Links

- **OAuth Setup**: See `OAUTH_SETUP.md`
- **API Docs**: See `API_DOCUMENTATION.md`
- **Summary**: See `IMPLEMENTATION_SUMMARY.md`

## 🆘 Need Help?

1. Check the documentation files
2. Review console logs for errors
3. Verify environment variables are set
4. Check OAuth app configurations
5. Open an issue on GitHub

---

**Ready to code!** 🎉

Your authentication system is fully set up and ready to use. Start building your features!
