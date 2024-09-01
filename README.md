# ha-python-auto-shutdown
home assistant(以下簡稱ha)自動化的應用<br>
UPS沒有USB數據連接線,停電時讓設備與ha關機</br></br>
在ha上開啟使用者進階模式<br>
進入到 設定>附加元件>Advanced SSH & Web Terminal(保護模式設定為關閉)<br>
登入ha ssh後執行以下指令進入到docker產出ssh公私鑰<br>
```
docker exec -it homeassistant bash;
ssh-keygen -t rsa -b 2048 -f /root/.ssh/id_rsa;
mkdir -p /config/ssh/;
cp /root/.ssh/* /config/ssh/;
chmod 600 /config/ssh/id_rsa
```
退出docker容器指令<br>
```exit```<br>

關機腳本：<br>
nano /config/scripts.yaml
```
shutdown_nas:
  alias: 'Shutdown: pc'
  sequence:
  - service: shell_command.run_python_script_poweroff
```
按鍵crtl+s=save (存檔) , 按鍵ctrl+x=exit (離開nano)</br>
nano /config/configuration.yaml
```
shell_command:
  run_python_script_poweroff: "python3 /config/py/poweroff.py"
```
```
mkdir -p /config/py;nano /config/py/poweroff.py
```
/config/py/poweroff.py
```
import paramiko

def shutdown_remote_server(hostname, username, os_type, key_path):
    try:
        # SSH 客戶端
        ssh = paramiko.SSHClient()

        # 自動增加不在已知主機列表中的主機密鑰
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 通過私鑰連接
        ssh.connect(hostname, username=username, key_filename=key_path)

        # 分辨 Linux 或 windows 執行關機指令
        if os_type.lower() == 'linux':
            command = 'sudo poweroff'
        elif os_type.lower() == 'windows':
            command = 'shutdown /s /f /t 0'
        else:
            print(f"Unsupported OS type: {os_type}")
            ssh.close()
            return

        # 執行關機指令
        stdin, stdout, stderr = ssh.exec_command(command)

        # 列出執行結果
        print(stdout.read().decode())

        # 關閉連線
        ssh.close()
        print(f"Successfully shut down {hostname} ({os_type})")
    except Exception as e:
        print(f"Failed to shut down {hostname} ({os_type}): {e}")

# hostname=登入主機ip username=登入帳號 os_type=作業系統類別
# 以下為範例,  自行修改,根據需求增加減少
servers = [
    {"hostname": "192.168.222.222", "username": "your_account", "os_type": "linux"},
    {"hostname": "192.168.222.223", "username": "admin", "os_type": "windows"}
]
key_path = "/config/ssh/id_rsa"  # 更改為 ssh 私鑰檔案路徑,如照上方指令略過既可

# 調用函數執行關機指令
for server in servers:
    shutdown_remote_server(server['hostname'], server['username'], server['os_type'], key_path)

```
重啟HA</br>
將 ssh publickey 複製到電腦或Linux上, your_account=你的帳號名稱 pc_ip=你的電腦ip</br>
```
cat /config/ssh/id_rsa.pub | ssh your_account@pc_ip 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys'
```
已具備 sudo 權限的user執行下列指令,限制 ha 使用ssh登入系統後, sudo 權限只能執行 poweroff 與 reboot (reboot可省略)
```
sudo visudo
```
移到最下方添加以下內容 
```
your_account ALL=(root) NOPASSWD: /sbin/poweroff, /sbin/reboot
```
設定 > 自動化與場景 > 自動化  (新增自動化)</br>
說明: 取的 ups apc 的市電狀態,當變成不可用達1分鐘,執行 shell_command.run_python_script_poweroff,將設備與 Ha 關機</br>
alias：自動化名稱</br>
entity_id 自行更改符合環境的設備id,例如sonoff s31:pzem017...等此類能獲取市電電壓目前是有電，或無電狀態的設備id</br>
如果不知道 entity_id 可由 設定 > 裝置與服務 找到能獲取市電狀態設備後點選一下,再點選齒輪,複製 實體ID 將範例的entity_id更改為剛複製的 實體ID
```
alias: pc shutdown
description: ""
trigger:
  - platform: state
    entity_id:
      - sensor.apc_input_voltage
    from: null
    for:
      hours: 0
      minutes: 1
      seconds: 0
    to: unavailable
condition: []
action:
  - service: shell_command.run_python_script_poweroff
    data: {}
  - service: hassio.host_shutdown
    data: {}
mode: single
```



