#!/usr/bin/env python3

"""
    This script reads CSVs created by  the ccda_coverage_snooper.py and
the conversion process from CCDA_OMOP_by_Python in data_driven_parse.py
(also called by layer_datasets.py), into a duckdb. The snooper creates
ccda_coverage_snooper.csv and the conversion process creates trace.csv

"""
import duckdb
import pandas as pd

conn = duckdb.connect()
#pd.set_option('display.max_columns', 10)
#pd.set_option('display.width', 1000)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


snooper_fields = ['filename', 'template_id', 'path', 'field_tag', 'attributes']
snooper_ddl = """
    CREATE TABLE snooper (
        filename varchar(200),
        template_id varchar(20),
        path varchar(250),
        field_tag varchar(20),
        attributes varchar(200) );
"""


snooper_insert = """
        INSERT INTO snooper
        SELECT filename, template_id, path, field_tag, attributes
        FROM read_csv("ccda_coverage_snooper.csv", delim=',', header=True)
"""

trace_fields = ['filename', 'template_id', 'root_xpath', 'element_tag', 'config_type',
                'domain', 'omop_field_tag', 'attribute_value', 'attributes' ]
trace_ddl = """
    CREATE TABLE trace (
        filename varchar(200),
        template_id varchar(20),
        root_xpath varchar(250),
        element_tag varchar(20),
        config_type varchar(20),
        domain varchar(20),
        omop_field_tag varchar(20),
        attribute_value varchar(20),
        attributes varchar(200) );
"""

trace_insert = """
        INSERT INTO  trace
        SELECT filename, template_id, root_xpath, element_tag, config_type,
                domain, omop_field_tag, attribute_value, attributes
        FROM read_csv("../CCDA_OMOP_by_Python/trace.csv", delim=',', header=True)
"""

conn.execute(snooper_ddl)
conn.execute(trace_ddl)
#df = conn.sql("SHOW ALL TABLES;").df()
#print(df[['database', 'schema', 'name']])
#print("")


conn.execute(snooper_insert)
conn.execute(trace_insert)

df=conn.execute("""SELECT count(*) as row_ct, count(distinct path) as path_ct
                FROM snooper
            """).df()
print("snooper")
print(df)
print("")

df=conn.execute("""SELECT count(*) as row_ct, count(distinct root_xpath) as path_ct
                FROM trace
                WHERE config_type = 'FIELD'
            """).df()
print("trace")
print(df)
print("")


df=conn.execute("""select  count(*) as row_ct, count(distinct path) as path_ct, count(distinct root_xpath) as xpath_ct
                   from snooper s 
                   join trace t on  s.path = t.root_xpath  and s.field_tag = t.element_tag
                """).df()
print("join on path and field")
print(df)
print("")


if False:
    print("======== path ============")
    df=conn.execute("""SELECT distinct path
                    FROM snooper
                """).df()
    print(df)
    print(type(df))
    df=conn.execute("""SELECT distinct root_xpath
                    FROM trace 
                """).df()
    print(df)
    print(type(df))

if False:
    print("======== field/element ============")
    df=conn.execute("""SELECT distinct  field_tag
                    FROM snooper
                """).df()
    print(df)
    print(type(df))
    df=conn.execute("""SELECT distinct element_tag
                    FROM trace 
                """).df()
    print(df)
    print(type(df))


if False:
    df=conn.execute("""SELECT distinct path
                    FROM snooper
                    LIMIT 10
                """).df()
    print(df)
    print(type(df))

    print("trace")
    #df=conn.execute("""SELECT distinct root_xpath
    df=conn.execute("""SELECT distinct *
                    FROM trace
                    WHERE config_type = 'FIELD'
                """).df()
    print(df)
    print(type(df))

if True:
    df=conn.execute("""SELECT distinct concat(path, '/', field_tag)
                    FROM snooper
                    LIMIT 10
                """).df()
    print(df)
    print("")

    print("trace")
    df=conn.execute("""SELECT distinct concat(root_xpath, '/', element_tag)
                    FROM trace
                    WHERE config_type = 'FIELD'
                """).df()
    print(df)

if False:
    df=conn.execute("""select distinct s.path, concat(t.root_xpath, t.element_tag)
                   from snooper s
                   join trace t on  s.path = t.root_xpath  and s.field_tag = t.element_tag
                   WHERE t.config_type = 'FIELD'
                """).df()
    print("join")
    print(df.to_string())



