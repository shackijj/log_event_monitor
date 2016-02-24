Скрипт для отслеживания событий в логах. При появлении новых событий скрипт
отпраляет отбивки с этими событиями на почту.

Требования: python2.6

Как развернуть?
yum install log-event-monitor.noarch

1. Копируем скрипт на машину

$ cd ~

$ git clone git@gl.netris.ru:support/log_event_monitor.git

2. Конфигурируем

$ vim log_event_monitor/conf/config.xml

```
<LogEventMonitorApp>
        <-- Монитор. Содержит конфиг для отслеживания событий
		в конкретном файле. -->
        <LogEventMonitor>
                <!-- Шаблон для поиска события в логах.
                     работает на основе re.search()
                     или как с флагом g в PCRE -->
                <pattern>kernel</pattern>
                <!-- Абсолютный путь к файлу лога -->
                <logfile>/home/k.shatsky/test.log</logfile>
                <!-- Таймаут в течении которого ожидаем поступления новых событий
                     и ждем завершения процессов OnEvent.
                     По истечению таймаута все процессы OnEvent убиваются,
                     накопленный буфер событий и файлы процессов отправляются на почту
                     Параметр опциональный. По умолчанию 1мс
                     -->
                <timeout>10</timeout>
                <!-- Интервал обновления в миллисекундах т.е.
                     как часто мы проверяем наличие новых строк в файле
                     Параметр опциональный. По умолчанию 1мс-->
                <UpdateInterval>100</UpdateInterval>
                <OnEvent>
                        <!-- Команда bash. Эквивалент: command  2>1 1 > outfile.txt-->
                        <command>iostat -ktx 1 120</command>
                        <!-- Отправлять ли результирующий файл на почту?
                             Параметр необязательный по умолчанию false -->
                        <SendOutput>true</SendOutput>
                        <!-- Файл для перенаправления вывода команды.
                             Файл будет отправлен на почту во вложении
                             если установлен параметр SendOutput-->
                        <OutputFile>/home/k.shatsky/iostat1.txt</OutputFile>
                </OnEvent>
                <OnEvent>
                        <command>vmstat 1 120</command>
                        <SendOutput>false</SendOutput>
                        <OutputFile>/home/k.shatsky/vmstat2.txt</OutputFile>
                </OnEvent>
        </LogEventMonitor>
        <LogEventMonitor>
                <pattern>kernel</pattern>
                <logfile>/home/k.shatsky/test2.log</logfile>
                <timeout>10</timeout>
                <UpdateInterval>100</UpdateInterval>
                <mailconfig>
                        <server>localhost</server>
                        <subject>New log event</subject>
                        <sendfrom>zabbix@zabbix155.mos.ru</sendfrom>
                        <sendto>
                                <address>k.shatsky@netris.ru</address>
                        </sendto>
                        <copyto>
                                <address>k.shatsky@netris.ru</address>
                        </copyto>
                </mailconfig>
                <OnEvent>
                        <command>iostat -ktx 1 120</command>
                        <SendOutput>true</SendOutput>
                        <OutputFile>/home/k.shatsky/iostat.txt</OutputFile>
                </OnEvent>
                <OnEvent>
                        <command>vmstat 1 120</command>
                        <SendOutput>false</SendOutput>
                        <OutputFile>/home/k.shatsky/vmstat.txt</OutputFile>
                </OnEvent>
        </LogEventMonitor>
</LogEventMonitorApp>

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