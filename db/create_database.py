import psycopg

create_table_statement = """
drop table if exists dummy_metrics;
create table dummy_metrics(
	timestamp timestamp,
	fare_amount_mean float,
	prediction_drift float,
	num_drifted_columns integer,
	share_missing_values float
);
"""


def prep_db():
    with psycopg.connect(
        "host=localhost port=5432 user=postgres password=example",
        autocommit=True,
    ) as conn:
        res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
        if len(res.fetchall()) == 0:
            conn.execute("create database test;")

    with psycopg.connect(
        "host=localhost port=5432 dbname=test user=postgres password=example"
    ) as conn:
        conn.execute(create_table_statement)


if __name__ == "__main__":
    prep_db()
