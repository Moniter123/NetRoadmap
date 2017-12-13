1. install requirements.txt
 # pip install -r requirements.txt

2. install redis and start
 # ...

3. install celery and start
 # pip install -U Celery
 # celery worker -l INFO -A manage.celery

4. pip install requests   #(zabbix client request)

5. pip install redis  (manage.py中修改redis访问地址)

6. start app
 # python manage.py
