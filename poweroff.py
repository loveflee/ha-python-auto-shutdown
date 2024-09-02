import paramiko

def shutdown_remote_server(hostname, username, os_type, key_path):
    try:
        # SSH Client
        ssh = paramiko.SSHClient()

        # Automatically add keys for unknown hosts
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect using the private key
        ssh.connect(hostname, username=username, key_filename=key_path)

        # Determine whether to execute the shutdown command for Linux or Windows
        if os_type.lower() == 'linux':
            command = 'sudo poweroff'
        elif os_type.lower() == 'windows':
            command = 'shutdown /s /f /t 0'
        else:
            print(f"Unsupported OS type: {os_type}")
            ssh.close()
            return

        # Execute the shutdown command
        stdin, stdout, stderr = ssh.exec_command(command)

        # Display the result
        print(stdout.read().decode())

        # Close the connection
        ssh.close()
        print(f"Successfully shut down {hostname} ({os_type})")
    except Exception as e:
        print(f"Failed to shut down {hostname} ({os_type}): {e}")

# Define servers with hostname, username, and OS type (adjust as needed)
servers = [
    {"hostname": "192.168.222.222", "username": "your_account", "os_type": "linux"},
    {"hostname": "192.168.222.223", "username": "admin", "os_type": "windows"}
]
key_path = "/config/ssh/id_rsa"  # Modify to your SSH private key path if necessary

# Execute shutdown command for each server
for server in servers:
    shutdown_remote_server(server['hostname'], server['username'], server['os_type'], key_path)
