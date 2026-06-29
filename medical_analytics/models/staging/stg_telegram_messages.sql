{{ config(materialized='view') }}

with raw_data as (
    select * from {{ source('raw_source', 'telegram_messages') }}
)

select
    -- Primary unique structural compound business key
    md5(concat(channel_name, '_', message_id)) as unique_message_key,
    message_id,
    channel_name,
    
    -- Text transformations
    trim(message_text) as cleaned_message_text,
    
    -- Flag formatting & safety checks
    coalesce(has_media, false) as has_media,
    image_path,
    
    -- Metrics casting
    coalesce(views, 0) as views_count,
    coalesce(forwards, 0) as forwards_count,
    
    -- Chronological parsing
    cast(message_date as timestamp) as message_timestamp
from raw_data
where message_id is not null