-- create database Pweibo;
-- use Pweibo;
-- show tables

-- 创建微博card信息表
-- create table Mblog(
-- mid varchar(100) not null,
-- comments_count int null,
-- created_at varchar(100) null,
-- source varchar(50) null,
-- text varchar(1000) null,
-- user_id varchar(100) null,
-- constraint Mblog_User_user_id_fk foreign key(user_id) references user (user_id)
-- )

-- 给mid去重
-- alter table Mblog add constraint Mblog_mid_uindex unique(mid)
-- 给mid设置主键
-- alter table Mblog add constraint Mblog_pk primary key(mid)

-- 创建微博用户表
-- create table User(
-- user_id varchar(100) not null,
-- description varchar(1000) null,
-- follow_count int null,
-- followers_count int null,
-- gender varchar(10) null,
-- profile_url varchar(200) null,
-- screen_name varchar(100) null,
-- statuses_count int null
-- );

-- 设user_id主键
-- alter table User add constraint User_pk primary key(user_id)
-- 给user_id去重mblog
-- alter table User add constraint User_user_id_uindex unique(user_id)

-- select count(*) from mblog
-- 修改mblog中raw_text和text的长度
-- alter table mblog modify column text varchar(5000);
-- alter table mblog modify column raw_text varchar(5000);

-- 修改user中profile_url的长度
-- alter table user modify column profile_url varchar(1000);


-- 清空表
-- truncate table mblog

-- 删除mblog中的user外键(为了测试，清空表)
-- alter table mblog drop constraint Mblog_User_user_id_fk

-- 添加回来mblog中的外键
-- ALTER TABLE mblog
-- ADD CONSTRAINT Mblog_User_user_id_fk FOREIGN KEY (user_id) references user (user_id);


-- 创建分词表
-- create table mblogword(
-- mid varchar(100) not null,
-- word varchar(10) not null
-- )

select count(*) from mblog





