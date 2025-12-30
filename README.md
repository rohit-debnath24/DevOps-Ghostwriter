# 🤖⚙️ DevOps-Ghostwriter – Autonomous DevOps AI Agent

![Preview Image](screenshot.png)

An intelligent multi-agent AI system that acts as your virtual DevOps engineer. Monitor GitHub Pull Requests, perform deep security audits, execute code in sandboxes, and auto-generate documentation — all while maintaining full observability through Weights & Biases Weave. Sit back, relax ☕, and let AI handle your DevOps workflows!

## 🌟 Features

- 🔍 **Automated PR Audits** – AI-powered analysis of every pull request with detailed insights
- 🛡️ **Security Scanning** – Detect hardcoded secrets, SQL injections, and vulnerable dependencies
- ⚡ **Runtime Validation** – Execute code in secure sandboxes to verify logic and catch bugs
- 📝 **Auto Documentation** – Generate comprehensive docs from code changes automatically
- 📊 **Real-Time Observability** – Full tracing and monitoring via W&B Weave integration
- 🏥 **Repository Health Scores** – Track code quality and security trends over time
- 🤝 **Multi-Agent Collaboration** – Parallel agent execution using Google Agent Development Kit
- 🔔 **GitHub Webhook Integration** – Seamless PR event monitoring and automated responses
- 🎯 **Smart Analysis** – Powered by Gemini 1.5 Pro for reasoning and Gemini 1.5 Flash for testing
- 💬 **Live Agent Terminal** – Watch AI agents think and collaborate in real-time

## 🛠️ Technologies Used

### Frontend
- **Next.js** – React framework with server-side rendering
- **TypeScript** – Type-safe development
- **TailwindCSS** – Modern utility-first styling
- **Framer Motion** – Smooth animations and transitions
- **Radix UI** – Accessible component primitives
- **Lucide React** – Beautiful icon library

### Backend
- **Node.js / Express.js** – RESTful API server
- **FastAPI** – High-performance Python backend for AI agents
- **MongoDB** – Audit history and status tracking
- **Socket.io** – Real-time bidirectional communication

### AI & Agent Engine
- **Google Agent Development Kit (ADK)** – Multi-agent orchestration framework
- **Gemini 1.5 Pro** – Advanced reasoning and security analysis
- **Gemini 1.5 Flash** – Fast testing and linting operations
- **Weights & Biases Weave** – AI observability and tracing

### DevOps & Tools
- **GitHub Webhooks** – Automated PR event handling
- **Docker** – Containerized deployment (optional)
- **Python 3.10+** – Agent engine runtime

## ⚙️ Installation

### Prerequisites
- Node.js 18+ and npm/pnpm
- Python 3.10+
- MongoDB instance (local or cloud)
- GitHub account with webhook access
- Google AI API key (Gemini)
- Weights & Biases account

### 1. Clone the repository
```bash
git clone https://github.com/BikramMondal5/DevOps-Ghostwriter.git
cd DevOps-Ghostwriter
```

### 2. Install Frontend Dependencies
```bash
npm install
# or
pnpm install
```

### 3. Install Backend Dependencies
```bash
cd backend
npm install
cd ..
```

### 4. Install Python Agent Engine Dependencies
```bash
cd agent-engine
pip install -r requirements.txt
cd ..
```

### 5. Configure Environment Variables
Create a `.env` file in the root directory (see `EXAMPLE_ENV` for reference):
```env
# GitHub
GITHUB_TOKEN=your_github_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Google AI
GOOGLE_API_KEY=your_gemini_api_key

# MongoDB
MONGODB_URI=your_mongodb_connection_string

# Weights & Biases
WANDB_API_KEY=your_wandb_api_key

# JWT Secret
JWT_SECRET=your_jwt_secret
```

### 6. Run the Development Servers

**Terminal 1 - Frontend (Next.js):**
```bash
npm run dev
```

**Terminal 2 - Backend (Node.js):**
```bash
cd backend
node server.js
```

**Terminal 3 - Agent Engine (FastAPI):**
```bash
cd agent-engine
python main.py
```

### 7. Access the Application
Open your browser and navigate to `http://localhost:3000`

## 📸 Screenshots

> **Note:** Add your application screenshots to showcase the dashboard, audit console, and real-time agent activity!

## 🚀 How to Use

1. **🔐 Sign Up / Log In** – Create an account or authenticate with your credentials
2. **🔗 Connect GitHub Repository** – Link your repositories for automated monitoring
3. **⚙️ Configure Webhooks** – Set up GitHub webhooks to trigger PR audits automatically
4. **📊 View Dashboard** – Monitor repository health scores and security trends
5. **🔍 Audit Pull Requests** – Watch AI agents analyze PRs in real-time
6. **🛡️ Review Security Findings** – Check detected vulnerabilities and security issues
7. **📈 Track Observability** – Dive deep into agent reasoning traces via W&B Weave
8. **📝 Export Documentation** – Download auto-generated docs for your code changes

### Quick Testing
```bash
# Test individual agents
cd Agents
python test_individual_agents.py

# Test caching functionality
python test_cache.py

# Run agent test suite
.\test_agents.ps1
```

## 🤝 Contribution

**Got ideas? Found a bug? 🐞**

We welcome contributions from the community! Here's how you can help:

- 🌟 Star this repository to show your support
- 🐛 Report bugs by opening an issue
- 💡 Suggest new features or improvements
- 🔧 Submit pull requests with enhancements
- 📖 Improve documentation
- 🧪 Add test coverage

### Contribution Guidelines
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

<<<<<<< HEAD
---

<div align="center">

**Built with ❤️ by [BikramMondal5](https://github.com/BikramMondal5)**

⭐ Star us on GitHub — it motivates us to keep improving!

</div>
=======
>>>>>>> e75182aa37d721f3788dd47242f827589a920e53
