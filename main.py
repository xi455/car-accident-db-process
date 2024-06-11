import os
import pandas as pd
from pathlib import Path

import environ
from sqlalchemy import text, bindparam
from sqlalchemy.exc import SQLAlchemyError

from Base import DBServerConnectione


env = environ.Env()
env_file = Path(__file__).parent / ".env"

if env_file.exists():
    env.read_env()

# 定义模型和对应的字段
models = {
    'unit_name': ['id', '處理單位名稱警局層'],
    'vehicle_type': ['id', '當事者區分_類別_大類別名稱_車種'],
    'accident_records': ['發生年度', '發生月份', '發生日期', '發生時間', '事故類別名稱', '處理單位名稱警局層', '發生地點', '天候名稱', '光線名稱', '經度', '緯度'],
    'party_info': ['accident_id', '當事者區分_類別_大類別名稱_車種', '當事者性別名稱', '當事者事故發生時年齡', '保護裝備名稱', '當事者行動狀態子類別名稱', '車輛撞擊部位子類別名稱_最初', '車輛撞擊部位大類別名稱_其他', '車輛撞擊部位子類別名稱_其他'],
    'cause_analysis': ['accident_id', '肇因研判大類別名稱_主要', '肇因研判子類別名稱_主要', '肇因研判子類別名稱_個別', '肇事逃逸類別名稱_是否肇逃'],
    'traffic_facilities': ['accident_id', '號誌_號誌種類名稱', '號誌_號誌動作名稱'],
    'road_conditions': ['accident_id', '道路型態大類別名稱', '道路型態子類別名稱', '道路型態子類別名稱', '路面狀況_路面鋪裝名稱', '路面狀況_路面狀態名稱', '路面狀況_路面缺陷名稱', '道路障礙_障礙物名稱', '道路障礙_視距品質名稱', '道路障礙_視距名稱'],
}


class HandleSQLite(DBServerConnectione):
    
    def import_data(self, file_path, model, foreign_keys=None):
        df = pd.read_csv(file_path)

        # 查询和插入操作
        with self.engine.connect() as connection:            
            for _, row in df.iterrows():
                data = row.to_dict()

                if foreign_keys:
                    for key, table_name in foreign_keys.items():
                        if data[key]:
                            result = connection.execute(text(f"SELECT * FROM {table_name} WHERE id = :id"), {'id': data[key]}).fetchone()
                            if result:
                                data[key] = result.id
                            else:
                                data[key] = None
                        else:
                            data[key] = None

                # 动态生成插入语句
                column_names = ', '.join(data.keys())
                placeholders = ', '.join([f':{col}' for col in data.keys()])
                insert_statement = text(f"""
                    INSERT INTO {model} ({column_names}) 
                    VALUES ({placeholders})
                """).bindparams(*[bindparam(col, value=data[col]) for col in data.keys()])

                try:
                    print(_)
                    print(insert_statement)
                    connection.execute(insert_statement)
                except SQLAlchemyError as e:
                    print(f"Error occurred: {e}")
                    connection.rollback()
                else:
                    connection.commit()


    def handle(self, *args, **kwargs):

        # 子表 model 設定
        base_path = os.path.join(
            os.path.dirname(__file__), "fixtures/csv/subsidiary_table/",
        )

        data_parameters = {
            "unit_name": {"csv_file": "unit_name.csv", "foreign_keys": None},
            "vehicle_type": {"csv_file": "vehicle_type.csv", "foreign_keys": None},
        }

        for model, parameters in data_parameters.items():
            self.import_data(
                os.path.join(base_path, parameters["csv_file"]),
                model,
                parameters.get("foreign_keys"),
            )

        # 主表 model 設定
        base_path = os.path.join(
            os.path.dirname(__file__), "fixtures/csv/main_table/"
        )

        data_parameters = {
            "accident_records": {"csv_file": "accident_records.csv", "foreign_keys": {"處理單位名稱警局層": "unit_name"}},
            "cause_analysis": {"csv_file": "cause_analysis.csv", "foreign_keys": {"accident_id": "accident_records"}},
            "party_info": {"csv_file": "party_info.csv", "foreign_keys": {"accident_id": "accident_records", "當事者區分_類別_大類別名稱_車種": "vehicle_type",}},
            "road_conditions": {"csv_file": "road_conditions.csv", "foreign_keys": {"accident_id": "accident_records"}},
            "traffic_facilities": {"csv_file": "traffic_facilities.csv", "foreign_keys": {"accident_id": "accident_records"}},
        }

        for model, parameters in data_parameters.items():
            self.import_data(
                os.path.join(base_path, parameters["csv_file"]),
                model,
                parameters.get("foreign_keys"),
            )


sqlite_object = HandleSQLite(
    dbname=env("SQLITE_DBNAME"),
    server="sqlite",
)

sqlite_object.drop_and_init_table
sqlite_object.handle()