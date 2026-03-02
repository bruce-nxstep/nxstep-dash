# AI LinkedIn Commenter Workflow (Batch Support)

This n8n workflow uses an AI Agent (powered by OpenAI GPT-4o) to generate professional comments for a **batch** of LinkedIn posts.

## Features
- **Batch Processing**: Accepts a list of posts in a single request.
- **AI-Powered**: Uses GPT-4o to generate relevant comments for each post.
- **Mock Data**: Includes a built-in mock data generator for easy testing without external tools.

## Setup

1.  **Import the Workflow**:
    - Open your n8n dashboard.
    - Click "Workflows" -> "Import from File".
    - Select `n8n-linkedin-comment-workflow.json`.

2.  **Configure Credentials**:
    - Double-click the **OpenAI Chat Model** node.
    - Create or select your "OpenAI API" credentials.

3.  **Activate**:
    - Toggle the "Active" switch to use the Webhook.

## Usage

### Method 1: Manual Testing (Built-in)
1.  Click **"Execute Workflow"**.
2.  The workflow is pre-configured with a "Mock Data" node. It will simulate receiving 2 posts.
3.  Check the output of the **AI Agent** node to see the 2 generated comments.

### 3. Authentication (LinkedIn)
To auto-publish comments, you need to authenticate n8n with LinkedIn.
1.  **Create an App**: Go to the [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps).
2.  **Create App**: Click "Create app". Fill in details (Company page is required).
3.  **Products**: In the "Products" tab, request access to **"Share on LinkedIn"** and **"Sign In with LinkedIn using OpenID Connect"**. This gives you the `w_member_social` scope.
4.  **Auth Code (n8n)**:
    -   In n8n, create a new Credential: **LinkedIn OAuth2 API**.
    -   Copy the "OAuth Redirect URL" from n8n.
5.  **Auth Settings (LinkedIn)**:
    -   Go to "Auth" tab in your LinkedIn App.
    -   Paste the Redirect URL under "Authorized redirect URLs for your app".
    -   Copy the **Client ID** and **Client Secret**.
6.  **Finalize in n8n**:
    -   Paste Client ID/Secret into n8n credentials.
    -   Click "Connect".

### 4. Configuration
1.  **Open the Workflow**: Import `n8n-linkedin-monitor-workflow.json`.
2.  **Target Profiles**: Update the `Config` node.
3.  **Apify**: Ensure your `Apify API` credential is set in the Run/Get Data nodes.
4.  **LinkedIn**: Ensure your `LinkedIn OAuth2` credential is set in the "LinkedIn: Publish Comment" node.ts.

### Method 2: Webhook (External Feeds)
This is how you connect external scrapers (like PhantomBuster, TexAu, or custom scripts).

**Endpoint**: `POST https://your-n8n-instance.com/webhook/linkedin-batch`

**JSON Body Format**:
```json
{
  "posts": [
    {
      "text": "Full text of the first LinkedIn post...",
      "author": "Jane Doe",
      "url": "https://linkedin.com/feed/update/..."
    },
    {
      "text": "Text of the second post...",
      "author": "John Smith"
    }
  ]
}
```

**Workflow Behavior**:
1.  Receives the batch.
2.  Splits it into individual items.
3.  The **AI Agent** runs for *each* post.
4.  Returns the JSON array of results (input data + generated output).

## Integration Ideas
- **PhantomBuster**: Use the "LinkedIn Activity Scraper" Phantom. Set it to send results to a webhook (this n8n URL).
- **Browser Extensions**: Use a generic "Data Scraper" that can POST to a webhook.

## Monitor Specific Profiles (New)

The `n8n-linkedin-monitor-workflow.json` allows you to automatically comment on the latest posts from a specific list of profiles.

### 2. Configuration
1.  **Open the Workflow**: Import `n8n-linkedin-monitor-workflow.json`.
2.  **Target Profiles**:
    -   Double-click the `Config: Target Profiles` node.
    -   Update the JavaScript array with the LinkedIn usernames (slugs) you want to monitor.
    ```javascript
    return [
      { json: { username: "jean-luc-le-roux" } },
      { json: { username: "billgates" } }
    ];
    ```
### 2. Configuration
1.  **Open the Workflow**: Import `n8n-linkedin-monitor-workflow.json`.
2.  **Target Profiles**:
    -   Double-click the `Config: Target Profiles` node.
    -   Update the JavaScript array with the LinkedIn usernames (slugs) you want to monitor.
    ```javascript
    return [
      { json: { username: "jean-luc-le-roux" } },
      { json: { username: "billgates" } }
    ];
    ```
3.  **Data Source (Apify)**:
    -   **Prerequisite**: You must have the `@apify/n8n-nodes-apify` installed in n8n (or be on n8n cloud).
    -   **Credentials**:
        -   Open the `1. Run Apify Scraper` node.
        -   Create a new Credential for `Apify API`.
        -   Enter your **Apify API Token** (from [Apify Settings](https://console.apify.com/account/integrations)).
    -   **Actor**: The workflow uses `apimaestro/linkedin-profile-posts` (Profile Posts Scraper for LinkedIn [No Cookies]).
    -   **Input**: It is configured to pass the `username` field.
    -   **Note**: This setup uses a 2-step process: Run Scraper -> Get Data.

### How it works
1.  Runs on a Daily Schedule (or Manual Trigger).
2.  Loops through each profile in your list.
3.  Fetches the *latest* post.
4.  Generates a comment using the AI Agent.
5.  Outputs the draft comment.
