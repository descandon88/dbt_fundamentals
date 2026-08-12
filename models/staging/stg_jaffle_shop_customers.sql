with source as (

    select * from {{ source('jaffle_shop', 'jaffle_shop_customers') }}

),

renamed as (

    select
        id::integer as customer_id,
        first_name as first_name,
        last_name as last_name

    from source

)

select * from renamed
