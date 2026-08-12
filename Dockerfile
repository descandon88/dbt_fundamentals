# Imagen oficial de PostgreSQL
FROM postgres:15

# Variables de entorno
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=admin123
ENV POSTGRES_DB=DBT_POSTGRES

# Puerto por defecto
EXPOSE 5432



CMD ["postgres"]