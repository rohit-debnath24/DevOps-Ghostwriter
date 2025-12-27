import { Navigation } from "@/components/navigation"
import { AuditHeader } from "@/components/audit-header"
import { AuditVerdict } from "@/components/audit-verdict"
import { AuditConsole } from "@/components/audit-console"
import { SecurityFindings } from "@/components/security-findings"
import { AuditDetails } from "@/components/audit-details"
import { AuditObservability } from "@/components/audit-observability"

async function getAuditData(prId: string) {
  try {
    // Fetch from Node.js backend
    const res = await fetch('http://localhost:3001/api/audits', { cache: 'no-store' })
    if (!res.ok) {
      throw new Error('Failed to fetch audits')
    }
    const audits: any[] = await res.json()

    // If prId is 'wqdidu', return the most recent audit for demo purposes as requested
    if (prId === 'wqdidu') {
      return audits.length > 0 ? audits[0] : null
    }

    // Otherwise find by ID (which is owner/repo/number)
    // The ID in URL encoded owner%2Frepo%2Fnumber
    const decodedId = decodeURIComponent(prId)
    return audits.find((a: any) => a.id === decodedId || a.pr_id.toString() === prId) || null
  } catch (error) {
    console.error("Error fetching audit:", error)
    return null
  }
}

export default async function AuditCenterPage({ params }: { params: { prId: string } }) {
  const { prId } = await params
  const auditData = await getAuditData(prId)

  if (!auditData) {
    return (
      <main className="min-h-screen bg-[#0A0809] flex flex-col items-center justify-center text-white">
        <h1 className="text-4xl font-bold mb-4">Audit Not Found</h1>
        <p className="text-white/50">Could not find audit logs for ID: {prId}</p>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-[#0A0809] pb-20 selection:bg-[#69E300]/30 text-white font-sans">
      <Navigation />

      <section className="container mx-auto px-6 sm:px-8 lg:px-12 xl:px-16 pt-32 pb-20 max-w-[1400px] space-y-12">
        {/* Header Section */}
        <section>
          {/* @ts-ignore */}
          <AuditHeader prId={prId} data={auditData} />
        </section>

        {/* Verdict Banner */}
        <section>
          {/* @ts-ignore */}
          <AuditVerdict data={auditData} />
        </section>

        {/* Core Demo Section: Live Agent Execution */}
        <section className="space-y-6">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-[#69E300] animate-pulse" />
            <h3 className="text-sm font-bold text-[#F8F7F8] uppercase tracking-[0.2em]">Real-time Agent Reasoning</h3>
          </div>
          {/* @ts-ignore */}
          <AuditConsole data={auditData} />
        </section>

        {/* Audit Sections */}
        <section className="grid grid-cols-1 gap-12">
          {/* @ts-ignore */}
          <SecurityFindings data={auditData} />
          {/* @ts-ignore */}
          <AuditDetails data={auditData} />
        </section>

        {/* Observability Section */}
        <section>
          {/* @ts-ignore */}
          <AuditObservability data={auditData} />
        </section>
      </section>

      {/* Footer Pattern */}
      <footer className="mt-20 border-t border-white/5 py-12 text-center">
        <div className="container mx-auto px-4">
          <p className="text-white/20 text-sm">DevOps Ghostwriter • Verified by W&B</p>
        </div>
      </footer>
    </main>
  )
}
