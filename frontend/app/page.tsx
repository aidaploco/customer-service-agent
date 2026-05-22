'use client'

import { useState, useEffect } from 'react'
import type { AgentInfo, AgentEvent, GuardrailResult, Message } from '@/lib/types'
import Chat from '@/components/Chat'
import AgentPanel from '@/components/AgentPanel'

export default function Home() {
  const [sessionId] = useState(() => crypto.randomUUID())
  const [messages, setMessages] = useState<Message[]>([{
    id: crypto.randomUUID(),
    role: 'assistant',
    content: "Hi! I'm Zara, your customer service assistant for Brightloop. How can I help you today?",
  }])
  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [activeAgent, setActiveAgent] = useState<AgentInfo | null>(null)
  const [guardrails, setGuardrails] = useState<GuardrailResult[]>([])
  const [events, setEvents] = useState<AgentEvent[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetch('/api/agents')
      .then(r => r.json())
      .then(setAgents)
      .catch(console.error)
  }, [])

  async function sendMessage(content: string) {
    setMessages(prev => [...prev, { id: crypto.randomUUID(), role: 'user', content }])
    setLoading(true)
    setEvents([])
    setGuardrails([])

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: content }),
      })
      const data = await res.json()

      if (!res.ok) {
        setMessages(prev => [...prev, {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: data.error ?? 'Something went wrong.',
        }])
        return
      }

      setActiveAgent(data.agent)
      setGuardrails(data.guardrails)
      setEvents(data.events)
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.message,
        agent: data.agent.name,
      }])
    } catch {
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Unable to reach the backend.',
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <div className="w-3/5 border-r border-slate-800 overflow-y-auto">
        <AgentPanel
          agents={agents}
          activeAgent={activeAgent}
          guardrails={guardrails}
          events={events}
          sessionId={sessionId}
        />
      </div>
      <div className="w-2/5 flex flex-col">
        <Chat messages={messages} loading={loading} onSend={sendMessage} />
      </div>
    </div>
  )
}
