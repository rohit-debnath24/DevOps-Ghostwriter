import { Navigation } from "@/components/navigation"
import { RepoHeader } from "@/components/repo-header"
import { RepoHealthOverview } from "@/components/repo-health-overview"
import { PRAuditTimeline } from "@/components/pr-audit-timeline"
import { SecurityTrends } from "@/components/security-trends"
import { AgentActivitySummary } from "@/components/agent-activity-summary"

export default async function RepoDetailsPage({ params }: { params: { id: string } }) {
  const { id } = await params

  return (
    <main className="min-h-screen bg-[#0A0809] pb-20">
      <Navigation />

      <div className="container mx-auto px-4 pt-32 space-y-12">
        {/* Header Section */}
        <section className="animate-in fade-in slide-in-from-top-4 duration-700">
          <RepoHeader id={id} />
        </section>

        {/* Health Overview Grid */}
        <section className="animate-in fade-in slide-in-from-top-4 duration-700 delay-100">
          <RepoHealthOverview />
        </section>

        {/* Main Content: Timeline & Sidebars */}
        <div className="grid grid-cols-1 gap-12 lg:grid-cols-12">
          {/* Timeline & Trends */}
          <div className="space-y-12 lg:col-span-8">
            <section className="animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200">
              <PRAuditTimeline />
            </section>
            <section className="animate-in fade-in slide-in-from-bottom-4 duration-700 delay-300">
              <SecurityTrends />
            </section>
          </div>

          {/* Activity & Observability */}
          <aside className="space-y-12 lg:col-span-4">
            <section className="animate-in fade-in slide-in-from-right-4 duration-700 delay-400">
              <AgentActivitySummary />
            </section>
          </aside>
        </div>
      </div>

      {/* Minimal Footer Footer */}
      <footer className="mt-20 border-t border-white/5 py-12 text-center">
        <div className="container mx-auto px-4">
          <div className="flex flex-col items-center justify-center gap-4">
            <div className="flex items-center gap-2">
              <div className="h-6 w-6 rounded-md bg-[#69E300]/10 flex items-center justify-center border border-[#69E300]/20">
                <div className="h-3 w-3 rounded-full bg-[#69E300]" />
              </div>
              <span className="text-sm font-bold text-white tracking-tight">Ghostwriter Intelligence Platform</span>
            </div>
            <p className="text-xs text-white/20 uppercase tracking-[0.2em] font-medium">
              Autonomous DevOps • Powered by Google ADK • Observed by W&B
            </p>
          </div>
        </div>
      </footer>
    </main>
  )
}
