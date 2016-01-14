Скрипт для отслеживания событий в логах. При появлении новых событий скрипт
отпраляет отбивки с этими событиями на почту.

Требования: python2.6+ 

Как развернуть?

1. Копируем скрипт на машину

$ cd ~

$ git clone git@gl.netris.ru:support/log_event_monitor.git

2. Конфигурируем

$ vim log_event_monitor/conf/config.xml

```
<config>
        <pattern>kernel</pattern> 
        <logfile>/var/log/messages</logfile>
        <timeout>10</timeout>
        <mailconfig>
                <server>localhost</server>
                <subject>New log event</subject>
                <sendfrom>zabbix@mail.ru</sendfrom>
                <sendto>
                        <address>kolya@mail.ru</address>
                </sendto>
                <copyto>
                        <address>vasya@mail.ru</address>
                        <address>petya@mail.ru</address>
                </copyto>
        </mailconfig>
</config>
```
pattern - регулярное выражение которое будет сравниваться с каждой новой 
лога.

logfile - абсолютный путь к файлу лога

timeout - время (в секундах), в течении которого скрипт ожидает появления
новых событий перед отправкой их на почту. Необходимо для того, чтобы
скрипт не спамил при получении каждого нового события, а выжидал и оправлял
события "пачкой".

mailconfig:
    server - uri почтового сервера
    subject - тема письма
    sendfrom - ящик отправителя
    sendto - кому отправить
    copyto - кто в копии.
    
3. Добавляем скрипт запуска в init.d

$ sudo cp log_event_monitor/scripts/log_event_monitor /etc/init.d/log_event_monitor

Указываем абсолютный путь к файлу log_event_monitor.py в переменной DEAMON

$ sudo vim /etc/init.d/log_event_monitor

```
#!/bin/bash
# log_event_monitor daemon
# chkconfig: 345 20 80
# description: log_event_monitor daemon
# processname: log_event_monitor

# Меняем эту строку
DAEMON="/home/k.shatsky/log_event_monitor/log_event_monitor.py"

...

```



4. Запускаем 

$ sudo service log_event_monitor start

TODO:

1. В скрипте для init.d предусмотреть повторный запуск скрипта. Сейчас при
повторном вызове создается ещё один процесс - это неправильно.

2. Добавить проверки правильности конфига.

3. Предусмотреть отслеживание событий в нескольких файлах одновременно с общим конфигом.
