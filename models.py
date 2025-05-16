from sqlalchemy import Column, String, ARRAY, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from database import Base

class Trademark(Base):
    __tablename__ = "trademarks"

    applicationNumber = Column(String, primary_key=True)
    productName = Column(String)
    productNameEng = Column(String)
    applicationDate = Column(String)
    registerStatus = Column(String)
    publicationNumber = Column(String)
    publicationDate = Column(String)
    registrationNumber = Column(ARRAY(String))
    registrationDate = Column(ARRAY(String))
    registrationPubNumber = Column(String)
    registrationPubDate = Column(String)
    internationalRegDate = Column(String)
    internationalRegNumbers = Column(ARRAY(String))
    priorityClaimNumList = Column(ARRAY(String))
    priorityClaimDateList = Column(ARRAY(String))
    asignProductMainCodeList = Column(ARRAY(String))
    asignProductSubCodeList = Column(ARRAY(String))
    viennaCodeList = Column(ARRAY(String))

    # 검색 성능을 위한 인덱스 정의
    __table_args__ = (
        Index('idx_product_name', 'productName'),
        Index('idx_product_name_eng', 'productNameEng'),
        Index('idx_application_date', 'applicationDate'),
        Index('idx_register_status', 'registerStatus'),
    )

    def __repr__(self):
        return f"<Trademark(applicationNumber={self.applicationNumber}, productName={self.productName})>"
