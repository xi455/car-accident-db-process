import environ

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from pathlib import Path

from models import Base

env = environ.Env()
env_file = Path(__file__).parent / ".env"

if env_file.exists():
    env.read_env()

class DBServerConnectione:
    def __init__(self, dbname, server, user=None, password=None, host=None, port=None) -> None:        
        self.user = user
        self.pwd = password
        self.host = host
        self.port = port
        self.dbname = dbname
        self.server = server
    
    @property
    def engine(self):
        if not hasattr(self, "_engine"):
            self._engine = self.connection()
        
        return self._engine
    
    @property
    def session(self):
        if not hasattr(self, "_session"):
            Session = sessionmaker(bind=self.engine)  # 創建一個與數據庫的會話對象
            session = Session()
            self._session = session

        return self._session

    def connection(self):
        if self.server == "sqlite":
            engine_url = f"sqlite:///{self.dbname}"

        engine = create_engine(engine_url)  # 創建數據庫引擎, echo 為將這期間的 log 日誌打印出來

        return engine

    @property
    def get_connection_info(self):
        return {
            'server': self.server,
            'user': self.user,
            'password': self.pwd,
            'host': self.host,
            'port': self.port,
            'dbname': self.dbname
        }
    
    @property
    def get_db_class(self):
        Base = automap_base()
        Base.prepare(self.engine, reflect=True)

        return Base.classes
    
    @property
    def drop_and_init_table(self):
        """
        Drops all tables in the database.

        This method uses SQLAlchemy's MetaData object to reflect the existing tables
        in the database and then drops them using the drop_all() method.

        Returns:
            None
        """
        metadata = MetaData()
        metadata.reflect(bind=self.engine)

        if metadata.tables:
            metadata.drop_all(bind=self.engine)
            print("All tables have been dropped.")

        Base.metadata.create_all(self.engine)
        print("All tables have been created.")