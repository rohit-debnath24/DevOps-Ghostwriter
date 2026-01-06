require('dotenv').config({ path: '../.env.local' });
const express = require('express');
const { Octokit } = require('octokit');
const axios = require('axios');
const cors = require('cors');
const nodemailer = require('nodemailer');

const app = express();
const PORT = process.env.NODE_PORT || 3001;
const PYTHON_AGENT_URL = process.env.PYTHON_AGENT_URL || 'http://localhost:8000/analyze';

// In-memory store for audits (Mock Database)
const AUDITS = {};

app.use(express.json());
app.use(cors({
  origin: '*', // Allow all origins for now to prevent CORS issues
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Configure Email Transporter
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS
  }
});

// API to fetch audits (for Frontend)
app.get('/api/audits', (req, res) => {
  // Return as list sorted by new
  const list = Object.values(AUDITS).sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  console.log(`[API] Serving ${list.length} audits to frontend.`);
  res.json(list);
});

// API to fetch global stats (for Frontend "Global Telemetry")
app.get('/api/stats', (req, res) => {
  const audits = Object.values(AUDITS);
  const totalAudits = audits.length;

  // Calculate stats based on real data
  const vulnerabilities = audits.reduce((acc, audit) => {
    // Heuristic: if status is not success or if comment mentions 'vulnerability'
    // For now, let's assume 'error' or specific keywords imply issues. 
    // This is a basic mock logic on top of mock data structure.
    if (audit.result?.status === 'error' || (audit.result?.comment && audit.result.comment.toLowerCase().includes('vulnerability'))) {
      return acc + 1;
    }
    return acc;
  }, 0);

  // Calculate Success Rate
  const successCount = audits.filter(a => a.result?.status === 'success' || a.result?.status === 'approved').length;
  const successRate = totalAudits > 0 ? ((successCount / totalAudits) * 100).toFixed(1) : "100.0";

  // Calculate Avg Review Time (Mocked for now as we don't track start/end time of agents precisely in this store yet)
  // We can randomize slightly to make it look alive if static, or keep static.
  const avgTime = "42s";

  res.json({
    audits_reviewed: totalAudits,
    vulnerabilities_patched: vulnerabilities,
    avg_review_time: avgTime,
    agent_success_rate: successRate
  });
});

// Initialize Octokit
const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN || undefined,
});

app.post('/api/webhook/github', async (req, res) => {
  try {
    const event = req.headers['x-github-event'];
    const payload = req.body;

    // We only care about pull_request events
    if (event !== 'pull_request') {
      return res.status(200).send('Ignored event type');
    }

    const { action, pull_request, repository, email, github_token } = payload;

    if (!pull_request || !repository) {
      return res.status(400).send('Invalid payload');
    }

    // Initialize Octokit for this request, preferring user token
    // This allows accessing private repos if the user is authorized
    const requestOctokit = new Octokit({
      auth: github_token || process.env.GITHUB_TOKEN || undefined
    });

    // Only process opened or synchronized (updated) PRs
    if (action !== 'opened' && action !== 'synchronize') {
      return res.status(200).send('Ignored action');
    }

    const owner = repository.owner.login;
    const repo = repository.name;
    const pull_number = pull_request.number;

    console.log(`Processing PR #${pull_number} for ${owner}/${repo}`);

    // Call the shared analysis logic
    const result = await runAnalysis(owner, repo, pull_number, payload.diff, email, requestOctokit, pull_request);

    res.status(200).json(result);

  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).send('Server Error');
  }
});

// New Endpoint: List Open PRs
app.get('/api/github/repos/:owner/:repo/pulls', async (req, res) => {
  const { owner, repo } = req.params;
  try {
    const { data } = await octokit.request('GET /repos/{owner}/{repo}/pulls', {
      owner,
      repo,
      state: 'open'
    });
    res.json(data);
  } catch (error) {
    console.error('Error fetching PRs:', error);
    res.status(500).json({ error: error.message });
  }
});

