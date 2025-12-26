import { Navigation } from "@/components/navigation"
import { AuditHeader } from "@/components/audit-header"
import { AuditVerdict } from "@/components/audit-verdict"
import { AuditConsole } from "@/components/audit-console"
import { SecurityFindings } from "@/components/security-findings"
import { AuditDetails } from "@/components/audit-details"
import { AuditObservability } from "@/components/audit-observability"

export default async function AuditCenterPage({ params }: { params: { prId: string } }) {
  const { prId } = await params

  return (
    <main className="min-h-screen bg-[#0A0809] pb-20 selection:bg-[#69E300]/30">
      <Navigation />

      <section className="container mx-auto px-6 sm:px-8 lg:px-12 xl:px-16 pt-32 pb-20 max-w-[1400px] space-y-12">
        {/* Header Section */}
        <section>
          <AuditHeader prId={prId} />
        </section>

        {/* Verdict Banner */}
        <section>
          <AuditVerdict />
        </section>

        {/* Core Demo Section: Live Agent Execution */}
        <section className="space-y-6">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-[#69E300] animate-pulse" />
            <h3 className="text-sm font-bold text-[#F8F7F8] uppercase tracking-[0.2em]">Real-time Agent Reasoning</h3>
          </div>
          <AuditConsole />
        </section>

        {/* Audit Sections */}
        <section className="grid grid-cols-1 gap-12">
          <SecurityFindings />
          <AuditDetails />
        </section>

        {/* Observability Section */}
        <section>
          <AuditObservability />
        </section>
      </section>

      {/* Footer Pattern */}
      <footer className="mt-20 border-t border-white/5 py-12 text-center">
        <div className="container mx-auto px-4">
        </div>
      </footer>
    </main>
  )
}
