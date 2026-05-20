import type { AgentInfo } from '@/lib/types'

interface Props {
  sessionId: string
  activeAgent: AgentInfo | null
}

export default function ConversationContext({ sessionId, activeAgent }: Props) {
  return (
    <section>
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Session</h3>
      <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-3 space-y-2">
        <Row label="Session ID">
          <span className="font-mono text-[10px] text-slate-400 truncate" title={sessionId}>
            {sessionId.slice(0, 8)}…{sessionId.slice(-4)}
          </span>
        </Row>
        <Row label="Active agent">
          <span className={activeAgent ? 'text-indigo-300' : 'text-slate-600'}>
            {activeAgent?.name ?? '—'}
          </span>
        </Row>
        {activeAgent && (
          <>
            <Row label="Tools">
              <span className="text-slate-400">{activeAgent.tools.join(', ') || '—'}</span>
            </Row>
            <Row label="Handoffs to">
              <span className="text-slate-400">{activeAgent.handoffs.join(', ') || '—'}</span>
            </Row>
          </>
        )}
      </div>
    </section>
  )
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex justify-between items-baseline gap-4">
      <span className="text-xs text-slate-500 flex-shrink-0">{label}</span>
      <span className="text-xs text-right">{children}</span>
    </div>
  )
}
