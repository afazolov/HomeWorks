README.txt

Проект: Менеджер паролей для Linux
VM: Ubuntu в VirtualBox/VMware

1) Настройка виртуальной машины
- Установлена Ubuntu.
- Созданы пользователи:
  1) adminuser — администратор (в группе sudo)
  2) limiteduser — пользователь с ограниченными правами

2) Команды, которые использовались

Создание пользователей:
sudo adduser adminuser
sudo usermod -aG sudo adminuser
sudo adduser limiteduser

Создание группы и доступов:
sudo groupadd security
sudo usermod -aG security limiteduser

Создание директории и прав:
sudo mkdir -p /home/security
sudo chown root:security /home/security
sudo chmod 2770 /home/security

Файл passwords.txt (доступ только владельцу):
cd /home/security
touch passwords.txt
chmod 600 passwords.txt

3) Как запускать password_manager.py

Перейти в рабочую папку:
cd /home/security

Добавить запись:
python3 password_manager.py add <service> <login> <password>
пример:
python3 password_manager.py add google mylogin mypass

Показать список сервисов:
python3 password_manager.py list

Получить логин и пароль по сервису:
python3 password_manager.py get <service>
пример:
python3 password_manager.py get google

Удалить запись:
python3 password_manager.py del <service>
пример:
python3 password_manager.py del google

Генерация и сохранение пароля:
python3 password_manager.py addgen <service> <login> simple|complex [length]
пример:
python3 password_manager.py addgen bank mylogin complex 16

4) archive.py (архивация)
python3 archive.py
Результат: создаётся backup.tar.gz в /home/security, выводится размер архива.

5) usage_monitor.py (логирование операций)
Скрипт usage_monitor.py увеличивает счётчик операций и пишет usage.log.
usage.log хранит строку total=<число> и историю операций.
Проверка:
cat usage.log

6) Проблемы и решения (пример)
- После добавления пользователя в группу security доступ не появился сразу.
  Решение: перелогиниться (logout/login) под пользователем, чтобы группы применились.

7) Экспорт VM
VM выключена.
Файл конфигурации виртуальной машины сохранён как:
Linux_Project_ИмяФамилия.vbox