// New Endpoint: Manually Analyze PR
app.post('/api/analyze-pr', async (req, res) => {
  const { owner, repo, pull_number } = req.body;

  try {
    // Fetch PR details to get title/body if needed, or pass them if provided
    // For now we'll fetch them inside runAnalysis if we don't have them, 
    // but runAnalysis expects pull_request object for title/body.
    // Let's first fetch the PR object from GitHub.

    const { data: pull_request } = await octokit.request('GET /repos/{owner}/{repo}/pulls/{pull_number}', {
      owner,
      repo,
      pull_number
    });

    const result = await runAnalysis(owner, repo, pull_number, null, null, octokit, pull_request);
    res.json(result);

  } catch (error) {
    console.error('Manual analysis error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Shared Analysis Logic
async function runAnalysis(owner, repo, pull_number, providedDiff, email, requestOctokit, pull_request) {
  // Step 2: Fetch or Mock Diff
  let diffText = "";
  if (providedDiff) {
    diffText = providedDiff;
    console.log(`Using provided diff from local script (length: ${diffText.length})`);
  } else {
    try {
      const { data } = await requestOctokit.request('GET /repos/{owner}/{repo}/pulls/{pull_number}', {
        owner,
        repo,
        pull_number,
        mediaType: {
          format: "diff"
        }
      });
      diffText = data;
    } catch (octokitError) {
      console.error('Error fetching diff from GitHub:', octokitError.message);
      throw new Error(`Failed to fetch diff: ${octokitError.message}`);
    }
  }

  // Step 3: Forward to Python Service
  const analysisPayload = {
    repo_id: `${owner}/${repo}`,
    pr_id: pull_number,
    diff_text: diffText,
    title: pull_request.title,
    description: pull_request.body
  };

  let emailLog = "Skipped (Conditions not met)";

  try {
    const agentResponse = await axios.post(PYTHON_AGENT_URL, analysisPayload);
    console.log('Successfully forwarded to Python Agent Engine');

    const result = agentResponse.data;

    // Store result in memory
    const auditKey = `${owner}/${repo}/${pull_number}`;
    AUDITS[auditKey] = {
      id: auditKey,
      repo: `${owner}/${repo}`,
      pr_id: pull_number,
      timestamp: new Date().toISOString(),
      result: result,
      runtime_snapshot: result.runtime_snapshot,
      security_snapshot: result.security_snapshot,
      diff: diffText
    };
    console.log(`Stored audit for ${auditKey}`);

    // Step 4: Send Email Report
    if (email && process.env.EMAIL_USER) {
      console.log(`Sending email report to: ${email}`);
      const mailOptions = {
        from: process.env.EMAIL_USER,
        to: email,
        subject: `[DevOps Ghostwriter] Audit Report for PR #${pull_number} - ${repo}`,
        html: `
                <h2>Audit Report for Pull Request #${pull_number}</h2>
                <p><strong>Repository:</strong> ${owner}/${repo}</p>
                <p><strong>Confidence Score:</strong> ${Math.round(result.confidence_score * 100)}%</p>
                
                <h3>Verdict</h3>
                <p><strong>Status:</strong> ${result.status.toUpperCase()}</p>
                
                <h3>Analysis Summary</h3>
                <pre style="background: #f4f4f4; padding: 10px; border-radius: 5px;">${result.comment}</pre>
                
                <p><a href="http://localhost:3000/audit/${encodeURIComponent(auditKey)}">View Full Dashboard</a></p>
            `
      };

      try {
        await transporter.sendMail(mailOptions);
        emailLog = `Sent successfully`;
      } catch (mailError) {
        emailLog = `Failed: ${mailError.message}`;
      }
    }

    return {
      message: 'Processed',
      email_status: emailLog,
      audit: AUDITS[auditKey]
    };

  } catch (agentError) {
    console.error('Failed to contact Python Agent Engine:', agentError.message);

    // Store a partial audit with error status
    const auditKey = `${owner}/${repo}/${pull_number}`;
    AUDITS[auditKey] = {
      id: auditKey,
      repo: `${owner}/${repo}`,
      pr_id: pull_number,
      timestamp: new Date().toISOString(),
      result: {
        status: 'error',
        comment: `Failed to analyze PR: Python Agent Engine is not available.`,
        confidence_score: 0,
        error: agentError.message
      },
      runtime_snapshot: null,
      security_snapshot: null,
      diff: diffText
    };
    return {
      message: 'Analysis Failed',
      error: agentError.message
    };
  }
}

app.listen(PORT, () => {
  console.log(`Node.js Backend (Fetcher) running on port ${PORT}`);
  console.log("Environment Check:");
  console.log(`- EMAIL_USER: ${process.env.EMAIL_USER ? 'SET (' + process.env.EMAIL_USER + ')' : 'NOT SET'}`);
  console.log(`- EMAIL_PASS: ${process.env.EMAIL_PASS ? 'SET' : 'NOT SET'}`);
  console.log(`- PYTHON_AGENT_URL: ${PYTHON_AGENT_URL}`);
});
