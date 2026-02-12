from fastapi import FastAPI, HTTPException, Query, Body
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey, inspect
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import io, csv, math

DB_URL = "sqlite:///./points.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class MeasurementDB(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    points = relationship("PointDB", back_populates="measurement", cascade="all, delete-orphan")

class PointDB(Base):
    __tablename__ = "points"
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, index=True, nullable=True)
    distancia = Column(Float, nullable=False, default=0.0)
    inclinacion = Column(Float, nullable=False, default=0.0)
    azimut = Column(Float, nullable=False, default=0.0)
    measurement_id = Column(Integer, ForeignKey("measurements.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    measurement = relationship("MeasurementDB", back_populates="points")

Base.metadata.create_all(bind=engine)

class MeasurementIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = None

class MeasurementOut(MeasurementIn):
    id: int
    created_at: datetime

class PointIn(BaseModel):
    label: Optional[str] = Field(None, description="Etiqueta opcional")
    distancia: float = Field(ge=0)
    inclinacion: float = Field(ge=-90, le=90)
    azimut: float = Field(ge=0, lt=360)
    measurement_id: Optional[int] = Field(None, description="ID de la medición")

class PointOut(PointIn):
    id: int
    created_at: datetime

class PageMeas(BaseModel):
    page: int
    pages: int
    total: int
    items: List[MeasurementOut]

class PagePoints(BaseModel):
    page: int
    pages: int
    total: int
    items: List[PointOut]

app = FastAPI(title="TFG App Backend")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health():
    return {"status":"ok","ts": datetime.utcnow().isoformat()+"Z"}

# Measurements
@app.post("/measurements", response_model=MeasurementOut)
def create_measurement(m: MeasurementIn = Body(...)):
    with SessionLocal() as db:
        exists = db.query(MeasurementDB).filter(MeasurementDB.name == m.name).first()
        if exists: raise HTTPException(400, "Ya existe una medición con ese nombre")
        obj = MeasurementDB(name=m.name, description=m.description)
        db.add(obj); db.commit(); db.refresh(obj)
        return MeasurementOut(id=obj.id, name=obj.name, description=obj.description, created_at=obj.created_at)

@app.get("/measurements/{mid}", response_model=MeasurementOut)
def get_measurement(mid: int):
    with SessionLocal() as db:
        obj = db.get(MeasurementDB, mid)
        if not obj: raise HTTPException(404, "Measurement not found")
        return MeasurementOut(id=obj.id, name=obj.name, description=obj.description, created_at=obj.created_at)

@app.put("/measurements/{mid}", response_model=MeasurementOut)
def update_measurement(mid: int, m: MeasurementIn = Body(...)):
    with SessionLocal() as db:
        obj = db.get(MeasurementDB, mid)
        if not obj: raise HTTPException(404, "Measurement not found")
        if m.name != obj.name:
            dup = db.query(MeasurementDB).filter(MeasurementDB.name == m.name).first()
            if dup: raise HTTPException(400, "Ya existe una medición con ese nombre")
        obj.name, obj.description = m.name, m.description
        db.commit(); db.refresh(obj)
        return MeasurementOut(id=obj.id, name=obj.name, description=obj.description, created_at=obj.created_at)

@app.delete("/measurements/{mid}")
def delete_measurement(mid: int):
    with SessionLocal() as db:
        obj = db.get(MeasurementDB, mid)
        if not obj: raise HTTPException(404, "Measurement not found")
        db.delete(obj); db.commit()
        return JSONResponse({"deleted": mid})

@app.get("/measurements", response_model=PageMeas)
def list_measurements(page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200), q: Optional[str] = Query(None)):
    with SessionLocal() as db:
        query = db.query(MeasurementDB)
        if q: query = query.filter(MeasurementDB.name.ilike(f"%{q}%"))
        total = query.count()
        pages = max(1, math.ceil(total / limit))
        items = query.order_by(MeasurementDB.id.desc()).offset((page - 1) * limit).limit(limit).all()
        out = [MeasurementOut(id=o.id, name=o.name, description=o.description, created_at=o.created_at) for o in items]
        return PageMeas(page=page, pages=pages, total=total, items=out)

# Points
@app.post("/points", response_model=PointOut)
def create_point(p: PointIn = Body(...)):
    with SessionLocal() as db:
        if p.measurement_id is not None and not db.get(MeasurementDB, p.measurement_id):
            raise HTTPException(400, "measurement_id no existe")
        obj = PointDB(label=p.label, distancia=p.distancia, inclinacion=p.inclinacion, azimut=p.azimut, measurement_id=p.measurement_id)
        db.add(obj); db.commit(); db.refresh(obj)
        return PointOut(id=obj.id, label=obj.label, distancia=obj.distancia, inclinacion=obj.inclinacion, azimut=obj.azimut, measurement_id=obj.measurement_id, created_at=obj.created_at)

@app.get("/points/{pid}", response_model=PointOut)
def get_point(pid: int):
    with SessionLocal() as db:
        obj = db.get(PointDB, pid)
        if not obj: raise HTTPException(404, "Point not found")
        return PointOut(id=obj.id, label=obj.label, distancia=obj.distancia, inclinacion=obj.inclinacion, azimut=obj.azimut, measurement_id=obj.measurement_id, created_at=obj.created_at)

@app.put("/points/{pid}", response_model=PointOut)
def update_point(pid: int, p: PointIn = Body(...)):
    with SessionLocal() as db:
        obj = db.get(PointDB, pid)
        if not obj: raise HTTPException(404, "Point not found")
        if p.measurement_id is not None and not db.get(MeasurementDB, p.measurement_id):
            raise HTTPException(400, "measurement_id no existe")
        obj.label = p.label 
        obj.distancia = p.distancia
        obj.inclinacion = p.inclinacion
        obj.azimut = p.azimut
        obj.measurement_id = p.measurement_id
        db.commit(); db.refresh(obj)
        return PointOut(id=obj.id, label=obj.label, distancia=obj.distancia, inclinacion=obj.inclinacion, azimut=obj.azimut, measurement_id=obj.measurement_id, created_at=obj.created_at)

@app.delete("/points/{pid}")
def delete_point(pid: int):
    with SessionLocal() as db:
        obj = db.get(PointDB, pid)
        if not obj: raise HTTPException(404, "Point not found")
        db.delete(obj); db.commit()
        return JSONResponse({"deleted": pid})

@app.get("/points", response_model=PagePoints)
def list_points(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), q: Optional[str] = Query(None), measurement_id: Optional[int] = Query(None)):
    with SessionLocal() as db:
        query = db.query(PointDB)
        if q: query = query.filter(PointDB.label.ilike(f"%{q}%"))
        if measurement_id is not None: query = query.filter(PointDB.measurement_id == measurement_id)
        total = query.count()
        pages = max(1, math.ceil(total / limit))
        items = query.order_by(PointDB.id.desc()).offset((page - 1) * limit).limit(limit).all()
        out = [PointOut(id=o.id, label=o.label, distancia=o.distancia, inclinacion=o.inclinacion, azimut=o.azimut, measurement_id=o.measurement_id, created_at=o.created_at) for o in items]
        return PagePoints(page=page, pages=pages, total=total, items=out)

@app.get("/export.csv")
def export_csv(q: Optional[str] = None, measurement_id: Optional[int] = None):
    with SessionLocal() as db:
        query = db.query(PointDB)
        if q: query = query.filter(PointDB.label.ilike(f"%{q}%"))
        if measurement_id is not None: query = query.filter(PointDB.measurement_id == measurement_id)
        rows = query.order_by(PointDB.id.asc()).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id","label","distancia","inclinacion","azimut","measurement_id","created_at"])
    for o in rows:
        ts = o.created_at.replace(tzinfo=timezone.utc).isoformat()
        w.writerow([o.id, o.label or "", o.distancia, o.inclinacion, o.azimut, o.measurement_id if o.measurement_id is not None else "", ts])
    buf.seek(0)
    return StreamingResponse(iter([buf.read()]), media_type="text/csv")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)