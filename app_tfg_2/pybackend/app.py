from fastapi import FastAPI, HTTPException, Query, Body
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey, inspect
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import io, csv, math

DB_URL = "sqlite:///./puntos.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class MedidaDB(Base):
    __tablename__ = "medidas"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    puntos = relationship("PuntosDB", back_populates="medida", cascade="all, delete-orphan")

class RadiacionDB(Base):
    __tablename__ = "radiaciones"
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, index=True, nullable=True)
    distancia = Column(Float, nullable=False, default=0.0)
    inclinacion = Column(Float, nullable=False, default=0.0)
    azimut = Column(Float, nullable=False, default=0.0)

    base_point_id = Column(Integer, ForeignKey("puntos.id"), nullable=False, index=True)
    medida_id = Column(Integer, ForeignKey("medidas.id"), nullable=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    base_point = relationship("PuntosDB", back_populates="radiaciones")

class PuntosDB(Base):
    __tablename__ = "puntos"
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, index=True, nullable=True)
    distancia = Column(Float, nullable=False, default=0.0)
    inclinacion = Column(Float, nullable=False, default=0.0)
    azimut = Column(Float, nullable=False, default=0.0)
    medida_id = Column(Integer, ForeignKey("medidas.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    medida = relationship("MedidaDB", back_populates="puntos")
    radiaciones = relationship("RadiacionDB", back_populates="base_point", cascade="all, delete-orphan")
Base.metadata.create_all(bind=engine)

class MedidaIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = None

class MedidaOut(MedidaIn):
    id: int
    created_at: datetime

class PointIn(BaseModel):
    label: Optional[str] = Field(None, description="Etiqueta opcional")
    distancia: float = Field(ge=0)
    inclinacion: float = Field(ge=-90, le=90)
    azimut: float = Field(ge=0, lt=360)
    medida_id: Optional[int] = Field(None, description="ID de la medición")

class PointOut(PointIn):
    id: int
    created_at: datetime

class RadacionIn(BaseModel):
    label: Optional[str] = Field(None)
    distancia: float = Field(ge=0)
    inclinacion: float = Field(ge=-90, le=90)
    azimut: float = Field(ge=0, lt=360)
    base_point_id: int

class RadacionOut(RadacionIn):
    id: int
    medida_id: Optional[int]
    created_at: datetime

class PageRadiaciones(BaseModel):
    page: int
    pages: int
    total: int
    items: List[RadacionOut]

class PageMedidas(BaseModel):
    page: int
    pages: int
    total: int
    items: List[MedidaOut]

class PagePuntos(BaseModel):
    page: int
    pages: int
    total: int
    items: List[PointOut]

app = FastAPI(title="TFG App Backend")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health():
    return {"status":"ok","ts": datetime.utcnow().isoformat()+"Z"}

# EVENTOS GET, PUT, POST Y DELETE DE MEDIDAS. TAMBIÉN SE AÑADE EL LISTAR MEDIDAS
@app.post("/medidas", response_model=MedidaOut)
def create_medida(m: MedidaIn = Body(...)):
    with SessionLocal() as db:
        exists = db.query(MedidaDB).filter(MedidaDB.name == m.name).first()
        if exists: raise HTTPException(400, "Ya existe una medición con ese nombre")
        obj = MedidaDB(name=m.name, description=m.description)
        db.add(obj); db.commit(); db.refresh(obj)
        return MedidaOut(id=obj.id, name=obj.name, description=obj.description, created_at=obj.created_at)

@app.get("/medidas/{mid}", response_model=MedidaOut)
def get_medida(mid: int):
    with SessionLocal() as db:
        obj = db.get(MedidaDB, mid)
        if not obj: raise HTTPException(404, "medida not found")
        return MedidaOut(id=obj.id, name=obj.name, description=obj.description, created_at=obj.created_at)

@app.put("/medidas/{mid}", response_model=MedidaOut)
def update_medida(mid: int, m: MedidaIn = Body(...)):
    with SessionLocal() as db:
        obj = db.get(MedidaDB, mid)
        if not obj: raise HTTPException(404, "medida not found")
        if m.name != obj.name:
            dup = db.query(MedidaDB).filter(MedidaDB.name == m.name).first()
            if dup: raise HTTPException(400, "Ya existe una medición con ese nombre")
        obj.name, obj.description = m.name, m.description
        db.commit(); db.refresh(obj)
        return MedidaOut(id=obj.id, name=obj.name, description=obj.description, created_at=obj.created_at)

@app.delete("/medidas/{mid}")
def delete_medida(mid: int):
    with SessionLocal() as db:
        obj = db.get(MedidaDB, mid)
        if not obj: raise HTTPException(404, "medida not found")
        db.delete(obj); db.commit()
        return JSONResponse({"deleted": mid})

@app.get("/medidas", response_model=PageMedidas)
def list_medidas(page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200), q: Optional[str] = Query(None)):
    with SessionLocal() as db:
        query = db.query(MedidaDB)
        if q: query = query.filter(MedidaDB.name.ilike(f"%{q}%"))
        total = query.count()
        pages = max(1, math.ceil(total / limit))
        items = query.order_by(MedidaDB.id.desc()).offset((page - 1) * limit).limit(limit).all()
        out = [MedidaOut(id=o.id, name=o.name, description=o.description, created_at=o.created_at) for o in items]
        return PageMedidas(page=page, pages=pages, total=total, items=out)

# EVENTOS GET, POST Y DELETE DE PUNTOS
@app.post("/puntos", response_model=PointOut)
def create_point(p: PointIn = Body(...)):
    with SessionLocal() as db:
        if p.medida_id is not None and not db.get(MedidaDB, p.medida_id):
            raise HTTPException(400, "medida_id no existe")
        obj = PuntosDB(label=p.label, distancia=p.distancia, inclinacion=p.inclinacion, azimut=p.azimut, medida_id=p.medida_id)
        db.add(obj); db.commit(); db.refresh(obj)
        return PointOut(id=obj.id, label=obj.label, distancia=obj.distancia, inclinacion=obj.inclinacion, azimut=obj.azimut, medida_id=obj.medida_id, created_at=obj.created_at)

@app.get("/puntos/{pid}", response_model=PointOut)
def get_point(pid: int):
    with SessionLocal() as db:
        obj = db.get(PuntosDB, pid)
        if not obj: raise HTTPException(404, "Point not found")
        return PointOut(id=obj.id, label=obj.label, distancia=obj.distancia, inclinacion=obj.inclinacion, azimut=obj.azimut, medida_id=obj.medida_id, created_at=obj.created_at)

@app.put("/puntos/{pid}", response_model=PointOut)
def update_point(pid: int, p: PointIn = Body(...)):
    with SessionLocal() as db:
        obj = db.get(PuntosDB, pid)
        if not obj: raise HTTPException(404, "Point not found")
        if p.medida_id is not None and not db.get(MedidaDB, p.medida_id):
            raise HTTPException(400, "medida_id no existe")
        obj.label = p.label 
        obj.distancia = p.distancia
        obj.inclinacion = p.inclinacion
        obj.azimut = p.azimut
        obj.medida_id = p.medida_id
        db.commit(); db.refresh(obj)
        return PointOut(id=obj.id, label=obj.label, distancia=obj.distancia, inclinacion=obj.inclinacion, azimut=obj.azimut, medida_id=obj.medida_id, created_at=obj.created_at)

@app.delete("/puntos/{pid}")
def delete_point(pid: int):
    with SessionLocal() as db:
        obj = db.get(PuntosDB, pid)
        if not obj: raise HTTPException(404, "Point not found")
        db.delete(obj)
        db.commit()
        return JSONResponse({"deleted": pid})

@app.get("/puntos", response_model=PagePuntos)
def list_puntos(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), q: Optional[str] = Query(None), medida_id: Optional[int] = Query(None)):
    with SessionLocal() as db:
        query = db.query(PuntosDB)
        if q: query = query.filter(PuntosDB.label.ilike(f"%{q}%"))
        if medida_id is not None: query = query.filter(PuntosDB.medida_id == medida_id)
        total = query.count()
        pages = max(1, math.ceil(total / limit))
        items = query.order_by(PuntosDB.id.desc()).offset((page - 1) * limit).limit(limit).all()
        out = [PointOut(id=o.id, label=o.label, distancia=o.distancia, inclinacion=o.inclinacion, azimut=o.azimut, medida_id=o.medida_id, created_at=o.created_at) for o in items]
        return PagePuntos(page=page, pages=pages, total=total, items=out)

