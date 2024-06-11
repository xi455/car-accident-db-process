from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, DECIMAL

Base = declarative_base()

# 定义UnitName模型
class UnitName(Base):
    __tablename__ = 'unit_name'
    __table_args__ = {'comment': '處理單位名稱警局層表'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    處理單位名稱警局層 = Column(String(10), nullable=False)

    def __repr__(self):
        return f"<UnitName(處理單位名稱警局層='{self.處理單位名稱警局層}')>"

# 定义VehicleType模型
class VehicleType(Base):
    __tablename__ = 'vehicle_type'
    __table_args__ = {'comment': '當事者區分_類別_大類別名稱_車種表'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    當事者區分_類別_大類別名稱_車種 = Column(String(15), nullable=False)

    def __repr__(self):
        return f"<VehicleType(當事者區分_類別_大類別名稱_車種='{self.當事者區分_類別_大類別名稱_車種}')>"



# 主表 model 定義
# AccidentRecords Model
class AccidentRecords(Base):
    __tablename__ = 'accident_records'
    id = Column(Integer, primary_key=True)
    發生年度 = Column(String(4))
    發生月份 = Column(String(2))
    發生日期 = Column(String(8))
    發生時間 = Column(String(6))
    事故類別名稱 = Column(String(2))
    處理單位名稱警局層 = Column(Integer, ForeignKey('unit_name.id'))
    發生地點 = Column(String(80))
    天候名稱 = Column(String(3))
    光線名稱 = Column(String(20))
    經度 = Column(DECIMAL(9, 6))
    緯度 = Column(DECIMAL(9, 6))

    def __str__(self):
        return self.發生地點


# PartyInfo Model
class PartyInfo(Base):
    __tablename__ = 'party_info'
    id = Column(Integer, primary_key=True)
    accident_id = Column(Integer, ForeignKey('accident_records.id'))
    當事者區分_類別_大類別名稱_車種 = Column(Integer, ForeignKey('vehicle_type.id'), nullable=True)
    當事者性別名稱 = Column(String(15))
    當事者事故發生時年齡 = Column(Integer)
    保護裝備名稱 = Column(String(25))
    當事者行動狀態子類別名稱 = Column(String(10))
    車輛撞擊部位子類別名稱_最初 = Column(String(10))
    車輛撞擊部位大類別名稱_其他 = Column(String(25))
    車輛撞擊部位子類別名稱_其他 = Column(String(10))

    def __str__(self):
        return self.保護裝備名稱


# CauseAnalysis Model
class CauseAnalysis(Base):
    __tablename__ = 'cause_analysis'
    id = Column(Integer, primary_key=True)
    accident_id = Column(Integer, ForeignKey('accident_records.id'))
    肇因研判大類別名稱_主要 = Column(String(15))
    肇因研判子類別名稱_主要 = Column(String(25))
    肇因研判子類別名稱_個別 = Column(String(25))
    肇事逃逸類別名稱_是否肇逃 = Column(String(2))

    def __str__(self):
        return self.肇因研判大類別名稱_主要


# TrafficFacilities Model
class TrafficFacilities(Base):
    __tablename__ = 'traffic_facilities'
    id = Column(Integer, primary_key=True)
    accident_id = Column(Integer, ForeignKey('accident_records.id'))
    號誌_號誌種類名稱 = Column(String(20))
    號誌_號誌動作名稱 = Column(String(3))

    def __str__(self):
        return self.號誌_號誌種類名稱


# RoadConditions Model
class RoadConditions(Base):
    __tablename__ = 'road_conditions'
    id = Column(Integer, primary_key=True)
    accident_id = Column(Integer, ForeignKey('accident_records.id'))
    道路型態大類別名稱 = Column(String(4))
    道路型態子類別名稱 = Column(String(10))
    道路型態子類別名稱 = Column(String(4))
    路面狀況_路面鋪裝名稱 = Column(String(4))
    路面狀況_路面狀態名稱 = Column(String(2))
    路面狀況_路面缺陷名稱 = Column(String(10))
    道路障礙_障礙物名稱 = Column(String(10))
    道路障礙_視距品質名稱 = Column(String(10))
    道路障礙_視距名稱 = Column(String(10))

    def __str__(self):
        return self.道路型態大類別名稱
