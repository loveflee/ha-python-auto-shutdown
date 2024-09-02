[繁體中文點我](#繁體中文)</br></br>
Here's the translated document into English:
# ha-python-auto-shutdown

This is an automation application for Home Assistant (referred to as HA below). It is designed to shut down devices and HA during a power outage when the UPS does not have a USB data connection cable.

## Steps:

1. **Enable Advanced Mode in HA:**
   - Go to `Settings > Add-ons > Advanced SSH & Web Terminal` (set Protection Mode to off).

2. **Generate SSH Key Pair:**
   - Log in to HA via SSH and execute the following commands to generate an SSH key pair in the Docker container:
   ```bash
   docker exec -it homeassistant bash;
   ssh-keygen -t rsa -b 2048 -f /root/.ssh/id_rsa;
   mkdir -p /config/ssh/;
   cp /root/.ssh/* /config/ssh/;
   chmod 600 /config/ssh/id_rsa
   ```
   - Exit the Docker container using the command:
   ```bash
   exit
   ```

3. **Shutdown Script:**
   - Open the `scripts.yaml` file:
   ```bash
   nano /config/scripts.yaml
   ```
   - Add the following content:
   ```yaml
   shutdown_nas:
     alias: 'Shutdown: PC'
     sequence:
     - service: shell_command.run_python_script_poweroff
   ```
   - Save and exit using `Ctrl + S` (Save) and `Ctrl + X` (Exit).

4. **Configure Shell Command in HA:**
   - Open the `configuration.yaml` file:
   ```bash
   nano /config/configuration.yaml
   ```
   - Add the following content:
   ```yaml
   shell_command:
     run_python_script_poweroff: "python3 /config/py/poweroff.py"
   ```

5. **Create the Python Script:**
   - Create a directory and a Python script:
   ```bash
   mkdir -p /config/py;nano /config/py/poweroff.py
   ```
   - Add the following code to the script:
   ```python
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
   ```

6. **Restart HA:**

7. **Copy SSH Public Key to PC or Linux:**
   - Copy the SSH public key to your PC or Linux machine. Replace `your_account` with your username and `pc_ip` with your PC's IP:
   ```bash
   cat /config/ssh/id_rsa.pub | ssh your_account@pc_ip 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys'
   ```

8. **Set Up Sudo Permissions on Linux:**
   - Log in to Linux with a user that has sudo privileges and restrict the HA user to only execute `poweroff` and `reboot` commands (reboot can be omitted):
   ```bash
   sudo visudo
   ```
   - Add the following at the bottom of the file:
   ```bash
   your_account ALL=(root) NOPASSWD: /sbin/poweroff, /sbin/reboot
   ```

9. **Configure Automation in HA:**
   - Go to `Settings > Automations & Scenes > Automations` (create a new automation).
   - Description: Monitor the UPS APC power status. When it becomes unavailable for 1 minute, execute `shell_command.run_python_script_poweroff` to shut down devices and HA.
   - Alias: Name your automation.
   - `entity_id`: Modify to match your environment's device ID, such as a Sonoff S31 or PZEM017 that can detect power voltage. If you don't know the `entity_id`, go to `Settings > Devices & Services`, find the device that can detect power status, click on it, and copy the `entity_id`. Replace the example `entity_id` with the copied ID.
   ```yaml
   alias: PC Shutdown
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

## **Windows 10 Setup:**

1. **Install OpenSSH and Set to Start Automatically:**
   - Run PowerShell as Administrator and execute:
   ```bash
   Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
   Set-Service -Name sshd -StartupType 'Automatic'
   ```

2. **Restrict SSH Login and Force Shutdown:**
   - Edit the SSH configuration:
   ```bash
   notepad C:\ProgramData\ssh\sshd_config
   ```
   - Scroll to the bottom of the file and change:
   ```bash
   Match Group administrators
          AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
   ```
   - To:
   ```bash
   #Match Group administrators
   #       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
   PasswordAuthentication no
   PubkeyAuthentication yes
   AllowUsers your_account
   Match User your_account
       ForceCommand shutdown /s /f /t 60 /c "System will shut down in 60 seconds. Please save your work."
   ```
   - This configuration disables password authentication, uses SSH public key authentication, allows `your_account` to log in, and displays a warning message "System will shut down in 60 seconds. Please save your work" upon login.

3. **Restart SSH to Apply Changes:**
   ```bash
   Restart-Service sshd
   ```

4. **Copy SSH Public Key to Windows:**
   - Open the `authorized_keys` file:
   ```bash
   notepad C:\Users\your_account\.ssh\authorized_keys
   ```
   - Paste the SSH public key created earlier into this file. The format should be: `ssh-rsa AAAAB3NzaC1...` (ensure there are no spaces or breaks).
copy HA ssh publickey and paste
```
cat /config/ssh/id_rsa
```
windown path
```
notepad C:\Users\your_account\.ssh\authorized_keys
```
This is the translated content use chatgpt
---
# 繁體中文

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
使用擁有 sudo 權限的帳號登入 Linux 執行下述方式,限制 ha 用 ssh 登入帳號後,該帳號 sudo 只能執行 poweroff 與 reboot (reboot可省略)
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
entity_id 自行更改符合環境的設備id,例如 sonoff s31;pzem017...等此類能獲取市電電壓目前是有電，或無電狀態的設備id</br>
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
<b>Windows 10</b></br>
用系統管理員身分執行 PowerShell</br>
安裝 openssh 與設為開機執行
```
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Set-Service -Name sshd -StartupType 'Automatic'
```
限制openssh 登入帳號,與登入openssh後顯示提醒存檔,並將在60秒後強制關機
```
notepad C:\ProgramData\ssh\sshd_config
```
移到文件最下方將
```
Match Group administrators
       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
```
修改為
```
#Match Group administrators
#       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers your_account
Match User your_account
    ForceCommand shutdown /s /f /t 60 /c "60秒後將關機，請盡快存檔"
```
作用:關閉密碼認證使用ssh publickey認證,允許 your_account 登入,一但有登入行為,顯示提醒 "60秒後將關機，請盡快存檔" </br>
以下指令為重啟ssh載入修改
```
Restart-Service sshd
```
將上方製作的ssh publickey 複製到下方位置</br>
格式為: ssh-rsa AAAAB3NzaC1不能有空格或斷開</br>
copy HA ssh publickey and paste
```
cat /config/ssh/id_rsa
```
windown path
```
notepad C:\Users\your_account\.ssh\authorized_keys
```