@app.post("/radiaciones", response_model=RadacionOut)
def create_radacion(r: RadacionIn = Body(...)):
    with SessionLocal() as db:
        bp = db.get(PuntosDB, r.base_point_id)
        if not bp:
            raise HTTPException(400, "base_point_id no existe")

        obj = RadiacionDB(
            label=r.label,
            distancia=r.distancia,
            inclinacion=r.inclinacion,
            azimut=r.azimut,
            base_point_id=r.base_point_id,
            medida_id=bp.medida_id
        )
        db.add(obj); db.commit(); db.refresh(obj)
        return RadacionOut(
            id=obj.id, label=obj.label, distancia=obj.distancia,
            inclinacion=obj.inclinacion, azimut=obj.azimut,
            base_point_id=obj.base_point_id, medida_id=obj.medida_id,
            created_at=obj.created_at
        )

# EVENTOS GET, POST Y DELETE DE RADIACIONES
@app.get("/radiaciones/{rid}", response_model=RadacionOut)
def get_radacion(rid: int):
    with SessionLocal() as db:
        obj = db.get(RadiacionDB, rid)
        if not obj:
            raise HTTPException(404, "radacion not found")
        return RadacionOut(
            id=obj.id, label=obj.label, distancia=obj.distancia,
            inclinacion=obj.inclinacion, azimut=obj.azimut,
            base_point_id=obj.base_point_id, medida_id=obj.medida_id,
            created_at=obj.created_at
        )

