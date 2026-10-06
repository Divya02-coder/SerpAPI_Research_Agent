from .agent import research_agent


def print_banner():

    print("\n")
    print("=" * 65)
    print("        ASK & VERIFY — AI RESEARCH AGENT")
    print("=" * 65)
    print()
    print("Ask a question and the agent will research it using")
    print("Gemini + live SerpApi search.")
    print()
    print("Commands:")
    print("  /help       Show commands")
    print("  /reset      Reset conversation")
    print("  /challenge  Re-verify the previous answer")
    print("  /sources    Show collected evidence")
    print("  /exit       Exit")
    print()
    print("=" * 65)


def print_help():

    print("""
Examples:

  What is SerpApi used for?

  What are the latest developments in India's semiconductor
  industry?

  Compare India's semiconductor ecosystem with Taiwan's.

  What is the current market size of AI?

  Should India prioritize semiconductor manufacturing or design?

Commands:

  /reset
  /challenge
  /sources
  /help
  /exit
""")


def main():

    print_banner()

    while True:

        try:

            user_input = input("\nYou: ").strip()

        except KeyboardInterrupt:

            print("\nGoodbye!")
            break

        if not user_input:
            continue

        # --------------------------------------------------
        # Commands
        # --------------------------------------------------

        if user_input.lower() == "/exit":

            print("Goodbye!")
            break

        if user_input.lower() == "/help":

            print_help()
            continue

        if user_input.lower() == "/reset":

            research_agent.reset()

            print("Conversation and evidence reset.")
            continue

        if user_input.lower() == "/sources":

            summary = research_agent.evidence.summary()

            print("\nEvidence Ledger")
            print("-" * 50)

            print(
                f"Sources: {summary['total_sources']}"
            )

            print(
                f"Unique domains: {summary['unique_domains']}"
            )

            print()

            print(
                research_agent.evidence.formatted_sources()
                or "No sources collected yet."
            )

            continue

        if user_input.lower() == "/challenge":

            print("\nRe-verifying previous answer...\n")

            answer = research_agent.challenge()

            print("\nAgent:")
            print(answer)

            continue

        # --------------------------------------------------
        # Normal research question
        # --------------------------------------------------

        print("\nResearching...\n")

        try:

            answer = research_agent.ask(user_input)

            print("Agent:")
            print(answer)

        except Exception as e:

            print("\nERROR:")
            print(e)


if __name__ == "__main__":
    main()