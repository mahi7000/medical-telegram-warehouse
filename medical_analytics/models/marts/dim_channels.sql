{{ config(materialized='table') }}

select
    row_number() over (order by channel_name) as channel_sk,
    channel_name,
    count(message_id) as total_messages_scraped
from {{ ref('stg_telegram_messages') }}
group by channel_name