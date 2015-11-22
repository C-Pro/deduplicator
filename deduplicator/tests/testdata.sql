create user scott with password 'tiger';
create database db with owner scott;
\c db

create table iptable (user_id bigint,
                      ip_address varchar(15),
                      "date" timestamp default clock_timestamp());

/*
Tests
(1,2) and (4,7) are duplicates
others are not
*/
insert into iptable(user_id,ip_address) 
values (1,'127.0.0.1'), --dup1
       (1,'128.0.0.1'), --dup1
       (2,'127.0.0.1'), --dup1
       (2,'128.0.0.2'),
       (2,'128.0.0.1'), --dup1
       (3,'128.0.0.1'),
       (3,'128.0.0.2'),
       (4,'128.0.0.1'), --dup2
       (4,'100.0.0.0'), --dup2
       (5,'100.000.00.2'),
       (7,'128.0.0.1'), --dup2
       (7,'100.0.0.0')  --dup2
       ;

--Helper function for random IP generation
create or replace function rnd_octet() returns varchar
as $$
 select (trunc(random()*256.0)::int)::varchar;
$$ language sql;

--Inserting 1M records of random test data
--Possibility of duplicates is low
insert into iptable(user_id, ip_address, "date")
select user_id,
       ip_address,
       '01.01.2000'::timestamp + (r.r || ' seconds')::interval
from
(select (random()*10^4)::int as user_id,
       rnd_octet() || '.' ||
       rnd_octet() || '.' ||
       rnd_octet() || '.' ||
       rnd_octet() as ip_address,
       row_number() over () r
  from generate_series(1,(10^6)::int)) r;
;

drop function rnd_octet();

--May fail if there are unique violations due to
--previously inserted random data
--probability of duplication is very low (1/10000000000)
alter table iptable add constraint iptable_uk unique (user_id, ip_address);

--Index for fast extraction of new data
create index iptable_date_i on iptable("date");

alter table iptable owner to scott;

