"use client"

import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Cell } from "recharts"

interface SecurityTrendsProps {
  audits: any[]
}

export function SecurityTrends({ audits }: SecurityTrendsProps) {
  // Group audits by day and calculate metrics
  const calculateTrends = () => {
    const today = new Date()
    const last7Days = []

    for (let i = 6; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(date.getDate() - i)
      const dayName = date.toLocaleDateString('en-US', { weekday: 'short' })

      // Filter audits for this day
      const dayAudits = audits.filter(audit => {
        if (!audit.timestamp) return false
        const auditDate = new Date(audit.timestamp)
        return auditDate.toDateString() === date.toDateString()
      })

      // Calculate vulnerabilities (failed or error audits)
      const vulnerabilities = dayAudits.filter(a =>
        a.result?.status === 'error' || a.result?.status === 'failed'
      ).length

      // Calculate quality score (based on confidence and success rate)
      const successfulAudits = dayAudits.filter(a => a.result?.status === 'success').length
      const avgConfidence = dayAudits.length > 0
        ? dayAudits.reduce((acc, a) => acc + ((a.result?.confidence_score || 0.5) * 100), 0) / dayAudits.length
        : 85
      const quality = dayAudits.length > 0
        ? Math.round((successfulAudits / dayAudits.length) * avgConfidence)
        : 85

      last7Days.push({
        name: dayName,
        vulnerabilities,
        quality: Math.min(quality, 100)
      })
    }

    return last7Days
  }

  const data = calculateTrends()

  // Calculate summary stats
  const totalVulnerabilities = data.reduce((acc, d) => acc + d.vulnerabilities, 0)
  const avgQuality = Math.round(data.reduce((acc, d) => acc + d.quality, 0) / data.length)
  const vulnerabilityTrend = data[0].vulnerabilities > data[6].vulnerabilities ? '-' : '+'
  const vulnerabilityChange = data[0].vulnerabilities !== 0
    ? Math.round(((data[6].vulnerabilities - data[0].vulnerabilities) / data[0].vulnerabilities) * 100)
    : 0

  // Calculate runtime errors (estimate from failed audits)
  const runtimeErrors = audits.filter(a =>
    a.result?.comment?.toLowerCase().includes('runtime') ||
    a.result?.comment?.toLowerCase().includes('error')
  ).length

  // Calculate docs generated (estimate from audits mentioning documentation)
  const docsGenerated = audits.filter(a =>
    a.result?.comment?.toLowerCase().includes('doc') ||
    a.result?.comment?.toLowerCase().includes('documentation')
  ).length

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold tracking-tight text-white">Security & Quality Trends</h2>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-[#69E300]" />
            <span className="text-[10px] font-bold uppercase tracking-widest text-white/40">Quality Score</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-white/20" />
            <span className="text-[10px] font-bold uppercase tracking-widest text-white/40">Vulnerabilities</span>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-white/5 bg-[#171717] p-6">
        <div className="h-[240px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <XAxis dataKey="name" stroke="#71717A" fontSize={10} tickLine={false} axisLine={false} dy={10} />
              <YAxis
                stroke="#71717A"
                fontSize={10}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => `${value}`}
              />
              <Tooltip
                cursor={{ fill: "rgba(255, 255, 255, 0.05)" }}
                contentStyle={{
                  backgroundColor: "#171717",
                  border: "1px solid rgba(255, 255, 255, 0.1)",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
              <Bar dataKey="quality" radius={[4, 4, 0, 0]}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill="#69E300" fillOpacity={0.8} />
                ))}
              </Bar>
              <Bar dataKey="vulnerabilities" fill="rgba(255, 255, 255, 0.1)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-6 grid grid-cols-3 gap-4 border-t border-white/5 pt-6 text-center">
          <div className="space-y-1">
            <div className="text-[10px] font-bold uppercase tracking-widest text-white/20">Vulnerabilities</div>
            <div className="text-xl font-black text-white">
              {vulnerabilityTrend}{Math.abs(vulnerabilityChange)}%
            </div>
          </div>
          <div className="space-y-1">
            <div className="text-[10px] font-bold uppercase tracking-widest text-white/20">Runtime Errors</div>
            <div className="text-xl font-black text-white">{runtimeErrors}</div>
          </div>
          <div className="space-y-1">
            <div className="text-[10px] font-bold uppercase tracking-widest text-white/20">Docs Gen</div>
            <div className="text-xl font-black text-white">+{docsGenerated}</div>
          </div>
        </div>
      </div>
    </div>
  )
}
