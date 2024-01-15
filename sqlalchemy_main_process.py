from sqlalchemy import create_engine, update
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from django.contrib.auth.models import Group

import sqlalchemy_old_db_process as sqlalchemy_old_db_process

from pathlib import Path
import environ

env = environ.Env()
env_file = Path(__file__).parent / ".env"

if env_file.exists():
    env.read_env()

group = Group.objects.get(name="General_Affairs_Office")
user = env("POSTGRES_USER")  # 帳號
pwd = env("POSTGRES_PASSWORD")  # 密碼
host = env("POSTGRES_HOST")  # 資料庫主機位置(名稱)
port = env("POSTGRES_PORT")  # 連接阜
dbname = env("POSTGRES_DBNAME")  # db名稱

engine_url = f"postgresql://{user}:{pwd}@{host}:{port}/{dbname}"  # 定義數據庫引擎的 URL

engine = create_engine(engine_url)  # 創建數據庫引擎, echo 為將這期間的 log 日誌打印出來

Session = sessionmaker(bind=engine)  # 創建一個與數據庫的會話對象
session = Session()

# 我們使用 automap_base() 創建了基底類 Base，並通過 Base.prepare(engine, reflect=True) 自動映射現有的資料庫結構。
# 這樣一來，Base 將自動為資料庫中的每個資料表創建一個對應的模型類。
Base = automap_base()
Base.prepare(engine, reflect=True)

# 透過 Base.classes 屬性來獲取這些自動映射的模型類
Mytabe = Base.classes.losses_found

data_id = list()
found_have_id = list()

querys = session.query(Mytabe).all()
for query in querys:
    data_id.append(query.id)

found_have_id += data_id

def found_update():
    Mytable2 = sqlalchemy_old_db_process.db_class.Found

    for i in data_id:
        query = (
            sqlalchemy_old_db_process.session.query(Mytable2).filter_by(Id=i).first()
        )
        u = (
            update(Mytabe)
            .where(Mytabe.id == i)
            .values(
                found_count=query.count,
                found_date=query.date,
                found_name=query.item_name,
                handler=query.handler,
                is_found=query.isScrap,
                is_picture_show=query.isPictureShow,
                is_show=query.isShow,
                name=query.name,
                phone=query.phone,
                scrap_place=query.location,
                student_id=query.studentid,
                unit=query.unit,
                annotation=query.exterior,
            )
        )
        session.execute(u)

    session.commit()
    session.close()

    found_add()


def found_add():
    Mytable2 = sqlalchemy_old_db_process.db_class.Found
    result2 = sqlalchemy_old_db_process.session.query(Mytable2).all()

    for res in result2:
        if res.Id in data_id:
            continue

        data_obj = {
            "id": res.Id,
            "group_id_id": group.id,
            "found_count": res.count,
            "found_date": res.date,
            "found_name": res.item_name,
            "handler": res.handler,
            "is_found": res.isScrap,
            "picture": "未輸入",
            "is_picture_show": res.isPictureShow,
            "is_show": res.isShow,
            "name": res.name,
            "phone": res.phone,
            "scrap_place": res.location,
            "student_id": res.studentid,
            "unit": res.unit,
            "annotation": res.exterior,
        }
        found_have_id.append(res.Id)
        session.add(Mytabe(**data_obj))
        session.commit()
    session.close()

    global Mytabe_register
    Mytabe_register = Base.classes.losses_register
    receive_add()


def receive_add():
    Mytable2 = sqlalchemy_old_db_process.db_class.Receive
    result2 = sqlalchemy_old_db_process.session.query(Mytable2).all()

    receive_id = []
    for res in result2:
        if res.itemID not in receive_id and res.itemID in found_have_id:
            if (
                "一" in res.unit
                or "二" in res.unit
                or "三" in res.unit
                or "四" in res.unit
                or "五" in res.unit
                or "六" in res.unit
            ):
                ident = "學生"
            elif "系" in res.unit or "組" in res.unit or "室" in res.unit:
                ident = "老師"
            else:
                ident = "其他"

            data_obj = {
                "found_id_id": res.itemID,
                "handler": res.handler,
                "ident": ident,
                "name": res.name,
                "phone": res.phone,
                "register_date": res.date,
                "student_id": res.studentID,
                "unit": res.unit,
            }
            session.add(Mytabe_register(**data_obj))
            session.commit()
            receive_id.append(res.itemID)
    session.close()
