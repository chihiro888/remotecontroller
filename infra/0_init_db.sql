CREATE DATABASE remotecontroller;

create user remotecontroller@'%' identified by 'XbBtyL3Z9NzYUgzK8e6A' ;
grant all privileges on remotecontroller.* to remotecontroller@'%' with grant option;
ALTER USER remotecontroller@'%' IDENTIFIED WITH mysql_native_password BY 'XbBtyL3Z9NzYUgzK8e6A';
flush privileges;