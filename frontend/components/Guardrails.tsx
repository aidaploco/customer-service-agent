import type { GuardrailResult } from '@/lib/types'
import { Shield, ShieldAlert } from 'lucide-react'

const GUARDRAILS = [
  { id: 'message_length_guardrail', label: 'Msg Length' },
  { id: 'off_topic_guardrail', label: 'Off Topic' },
  { id: 'prompt_injection_guardrail', label: 'Prompt Injection' },
]

interface Props {
  triggered: GuardrailResult[]
}

export default function Guardrails({ triggered }: Props) {
  const triggeredMap = new Map(triggered.map(g => [g.name, g]))

  return (
    <section>
      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Guardrails</h3>
      <div className="flex gap-2">
        {GUARDRAILS.map(gr => {
          const hit = triggeredMap.get(gr.id)
          const isTriggered = !!hit
          return (
            <div
              key={gr.id}
              className={`flex-1 rounded-xl p-3 border transition-all duration-200 ${
                isTriggered
                  ? 'bg-red-500/10 border-red-500'
                  : 'bg-slate-50 border-slate-200 dark:bg-slate-800/50 dark:border-slate-700'
              }`}
            >
              <div className="flex items-center gap-1.5 mb-1">
                {isTriggered
                  ? <ShieldAlert size={12} className="text-red-400 flex-shrink-0" />
                  : <Shield size={12} className="text-slate-400 dark:text-slate-600 flex-shrink-0" />
                }
                <span className={`text-xs font-medium leading-tight ${isTriggered ? 'text-red-300' : 'text-slate-500'}`}>
                  {gr.label}
                </span>
              </div>
              {isTriggered && hit?.reasoning && (
                <p className="text-[10px] text-red-400 leading-tight mt-1 line-clamp-2">
                  {hit.reasoning}
                </p>
              )}
            </div>
          )
        })}
      </div>
    </section>
  )
}
