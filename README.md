# ha-python-auto-shutdown
home assistant(以下簡稱ha)自動化的應用<br>
易於使用為宗旨<br>
在ha上開啟使用者進階模式<br>
進入到 設定>附加元件>Advanced SSH & Web Terminal(保護模式設定為關閉)<br>
登入ha ssh後執行以下指令進入到docker產出ssh公私鑰<br>
```docker exec -it homeassistant bash```<br>
```ssh-keygen -t rsa -b 4096 -f /root/.ssh/id_rsa```<br>
```mkdir -p /config/ssh/;cp /root/.ssh/* /config/ssh/```<br>
退出docker容器指令<br>
```exit```<br>

關機腳本生成：<br>
編輯 nano /config/scripts.yaml
```
shutdown_nas:
  alias: 'Shutdown: nas'
  sequence:
  - service: shell_command.run_python_script_poweroff
```
crtl+s=save , ctrl+x=exit </br>
編輯 nano /config/configuration.yaml
```
shell_command:
  run_python_script_poweroff: "python3 /config/py/poweroff.py"
```
```mkdir -p /config/py;nano /config/py/poweroff.py```</br>
編輯 nano /config/py/poweroff.py
```
import paramiko

def shutdown_remote_server(hostname, username, key_path):
    try:
        # 创建一个 SSH 客户端对象
        ssh = paramiko.SSHClient()

        # 自动添加不在已知主机列表中的主机密钥
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 通过密钥进行身份验证并连接到远程主机
        ssh.connect(hostname, username=username, key_filename=key_path)

        # 执行关机命令
        stdin, stdout, stderr = ssh.exec_command('sudo poweroff')

        # 输出执行结果（可以省略）
        print(stdout.read().decode())

        # 关闭 SSH 连接
        ssh.close()
        print(f"Successfully shut down {hostname}")
    except Exception as e:
        print(f"Failed to shut down {hostname}: {e}")

# 设置远程服务器的主机名、用户名和 SSH 密钥路径
hostname = "nas_ip"
username = "your_account"
key_path = "/config/ssh/id_rsa"  # 替换为你的 SSH 密钥路径

# 调用函数执行关机操作
shutdown_remote_server(hostname, username, key_path)
```
最後重啟HA

---

### **HA-Python Auto Shutdown**

Home Assistant (referred to as HA) automation applications should be easy to use, as simplicity is key.

1. **Enable Advanced Mode in HA**:
   - Go to **Settings > Add-ons > Advanced SSH & Web Terminal** (set Protection Mode to Off).
   - Log in to HA SSH and execute the following command to enter the Docker SSH public/private key configuration:
     ```bash
     docker exec -it homeassistant bash
     ```

2. **Generate SSH Keys and Configure**:
   - **Step 1**: Generate SSH keys.
     ```bash
     ssh-keygen -t rsa -b 4096 -f /root/.ssh/id_rsa
     ```
     This will generate a 4096-bit RSA key pair in the `/root/.ssh/` directory within the container.

   - **Step 2**: Copy the generated keys to the Home Assistant configuration directory:
     ```bash
     mkdir -p /config/ssh/; cp /root/.ssh/* /config/ssh/
     ```

   - **Step 3**: Exit the Docker container:
     ```bash
     exit
     ```

3. **Creating the Shutdown Script Automation Configuration**:
   - **Step 1**: Edit the `/config/scripts.yaml` file and add a script configuration named `shutdown_nas`:
     ```yaml
     shutdown_nas:
       alias: 'Shutdown: nas'
       sequence:
         - service: shell_command.run_python_script_poweroff
     ```
     This will create a script called "Shutdown: nas" in Home Assistant, which will call the shell command you define.

   - **Step 2**: Edit the `/config/configuration.yaml` file to define a shell command that executes your Python shutdown script:
     ```yaml
     shell_command:
       run_python_script_poweroff: "python3 /config/py/poweroff.py"
     ```
     This ensures that when you execute `run_python_script_poweroff`, Home Assistant will run your Python script within the container.

4. **Writing the Python Shutdown Script**:
   - **Step 1**: Create the `poweroff.py` file in the `/config/py` directory:
     ```bash
     mkdir -p /config/py
     nano /config/py/poweroff.py
     ```

   - **Step 2**: Write the Python script:
     ```python
     import paramiko

     def shutdown_remote_server(hostname, username, key_path):
         try:
             # Create an SSH client object
             ssh = paramiko.SSHClient()

             # Automatically add the host key if not already in the known hosts list
             ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

             # Authenticate with the key and connect to the remote host
             ssh.connect(hostname, username=username, key_filename=key_path)

             # Execute the shutdown command
             stdin, stdout, stderr = ssh.exec_command('sudo poweroff')

             # Print the execution result (optional)
             print(stdout.read().decode())

             # Close the SSH connection
             ssh.close()
             print(f"Successfully shut down {hostname}")
         except Exception as e:
             print(f"Failed to shut down {hostname}: {e}")

     # Set the hostname, username, and SSH key path for the remote server
     hostname = "nas_ip"  # Replace with your NAS IP address
     username = "your_account"  # Replace with your username
     key_path = "/config/ssh/id_rsa"  # Replace with your SSH key path

     # Call the function to execute the shutdown operation
     shutdown_remote_server(hostname, username, key_path)
     ```

5. **Verification and Testing**:
   - **Ensure all files are saved, then restart Home Assistant** to apply the new configuration.
   - **Execute the automation or script**: Via the Home Assistant interface or by triggering the automation, verify that the `shutdown_nas` script can successfully shut down the remote server.

### **Points to Note**:
- **SSH Key Path**: Ensure the SSH key path is correct and that the target server is configured to accept this key.
- **sudo Configuration on NAS**: The user on the target NAS server needs to have permission to execute the `sudo poweroff` command.

This setup should enable you to achieve the remote shutdown of your NAS through Home Assistant.

--- 

This is the translated content use chatgpt
