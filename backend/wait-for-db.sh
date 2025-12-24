#!/bin/sh
echo "Waiting for database..."
export PGPASSWORD=$POSTGRES_PASSWORD

until psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c '\q'; do
  echo "Postgres is unavailable - sleeping"
  sleep 2
done

echo "Postgres is up - executing command"
exec "$@"
