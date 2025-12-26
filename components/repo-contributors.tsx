"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"

const CONTRIBUTORS = [
    {
        id: 1,
        name: "Sarah Chen",
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah",
        commits: 247,
        prs: 42,
        role: "Lead Developer",
    },
    {
        id: 2,
        name: "Mike Johnson",
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Mike",
        commits: 189,
        prs: 31,
        role: "Senior Dev",
    },
    {
        id: 3,
        name: "Emily Rodriguez",
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Emily",
        commits: 156,
        prs: 28,
        role: "Developer",
    },
    {
        id: 4,
        name: "Alex Kim",
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Alex",
        commits: 134,
        prs: 24,
        role: "Developer",
    },
    {
        id: 5,
        name: "Jordan Taylor",
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Jordan",
        commits: 98,
        prs: 18,
        role: "Junior Dev",
    },
    {
        id: 6,
        name: "Chris Anderson",
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Chris",
        commits: 87,
        prs: 15,
        role: "Junior Dev",
    },
    {
        id: 7,
        name: "Lisa Wang",
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Lisa",
        commits: 76,
        prs: 13,
        role: "Developer",
    },
    {
        id: 8,
        name: "David Park",
        avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=David",
        commits: 64,
        prs: 11,
        role: "Junior Dev",
    },
]

export function RepoContributors() {
    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold tracking-tight text-white">Top Contributors</h2>
                <Badge variant="outline" className="border-[#69E300]/20 bg-[#69E300]/10 text-[#69E300] text-[10px] font-bold uppercase tracking-widest">
                    {CONTRIBUTORS.length} Active
                </Badge>
            </div>

            <div className="rounded-xl border border-white/5 bg-[#171717] p-6">
                <div className="h-[240px] overflow-y-auto space-y-4 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent hover:scrollbar-thumb-white/20">
                    {CONTRIBUTORS.map((contributor, index) => (
                        <div
                            key={contributor.id}
                            className="flex items-center justify-between gap-4 rounded-lg border border-white/5 bg-white/[0.02] p-4 transition-all hover:border-white/10 hover:bg-white/[0.04]"
                        >
                            <div className="flex items-center gap-3">
                                <div className="relative">
                                    <Avatar className="h-10 w-10 border-2 border-white/10">
                                        <AvatarImage src={contributor.avatar} alt={contributor.name} />
                                        <AvatarFallback className="bg-[#69E300]/20 text-[#69E300] text-xs font-bold">
                                            {contributor.name
                                                .split(" ")
                                                .map((n) => n[0])
                                                .join("")}
                                        </AvatarFallback>
                                    </Avatar>
                                    {index === 0 && (
                                        <div className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-[#69E300] text-[10px] font-black text-black">
                                            1
                                        </div>
                                    )}
                                </div>
                                <div className="space-y-0.5">
                                    <div className="flex items-center gap-2">
                                        <p className="text-sm font-semibold text-white">{contributor.name}</p>
                                    </div>
                                    <p className="text-[10px] font-medium uppercase tracking-wider text-white/40">
                                        {contributor.role}
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-center gap-6">
                                <div className="text-right">
                                    <div className="text-lg font-black text-white">{contributor.commits}</div>
                                    <div className="text-[9px] font-bold uppercase tracking-widest text-white/30">Commits</div>
                                </div>
                                <div className="text-right">
                                    <div className="text-lg font-black text-[#69E300]">{contributor.prs}</div>
                                    <div className="text-[9px] font-bold uppercase tracking-widest text-white/30">PRs</div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="mt-6 grid grid-cols-2 gap-4 border-t border-white/5 pt-6">
                    <div className="space-y-1 text-center">
                        <div className="text-[10px] font-bold uppercase tracking-widest text-white/20">Total Commits</div>
                        <div className="text-2xl font-black text-white">
                            {CONTRIBUTORS.reduce((sum, c) => sum + c.commits, 0)}
                        </div>
                    </div>
                    <div className="space-y-1 text-center">
                        <div className="text-[10px] font-bold uppercase tracking-widest text-white/20">Total PRs</div>
                        <div className="text-2xl font-black text-[#69E300]">
                            {CONTRIBUTORS.reduce((sum, c) => sum + c.prs, 0)}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
