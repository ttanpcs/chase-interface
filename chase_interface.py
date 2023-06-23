import os
import argparse
from models import Base, Transaction
from pathlib import Path
from parsing import parse_files
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

basedir = Path(os.path.abspath(os.path.dirname(__file__)))
credit_path = basedir / 'credit_statements'
debit_path = basedir / 'debit_statements'
mapping_path = basedir / 'mapping.json'

def create_session(reset):
    engine = create_engine(f"sqlite:///{os.path.join(basedir, 'finances.sqlite')}")
    if reset:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind = engine)
    session = Session()

    return session

def generate():
    parser = argparse.ArgumentParser("chase-interface", description="generate sorted and prettified statements and statistics.")
    parser.add_argument("--credit", "-c", type=Path, default=credit_path, help="Credit card statement path")
    parser.add_argument("--debit", "-d", type=Path, default=debit_path, help="Debit card statement path")
    parser.add_argument("--mapping", "-m", type=Path, default=mapping_path, help="Regexes used to map categories")
    parser.add_argument("--default", type=str, default=None, help="Default category")
    parser.add_argument("--reset", "-r", action='store_true', help="Apply flag to reset database")
    args = parser.parse_args()
    session = create_session(args.reset)
    parse_files(args.mapping, args.credit, args.debit, args.default, session)

    # Summary statistics using plotly
    # then create summary statistics? / csvs from this information

if __name__ == "__main__":
    generate()