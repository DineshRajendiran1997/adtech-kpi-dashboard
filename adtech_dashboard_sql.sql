use AdDataDB;


-- view 1: daily market KPI summary
-- collapses the 3 device rows into one row per market per day
-- CTR and CPC are recalculated from totals rather than averaged
-- to avoid distortion across the desktop/mobile/tablet split

create or alter view vw_Daily_Market_KPI as
select
    Date,
    Market,
    sum(Impressions) as Total_Impressions,
    sum(Clicks) as Total_Clicks,
    round(
        cast(sum(Clicks) as float) / nullif(sum(Impressions), 0) * 100
    , 3) as CTR_Pct,
    round(
        sum(Ad_Spend_USD) / nullif(sum(Clicks), 0)
    , 2) as CPC_USD,
    sum(Ad_Spend_USD) as Total_Spend,
    sum(Revenue_USD) as Total_Revenue,
    sum(Conversions) as Total_Conversions,
    round(
        sum(Revenue_USD) / nullif(sum(Ad_Spend_USD), 0)
    , 2) as ROAS,
    max(Alert_Fired) as Alert_Fired
from adtech_raw_data
group by Date, Market;
go


-- view 2: alert events only
-- filters to anomaly days and adds a severity label
-- thresholds: CPC > 2.0 or CTR > 6.0 or impressions < 200k = high impact

create or alter view vw_Alert_Events as
select
    Date,
    Market,
    Alert_Type,
    sum(Impressions) as Total_Impressions,
    round(avg(CTR_Pct), 3) as Avg_CTR,
    round(avg(CPC_USD), 2) as Avg_CPC,
    sum(Revenue_USD) as Total_Revenue,
    sum(Ad_Spend_USD) as Total_Spend,
    round(sum(Revenue_USD) / nullif(sum(Ad_Spend_USD), 0), 2) as ROAS,
    case
        when avg(CPC_USD) > 2.0 then 'High Impact'
        when avg(CTR_Pct) > 6.0 then 'High Impact'
        when sum(Impressions) < 200000 then 'High Impact'
        else 'Medium Impact'
    end as Severity
from adtech_raw_data
where Alert_Fired = 1
group by Date, Market, Alert_Type;
go


-- view 3: day over day revenue change
-- uses a CTE to get daily totals first, then LAG to compare with previous day
-- partition by market so each market's trend is calculated independently

create or alter view vw_DoD_Revenue_Change as
with daily as (
    select
        Date,
        Market,
        sum(Revenue_USD) as Total_Revenue,
        round(avg(CTR_Pct), 3) as Avg_CTR,
        round(avg(CPC_USD), 2) as Avg_CPC
    from adtech_raw_data
    group by Date, Market
),
with_lag as (
    select
        Date,
        Market,
        Total_Revenue,
        Avg_CTR,
        Avg_CPC,
        lag(Total_Revenue) over (
            partition by Market
            order by Date
        ) as Prev_Day_Revenue
    from daily
)
select
    Date,
    Market,
    Total_Revenue,
    Avg_CTR,
    Avg_CPC,
    Prev_Day_Revenue,
    round(Total_Revenue - Prev_Day_Revenue, 0) as Revenue_Change,
    round(
        (Total_Revenue - Prev_Day_Revenue) / nullif(Prev_Day_Revenue, 0) * 100
    , 1) as Revenue_Change_Pct
from with_lag
where Prev_Day_Revenue is not null;
go


-- verify
select top 5 * from vw_Daily_Market_KPI order by Date, Market;
select * from vw_Alert_Events order by Date;
select top 5 * from vw_DoD_Revenue_Change order by Market, Date;