@app.put("/radiaciones/{rid}", response_model=RadacionOut)
def update_radacion(rid: int, r: RadacionIn = Body(...)):
    with SessionLocal() as db:
        obj = db.get(RadiacionDB, rid)
        if not obj:
            raise HTTPException(404, "radacion not found")

        bp = db.get(PuntosDB, r.base_point_id)
        if not bp:
            raise HTTPException(400, "base_point_id no existe")

        obj.label = r.label
        obj.distancia = r.distancia
        obj.inclinacion = r.inclinacion
        obj.azimut = r.azimut
        obj.base_point_id = r.base_point_id
        obj.medida_id = bp.medida_id

        db.commit(); db.refresh(obj)
        return RadacionOut(
            id=obj.id, label=obj.label, distancia=obj.distancia,
            inclinacion=obj.inclinacion, azimut=obj.azimut,
            base_point_id=obj.base_point_id, medida_id=obj.medida_id,
            created_at=obj.created_at
        )

@app.get("/radiaciones", response_model=PageRadiaciones)
def list_radiaciones(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    q: Optional[str] = Query(None),
    medida_id: Optional[int] = Query(None),
    base_point_id: Optional[int] = Query(None),
):
    with SessionLocal() as db:
        query = db.query(RadiacionDB)
        if q:
            query = query.filter(RadiacionDB.label.ilike(f"%{q}%"))
        if medida_id is not None:
            query = query.filter(RadiacionDB.medida_id == medida_id)
        if base_point_id is not None:
            query = query.filter(RadiacionDB.base_point_id == base_point_id)

        total = query.count()
        pages = max(1, math.ceil(total / limit))
        items = query.order_by(RadiacionDB.id.desc()).offset((page-1)*limit).limit(limit).all()

        out = [
            RadacionOut(
                id=o.id, label=o.label, distancia=o.distancia,
                inclinacion=o.inclinacion, azimut=o.azimut,
                base_point_id=o.base_point_id, medida_id=o.medida_id,
                created_at=o.created_at
            ) for o in items
        ]
        return PageRadiaciones(page=page, pages=pages, total=total, items=out)

@app.delete("/radiaciones/{rid}")
def delete_radacion(rid: int):
    with SessionLocal() as db:
        obj = db.get(RadiacionDB, rid)
        if not obj:
            raise HTTPException(404, "radacion not found")
        db.delete(obj)
        db.commit()
        return JSONResponse({"deleted": rid})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)