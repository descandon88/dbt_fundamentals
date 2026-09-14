with source as (

    select * from {{ source('stripe', 'payment') }}

),

renamed as (

    select
        id::integer as payment_id,
        orderid::integer as order_id,
        paymentmethod as payment_method,
        status,

        -- amount is stored in cents, convert it to dollars
        amount::integer / 100 as amount,
        created as created_at
        

    from source

)

select * from renamed