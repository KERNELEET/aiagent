import os
import subprocess

def run_python_file(working_directory, file_path, args=[]):
    working_path = os.path.abspath(working_directory)
    full_path = os.path.abspath(os.path.join(working_path, file_path))

    # Security checks
    if not full_path.startswith(working_path):
        return {"error": f'Cannot execute "{file_path}" outside working directory.'}
    if not os.path.exists(full_path):
        return {"error": f'File "{file_path}" not found.'}
    if os.path.splitext(full_path)[1] != ".py":
        return {"error": f'"{file_path}" is not a Python file.'}

    command = ["python", full_path] + args

    try:
        result = subprocess.run(
            command,
            timeout=30,
            capture_output=True,
            cwd=working_path,
            text=True
        )

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }

    except Exception as e:
        return {"error": str(e)}


schema_run_python_file = {
    "name": "run_python_file",
    "description": "Execute a Python file with optional arguments",
    "parameters": {
        "type": "object",
        "properties": {
            "working_directory": {
                "type": "string",
                "description": "The base working directory where the file is located"
            },
            "file_path": {
                "type": "string",
                "description": "The relative path to the Python file"
            },
            "args": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional command line arguments"
            }
        },
        "required": ["working_directory", "file_path"]
    }
}
