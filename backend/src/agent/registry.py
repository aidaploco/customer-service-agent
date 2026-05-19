from agents import Agent

from agent.billing import create_billing_agent
from agent.general import create_general_agent
from agent.support import create_support_agent
from agent.supervisor import create_supervisor_agent


def build_agent_registry() -> dict[str, Agent[None]]:
    """
    Create all agents, wire handoffs, and return a name→agent mapping.

    Graph:
        Supervisor → Billing, Support, General   (forward routing)
        Billing    → Supervisor                  (back-handoff for off-topic)
        Support    → Supervisor                  (back-handoff for off-topic)
        General    → Supervisor                  (back-handoff for off-topic)
    """
    billing = create_billing_agent()
    support = create_support_agent()
    general = create_general_agent()
    supervisor = create_supervisor_agent(handoffs=[billing, support, general])

    # Back-handoffs added after supervisor exists to avoid circular construction.
    billing.handoffs.append(supervisor)
    support.handoffs.append(supervisor)
    general.handoffs.append(supervisor)

    return {
        supervisor.name: supervisor,
        billing.name: billing,
        support.name: support,
        general.name: general,
    }
