# Admin Guide: Migrating n8n LinkedIn Trigger to a New Gmail Account

This document outlines the exact, step-by-step process to migrate your automated LinkedIn comment workflow from `j.sam.bruce@gmail.com` to `jeanluc.leroux78@gmail.com`.

This migration contains three major phases:
1. Setting up the Google Cloud API Credentials (Client ID & Secret).
2. Authorizing n8n to read the new inbox.
3. Moving the Apps Script trigger to the new inbox.

---

## Phase 1: Generating Google Cloud API Credentials
n8n needs a specific "Client ID" and "Client Secret" from Google to securely read emails from `jeanluc.leroux78@gmail.com` without storing your actual password.

### 1. Create a Google Cloud Project
1. Open an Incognito/Private browsing window (to ensure you don't accidentally use the wrong Google account).
2. Log into exactly **`jeanluc.leroux78@gmail.com`**.
3. Go to the [Google Cloud Console](https://console.cloud.google.com/).
4. Accept the terms of service if prompted.
5. In the top-left corner (next to the Google Cloud logo), click the dropdown that says **"Select a project"**.
6. Click **"New Project"** in the top right of the popup window.
7. Name it something like `n8n-gmail-integration` and click **Create**.
8. Wait a few seconds, then select your new project from the top-left dropdown.

### 2. Enable the Gmail API
1. Using the left-hand navigation menu (the "hamburger" icon), go to **APIs & Services** > **Library**.
2. Search for **"Gmail API"**.
3. Click on the **Gmail API** result.
4. Click the blue **Enable** button.

### 3. Configure the Google Auth Platform (OAuth)
1. Once the Gmail API is enabled, go back to the left menu: **APIs & Services** > **OAuth consent screen** (this may also be called **Google Auth Platform**).
2. On the left sidebar of the Auth Platform, click **Branding**. Fill out the required App information:
   - **App name:** `n8n-linkedin-bot`
   - **User support email:** Select `jeanluc.leroux78@gmail.com`
   - **Developer contact information:** Type `jeanluc.leroux78@gmail.com`
   - Click **Save**.
3. On the left sidebar, click **Audience**.
4. Under User Type, ensure **External** is selected.
5. Scroll down to **Test users** and click the blue **+ Add users** button.
6. Type exactly `jeanluc.leroux78@gmail.com` and click **Add** or **Save**.

### 4. Create the Client ID & Secret
1. On the left sidebar of the Auth Platform, click **Clients**.
2. Click **Create Client** at the top.
3. Select **Web application** as the Application type.
5. Name it `n8n Webhook`.
6. Scroll down to **Authorized redirect URIs** and click **+ Add URI**.
7. Go to your n8n dashboard, open your workflow, and double-click the `Gmail: Get Full Message` node.
8. Click the `Credential for Gmail API` dropdown, and click **Create New Credential**.
9. Look at the top of that popup box—there is a URL provided called the **OAuth Redirect URL** (it usually ends in `/rest/oauth2-credential/callback`). Copy this URL.
10. Go back to Google Cloud and paste that URL into the **Authorized redirect URIs** box.
11. Click **Create**.
12. Google will display a popup with **Your Client ID** and **Your Client Secret**. Leave this tab open!

---

## Phase 2: Authorizing n8n
Now that Google has given us the secure keys, we give them to n8n.

1. Go back to the n8n popup box where you copied the Redirect URL.
2. Paste the **Client ID** into the matching box.
3. Paste the **Client Secret** into the matching box.
4. Click **Sign in with Google** at the bottom.
5. A new window will pop up asking which Google account to use. Select `jeanluc.leroux78@gmail.com`.
6. Google will show a scary warning saying "Google hasn't verified this app." 
   - *This is completely normal because you just created it 2 minutes ago.*
   - Click **Advanced** (at the bottom).
   - Click **Go to n8n-linkedin-bot (unsafe)**.
7. Check the boxes to allow the app to view and manage your mail, then click **Continue**.
8. The window will close, and n8n will say **"Account connected successfully"**. Save the credential!
9. Finally, in the `Gmail: Get Full Message` node, make sure your new credential is selected in the dropdown. Save your workflow.

---

## Phase 3: Moving the Automatic Trigger
Now n8n has permission, we just need to tell the new Gmail account to actually send the trigger when an email arrives.

### 1. Set up the Label & Filter in the new account
1. Go to the inbox of `jeanluc.leroux78@gmail.com`.
2. Create a new label named exactly **`LinkedIn-AI`**.
3. Create a Filter that finds emails from `updates@linkedin.com`.
4. Set the filter rules to automatically apply the `LinkedIn-AI` label **AND** check the box for "Skip the Inbox (Archive it)".

### 2. Create the Apps Script
1. While logged into `jeanluc.leroux78@gmail.com`, go to [script.google.com](https://script.google.com/).
2. Click **New Project** and name it `LinkedIn n8n Trigger`.
3. Paste the Javascript payload code:
```javascript
// Ensure this is your PRODUCTION n8n webhook URL
const N8N_WEBHOOK_URL = 'YOUR_PRODUCTION_WEBHOOK_URL_HERE';

function processLinkedInEmails() {
  const SEARCH_QUERY = 'label:LinkedIn-AI is:unread';
  const threads = GmailApp.search(SEARCH_QUERY);
  
  if (threads.length === 0) return;
  
  for (let i = 0; i < threads.length; i++) {
    const messages = threads[i].getMessages();
    const latestMessage = messages[messages.length - 1];
    
    if (latestMessage.isUnread()) {
      const payload = {
        "messageId": latestMessage.getId(),
        "subject": latestMessage.getSubject()
      };
      
      const options = {
        'method': 'post',
        'contentType': 'application/json',
        'payload': JSON.stringify(payload)
      };
      
      try {
        UrlFetchApp.fetch(N8N_WEBHOOK_URL, options);
        latestMessage.markRead();
      } catch (e) {
        console.error("Failed to trigger n8n: " + e.toString());
      }
    }
  }
}
```
4. Paste your exact n8n Production Webhook URL into Line 2.
5. Save the script (floppy disk icon).

### 3. Schedule the Automated Trigger
1. On the left side of the Apps Script dashboard, click the **Triggers** icon (looks like an alarm clock).
2. Click **+ Add Trigger** (bottom right).
3. Set the configuration exactly to:
   - Function to run: `processLinkedInEmails`
   - Event source: `Time-driven`
   - Type of time based trigger: `Minutes timer`
   - Minute interval: `Every minute`
4. Click **Save**.
5. Google will ask you to authorize the script (it's the exact same "Advanced -> Go to script -> Allow" process as before).

### 4. Clean up the Old Account
1. Log back into your **old** `j.sam.bruce@gmail.com` account.
2. Go to [script.google.com](https://script.google.com/).
3. Open the old "LinkedIn n8n Trigger" project.
4. Go to Triggers, find the "Every minute" trigger, click the three dots `...` next to it, and click **Delete**.
   - *(This prevents the old email account from triggering n8n for no reason).*

**You are completely done!** The automation is now permanently tied to `jeanluc.leroux78@gmail.com`.
