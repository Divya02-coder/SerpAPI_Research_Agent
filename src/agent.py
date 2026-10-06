import json
import os
import time

from dotenv import load_dotenv
from google import genai

from .tools import TOOL_SCHEMAS, TOOL_FUNCTIONS
from .prompts import SYSTEM_PROMPT
from .evidence import EvidenceLedger


load_dotenv()

GOOGLEAI_API_KEY = os.getenv("GOOGLEAI_API_KEY")

if not GOOGLEAI_API_KEY:
    raise ValueError(
        "GOOGLEAI_API_KEY is missing from your .env file."
    )


client = genai.Client(
    api_key=GOOGLEAI_API_KEY
)

MODEL = "gemini-3.8-flash"

MAX_RESEARCH_TURNS = 6


class ResearchAgent:

    def __init__(self):

        self.previous_interaction_id = None
        self.evidence = EvidenceLedger()

        self.search_count = 0
        self.last_answer = ""

    def reset(self):

        self.previous_interaction_id = None
        self.evidence.reset()

        self.search_count = 0
        self.last_answer = ""

    def ask(self, user_query):

        # New research question gets a fresh evidence ledger.
        # Conversation memory is preserved through Gemini's
        # previous_interaction_id.

        self.evidence.reset()
        self.search_count = 0

        current_input = user_query
        interaction_id = self.previous_interaction_id

        for turn in range(MAX_RESEARCH_TURNS):

            request = {
                "model": MODEL,
                "input": current_input,
                "tools": TOOL_SCHEMAS,
                "system_instruction": SYSTEM_PROMPT,
                "generation_config": {
                    "thinking_level": "medium"
                }
            }

            # Only send previous_interaction_id after we have one.
            if interaction_id:
                request["previous_interaction_id"] = interaction_id

            
            # --------------------------------------------------
# Gemini request with automatic retry
# --------------------------------------------------
max_retries = 3

for attempt in range(max_retries):

    try:
        interaction = client.interactions.create(**request)
        break

    except Exception as e:

        error_text = str(e)

        # Retry temporary server/capacity errors
        if (
            "503" in error_text
            or "service_unavailable" in error_text
            or "high demand" in error_text
        ):

            if attempt == max_retries - 1:
                raise

            wait_time = 2 ** attempt

            print(
                f"Gemini is temporarily busy. "
                f"Retrying in {wait_time}s..."
            )

            time.sleep(wait_time)

        else:
            raise
            interaction_id = interaction.id

            steps = getattr(interaction, "steps", [])

            function_calls = [
                step
                for step in steps
                if getattr(step, "type", None) == "function_call"
            ]

            # --------------------------------------------------
            # No tool call = final answer
            # --------------------------------------------------

            if not function_calls:

                answer = getattr(
                    interaction,
                    "output_text",
                    "I could not generate an answer."
                )

                self.previous_interaction_id = interaction_id
                self.last_answer = answer

                return answer

            # --------------------------------------------------
            # Execute tool calls
            # --------------------------------------------------

            function_results = []

            for call in function_calls:

                tool_name = getattr(call, "name", None)

                if tool_name not in TOOL_FUNCTIONS:

                    result = {
                        "error": (
                            f"Unknown tool requested: "
                            f"{tool_name}"
                        )
                    }

                else:

                    arguments = getattr(
                        call,
                        "arguments",
                        {}
                    )

                    # Some SDK versions may return arguments
                    # as JSON text rather than a dictionary.
                    if isinstance(arguments, str):

                        try:
                            arguments = json.loads(arguments)

                        except json.JSONDecodeError:

                            arguments = {}

                    try:

                        result = TOOL_FUNCTIONS[
                            tool_name
                        ](**arguments)

                    except Exception as e:

                        result = {
                            "error": str(e)
                        }

                # Add evidence IDs to search results
                if isinstance(result, dict):

                    if "sources" in result:

                        result = self.evidence.process_result(
                            result
                        )

                self.search_count += 1

                function_results.append({
                    "type": "function_result",
                    "name": tool_name,
                    "call_id": call.id,
                    "result": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                result,
                                ensure_ascii=False
                            )
                        }
                    ]
                })

            # --------------------------------------------------
            # Send tool results back to Gemini
            # --------------------------------------------------

            current_input = function_results

        return (
            "I could not complete the research within the "
            "allowed research depth. Please try a more focused "
            "question."
        )

    def challenge(self):

        if not self.last_answer:

            return (
                "There is no previous answer to challenge. "
                "Ask a research question first."
            )

        challenge_prompt = f"""
Re-verify your previous answer independently.

Previous answer:

{self.last_answer}

Do NOT simply repeat the previous answer.

Perform fresh searches.

Look specifically for:

1. unsupported claims
2. outdated information
3. contradictory evidence
4. stronger primary sources
5. important information that was missed

Then provide a corrected or confirmed answer.

Clearly mention whether the original answer was:

- CONFIRMED
- PARTIALLY CONFIRMED
- NEEDS CORRECTION

Use source IDs for factual claims.
"""

        return self.ask(challenge_prompt)


research_agent = ResearchAgent()


def run_agent(user_query):

    return research_agent.ask(user_query)