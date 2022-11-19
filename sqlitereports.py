#!/usr/bin/env python3

"""
A command line tool to generate reports from a SQLite database.
The tool ingests CSV files and generates a schema for the database based on columns in the CSV files.
"""
import click
import csv
import sqlite3
import glob
import tempfile

DEFAULT_DB = "databases/data.db"
REPORTS = "reports"

# return all of full paths to all csv files in the reports directory
def get_csv_files(reports=REPORTS):
    # iterate through the csv files
    for csv_file in glob.glob(f"{reports}/*.csv"):
        # yield the csv file
        yield csv_file


# build a function that converts the header name with spaces to a header name with underscores
def convert_header_name(header_name):
    # return the header name with underscores
    return header_name.replace(" ", "_")


# build a function to convert the schema of a dollar amount to a float for two columns
# pylint: disable=dangerous-default-value
def convert_dollar_amount_to_float(
    db=DEFAULT_DB, columns=["Commission_Earned", "Sales"]
):
    # create a connection to the sqlite database
    conn = sqlite3.connect(db)
    # create a cursor object
    c = conn.cursor()
    # iterate through the columns
    for column in columns:
        # update the column to be a float
        c.execute(f"UPDATE data SET {column} = REPLACE({column}, '$', '')")
        c.execute(f"UPDATE data SET {column} = REPLACE({column}, ',', '')")
        c.execute(f"UPDATE data SET {column} = CAST({column} AS FLOAT)")
    # commit the changes to the database
    conn.commit()
    # close the connection to the database
    conn.close()


# build a function that returns an in memory csv file from combined csv files
def get_combined_csv_file(reports=REPORTS):
    # create a new file object in temp location and delete it when done
    combined_csv_file = tempfile.NamedTemporaryFile(mode="w", delete=True)
    # create a csv writer object
    csv_writer = csv.writer(combined_csv_file)
    # iterate through the csv files
    for csv_file in get_csv_files(reports):
        # open the csv file
        with open(csv_file, encoding="utf-8-sig") as f:
            # create a csv reader object
            csv_reader = csv.reader(f)
            # iterate through the csv reader object
            for row in csv_reader:
                # write the row to the combined csv file
                csv_writer.writerow(row)
    # return the combined csv file
    return combined_csv_file


# build a function that import the combined csv files into a sqlite database
# the first row of the csv file is the header and the rest of the rows are the data
def import_csv_to_sqlite(db=DEFAULT_DB, reports=REPORTS):
    # create a connection to the sqlite database
    conn = sqlite3.connect(db)
    # create a cursor object
    c = conn.cursor()
    # get the combined csv file
    combined_csv_file = get_combined_csv_file(reports)
    # open the combined csv file
    with open(combined_csv_file.name, encoding="utf-8-sig") as f:
        # create a csv reader object
        csv_reader = csv.reader(f)
        # get the header and clean it to remove spaces
        header = [convert_header_name(h) for h in next(csv_reader)]
        # create a table name
        table_name = "data"
        # create a table
        c.execute(f"CREATE TABLE {table_name} ({','.join(header)})")
        # iterate through the csv reader object
        for row in csv_reader:
            # insert the row into the table
            c.execute(
                f"INSERT INTO {table_name} VALUES ({','.join('?' * len(row))})", row
            )
    # commit the changes to the database
    conn.commit()
    # close the connection to the database
    conn.close()
    # convert the dollar amount to a float
    convert_dollar_amount_to_float(db)


# build a function that returns the schema of the database
def get_schema(db=DEFAULT_DB):
    # create a connection to the sqlite database
    conn = sqlite3.connect(db)
    # create a cursor object
    c = conn.cursor()
    # get the schema of the database
    schema = c.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall()
    # close the connection to the database
    conn.close()
    # return the schema
    return schema


# build a function that returns the the top revenue generating products "Title" and "Commission_Earned" and a limit of 10
def get_top_revenue_generating_products(db=DEFAULT_DB, limit=10):
    # create a connection to the sqlite database
    conn = sqlite3.connect(db)
    # create a cursor object
    c = conn.cursor()
    # get the top revenue generating products
    top_revenue_generating_products = c.execute(
        f"""
        SELECT Title, Commission_Earned
        FROM data
        ORDER BY Commission_Earned DESC
        LIMIT {limit}
        """
    ).fetchall()
    # close the connection to the database
    conn.close()
    # return the top revenue generating products
    return top_revenue_generating_products


# build a click group
@click.group()
def cli():
    """A command line tool to generate reports from a SQLite database."""


@cli.command("sales")
@click.option("--db", default=DEFAULT_DB, help="The database to use.")
@click.option(
    "--limit",
    default=10,
    help="The number of top revenue generating products to return.",
)
def sales(db, limit):
    """Generate a sales report."""
    # get the top revenue generating products
    top_revenue_generating_products = get_top_revenue_generating_products(db, limit)
    # print the top revenue generating products different color for product name and different colore for revenue using click color
    for product in top_revenue_generating_products:
        click.echo(
            click.style(product[0], fg="yellow")
            + " - "
            + click.style(str(product[1]), fg="blue")
        )


@cli.command("schema")
@click.option("--db", default=DEFAULT_DB, help="The database to use.")
def schemacli(db):
    """Print the schema of the database."""
    # get the schema of the database
    schema = get_schema(db)
    # print the schema
    print(schema)


# build a click command to import csv files into a sqlite database
@cli.command("import")
@click.option(
    "--db", default=DEFAULT_DB, help="The database to import the CSV files into."
)
@click.option(
    "--reports",
    default=REPORTS,
    help="The directory containing the CSV files to import.",
)
def import_csv_files(reports, db):
    """Import CSV files from the reports directory into a SQLite database."""
    # import the csv files into the sqlite database
    # print colored text importing csv files into sqlite database and the database
    print(f"Importing CSV files into SQLite database {db}... with reports {reports}")
    # import the csv files into the sqlite database
    import_csv_to_sqlite(db, reports)


# build a click command
@cli.command("printcsv")
@click.option(
    "--reports", default=REPORTS, help="The directory containing the CSV files."
)
def print_csv(reports):
    """Print the combined CSV file."""
    # get the combined csv file
    combined_csv_file = get_combined_csv_file(reports)
    # open the combined csv file
    with open(combined_csv_file.name, encoding="utf-8") as f:
        # create a csv reader object
        csv_reader = csv.reader(f)
        # iterate through the csv reader object
        for row in csv_reader:
            # print the row
            print(row)


# instantiate the click group
if __name__ == "__main__":
    cli()
