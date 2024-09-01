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
```mkdir -p /config/py```</br>
編輯 nano 
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
