from typing_extensions import Annotated
import os
import autogen
import subprocess
import json

config_list = [
    {"model": "gpt-4o", "api_key": "sk_key"}
    ]
default_path = "source-code/"
llm_config = {
    "temperature": 0,
    "config_list": config_list,
}

def termination_msg(x):
    return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

# Defination
engineer = autogen.AssistantAgent(
    name="Engineer",
    llm_config=llm_config,
    system_message="""
    I'm Engineer. I'm expert in programming. I'm executing code tasks required by Admin. After modify the code, I need Tester to test it
    """,
)

tester = autogen.AssistantAgent(
    name="Tester",
    llm_config=llm_config,
    is_termination_msg=termination_msg,
    system_message="""
    I am Tester, a QA Engineer specializing in testing. I handle code testing tasks as requested by Admin. 
    If all tests pass successfully, Reply `TERMINATE` in the end when everything is done.
    """,
)

user_proxy = autogen.UserProxyAgent(
    name="Admin",
    human_input_mode="NEVER",
    default_auto_reply="Reply `TERMINATE` if the task is done.",
    code_execution_config=False,
    is_termination_msg=termination_msg,
)

@user_proxy.register_for_execution()
@engineer.register_for_llm(description="List files in choosen directory.")
def list_dir(directory: Annotated[str, "Directory to check."]):
    files = os.listdir(default_path + directory)
    return 0, files


@user_proxy.register_for_execution()
@engineer.register_for_llm(description="Check the contents of a chosen file.")
def see_file(filename: Annotated[str, "Name and path of file to check."]):
    with open(default_path + filename, "r") as file:
        lines = file.readlines()
    formatted_lines = [f"{i+1}:{line}" for i, line in enumerate(lines)]
    file_contents = "".join(formatted_lines)

    return 0, file_contents


@user_proxy.register_for_execution()
@engineer.register_for_llm(description="Replace old piece of code with new one. Proper indentation is important.")
def modify_code(
    filename: Annotated[str, "Name and path of file to change."],
    start_line: Annotated[int, "Start line number to replace with new code."],
    end_line: Annotated[int, "End line number to replace with new code."],
    new_code: Annotated[str, "New piece of code to replace old code with. Remember about providing indents."],
):
    with open(default_path + filename, "r+") as file:
        file_contents = file.readlines()
        file_contents[start_line - 1 : end_line] = [new_code + "\n"]
        file.seek(0)
        file.truncate()
        file.write("".join(file_contents))
    return 0, "Code modified"

@user_proxy.register_for_execution()
@engineer.register_for_llm(description="Create a new file with code.")
def create_file_with_code(
    filename: Annotated[str, "Name and path of file to create."], code: Annotated[str, "Code to write in the file."]
):
    with open(default_path + filename, "w") as file:
        file.write(code)
    return 0, "File created successfully"

@user_proxy.register_for_execution()
@tester.register_for_llm(description="Run the test file")
def run_test():
    try:
        result = subprocess.run("cd ./source-code && npm run test", shell=True, capture_output=True, text=True)
        print(result.stderr)
        return 0, result.stderr 
    except Exception as e:
        return 1, e

# Group chat
groupchat = autogen.GroupChat(
    agents=[user_proxy, engineer, tester],
    messages=[],
    max_round=100,
    speaker_selection_method="round_robin",
    enable_clear_history=True,
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

chat_result = user_proxy.initiate_chat(
    manager,
    message="""
Write unit tests for all .js files in the application. Focus exclusively on .js files.
If a tests folder doesn’t exist, create it in the root directory.
Place all unit tests in the tests folder, ensuring each .js file has a corresponding test file with comprehensive test cases.
Once the tests are written, run them to validate the code functionality.
""",
)
