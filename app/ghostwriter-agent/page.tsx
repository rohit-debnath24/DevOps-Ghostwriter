import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Shield, Zap, Terminal, Bot, GitPullRequest, Workflow, CheckCircle2 } from "lucide-react"
import Link from "next/link"

export default function GhostwriterAgentPage() {
  return (
    <div className="min-h-screen bg-[#0a0809] text-white selection:bg-[#69E300]/30 pt-20">
      
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-24 lg:pt-20 lg:pb-32">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 h-[500px] w-full max-w-7xl bg-[#69E300]/5 blur-[120px] rounded-full pointer-events-none" />
        
        <div className="container mx-auto px-6 sm:px-8 lg:px-12 xl:px-16 max-w-[1400px] relative z-10 text-center">
            <Badge variant="outline" className="mb-6 border-[#69E300]/20 bg-[#69E300]/5 text-[#69E300] py-1 px-4 text-sm">
                <Bot className="mr-2 h-3.5 w-3.5" />
                Autonomous Copilot v2.0
            </Badge>
            
            <h1 className="text-5xl font-display font-bold tracking-tight text-white md:text-7xl lg:text-8xl mb-6">
                Meet <span className="text-[#69E300]">Ghostwriter</span>
            </h1>
            
            <p className="text-xl text-white/60 leading-relaxed max-w-2xl mx-auto mb-10">
                The AI agent that lives in your pull requests. It audits code, simulates runtime execution, and orchestrates fixes before you even start your review.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Button size="lg" className="bg-[#69E300] text-black hover:bg-[#5bc200] font-bold h-14 px-8 text-lg w-full sm:w-auto">
                    Install on GitHub
                </Button>
                <Button size="lg" variant="outline" className="border-white/10 bg-white/5 hover:bg-white/10 text-white font-bold h-14 px-8 text-lg w-full sm:w-auto">
                    View Documentation
                </Button>
            </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="py-24 bg-white/[0.02] border-y border-white/5">
        <div className="container mx-auto px-6 sm:px-8 lg:px-12 xl:px-16 max-w-[1400px]">
             <div className="text-center mb-16">
                <h2 className="text-3xl md:text-4xl font-display font-bold text-white mb-4">Three Agents. One Mind.</h2>
                <p className="text-white/50 max-w-xl mx-auto">Ghostwriter isn't just a chatbot. It's a multi-agent system powered by Google Gemini 2.0 and Weave.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Agent 1 */}
                <div className="group relative p-8 rounded-2xl bg-white/5 border border-white/10 hover:border-[#69E300]/50 transition-all duration-300">
                    <div className="mb-6 h-12 w-12 rounded-lg bg-[#69E300]/10 flex items-center justify-center group-hover:bg-[#69E300] transition-colors duration-300">
                        <Shield className="h-6 w-6 text-[#69E300] group-hover:text-black" />
                    </div>
                    <h3 className="text-xl font-bold text-white mb-3">Security Auditor</h3>
                    <p className="text-white/60 leading-relaxed">
                        Scans diffs for secret leaks, injection risks, and dependency vulnerabilities using Chain-of-Thought reasoning.
                    </p>
                </div>

                 {/* Agent 2 */}
                 <div className="group relative p-8 rounded-2xl bg-white/5 border border-white/10 hover:border-[#69E300]/50 transition-all duration-300">
                    <div className="mb-6 h-12 w-12 rounded-lg bg-[#69E300]/10 flex items-center justify-center group-hover:bg-[#69E300] transition-colors duration-300">
                        <Terminal className="h-6 w-6 text-[#69E300] group-hover:text-black" />
                    </div>
                    <h3 className="text-xl font-bold text-white mb-3">Runtime Validator</h3>
                    <p className="text-white/60 leading-relaxed">
                        Actually runs your code. Generates test cases, executes them in a sandbox, and verifies logic before merge.
                    </p>
                </div>

                 {/* Agent 3 */}
                 <div className="group relative p-8 rounded-2xl bg-white/5 border border-white/10 hover:border-[#69E300]/50 transition-all duration-300">
                    <div className="mb-6 h-12 w-12 rounded-lg bg-[#69E300]/10 flex items-center justify-center group-hover:bg-[#69E300] transition-colors duration-300">
                        <Workflow className="h-6 w-6 text-[#69E300] group-hover:text-black" />
                    </div>
                    <h3 className="text-xl font-bold text-white mb-3">Orchestrator</h3>
                    <p className="text-white/60 leading-relaxed">
                        Manages the workflow. Decomposes complex PRs, assigns tasks to sub-agents, and synthesizes a final report.
                    </p>
                </div>
            </div>
        </div>
      </section>

      {/* Tech Spec / Integration */}
      <section className="py-24">
        <div className="container mx-auto px-6 sm:px-8 lg:px-12 xl:px-16 max-w-[1400px]">
             <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                <div className="space-y-8">
                    <h2 className="text-3xl md:text-5xl font-display font-bold text-white">
                        Seamless Integration with <span className="text-[#69E300]">GitHub Actions</span>
                    </h2>
                    <p className="text-lg text-white/60">
                        No complex webhooks to manage. Ghostwriter installs as a GitHub App or runs directly via GitHub Actions.
                    </p>
                    
                    <ul className="space-y-4">
                        {[
                            "Zero-configuration setup for public repos",
                            "Private sandbox for code execution",
                            "Respects .gitignore and security policies",
                            "comment-based interaction (e.g. '/ghostwriter fix')"
                        ].map((item, i) => (
                             <li key={i} className="flex items-center gap-3 text-white/80">
                                <CheckCircle2 className="h-5 w-5 text-[#69E300]" />
                                {item}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Mock Code Block */}
                <div className="rounded-xl border border-white/10 bg-black/50 overflow-hidden shadow-2xl">
                    <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5 bg-white/5">
                        <div className="h-3 w-3 rounded-full bg-red-500/50" />
                        <div className="h-3 w-3 rounded-full bg-yellow-500/50" />
                        <div className="h-3 w-3 rounded-full bg-green-500/50" />
                        <span className="ml-2 text-xs font-mono text-white/40">ghostwriter-action.yml</span>
                    </div>
                    <div className="p-6 overflow-x-auto">
                        <pre className="text-sm font-mono leading-relaxed">
                            <span className="text-purple-400">name:</span> <span className="text-green-400">DevOps Ghostwriter</span>{'\n'}
                            <span className="text-purple-400">on:</span>{'\n'}
                            <span className="text-blue-400">  pull_request:</span>{'\n'}
                            <span className="text-blue-400">    types:</span> [opened, synchronize]{'\n'}
                            {'\n'}
                            <span className="text-purple-400">jobs:</span>{'\n'}
                            <span className="text-blue-400">  audit:</span>{'\n'}
                            <span className="text-purple-400">    runs-on:</span> ubuntu-latest{'\n'}
                            <span className="text-purple-400">    steps:</span>{'\n'}
                            <span className="text-white">      - </span><span className="text-purple-400">name:</span> Run Ghostwriter Agent{'\n'}
                            <span className="text-white">        </span><span className="text-purple-400">uses:</span> ghostwriter/agent-action@v2{'\n'}
                            <span className="text-white">        </span><span className="text-purple-400">with:</span>{'\n'}
                            <span className="text-white">          </span><span className="text-blue-400">api-key:</span> {'${{ secrets.GHOSTWRITER_KEY }}'}{'\n'}
                            <span className="text-white">          </span><span className="text-blue-400">enable-runtime:</span> true
                        </pre>
                    </div>
                </div>
             </div>
        </div>
      </section>

    </div>
  )
}
