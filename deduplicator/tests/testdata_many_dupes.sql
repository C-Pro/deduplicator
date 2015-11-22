--Many matching IPS, but no matching users
insert into iptable(user_id, ip_address)
select r.r + 10^4 as user_id,
       '8.' || ((random()*100+101)::int)::varchar ||
       '.' || ((random()*255)::int)::varchar ||
       '.' || (254 % r.r + 1)::varchar as ip_address
from
(select row_number() over () r
  from generate_series(1,(10^5)::int)) r;
insert into iptable(user_id, ip_address)
select r.r + 20^4 as user_id,
       '8.' || ((random()*100)::int)::varchar ||
       '.' || ((random()*255)::int)::varchar ||
       '.' || (254 % r.r + 1)::varchar as ip_address
from
(select row_number() over () r
  from generate_series(1,(10^5)::int)) r;

--10000 full duplicates
with source as 
(
    select r.r * 2 as user_id,
           '9.' || ((random()*100)::int)::varchar ||
           '.' || ((random()*255)::int)::varchar ||
           '.' || (254 % r.r + 1)::varchar as ip_address,
           '10.' || ((random()*100)::int)::varchar ||
           '.' || ((random()*255)::int)::varchar ||
           '.' || (254 % r.r + 1)::varchar as ip_address2
    from
    (select row_number() over () r
      from generate_series(1,(10^4)::int)) r
)
insert into iptable(user_id, ip_address)
select user_id - 1,
       ip_address
from source
union all
select user_id,
       ip_address
from source
union all
select user_id - 1,
       ip_address2
from source 
union all
select user_id,
       ip_address2
from source;


