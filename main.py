import os
from pathlib import Path

import environ
from sqlalchemy import update

from Base import DBServerConnectione, PictureProcess

env = environ.Env()
env_file = Path(__file__).parent / ".env"

if env_file.exists():
    env.read_env()

sqlserver_object = DBServerConnectione(
    user=env("SQLSERVER_USER"),
    password=env("SQLSERVER_PASSWORD"),
    host=env("SQLSERVER_HOST"),
    port=env("SQLSERVER_PORT"),
    dbname=env("SQLSERVER_DBNAME"),
    server="sqlserver",
)

postgresql_object = DBServerConnectione(
    user=env("POSTGRES_USER"),
    password=env("POSTGRES_PASSWORD"),
    host=env("POSTGRES_HOST"),
    port=env("POSTGRES_PORT"),
    dbname=env("POSTGRES_DBNAME"),
    server="postgresql",
)

# Found----------------------
sql_server_idcorrespond_dict = dict()


def found_handle():
    queryset = sqlserver_object.session.query(sqlserver_object.get_db_class.Found).all()
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    phote_process = PictureProcess(downloads_path)

    for index, query in enumerate(queryset):

        if query.picture:
            phote_name = query.picture.split("\\")[-1]
            phote_name, phote_base64 = phote_process.picture_process(
                phote_name, type="png"
            )
            phote_process.upload_to_s3(phote_name=phote_name, phote_base64=phote_base64)
            phote_name = f"found_picture/{phote_name}"
        else:
            phote_name = None

        sql_server_idcorrespond_dict[query.Id] = index + 935

        data_obj = {
            "found_date": query.date,
            "scrap_place": query.location,
            "unit": query.unit,
            "student_id": query.studentid,
            "name": query.name,
            "phone": query.phone,
            "handler": query.handler,
            "annotation": query.exterior,
            "found_name": query.item_name,
            "found_count": query.count,
            "picture": phote_name,
            "is_found": query.isScrap,
            "is_show": query.isShow,
            "is_picture_show": query.isPictureShow,
            "group_id_id": 1,
        }

        postgresql_object.session.add(
            postgresql_object.get_db_class.losses_found(**data_obj)
        )
        postgresql_object.session.commit()

# found_handle()


# Receive--------------------
def ident_assort(query):
    unit = query.unit
    if (
        "一" in unit
        or "二" in unit
        or "三" in unit
        or "四" in unit
        or "五" in unit
        or "六" in unit
    ):
        ident = "學生"
    elif "系" in unit or "組" in unit or "室" in unit:
        ident = "老師"
    else:
        ident = "其他"

    return ident


def Receive_handle():
    queryset = sqlserver_object.session.query(
        sqlserver_object.get_db_class.Receive
    ).all()
    save_id_list = list()

    for query in queryset:
        if (
            query.itemID not in sql_server_idcorrespond_dict
            or query.itemID in save_id_list
        ):
            continue

        itemID = sql_server_idcorrespond_dict[query.itemID]
        save_id_list.append(query.itemID)
        ident = ident_assort(query)

        data_obj = {
            "found_id_id": itemID,
            "handler": query.handler,
            "handler_email": query.writeID,
            "ident": ident,
            "name": query.name,
            "phone": query.phone,
            "register_date": query.date,
            "student_id": query.studentID,
            "unit": query.unit,
        }

        print(data_obj)
        postgresql_object.session.add(
            postgresql_object.get_db_class.losses_register(**data_obj)
        )
        postgresql_object.session.commit()

# Receive_handle()


def found_data_update():
    Found_old_queryset = sqlserver_object.session.query(
        sqlserver_object.get_db_class.Found
    ).all()
    Found_new_queryset = postgresql_object.session.query(
        postgresql_object.get_db_class.losses_found
    ).all()

    objects_list = list()
    for query in Found_old_queryset:
        if query.ScrapDeal:
            objects_list.append(query)

    lf_table = postgresql_object.get_db_class.losses_found

    for query in Found_new_queryset:
        for old_query in objects_list:
            if (
                query.scrap_place == old_query.location
                and query.name == old_query.name
                and query.found_name == old_query.item_name
            ):
                u = (
                    update(lf_table)
                    .where(lf_table.id == query.id)
                    .values(
                        scrap=old_query.ScrapDeal,
                        creation_scrap_datetime=old_query.ScrapDealTime,
                    )
                )
                postgresql_object.session.execute(u)

        postgresql_object.session.commit()