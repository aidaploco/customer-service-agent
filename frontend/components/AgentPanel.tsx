'use client'

import { Sun, Moon } from 'lucide-react'
import type { AgentInfo, AgentEvent, GuardrailResult } from '@/lib/types'
import AgentsList from './AgentsList'
import Guardrails from './Guardrails'
import RunnerOutput from './RunnerOutput'
import ConversationContext from './ConversationContext'

interface Props {
  agents: AgentInfo[]
  activeAgent: AgentInfo | null
  guardrails: GuardrailResult[]
  events: AgentEvent[]
  sessionId: string
  dark: boolean
  onToggleTheme: () => void
}

export default function AgentPanel({ agents, activeAgent, guardrails, events, sessionId, dark, onToggleTheme }: Props) {
  return (
    <div className="flex flex-col min-h-full">
      <div className="px-4 py-3 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
        <h2 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Agent View</h2>
        <button
          onClick={onToggleTheme}
          className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          aria-label="Toggle theme"
        >
          {dark ? <Sun size={15} /> : <Moon size={15} />}
        </button>
      </div>
      <div className="p-4 space-y-5 flex-1">
        <AgentsList agents={agents} activeAgent={activeAgent} events={events} />
        <Guardrails triggered={guardrails} />
        <RunnerOutput events={events} />
        <ConversationContext sessionId={sessionId} activeAgent={activeAgent} />
      </div>
    </div>
  )
}