---
Home Assistant (HA) Python Auto Shutdown

This guide is focused on automating the shutdown of remote servers through Home Assistant (HA) using Python. The goal is to simplify the process, making it user-friendly and effective for automating tasks like shutting down NAS devices or PCs over the network.

Enable Advanced Mode in Home Assistant:

Go to Settings > Add-ons > Advanced SSH & Web Terminal and turn off the protection mode.
Access HA via SSH and execute the following commands to generate SSH keys within the Docker container:
bash
```
docker exec -it homeassistant bash
ssh-keygen -t rsa -b 2048 -f /root/.ssh/id_rsa
mkdir -p /config/ssh/
cp /root/.ssh/* /config/ssh/
chmod 600 /config/ssh/id_rsa
```
Exit the Docker container with the exit command.
Create the Shutdown Script:

Edit /config/scripts.yaml to include the following script for shutting down a PC:</br>
yaml
```
shutdown_nas:
  alias: 'Shutdown: pc'
  sequence:
  - service: shell_command.run_python_script_poweroff
```
Save the file with ctrl+s and exit with ctrl+x.
Configure Shell Command in Home Assistant:

Add the following configuration in /config/configuration.yaml:</br>
yaml
```
shell_command:
  run_python_script_poweroff: "python3 /config/py/poweroff.py"
```
Create a directory and script file:</br>
bash
```
mkdir -p /config/py
nano /config/py/poweroff.py
```
Python Script for Shutdown:

Use the following Python code in poweroff.py to shut down both Linux and Windows servers:
python
```
import paramiko

def shutdown_remote_server(hostname, username, os_type, key_path):
    try:
        # SSH Client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, key_filename=key_path)

        # Determine OS type and execute shutdown command
        if os_type.lower() == 'linux':
            command = 'sudo poweroff'
        elif os_type.lower() == 'windows':
            command = 'shutdown /s /f /t 0'
        else:
            print(f"Unsupported OS type: {os_type}")
            ssh.close()
            return

        # Execute shutdown command
        stdin, stdout, stderr = ssh.exec_command(command)
        print(stdout.read().decode())

        # Close SSH connection
        ssh.close()
        print(f"Successfully shut down {hostname} ({os_type})")
    except Exception as e:
        print(f"Failed to shut down {hostname} ({os_type}): {e}")

# Define the servers and their details
servers = [
    {"hostname": "192.168.222.222", "username": "your_account", "os_type": "linux"},
    {"hostname": "192.168.222.223", "username": "admin", "os_type": "windows"}
]
key_path = "/config/ssh/id_rsa"  # Adjust if necessary

# Execute shutdown for each server
for server in servers:
    shutdown_remote_server(server['hostname'], server['username'], server['os_type'], key_path)
```
Restart Home Assistant
Copy the SSH Public Key to Remote Computers:

To copy the SSH public key to your remote computers (replace your_account and pc_ip with the appropriate values):</br>
bash
```
cat /config/ssh/id_rsa.pub | ssh your_account@pc_ip 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys'
```
Set Up Sudo Permissions for Poweroff and Reboot:

If the user has sudo privileges, restrict HA's SSH access so that sudo can only execute poweroff and reboot commands:</br>
bash
```
sudo visudo
```
Add the following line at the end:
```
your_account ALL=(root) NOPASSWD: /sbin/poweroff, /sbin/reboot
```
This setup will allow you to automate the shutdown of Linux and Windows servers through Home Assistant with minimal intervention.
This is the translated content use chatgpt
