import os
def write_file(working_directory, file_path, content):
 try:
    working_path = os.path.abspath(working_directory)
    full_path = os.path.abspath(os.path.join(working_path,file_path))
    if not full_path.startswith(working_path):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(os.path.dirname(full_path)):
        os.makedirs(os.path.dirname(full_path),exist_ok=True)
    with open(full_path,"w") as f:
        _ = f.write(content)
    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
 except Exception as e:
    return f'Error "{e}"'
schema_write_file = {
    "name": "write_file",
    "description": "Write or overwrite a file with given content",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file"
            },
            "content": {
                "type": "string",
                "description": "The text content to write into the file"
            }
        },
        "required": ["file_path", "content"]
    }
}

