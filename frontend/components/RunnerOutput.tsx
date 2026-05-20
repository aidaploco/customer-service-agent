import type { AgentEvent } from '@/lib/types'
import { ArrowRight, Wrench, FileOutput } from 'lucide-react'

interface Props {
  events: AgentEvent[]
}

function EventIcon({ type }: { type: AgentEvent['type'] }) {
  if (type === 'handoff') return <ArrowRight size={11} className="text-violet-400 flex-shrink-0 mt-0.5" />
  if (type === 'tool_call') return <Wrench size={11} className="text-amber-400 flex-shrink-0 mt-0.5" />
  return <FileOutput size={11} className="text-sky-400 flex-shrink-0 mt-0.5" />
}

const TYPE_COLOURS: Record<AgentEvent['type'], string> = {
  handoff: 'text-violet-400',
  tool_call: 'text-amber-400',
  tool_output: 'text-sky-400',
}

export default function RunnerOutput({ events }: Props) {
  return (
    <section>
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Runner Output</h3>
      <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-3 min-h-20">
        {events.length === 0 ? (
          <p className="text-xs text-slate-600 italic">No events this turn.</p>
        ) : (
          <div className="space-y-2">
            {events.map((event, i) => (
              <div key={i} className="flex items-start gap-2">
                <EventIcon type={event.type} />
                <div className="min-w-0 flex-1">
                  <span className={`text-[10px] font-semibold uppercase mr-1.5 ${TYPE_COLOURS[event.type]}`}>
                    {event.type.replace('_', ' ')}
                  </span>
                  <span className="text-xs text-slate-400 font-mono break-all">
                    {event.type === 'handoff'
                      ? `${event.agent} → ${event.content}`
                      : event.content}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
