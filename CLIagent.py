from conversation import Conversation
from ollama_client import OllamaClient
from ollama_setup import ensure_ollama_ready


def main() -> None:
    if not ensure_ollama_ready():
        print("\n❌ Ollama setup failed. Please fix the issues above and try again.")
        print("   See RUN_CHECKLIST.md for manual setup instructions.")
        return

    print("\n🚀 Starting CLI Agent...\n")
    conversation = Conversation()
    agent = OllamaClient(conversation)
    agent.run()


if __name__ == "__main__":
    main()
