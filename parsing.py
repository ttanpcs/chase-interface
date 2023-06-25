from os import system
from json import load, dump
import re
from models import Statement, Transaction
import pandas as pd
from datetime import datetime

def read_from_mapping(regex_map_path):
    with open(regex_map_path, 'r') as f:
        data = load(f)
        return data

def write_to_mapping(regex_map_path, regex_map):
    with open(regex_map_path, "w") as outfile:
        dump(regex_map, outfile)

def find_new_files(directory, type, session):
    new_files = []
    for path in directory.glob("*.csv"):
        if session.query(Statement.name).filter(Statement.name == str(path.name), Statement.type == type).scalar() is None:
            new_files.append(path)
    return new_files

def determine_type(description, date, session, default, regex_map):
    # Avoid duplicate transactions across different files
    if session.query(Transaction.id).filter(Transaction.description == description, Transaction.date == date.to_pydatetime()).all() != []:
        return "Drop"
    
    # Check for regex rules
    for label in regex_map:
        if re.search("|".join(regex_map[label]), description) is not None:
            return label

    # Manual user input if default is not set
    if default is None:
        system('cls')
        print({i: list(regex_map.keys())[i] for i in range(len(regex_map))})
        print(description)
        label_index = input()
        while not (label_index.isdigit() and int(label_index) < len(regex_map) and int(label_index) > -1):
            label_index = input()
        label_index = int(label_index)
        print("Add label? (y/n)")
        choice = input()
        if choice == 'y':
            print("Type new search term:")
            new_term = input()
            regex_map[list(regex_map.keys())[label_index]].append(new_term)

        return list(regex_map.keys())[label_index]
    else:
        return default

def read_files(files, default, session, regex_map, dropped_columns, renamed_map, transaction_type):
    format = '%m/%d/%Y'
    def re_type(description, date):
        return determine_type(description, date, session, default, regex_map)

    def re_date(unformatted_date):
        return datetime.strptime(unformatted_date, format)

    for f in files:
        df = pd.read_csv(str(f), index_col=False)
        df.drop(columns=dropped_columns, inplace=True)
        df.rename(columns=renamed_map, inplace=True)
        df['Date'] = df['Date'].map(re_date)
        df['Type'] = list(map(re_type, df['Description'], df['Date']))

        df.drop(df[(df['Type'] == 'Drop')].index , inplace=True)
        current_statement = Statement(name = f.name, type = transaction_type)
        session.add(current_statement)
        df.to_sql('transactions', session.bind, if_exists="append", index=False) # Need to do something instead of to_sql that checks for if records already exist
        session.commit()

def read_credit_files(credit_file_path, default, session, regex_map):
    credit_files = find_new_files(credit_file_path, "credit", session)
    read_files(
        credit_files,
        default,
        session,
        regex_map,
        ['Transaction Date', 'Category', 'Type', 'Memo'],
        {'Post Date' : 'Date'},
        "credit"
    )

def read_debit_files(debit_file_path, default, session, regex_map):
    debit_files = find_new_files(debit_file_path, "debit", session)
    read_files(
        debit_files,
        default,
        session,
        regex_map,
        ['Details', 'Type', 'Balance', 'Check or Slip #'],
        {'Posting Date' : 'Date'},
        "debit"
    )

def parse_files(mapping, credit_file_path, debit_file_path, default, session):
    regex_map = read_from_mapping(mapping)
    read_credit_files(credit_file_path, default, session, regex_map)
    read_debit_files(debit_file_path, default, session, regex_map)
    write_to_mapping(mapping, regex_map)
