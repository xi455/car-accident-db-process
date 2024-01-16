import base64
import os
from io import BytesIO
from pathlib import Path

import boto3
import environ
from botocore.exceptions import NoCredentialsError
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

env = environ.Env()
env_file = Path(__file__).parent / ".env"

if env_file.exists():
    env.read_env()

class DBServerConnectione:
    def __init__(self, user, password, host, port, dbname, server) -> None:        
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
        if self.server == "sqlserver":
            driver = "ODBC Driver 17 for SQL Server"
            engine_url = f"mssql+pyodbc://{self.user}:{self.pwd}@{self.host}:{self.port}/{self.dbname}?driver={driver}"
        
        if self.server == "postgresql":
            engine_url = f"postgresql://{self.user}:{self.pwd}@{self.host}:{self.port}/{self.dbname}"  # 定義數據庫引擎的 URL

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
        

class PictureProcess:
    def __init__(self, path) -> None:
        self.path = path

    @property
    def get_path(self):
        return self.path

    def picture_process(self, picture_name, type=None):
        photo_path = os.path.join(self.get_path, "LostAndFound", picture_name)
        # photo_path = os.path.join(self.get_path, picture_name)

        # 檢查檔案是否存在
        if os.path.exists(photo_path):
            print(f"尚未處理照片路徑: {photo_path}")

            picture_base64 = self.picture_base64_process(photo_path)

            if type:
                picture_name = picture_name[0:-5] + f"_1.{type}"

            return picture_name, picture_base64

    def picture_base64_process(self, photo_path):
        # 讀取照片並轉換成 Base64
        with open(photo_path, 'rb') as image_file:
            # 讀取圖片二進位數據
            image_binary = image_file.read()
            # 將二進位數據轉換成 Base64 字串
            base64_encoded = base64.b64encode(image_binary).decode('utf-8')

        return base64_encoded

    def output_picture(self, output_path, picture_name, base64_encoded):        
        # 檢查 output_path 目錄是否存在，如果不存在就創建
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # 寫入新的圖片檔案
        with open(f"{output_path}/{picture_name}", 'wb') as new_image_file:
            new_image_file.write(base64.b64decode(base64_encoded))

        # 檢查新圖片是否存在
        if os.path.exists(f"{output_path}/{picture_name}"):
            return f"新圖片 {picture_name} 成功生成！"
        else:
            return f"新圖片 {picture_name} 生成失敗。"
        
    def upload_to_s3(self, phote_name, phote_base64):
        session = boto3.Session(
            aws_access_key_id=env("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=env("AWS_SECRET_ACCESS_KEY"),
            region_name=env("AWS_ACCESS_NAME"),
        )
        s3 = session.client("s3", endpoint_url=env("AWS_ACCESS_URL"))

        try:
            # 將 Base64 字串轉換為 BytesIO 類型，以便上傳至 S3
            byte_data = BytesIO(base64.b64decode(phote_base64))

            # 上傳檔案至 S3 存儲桶
            s3.put_object(Body=byte_data, Bucket=env("AWS_STORAGE_BUCKET_NAME"), Key=f"found_picture/{phote_name}")
            print(f"照片 {phote_name} 成功上傳至 S3 存儲桶 {env("AWS_STORAGE_BUCKET_NAME")}")
        except FileNotFoundError:
            print(f"找不到檔案 {phote_name}")
        except NoCredentialsError:
            print("AWS 認證資訊不正確")




# example
# test = DBServerConnectione(
#     user=env("SQLSERVER_USER"),
#     password=env("SQLSERVER_PASSWORD"),
#     host=env("SQLSERVER_HOST"),
#     port=env("SQLSERVER_PORT"),
#     dbname=env("SQLSERVER_DBNAME"),
#     server="sqlserver"
# )

# picture_object = PictureProcess(os.path.join(os.path.expanduser("~"), "Downloads"))
# print(picture_object.get_path)
            
# query = test.session.query(test.get_db_class.Found).filter_by(Id="6124").first()
# phote_name = query.picture.split("\\")[-1]
# phote_name = "9e947315-1d55-4d3c-b228-1606793c97d4.jpeg"
# phote_name, phote_base64 = picture_object.picture_process(phote_name, type="png")

# phote_name = "1236.png"
# picture_object.output_picture(output_path="static", picture_name=phote_name, base64_encoded=phote_base64)
# picture_object.upload_to_s3(phote_name=phote_name, phote_base64=phote_base64)