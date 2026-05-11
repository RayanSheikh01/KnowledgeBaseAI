from sqlalchemy import Column, DateTime, Integer, String

class Base(sqlalchemy.orm.declarative_base()):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    source_type = Column(String, index=True)
    source_uri = Column(String, index=True)
    content_hash = Column(String, index=True)
    chunk_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow, timezone=True)
