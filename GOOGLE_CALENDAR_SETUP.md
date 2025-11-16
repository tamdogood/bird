# Google Calendar OAuth2 Setup Guide

This guide provides detailed instructions for setting up Google Calendar integration with the Bird MCP server using OAuth2 authentication.

## Overview

The Google Calendar integration uses OAuth2 authentication to securely access your Google Calendar. This requires:

1. A Google Cloud project with the Calendar API enabled
2. OAuth2 credentials (client ID and secret)
3. User consent to access calendar data
4. A stored access token for ongoing requests

## Prerequisites

- A Google account
- Access to [Google Cloud Console](https://console.cloud.google.com/)
- The Bird MCP server installed and configured

## Step-by-Step Setup

### 1. Create a Google Cloud Project

1. Navigate to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top of the page
3. Click "New Project"
4. Enter project details:
   - **Project name**: `Bird MCP Calendar` (or your preferred name)
   - **Organization**: Leave as "No organization" (unless you have one)
5. Click "Create"
6. Wait for the project to be created (you'll see a notification)
7. Select your new project from the dropdown

### 2. Enable Google Calendar API

1. In the Google Cloud Console, open the navigation menu (☰)
2. Go to "APIs & Services" > "Library"
3. In the search box, type "Google Calendar API"
4. Click on "Google Calendar API" in the results
5. Click the "Enable" button
6. Wait for the API to be enabled (you'll see the API dashboard)

### 3. Configure OAuth Consent Screen

This screen is what users see when they grant calendar access to your app.

#### Basic Information

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select user type:
   - **External**: For personal Google accounts (recommended for most users)
   - **Internal**: Only if you have a Google Workspace organization
3. Click "Create"

#### App Information

Fill in the required fields:

- **App name**: `Bird MCP Server`
- **User support email**: Your email address
- **App logo**: (Optional) You can skip this
- **Application home page**: (Optional) You can leave blank
- **Application privacy policy link**: (Optional) You can leave blank
- **Application terms of service link**: (Optional) You can leave blank
- **Authorized domains**: (Optional) You can leave blank

Developer contact information:
- **Email addresses**: Your email address

Click "Save and Continue"

#### Scopes Configuration

1. On the "Scopes" page, click "Add or Remove Scopes"
2. In the filter box, type "calendar"
3. Find and select the following scope:
   - `https://www.googleapis.com/auth/calendar` (Full calendar access)
   - Description: "See, edit, share, and permanently delete all the calendars you can access using Google Calendar"
4. Click "Update" at the bottom
5. Verify the scope appears in the "Your sensitive scopes" section
6. Click "Save and Continue"

#### Test Users

For development and personal use, you need to add your Google account as a test user:

1. On the "Test users" page, click "+ Add Users"
2. Enter your Google account email address
3. Click "Add"
4. You should see your email in the test users list
5. Click "Save and Continue"

#### Review and Confirm

1. Review your OAuth consent screen configuration
2. Click "Back to Dashboard"

**Important**: Your app will be in "Testing" mode, which means:
- Only test users (the email you added) can authorize the app
- You don't need to go through Google's verification process
- The app works perfectly for personal use
- To allow any Google account, you'd need to publish and verify the app (not required)

### 4. Create OAuth2 Credentials

Now you'll create the actual credentials file that the Bird MCP server uses.

1. Go to "APIs & Services" > "Credentials"
2. Click "+ Create Credentials" at the top
3. Select "OAuth client ID"
4. Configure the OAuth client:
   - **Application type**: Select "Desktop app"
   - **Name**: `Bird MCP Desktop` (or your preferred name)
5. Click "Create"
6. A dialog will appear showing your client ID and secret
7. Click "Download JSON" to download the credentials file
8. Save the file to a secure location on your computer
   - Suggested location: `~/.bird_mcp/credentials.json`
   - Or keep it in a secure folder like `~/Documents/api-credentials/`

**Important Security Notes**:
- This credentials file contains your OAuth2 client secret
- Keep it secure and never commit it to version control
- Never share it publicly

### 5. Configure Bird MCP Server

#### Set Environment Variables

Create or edit your `.env` file in the Bird MCP project directory:

```bash
# Google Calendar Integration
GOOGLE_CALENDAR_CREDENTIALS_PATH=/absolute/path/to/credentials.json

# Optional: Custom token storage location (defaults to ~/.bird_mcp/google_calendar_token.pickle)
# GOOGLE_CALENDAR_TOKEN_PATH=/custom/path/to/token.pickle
```

**Path Requirements**:
- Must be an absolute path (not relative)
- Good: `/Users/username/.bird_mcp/credentials.json`
- Good: `/home/username/Documents/credentials.json`
- Bad: `~/credentials.json` (tilde won't expand)
- Bad: `./credentials.json` (relative path)

#### Verify Configuration

Before running the server, verify:

1. Credentials file exists at the specified path:
   ```bash
   ls -l /path/to/credentials.json
   ```

2. File has proper permissions (readable by you):
   ```bash
   chmod 600 /path/to/credentials.json
   ```

3. Environment variable is set:
   ```bash
   grep GOOGLE_CALENDAR_CREDENTIALS_PATH .env
   ```

### 6. Initial Authentication

The first time you use the Google Calendar integration, you'll authenticate via OAuth2 flow:

#### Run the Server

```bash
# Activate virtual environment if using one
source venv/bin/activate  # or: source .venv/bin/activate

# Start the server
python -m bird_mcp.server
```

#### Authentication Flow

1. **Browser Opens Automatically**:
   - A browser window will open automatically
   - You'll see the Google sign-in page

2. **Sign In**:
   - Sign in with the Google account you added as a test user
   - If you're already signed in, select the correct account

3. **Grant Permissions**:
   - Review the permissions requested (Calendar access)
   - Click "Allow" or "Continue"

4. **Success**:
   - You'll see a success message in your browser
   - The browser will say "The authentication flow has completed"
   - You can close the browser window

5. **Token Saved**:
   - The access token is automatically saved to `~/.bird_mcp/google_calendar_token.pickle`
   - Future requests will use this token without opening a browser

#### Troubleshooting Authentication

**Browser doesn't open automatically**:
- Check the terminal output for an authentication URL
- Copy and paste the URL into your browser manually
- Complete the authentication in the browser

**"Access blocked: This app's request is invalid"**:
- Verify you added your email as a test user in OAuth consent screen
- Make sure the Google Calendar API is enabled
- Check that you're using the correct Google account

**"Error: invalid_client"**:
- Your credentials file may be incorrect
- Re-download the credentials.json from Google Cloud Console
- Verify GOOGLE_CALENDAR_CREDENTIALS_PATH points to the correct file

### 7. Verify Integration

After authentication, test the integration:

```python
# In Claude Code or MCP client, try:
"List my Google calendars"
"What events do I have today?"
"Create a calendar event tomorrow at 2pm called 'Test Event'"
```

Or use the health check:

```python
"Check the health of my MCP server"
```

You should see Google Calendar listed as "connected" in the health check results.

## Token Management

### Token Storage

- **Default location**: `~/.bird_mcp/google_calendar_token.pickle`
- **Custom location**: Set via `GOOGLE_CALENDAR_TOKEN_PATH` environment variable
- **Format**: Pickled Python object containing OAuth2 credentials
- **Security**: Keep this file secure - it grants access to your calendar

### Token Lifecycle

1. **Initial Creation**: Created during first authentication
2. **Automatic Refresh**: Token is automatically refreshed when it expires (typically after 1 hour)
3. **Persistent Storage**: Refreshed tokens are saved back to the file
4. **Long-term Validity**: Refresh tokens are valid until revoked

### Revoking Access

To revoke calendar access:

1. **Delete the token file**:
   ```bash
   rm ~/.bird_mcp/google_calendar_token.pickle
   ```

2. **Revoke from Google Account**:
   - Go to [Google Account Permissions](https://myaccount.google.com/permissions)
   - Find "Bird MCP Server" in the list
   - Click "Remove Access"

3. **Re-authenticate**: Next time you use the integration, you'll need to authenticate again

## Using with Docker

Docker requires special configuration for OAuth2 authentication:

### Prepare Credentials

```bash
# Create directory for credentials
mkdir -p ~/.bird_mcp

# Copy credentials file
cp /path/to/downloaded/credentials.json ~/.bird_mcp/
```

### First-Time Authentication

OAuth2 authentication requires browser interaction, which doesn't work inside Docker. You have two options:

#### Option A: Authenticate Outside Docker First (Recommended)

1. Run authentication on your host machine:
   ```bash
   # Without Docker
   python -m bird_mcp.server
   ```

2. Complete the browser authentication flow

3. Verify token was created:
   ```bash
   ls ~/.bird_mcp/google_calendar_token.pickle
   ```

4. Now run with Docker, mounting the token:
   ```bash
   docker run -i --rm \
     --env-file .env \
     -v ~/.bird_mcp:/root/.bird_mcp:rw \
     -e GOOGLE_CALENDAR_CREDENTIALS_PATH=/root/.bird_mcp/credentials.json \
     -e GOOGLE_CALENDAR_TOKEN_PATH=/root/.bird_mcp/google_calendar_token.pickle \
     bird-mcp
   ```

#### Option B: Use Docker with Port Forwarding

```bash
# Run Docker with port mapping for OAuth callback
docker run -i --rm \
  --env-file .env \
  -v ~/.bird_mcp:/root/.bird_mcp:rw \
  -p 8080:8080 \
  -e GOOGLE_CALENDAR_CREDENTIALS_PATH=/root/.bird_mcp/credentials.json \
  bird-mcp
```

### Docker Compose

Update your `docker-compose.yml`:

```yaml
services:
  bird-mcp:
    build: .
    stdin_open: true
    tty: true
    env_file:
      - .env
    environment:
      - GOOGLE_CALENDAR_CREDENTIALS_PATH=/root/.bird_mcp/credentials.json
      - GOOGLE_CALENDAR_TOKEN_PATH=/root/.bird_mcp/google_calendar_token.pickle
    volumes:
      # Mount credentials directory
      - ~/.bird_mcp:/root/.bird_mcp:rw
```

## Security Best Practices

### Credentials File Security

1. **Never commit to version control**:
   - Add `credentials.json` to `.gitignore`
   - Add `*.pickle` to `.gitignore`

2. **Restrict file permissions**:
   ```bash
   chmod 600 ~/.bird_mcp/credentials.json
   chmod 600 ~/.bird_mcp/google_calendar_token.pickle
   ```

3. **Store in secure location**:
   - User's home directory: `~/.bird_mcp/`
   - System credentials folder: `/etc/bird-mcp/` (for system-wide deployment)
   - Encrypted storage (if available)

### Scope Minimization

The integration uses the minimum required scope:
- `https://www.googleapis.com/auth/calendar` - Full calendar access

If you only need read-only access, you could modify the code to use:
- `https://www.googleapis.com/auth/calendar.readonly` - Read-only access

To change scopes:
1. Edit `src/bird_mcp/google_calendar_tools.py`
2. Change `SCOPES` constant
3. Delete existing token file
4. Re-authenticate

### Token Security

1. **Keep tokens secure**: Treat like passwords
2. **Regular rotation**: Revoke and re-create if compromised
3. **Monitor access**: Check [Google Account Activity](https://myaccount.google.com/security) regularly
4. **Limit exposure**: Don't copy tokens to multiple machines unnecessarily

## Publishing Your App (Optional)

If you want to allow any Google account to use your app (not just test users), you need to publish and verify:

### Verification Process

1. Go to "APIs & Services" > "OAuth consent screen"
2. Click "Publish App"
3. Confirm publication
4. Submit for verification:
   - Google will review your app
   - Process can take several weeks
   - Requires privacy policy and terms of service
   - May require additional documentation

### When to Publish

You should publish if:
- You want to share the integration with others
- You need to support multiple Google accounts
- You're deploying for a team or organization

You don't need to publish if:
- Using for personal use only
- All users can be added as test users (up to 100 users)
- You control all the accounts that will use it

## Troubleshooting

### Common Issues

#### "Credentials file not found"

**Cause**: Path in environment variable is incorrect

**Solution**:
```bash
# Verify file exists
ls -l /path/to/credentials.json

# Check environment variable
echo $GOOGLE_CALENDAR_CREDENTIALS_PATH

# Use absolute path in .env
GOOGLE_CALENDAR_CREDENTIALS_PATH=/Users/username/.bird_mcp/credentials.json
```

#### "Access blocked: This app's request is invalid"

**Cause**: Email not added as test user, or wrong Google account

**Solution**:
1. Go to OAuth consent screen in Google Cloud Console
2. Add your email as a test user
3. Sign in with the correct Google account during authentication
4. Wait a few minutes for changes to propagate

#### "Token has been expired or revoked"

**Cause**: Token file is corrupted or access was revoked

**Solution**:
```bash
# Delete token file
rm ~/.bird_mcp/google_calendar_token.pickle

# Restart server to re-authenticate
python -m bird_mcp.server
```

#### "Calendar API has not been used in project"

**Cause**: Calendar API not enabled in Google Cloud project

**Solution**:
1. Go to APIs & Services > Library
2. Search for "Google Calendar API"
3. Click "Enable"
4. Wait a minute, then try again

### Getting Help

If you encounter issues not covered here:

1. **Check server logs**: Run with `python -m bird_mcp.server` to see error messages
2. **Verify API status**: Check [Google Cloud Status Dashboard](https://status.cloud.google.com/)
3. **Review quotas**: Check API quotas in Google Cloud Console
4. **Test API directly**: Use [Google API Explorer](https://developers.google.com/calendar/api/v3/reference) to test Calendar API

## Additional Resources

- [Google Calendar API Documentation](https://developers.google.com/calendar/api/guides/overview)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Bird MCP Server Documentation](README.md)

## Summary Checklist

- [ ] Google Cloud project created
- [ ] Google Calendar API enabled
- [ ] OAuth consent screen configured
- [ ] Test user added (your email)
- [ ] OAuth2 credentials created and downloaded
- [ ] Credentials file saved securely
- [ ] Environment variable set in `.env`
- [ ] Initial authentication completed
- [ ] Token file created successfully
- [ ] Integration tested and working

Once all items are checked, your Google Calendar integration is fully configured and ready to use.
