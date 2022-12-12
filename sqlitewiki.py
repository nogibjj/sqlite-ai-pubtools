#!/usr/bin/env python3
"""
Build a script that dumps the content of a wikipedia page into a sqlite database.
"""

import wikipedia
import click
import sqlite3


#build a function that queries the wikipedia api and returns the content of a page
def get_page_content(page_title):
    page = wikipedia.page(page_title)
    return page.content

#build a function that creates a sqlite database and a table
def create_db(db_name, table_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('CREATE TABLE {tn} (content TEXT)'.format(tn=table_name))
    conn.commit()
    conn.close()

#build a function that inserts the content of a page into the table
def insert_content(db_name, table_name, page_title):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('INSERT INTO {tn} VALUES (?)'.format(tn=table_name), (get_page_content(page_title),))
    conn.commit()
    conn.close()

#build a function that queries the database and returns the content of a page
def query_db(db_name, table_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('SELECT content FROM {tn}'.format(tn=table_name))
    content = c.fetchone()
    conn.close()
    return content

#build a function that deletes the database
def delete_db(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('DROP TABLE {tn}'.format(tn=table_name))
    conn.commit()
    conn.close()

@click.group()
def cli():
    """wiki to cli
    """


@cli.command("ingest")
@click.argument("page_title", default="Python (programming language)")
@click.argument("db_name", default="wiki.db")
@click.argument("table_name", default="wiki")
def ingest(page_title, db_name, table_name):
    """ingest a wikipedia page into a sqlite database
    """
    create_db(db_name, table_name)
    insert_content(db_name, table_name, page_title)
    print("Ingested page '{}' into database '{}' table '{}'".format(page_title, db_name, table_name))

@cli.command("query")
@click.argument("db_name", default="wiki.db")
@click.argument("table_name", default="wiki")
def query(db_name, table_name):
    """query a wikipedia page from a sqlite database
    """
    content = query_db(db_name, table_name)
    print(content)

@cli.command("delete")
@click.argument("db_name", default="wiki.db")
@click.argument("table_name", default="wiki")
def delete(db_name, table_name):
    """delete a wikipedia page from a sqlite database
    """
    delete_db(db_name)
    print("Deleted database '{}' table '{}'".format(db_name, table_name))

if __name__ == "__main__":
    cli()



