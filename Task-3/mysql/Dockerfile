FROM mysql:8.4

ENV APP_DB_NAME=webapp \
    APP_DB_USER=webapp \
    APP_DB_PASSWORD=webapp123 \
    MYSQL_REPL_USER=repl \
    MYSQL_REPL_PASSWORD=repl123 \
    MYSQL_ROLE=source \
    MYSQL_INITDB_SKIP_TZINFO=1

COPY conf/replication.cnf /etc/mysql/conf.d/replication.cnf

COPY schema/schema.sql /opt/webapp/schema.sql

COPY initdb/01-setup.sh /docker-entrypoint-initdb.d/01-setup.sh
RUN chmod 0644 /docker-entrypoint-initdb.d/01-setup.sh
