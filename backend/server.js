require('dotenv').config({ path: '../.env.local' });
const express = require('express');
const { Octokit } = require('octokit');
const axios = require('axios');
const cors = require('cors');

const app = express();
const PORT = process.env.NODE_PORT || 3001;
const PYTHON_AGENT_URL = process.env.PYTHON_AGENT_URL || 'http://localhost:8000/analyze';

// In-memory store for audits (Mock Database)
const AUDITS = {};

app.use(express.json());
app.use(cors());

// API to fetch audits (for Frontend)
app.get('/api/audits', (req, res) => {
  // Return as list sorted by new
  const list = Object.values(AUDITS).sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  res.json(list);
});

// Initialize Octokit
const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN,
});

app.post('/api/webhook/github', async (req, res) => {
  try {
    const event = req.headers['x-github-event'];
    const payload = req.body;

    // We only care about pull_request events
    if (event !== 'pull_request') {
      return res.status(200).send('Ignored event type');
    }

    const { action, pull_request, repository } = payload;

    if (!pull_request || !repository) {
      return res.status(400).send('Invalid payload');
    }

    // Only process opened or synchronized (updated) PRs
    if (action !== 'opened' && action !== 'synchronize') {
      return res.status(200).send('Ignored action');
    }

    const owner = repository.owner.login;
    const repo = repository.name;
    const pull_number = pull_request.number;

    console.log(`Processing PR #${pull_number} for ${owner}/${repo}`);

    // Step 2: Fetch or Mock Diff
    let diffText = "";

    console.log(`Debug Check: Owner='${owner}' Repo='${repo}'`);

    if (owner === 'test_owner' && repo === 'test_repo') {
      console.log("Using Mock Diff for Test Repo");
      diffText = `diff --git a/server.js b/server.js
index 83db48f..5a3c20 100644
--- a/server.js
+++ b/server.js
@@ -10,6 +10,7 @@ const app = express();
 // Vulnerability: Hardcoded secret (Mock)
 const API_KEY = "12345-ABCDE";
 
+// Logic Error: Infinite loop (Mock)
 function calculate() {
-  return 1 + 1;
+  while(true) {}
 }`;
    } else {
      try {
        const { data } = await octokit.request('GET /repos/{owner}/{repo}/pulls/{pull_number}', {
          owner,
          repo,
          pull_number,
          mediaType: {
            format: "diff"
          }
        });
        diffText = data;
        console.log(`Fetched diff (length: ${diffText.length})`);
      } catch (octokitError) {
        console.error('Error fetching diff from GitHub:', octokitError.message);
        return res.status(500).send('Failed to fetch diff');
      }
    }

    // Step 3: Forward to Python Service
    const analysisPayload = {
      repo_id: repository.full_name,
      pr_id: pull_number,
      diff_text: diffText,
      title: pull_request.title,
      description: pull_request.body
    };

    try {
      const agentResponse = await axios.post(PYTHON_AGENT_URL, analysisPayload);
      console.log('Successfully forwarded to Python Agent Engine');

      // Store result in memory
      const auditKey = `${owner}/${repo}/${pull_number}`;
      AUDITS[auditKey] = {
        id: auditKey,
        repo: `${owner}/${repo}`,
        pr_id: pull_number,
        timestamp: new Date().toISOString(),
        result: agentResponse.data, // { status: 'success', comment: '...' }
        diff: diffText // Store the fetched diff for display
      };
      console.log(`Stored audit for ${auditKey}`);

    } catch (agentError) {
      console.error('Failed to contact Python Agent Engine:', agentError.message);
    }

    res.status(200).send('Processed');

  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).send('Server Error');
  }
});


app.listen(PORT, () => {
  console.log(`Node.js Backend (Fetcher) running on port ${PORT}`);
});
