import subprocess

def llm_execute(command):
    try:
        return subprocess.check_output(command, shell=True, text=True)
    except Exception as e:
        return str(e)

# Example
while True:
    user_cmd = input("LLM says: ")
    print(llm_execute(user_cmd))
