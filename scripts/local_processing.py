"""
local_processing.py

Convert csv files to parquet and push to S3
"""

# %%
import pyarrow as pa
import pyarrow.csv as pv
import pyarrow.parquet as pq

from pathlib import Path

# %%
DIR_DATA = Path('../data')
AWS_BUCKET = ''

# %%
schema_actors = pa.schema([
    ('id', pa.int64()),
    ('name', pa.string()),
])

table = pv.read_csv(DIR_DATA / 'csv' / 'actors.csv')
table = table.cast(schema_actors)
pq.write_table(table, DIR_DATA / 'parquet' / 'actors.parquet')

# %%
ingestion_map = {
    'actors': {
        'csv_file_name': 'actors.csv',
        'parquet_file_name': 'actors.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('name', pa.string()),
        ]),
    },
    'countries': {
        'csv_file_name': 'countries.csv',
        'parquet_file_name': 'countries.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('country', pa.string()),
        ]),
    },
    'crew': {
        'csv_file_name': 'crew.csv',
        'parquet_file_name': 'crew.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('role', pa.string()),
            ('name', pa.string()),
        ]),
    },
    'genres': {
        'csv_file_name': 'genres.csv',
        'parquet_file_name': 'genres.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('genre', pa.string()),
        ]),
    },
    'languages': {
        'csv_file_name': 'languages.csv',
        'parquet_file_name': 'languages.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('type', pa.string()),
            ('language', pa.string()),
        ]),
    },
    'movies': {
        'csv_file_name': 'movies.csv',
        'parquet_file_name': 'movies.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('name', pa.string()),
            ('date', pa.int32()),
            ('tagline', pa.string()),
            ('description', pa.string()),
            ('minute', pa.int64()),
            ('rating', pa.float32()),
        ]),
    },
    'releases': {
        'csv_file_name': 'releases.csv',
        'parquet_file_name': 'releases.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('country', pa.string()),
            ('date', pa.date32()),
            ('type', pa.string()),
            ('rating', pa.string()),
        ]),
    },
    'studios': {
        'csv_file_name': 'studios.csv',
        'parquet_file_name': 'studios.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('studio', pa.string()),
        ]),
    },
    'themes': {
        'csv_file_name': 'themes.csv',
        'parquet_file_name': 'themes.parquet',
        'schema': pa.schema([
            ('id', pa.int64()),
            ('theme', pa.string()),
        ]),
    },
}
# %%
# convert csv to parquet
for table_name, table_info in ingestion_map.items():
    print(f"Converting '{table_name}'...")

    table = pv.read_csv(DIR_DATA / 'csv' / table_info['csv_file_name'])
    table = table.cast(table_info['schema'])
    pq.write_table(table, DIR_DATA / 'parquet' / table_info['parquet_file_name'])

    print(f"    '{table_info['csv_file_name']}' converted to '{table_info['parquet_file_name']}'")
    print(f"    {table.num_rows:,} records")


# %%
