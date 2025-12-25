import { RepositoryGrid } from "@/components/repository-grid"
import { GlobalStats } from "@/components/global-stats"
import { ActivityFeed } from "@/components/activity-feed"
import { Shield, Activity, Terminal, ChevronRight, Search, Bell, Settings, Github, Send } from "lucide-react"
import LaserFlow from "@/components/laser-flow"
import { Button } from "@/components/ui/button"

export default async function DashboardPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params

  return (
    <div className="min-h-screen bg-black text-white selection:bg-[#69E300]/30 font-sans">
      <div className="relative h-[750px] w-full overflow-hidden">
        {/* Background Visualization */}
        <div className="absolute inset-0 z-0">
          <LaserFlow
            color="#69E300"
            fogIntensity={1.0}
            wispDensity={2.0}
            flowSpeed={0.5}
            verticalSizing={4.0}
            horizontalSizing={1.2}
            className="scale-125 origin-top"
          />
        </div>

        {/* Dark Vignette Overlay */}
        <div className="absolute inset-0 z-10 bg-gradient-to-b from-black/60 via-transparent to-black" />

        {/* Hero Overlay Content */}
        <div className="absolute inset-0 z-20">
          <div className="container mx-auto px-6 h-full flex flex-col justify-center pt-6">
            <h1 className="text-7xl font-black tracking-tighter mb-6 max-w-3xl font-display leading-[0.9] animate-in fade-in slide-in-from-bottom-6 duration-1000 delay-100">
              Agentic <span className="text-[#69E300]">Observability</span>
            </h1>
            <p className="text-white/50 text-xl max-w-2xl leading-relaxed font-medium animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-200">
              Monitoring real-time heuristic processing nodes for <span className="text-white font-mono">{id}</span>.
              Visualizing the concurrent reasoning streams across your infrastructure.
            </p>
          </div>
        </div>
      </div>

      <main className="max-w-[75%] mx-auto px-6 -mt-32 relative z-30 space-y-12 mb-32">
        {/* Glass Dashboard Navigation Bar */}
        <div className="flex items-center justify-between bg-white/5 border border-white/10 rounded-2xl px-8 py-4 backdrop-blur-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)]">
          <div className="flex items-center gap-4 flex-1">
            <div className="relative flex-1 max-w-3xl">
              <textarea
                placeholder="Paste GitHub PR URL here..."
                className="bg-black/40 border border-white/5 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-[#69E300]/50 transition-all w-full placeholder:text-white/20 resize-none h-12 leading-relaxed"
                rows={1}
              />
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="h-12 w-12 text-white/40 hover:text-[#69E300] transition-colors"
              title="Connect GitHub"
            >
              <Github className="h-5 w-5" />
            </Button>
            <div className="h-10 w-px bg-white/10" />
            <Button
              variant="ghost"
              size="icon"
              className="h-12 w-12 text-white/40 hover:text-[#69E300] transition-colors"
              title="Notifications"
            >
              <Bell className="h-5 w-5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-12 w-12 text-white/40 hover:text-[#69E300] transition-colors"
              title="Settings"
            >
              <Settings className="h-5 w-5" />
            </Button>
            <Button
              className="bg-[#69E300] text-black font-bold text-sm px-6 h-12 rounded-lg hover:bg-[#5bc500] transition-all ml-2 flex items-center gap-2"
              title="Submit PR for Analysis"
            >
              <Send className="h-4 w-4" />
              Submit
            </Button>
          </div>
        </div>        {/* Global Performance Section */}
        <div className="space-y-6">
          <div className="flex items-center gap-2 text-[#69E300]">
            <Activity className="h-4 w-4" />
            <span className="text-xs font-bold uppercase tracking-[0.2em] font-mono">Global Telemetry</span>
          </div>
          <GlobalStats />
        </div>

        {/* Repository Health Section */}
        <div className="space-y-8 pt-4">
          <div className="flex items-end justify-between border-b border-white/5 pb-6">
            <div className="space-y-2">
              <h2 className="text-3xl font-bold tracking-tight font-display">Active Repositories</h2>
              <p className="text-white/40 text-sm">Ghostwriter nodes currently analyzing codebase health.</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" className="text-xs border-white/10 bg-white/5 h-9">
                Filtered: All
              </Button>
              <Button variant="outline" className="text-xs border-white/10 bg-white/5 h-9">
                Export Audit
              </Button>
            </div>
          </div>
          <RepositoryGrid />
        </div>

        {/* Activity & Security Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center gap-2 text-[#69E300] mb-2">
              <Terminal className="h-4 w-4" />
              <span className="text-xs font-bold uppercase tracking-[0.2em] font-mono">Real-time Reasoning</span>
            </div>
            <ActivityFeed />
          </div>

          <div className="space-y-10">
            <div className="rounded-3xl border border-[#69E300]/20 bg-gradient-to-br from-[#69E300]/10 to-transparent p-10 relative overflow-hidden group">
              <div className="absolute -top-12 -right-12 p-4 opacity-5 group-hover:opacity-10 transition-all duration-700">
                <Shield className="h-48 w-48 text-[#69E300] rotate-12" />
              </div>
              <div className="relative z-10 space-y-8">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#69E300] text-black shadow-[0_0_30px_rgba(105,227,0,0.3)]">
                  <Shield className="h-6 w-6" />
                </div>
                <div className="space-y-3">
                  <h3 className="text-2xl font-bold text-white tracking-tight font-display">Neural Isolation</h3>
                  <p className="text-white/50 leading-relaxed">
                    Zero-trust sandbox active. Every reasoning step is verified before execution.
                  </p>
                </div>
                <Button className="w-full bg-white text-black hover:bg-white/90 font-bold py-6 rounded-xl shadow-xl transition-all active:scale-[0.98]">
                  Security Audit Log
                </Button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
