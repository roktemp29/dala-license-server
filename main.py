from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./licenses.db"  # temporary local DB

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

app = FastAPI()


# ---------------------------
# Database Model
# ---------------------------
class License(Base):
    __tablename__ = "licenses"

    license_key = Column(String, primary_key=True, index=True)
    device_id = Column(String, nullable=True)


Base.metadata.create_all(bind=engine)


# ---------------------------
# Request Model
# ---------------------------
class LicenseRequest(BaseModel):
    license_key: str
    device_id: str


# ---------------------------
# Validation Endpoint
# ---------------------------
@app.post("/validate")
def validate_license(data: LicenseRequest):
    db = SessionLocal()

    license = db.query(License).filter(License.license_key == data.license_key).first()

    if not license:
        db.close()
        return {"status": "invalid"}

    # If first time activation
    if not license.device_id:
        license.device_id = data.device_id
        db.commit()
        db.close()
        return {"status": "valid"}

    # If same device
    if license.device_id == data.device_id:
        db.close()
        return {"status": "valid"}

    # If different device
    db.close()
    return {"status": "denied"}