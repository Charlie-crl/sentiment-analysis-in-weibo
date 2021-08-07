-- use pweibo
-- show tables

-- 微博都有哪些来源
-- select distinct source from mblog 

-- 统计每个来源的微博条数
-- select source,count(*) as count from mblog group by source order by count desc

-- 用户的性别分布
-- select gender,count(*) from user group by gender

select follow_count,count(*) from user group by follow_count