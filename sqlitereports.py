"""
A command line tool to generate reports from a SQLite database.
The tool ingests CSV files and generates a schema for the database based on columns in the CSV files.
"""
import click
import csv
import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


