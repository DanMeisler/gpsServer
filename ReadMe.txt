installation:
1) install mongodb Community Server
2) install python 3.5.2
3) install pymongo and fastkml(using pip)
4) install eds 16.1.1
5) install mongo v11 X86 TS extension (php 5.6)
6) add "extension=php_mongo.dll" to php.ini (php 5.6)
8) put php directory in the system path variable (check that lsass.dll is in the directory)
9) make static ip address
10) port forwarding
11) download py file from github
12) put site files into eds-www
13) change the Listen row in httpd.conf from 127.0.0.1:80 to *:80
