import pandas as pd
from sqlalchemy import create_engine

import config

# db var
DBHOST = config.DBHOST
DBUSER = config.DBUSER
DBPASSWORD = config.DBPASSWORD
DBNAME = config.DBNAME
TABLES = config.TABLES
TBNAME = 'reactions'


def sql_read_frame(DBUSER, DBPASSWORD, DBNAME, TBNAME):
    engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user=DBUSER, pw=DBPASSWORD, db=DBNAME, pool_recycle=3600))
    # recycle: – If set to a value other than -1, number of seconds between connection recycling,
    # which means upon checkout, if this timeout is surpassed the connection will be closed and
    # replaced with a newly opened connection. Defaults to -1.

    db_connection = engine.connect()

    df = pd.read_sql(f"select * from {DBNAME}.{TBNAME}", db_connection)

    # pd.set_option('display.expand_frame_repr', False)
    # allows for the representation of dataframes to stretch across pages, wrapped over the full column vs row-wise.
    # print(df)

    df.to_csv(f'{TBNAME}.csv', encoding='utf_8_sig')

    db_connection.close()

sql_read_frame(DBUSER, DBPASSWORD, DBNAME, TBNAME)




