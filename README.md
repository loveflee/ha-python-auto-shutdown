# ha-python-auto-shutdown
home assistant(以下簡稱ha)自動化的應用<br>
易於使用為宗旨<br>
在ha上開啟使用者進階模式<br>
進入到 設定>附加元件>Advanced SSH & Web Terminal(保護模式設定為關閉)<br>
登入ha ssh後執行以下指令進入到docker產出ssh公私鑰<br><br>
docker exec -it homeassistant bash<br><br>
ssh-keygen -t rsa -b 4096 -f /root/.ssh/id_rsa<br><br>
mkdir -p /config/ssh/;cp /root/.ssh/* /config/ssh/<br><br>
退出docker容器指令<br>
exit<br><br>

關機腳本生成：用慣用的方式於以下文件添加內容<br>





