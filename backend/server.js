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
app.use(cors());

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

    const { action, pull_request, repository, email } = payload;

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
    // If diff is passed in payload (from local script), use it
    if (payload.diff) {
      diffText = payload.diff;
      console.log(`Using provided diff from local script (length: ${diffText.length})`);
    } else {
      // Fallback to fetch from GitHub (existing logic)
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
      } catch (octokitError) {
        console.error('Error fetching diff from GitHub:', octokitError.message);
        // Don't fail entire request, try to proceed if possible or return error
        // Here we return error as diff is critical
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
        result: result, // { status: 'success', comment: '...' }
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
                <p><strong>Repository:</strong> ${repository.full_name}</p>
                <p><strong>Confidence Score:</strong> ${Math.round(result.confidence_score * 100)}%</p>
                
                <h3>Verdict</h3>
                <p><strong>Status:</strong> ${result.status.toUpperCase()}</p>
                
                <h3>Analysis Summary</h3>
                <pre style="background: #f4f4f4; padding: 10px; border-radius: 5px;">${result.comment}</pre>
                
                <p><a href="http://localhost:3000/audit/${encodeURIComponent(auditKey)}">View Full Dashboard</a></p>
            `
        };

        try {
          const info = await transporter.sendMail(mailOptions);
          emailLog = `Sent successfully: ${info.response}`;
          console.log('Email sent: ' + info.response);
        } catch (mailError) {
          emailLog = `Failed: ${mailError.message}`;
          console.error('Error sending email:', mailError);
        }
      } else {
        if (!email) emailLog = "Skipped: No email provided in payload.";
        if (!process.env.EMAIL_USER) emailLog = "Skipped: EMAIL_USER env var not set on server.";
        console.log(emailLog);
      }

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
          comment: `Failed to analyze PR: Python Agent Engine is not available. Please ensure the service is running on ${PYTHON_AGENT_URL}`,
          confidence_score: 0,
          error: agentError.message
        },
        runtime_snapshot: null,
        security_snapshot: null,
        diff: diffText
      };
      console.log(`Stored error audit for ${auditKey}`);
      emailLog = "Skipped: Analysis failed.";
    }

    res.status(200).json({
      message: 'Processed',
      email_status: emailLog || "Unknown"
    });

  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).send('Server Error');
  }
});

app.listen(PORT, () => {
  console.log(`Node.js Backend (Fetcher) running on port ${PORT}`);
  console.log("Environment Check:");
  console.log(`- EMAIL_USER: ${process.env.EMAIL_USER ? 'SET (' + process.env.EMAIL_USER + ')' : 'NOT SET'}`);
  console.log(`- EMAIL_PASS: ${process.env.EMAIL_PASS ? 'SET' : 'NOT SET'}`);
  console.log(`- PYTHON_AGENT_URL: ${PYTHON_AGENT_URL}`);
});
