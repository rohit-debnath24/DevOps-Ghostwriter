"use client"

import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Cell } from "recharts"

const DATA = [
  { name: "Mon", vulnerabilities: 12, quality: 88 },
  { name: "Tue", vulnerabilities: 8, quality: 92 },
  { name: "Wed", vulnerabilities: 15, quality: 85 },
  { name: "Thu", vulnerabilities: 5, quality: 95 },
  { name: "Fri", vulnerabilities: 3, quality: 98 },
  { name: "Sat", vulnerabilities: 2, quality: 99 },
  { name: "Sun", vulnerabilities: 4, quality: 97 },
]

export function SecurityTrends() {
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
            <BarChart data={DATA}>
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
                {DATA.map((entry, index) => (
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
            <div className="text-xl font-black text-white">-42%</div>
          </div>
          <div className="space-y-1">
            <div className="text-[10px] font-bold uppercase tracking-widest text-white/20">Runtime Errors</div>
            <div className="text-xl font-black text-white">-18%</div>
          </div>
          <div className="space-y-1">
            <div className="text-[10px] font-bold uppercase tracking-widest text-white/20">Docs Gen</div>
            <div className="text-xl font-black text-white">+124</div>
          </div>
        </div>
      </div>
    </div>
  )
}
