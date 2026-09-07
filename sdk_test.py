import asyncio
import sys
from dotenv import load_dotenv
from claude_code_sdk import query, ClaudeCodeOptions
from claude_code_sdk.types import ResultMessage

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

load_dotenv()

# This command to run the file on claude code: run python sdk_test.py


async def main():
    # prompt = "Add a docstring to the run_billing_cycle function in app/billing/cycle_runner.py" # This is costumized according to what I need the DSK to do.
    prompt = "Describe the contents of app/billing/cycle_runner.py"
    print(f"Prompt: {prompt}\n")
    async for message in query(
        prompt=prompt,
        options=ClaudeCodeOptions(
            allowed_tools=[
                "Read" # add "Edit" to create a doctring 
            ],  # This changes according to the project and according to the specific task you need to perform.
            cwd=r"C:\dev\flowbill",  # This changes according to the project
        ),
    ):
        if isinstance(message, ResultMessage):
            with open("sdk_output.txt", "w", encoding="utf-8") as f:
                f.write(message.result or "")
            print("Done — see sdk_output.txt")


asyncio.run(main())
