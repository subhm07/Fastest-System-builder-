# Connect Hermes to Your YouTube Channel Safely

Security Analyst, this is the safe connection method.

Do not give Hermes your Google password. Instead, connect through Google OAuth. OAuth lets you approve access in the browser and creates a local token that Hermes can use without knowing your password.

## Current status

Not connected yet.

Reason:
You need to create/download a Google Cloud OAuth Client JSON file first.

## What I created

Connector script:
/home/shubham/shubham-studio-youtube-channel/youtube_oauth.py

It can:
- Generate Google OAuth authorization URL
- Exchange browser approval code for a local YouTube token
- Check connection status
- Read your YouTube channel metadata
- Store token at ~/.hermes/youtube_token.json

## Step 1: Secure your Google account first

Because a password was shared in chat earlier, rotate it immediately:
https://myaccount.google.com/security

Enable:
- 2-Step Verification
- Recovery email
- Recovery phone
- Review logged-in devices

## Step 2: Create Google OAuth client

1. Go to Google Cloud Console:
https://console.cloud.google.com/projectselector2/home/dashboard

2. Create/select project:
Name suggestion:
Shubham Studio YouTube Automation

3. Enable YouTube Data API v3:
https://console.cloud.google.com/apis/library/youtube.googleapis.com

4. Open Credentials:
https://console.cloud.google.com/apis/credentials

5. Click:
Create Credentials -> OAuth client ID

6. If asked to configure consent screen:
- User type: External
- App name: Shubham Studio YouTube Automation
- User support email: your Gmail
- Developer contact email: your Gmail
- Publishing status can remain Testing
- Add your Gmail as a test user

7. OAuth client type:
Desktop app

8. Download JSON credentials file.

## Step 3: Give me the downloaded file path

Example message:
The OAuth JSON file path is: /mnt/c/Users/YOUR_WINDOWS_USER/Downloads/client_secret_XXXXX.json

Important CLI note:
Do not send only a path starting with / as a standalone message if your terminal treats it as a slash command. Put it in a sentence.

## Step 4: I will generate the auth URL

After you give the JSON path, I will run:
python3 /home/shubham/shubham-studio-youtube-channel/youtube_oauth.py auth-url --client-secret "YOUR_JSON_PATH"

Then I will give you an approval URL.

## Step 5: You approve access manually

Open the approval URL in your browser, select your Google account, approve access.

The browser may fail at:
http://localhost:1/

That is expected.

Copy the entire URL from the browser address bar and paste it back here.
It will look like:
http://localhost:1/?code=...&scope=...

## Step 6: I will finish the connection

I will exchange that code using:
python3 /home/shubham/shubham-studio-youtube-channel/youtube_oauth.py auth-code "PASTED_URL"

Then I will verify using:
python3 /home/shubham/shubham-studio-youtube-channel/youtube_oauth.py check
python3 /home/shubham/shubham-studio-youtube-channel/youtube_oauth.py channel

## YouTube scopes requested

The script requests:
- YouTube read-only access
- Upload access
- YouTube channel management access

Reason:
You said you want to access and stream/manage the channel through Hermes later.

## Security notes

- Your password is never used.
- OAuth token stays local under ~/.hermes/.
- You can revoke access anytime from:
https://myaccount.google.com/permissions

Local revoke command:
python3 /home/shubham/shubham-studio-youtube-channel/youtube_oauth.py revoke-local
