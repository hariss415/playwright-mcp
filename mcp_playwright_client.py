import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPClient, MCPAgent
import time

# Save results to file
def save_results_to_file(result, filename="output.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(result)
    print(f" Result saved to {filename}")

# Retry Wrapper
async def run_with_retries(agent, prompt, retries=3):
    for attempt in range(retries):
        try:
            print(f" Attempt {attempt + 1}...")
            result = await agent.run(prompt)
            return result
        except Exception as e:
            print(f" Error: {e}")
            if attempt < retries - 1:
                print(" Retrying...\n")
                time.sleep(2)
            else:
                return " Agent failed after multiple attempts."

# Main function
async def main():
    load_dotenv()

    print(" Connecting to MCP Server...")
    config = {
        "mcpServers": {
            "playwright": {
                "command": "npx",
                "args": ["@playwright/mcp@latest"],
                "env": {
                    "DISPLAY": ":1"
                }
            }
        }
    }

    client = MCPClient.from_dict(config)
    print(" MCPClient connected successfully!")

    # Create agent with smarter LLM and retries
    agent = MCPAgent(
        llm=ChatOpenAI(model="gpt-4o"), 
        client=client, 
        max_steps=20,
        verbose=False
    )

    # Ask user for short natural instruction
    print("\n What do you want to do?")
    user_query = input(" Your task: ").strip()

    # Smart meta prompt to make agent self-reliant
    smart_prompt = f"""
You are a browser automation agent.

User instruction: "{user_query}"

Your job is to understand the task without needing detailed explanation. Break it into steps and use the browser tools accordingly.

Always:
- Use `browser_navigate` to go to websites.
- Type in inputs using `browser_element_type` with the correct name or CSS.
- Click buttons using `browser_element_click`.
- Use `browser_extract` to get meaningful info (like href or text).
- If something fails, try a second time differently.

Do not ask the user for clarification. Behave like a real assistant that completes tasks based on best judgment.

Return the final answer in a clean format — no tool logs, no screenshots.
    """

    # Run with retries
    result = await run_with_retries(agent, smart_prompt)
    print("\n Final Output:\n", result)
    save_results_to_file(result)

if __name__ == "__main__":
    asyncio.run(main())
