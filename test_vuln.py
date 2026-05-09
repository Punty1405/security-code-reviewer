import subprocess

def process_command():
    user_input = input("Enter command: ")
    subprocess.call(user_input, shell=True)  # CWE-78 Command Injection
    
def sql_query():
    user_id = input("Enter ID: ")
    query = "SELECT * FROM users WHERE id = " + user_id  # CWE-89 SQL Injection
    return query

process_command()
