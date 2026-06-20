import json
from backend.mongo_repository import save_scenario

from backend.agent_repository import (
    get_agent,
    get_prompt,
    get_template,
    get_guardrail
)

from backend.ollama_client import (
    OllamaClient
)

def build_prompt(
    agent_id,
    user_input
):

    agent = get_agent(
        agent_id
    )

    prompt_doc = get_prompt(
        agent["prompt_template_id"]
    )

    template = get_template(
        "default"
    )

    prompt = prompt_doc[
        "template"
    ]

    prompt = prompt.replace(
        "{{schema}}",
        json.dumps(
            template["schema"],
            indent=2
        )
    )

    prompt = prompt.replace(
        "{{user_input}}",
        user_input
    )

    return (
        agent,
        prompt
    )

def execute_agent(
    agent_id,
    user_input
):

    agent, prompt = build_prompt(
        agent_id,
        user_input
    )

    client = OllamaClient()

    generated = client.generate(
        model=agent["model"],
        prompt=prompt
    )

    save_scenario(
        generated
    )
    print("SAVED TO MONGO")
    return generated