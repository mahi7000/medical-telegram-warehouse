{{ config(materialized='table') }}

select
    m.unique_message_key,
    m.message_id,
    c.channel_sk,
    cast(m.message_timestamp as date) as date_key,
    m.cleaned_message_text,
    m.has_media,
    m.image_path,
    m.views_count,
    m.forwards_count
from {{ ref('stg_telegram_messages') }} m
join {{ ref('dim_channels') }} c on m.channel_name = c.channel_name