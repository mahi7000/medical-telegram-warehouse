{{ config(materialized='table') }}

select
    distinct
    cast(message_timestamp as date) as date_key,
    extract(year from message_timestamp) as year,
    extract(month from message_timestamp) as month,
    extract(day from message_timestamp) as day,
    to_char(message_timestamp, 'Day') as day_name
from {{ ref('stg_telegram_messages') }}