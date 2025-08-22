import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_files_content import schema_get_file_content, get_file_content
from functions.run_python import schema_run_python_file, run_python_file
from functions.write_files import schema_write_file, write_file

def main():
    WORKING_DIRECTORY = "./calculator"

    # Schema declarations (for Gemini)
    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )

    # Actual implementations (for Python execution)
    FUNCTIONS = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "run_python_file": run_python_file,
    "write_file": write_file,
     }



    # Abstract function handler
    def call_function(function_call_part, verbose=False):
        function_name = function_call_part.name
        function_args = dict(function_call_part.args)

        # Inject working directory
        function_args["working_directory"] = WORKING_DIRECTORY

        if verbose:
            print(f"Calling function: {function_name}({function_args})")
        else:
            print(f" - Calling function: {function_name}")

        if function_name not in FUNCTIONS:
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_name,
                        response={"error": f"Unknown function: {function_name}"},
                    )
                ],
            )

        try:
            result = FUNCTIONS[function_name](**function_args)
        except Exception as e:
            result = f"Exception while running {function_name}: {e}"

        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": result},
                )
            ],
        )

    # ----------------------------
    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

    All paths you provide should be relative to the working directory. 
    You do not need to specify the working directory in your function calls 
    as it is automatically injected for security reasons.
    """

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    if len(sys.argv) < 2:
        print("1")
        sys.exit(1)

    # Parse args
    args = sys.argv[1:]
    verbose = False
    if "--verbose" in args:
        verbose = True
        args.remove("--verbose")

    prompt = " ".join(args)
    model = "gemini-2.0-flash-001"

    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)]),
    ]

    # Response from Gemini
    response = client.models.generate_content(
        model=model,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        )
    )

    prompt_tokens = response.usage_metadata.prompt_token_count
    response_tokens = response.usage_metadata.candidates_token_count

    if verbose:
        print(f"User prompt: {prompt}")
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Response tokens: {response_tokens}")

    # Function call or text?
    if response.candidates[0].content.parts[0].function_call:
        function_call_part = response.candidates[0].content.parts[0].function_call
        function_call_result = call_function(function_call_part, verbose=verbose)

        if not function_call_result.parts or not function_call_result.parts[0].function_response.response:
            raise RuntimeError("Fatal: function call returned no response")

        if verbose:
            print(f"-> {function_call_result.parts[0].function_response.response}")
    else:
        print(response.text)


if __name__ == "__main__":
    main()
