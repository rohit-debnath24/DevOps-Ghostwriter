import { Shield, Zap, Terminal, Database, Lock, Search, ArrowRight } from "lucide-react"

const features = [
  {
    title: "Autonomous Auditing",
    description:
      "Agents continuously scan your repositories for security vulnerabilities and architectural debt without human intervention.",
    icon: Shield,
    accent: "bg-[#69E300]/10 text-[#69E300]",
  },
  {
    title: "Instant Infrastructure",
    description:
      "Provision complex cloud environments across AWS, GCP, and Azure using natural language or existing architectural diagrams.",
    icon: Zap,
    accent: "bg-[#69E300]/10 text-[#69E300]",
  },
  {
    title: "Ghost Terminal",
    description:
      "An interactive, AI-powered shell that predicts your next command and automates repetitive DevOps workflows.",
    icon: Terminal,
    accent: "bg-[#69E300]/10 text-[#69E300]",
  },
  {
    title: "Stateful Intelligence",
    description:
      "Persistent memory across agent sessions ensures long-term projects maintain context and follow established patterns.",
    icon: Database,
    accent: "bg-[#69E300]/10 text-[#69E300]",
  },
  {
    title: "Zero-Trust Sandboxing",
    description:
      "Every agent operation occurs in a restricted, ephemeral container that self-destructs after task completion.",
    icon: Lock,
    accent: "bg-[#69E300]/10 text-[#69E300]",
  },
  {
    title: "Predictive Observability",
    description:
      "Analyze system logs and metrics to identify potential failures before they impact your production users.",
    icon: Search,
    accent: "bg-[#69E300]/10 text-[#69E300]",
  },
]

export function FeaturesSection() {
  return (
    <div className="space-y-12">
      <div className="text-center space-y-4 max-w-2xl mx-auto">
        <h2 className="text-4xl font-bold tracking-tight sm:text-5xl">Scale your DevOps with AI</h2>
        <p className="text-white/40 text-lg">
          The most advanced agentic platform designed specifically for high-growth engineering teams.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature, index) => (
          <div
            key={index}
            className="group relative rounded-2xl border border-white/5 bg-[#171717] p-8 transition-all hover:border-[#69E300]/20 hover:bg-[#1a1a1a]"
          >
            <div className={`mb-6 inline-flex h-12 w-12 items-center justify-center rounded-xl ${feature.accent}`}>
              <feature.icon className="h-6 w-6" />
            </div>
            <h3 className="mb-3 text-xl font-bold text-white">{feature.title}</h3>
            <p className="text-sm leading-relaxed text-white/40">{feature.description}</p>
            <div className="mt-6 flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-[#69E300] opacity-0 transition-opacity group-hover:opacity-100">
              Explore Feature <ArrowRight className="h-3 w-3" />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
