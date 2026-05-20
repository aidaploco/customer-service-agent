import type { AgentEvent, AgentInfo } from '@/lib/types'
import { Bot } from 'lucide-react'

interface Props {
  agents: AgentInfo[]
  activeAgent: AgentInfo | null
  events: AgentEvent[]
}

export default function AgentsList({ agents, activeAgent, events }: Props) {
  const calledTools = new Set(
    events
      .filter(e => e.type === 'tool_call')
      .map(e => `${e.agent}::${e.content.split('(')[0]}`)
  )
  return (
    <section>
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Agents</h3>
      <div className="grid grid-cols-2 gap-2">
        {agents.map(agent => {
          const isActive = activeAgent?.name === agent.name
          return (
            <div
              key={agent.name}
              className={`rounded-xl p-3 border transition-all duration-200 ${
                isActive
                  ? 'bg-indigo-500/10 border-indigo-500'
                  : 'bg-slate-800/50 border-slate-700'
              }`}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <Bot size={13} className={isActive ? 'text-indigo-400' : 'text-slate-500'} />
                <span className={`text-sm font-medium ${isActive ? 'text-indigo-300' : 'text-slate-300'}`}>
                  {agent.name}
                </span>
                {isActive && (
                  <span className="ml-auto relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75" />
                    <span className="relative inline-flex h-2 w-2 rounded-full bg-indigo-500" />
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 leading-snug line-clamp-2 mb-2">
                {agent.description}
              </p>
              <div className="flex flex-wrap gap-1">
                {agent.tools.map(t => {
                  const active = calledTools.has(`${agent.name}::${t}`)
                  return (
                    <span
                      key={t}
                      className={`text-[10px] rounded px-1.5 py-0.5 transition-colors duration-200 ${
                        active
                          ? 'bg-indigo-500/20 text-indigo-300 ring-1 ring-indigo-500/50'
                          : 'bg-slate-700 text-slate-400'
                      }`}
                    >
                      {t}
                    </span>
                  )
                })}
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
