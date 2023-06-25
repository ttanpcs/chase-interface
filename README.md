## Chase Interface
### Inspiration and Overview
Chase allows users to download bank statements in simple csv formats. Unfortunately, simple csvs are simply cancer to the eyes. The Chase interface is an app which intelligently conglomerates past credit and debit statements into an easily understandable Dash HTML frontend including charts and tables with statistics ranging from summaries to trends. 

### Installation
First install python and setup a virtual env named venv. Then activate the environment and install the following python libraries:
- argparse
- pandas
- dash
- plotly
- sqlalchemy

### Functionality
Run with the command `python chase_interface.py`. There are various flags which are explained with the `--help` or `-h` flag. 