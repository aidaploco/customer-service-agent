from agents import Agent
from agents.extensions.handoff_filters import remove_all_tools

from agent.billing import create_billing_agent
from agent.support import create_support_agent
from agent.supervisor import create_supervisor_agent

# Applied to every handoff via RunConfig. Without it the specialist sees the
# supervisor's `transfer_to_*` call in its history and, instead of calling its
# own tools, writes a plausible reply that claims an action it never took
# (e.g. "ticket created: BL-XXXXX"). Both RunConfig sites import this so the
# eval harness exercises the same behaviour as the API.
HANDOFF_INPUT_FILTER = remove_all_tools


def build_agent_registry() -> dict[str, Agent[None]]:
    """
    Create all agents, wire handoffs, and return a name→agent mapping.

    Graph:
        Supervisor → Billing, Support   (forward routing)
        Billing    → Supervisor         (back-handoff for off-topic)
        Support    → Supervisor         (back-handoff for off-topic)
    """
    billing = create_billing_agent()
    support = create_support_agent()
    supervisor = create_supervisor_agent(handoffs=[billing, support])

    # Back-handoffs added after supervisor exists to avoid circular construction.
    billing.handoffs.append(supervisor)
    support.handoffs.append(supervisor)

    return {
        supervisor.name: supervisor,
        support.name: support,
        billing.name: billing,
    }
