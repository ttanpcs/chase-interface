from os import system
from json import load, dump
import re
from models import Statement
import pandas as pd

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

def determine_type(transaction, regex_map):
    for label in regex_map:
        if re.search("|".join(regex_map[label]), transaction) is not None:
            return label
        
    system('cls')
    print({i: list(regex_map.keys())[i] for i in range(len(regex_map))})
    print(transaction)
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

def read_files(files, session, regex_map, dropped_columns, renamed_map, transaction_type):
    def re_type(transaction):
        return determine_type(transaction, regex_map)
    
    for f in files:
        df = pd.read_csv(str(f), index_col=False)
        df.drop(columns=dropped_columns, inplace=True)
        df.rename(columns=renamed_map, inplace=True)
        df['Type'] = df['Description'].map(re_type)
        current_statement = Statement(name = f.name, type = transaction_type)
        session.add(current_statement)
        df.to_sql('transactions', session.bind, if_exists="append", index=False)
    session.commit()

def read_credit_files(credit_file_path, session, regex_map):
    credit_files = find_new_files(credit_file_path, "credit", session)
    read_files(
        credit_files,
        session,
        regex_map,
        ['Transaction Date', 'Category', 'Type', 'Memo'],
        {'Post Date' : 'Date'},
        "credit"
    )

def read_debit_files(debit_file_path, session, regex_map):
    debit_files = find_new_files(debit_file_path, "debit", session)
    read_files(
        debit_files,
        session,
        regex_map,
        ['Details', 'Type', 'Balance', 'Check or Slip #'],
        {'Posting Date' : 'Date'},
        "debit"
    )

def parse_files(mapping, credit_file_path, debit_file_path, session):
    regex_map = read_from_mapping(mapping)
    read_credit_files(credit_file_path, session, regex_map)
    read_debit_files(debit_file_path, session, regex_map)
    write_to_mapping(mapping, regex_map)
