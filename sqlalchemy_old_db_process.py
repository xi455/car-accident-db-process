from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from pathlib import Path
import environ

env = environ.Env()
env_file = Path(__file__).parent / ".env"

if env_file.exists():
    env.read_env()

user = env("SQLSERVER_USER")  # 帳號
pwd = env("SQLSERVER_PASSWORD")  # 密碼
host = env("SQLSERVER_HOST")  # 資料庫主機位置(名稱)
port = env("SQLSERVER_PORT")  # 連接阜
dbname = env("SQLSERVER_DBNAME")  # db名稱
driver = "ODBC Driver 17 for SQL Server"
conn_str = f"mssql+pyodbc://{user}:{pwd}@{host}:{port}/{dbname}?driver={driver}"

print("conn_str", conn_str)
engine = create_engine(conn_str)  # sql 連線

Session = sessionmaker(bind=engine)  # 創建一個與數據庫的會話對象
session = Session()

# 我們使用 automap_base() 創建了基底類 Base，並通過 Base.prepare(engine, reflect=True) 自動映射現有的資料庫結構。
# 這樣一來，Base 將自動為資料庫中的每個資料表創建一個對應的模型類。
Base = automap_base()
Base.prepare(engine, reflect=True)

# 透過 Base.classes 屬性來獲取這些自動映射的模型類
db_class = Base.classes
print(dir(db_class))
print("db_class:", db_class)