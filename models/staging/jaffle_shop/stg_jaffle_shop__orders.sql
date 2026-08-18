with source as (

    select * from {{ source('jaffle_shop', 'jaffle_shop_orders') }}

),

renamed as (

    select
        id::integer as order_id,
        user_id::integer as customer_id,
        order_date::date as order_date,
        status

    from source

)

select * from renamed
