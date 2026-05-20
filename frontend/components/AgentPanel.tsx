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
}

export default function AgentPanel({ agents, activeAgent, guardrails, events, sessionId }: Props) {
  return (
    <div className="flex flex-col min-h-full">
      <div className="px-4 py-3 border-b border-slate-800">
        <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Agent View</h2>
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
