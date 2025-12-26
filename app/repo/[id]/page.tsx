import { Navigation } from "@/components/navigation"
import { RepoHeader } from "@/components/repo-header"
import { RepoHealthOverview } from "@/components/repo-health-overview"
import { PRAuditTimeline } from "@/components/pr-audit-timeline"
import { SecurityTrends } from "@/components/security-trends"
import { AgentActivitySummary } from "@/components/agent-activity-summary"
import { RepoContributors } from "@/components/repo-contributors"

export default async function RepoDetailsPage({ params }: { params: { id: string } }) {
  const { id } = await params

  return (
    <main className="min-h-screen bg-[#0A0809] pb-20">
      <Navigation />

      <div className="container mx-auto px-6 sm:px-8 lg:px-12 xl:px-16 pt-32 space-y-12 max-w-[1400px]">
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
            <section className="animate-in fade-in slide-in-from-right-4 duration-700 delay-500">
              <RepoContributors />
            </section>
          </aside>
        </div>
      </div>
    </main>
  )
}
