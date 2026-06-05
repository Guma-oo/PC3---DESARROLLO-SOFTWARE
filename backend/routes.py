from fastapi import APIRouter, HTTPException, UploadFile, File
import shutil
from models import IniciativaCreate, ComentarioCreate, ModificarIniciativa
from patterns import facade

router = APIRouter()

@router.post("/iniciativas")
def crear_iniciativa(data: IniciativaCreate):
    return facade.crear_iniciativa(data.titulo, data.contenido)

@router.get("/iniciativas")
def listar_iniciativas():
    return facade.listar_iniciativas()

@router.post("/firmar/{id_ini}")
def firmar(id_ini: str):
    try:
        return facade.firmar_iniciativa(id_ini)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/comentar/{id_ini}")
def comentar(id_ini: str, data: ComentarioCreate):
    try:
        return facade.comentar_iniciativa(id_ini, data.texto)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/adjuntar/{id_ini}")
def adjuntar_recurso(id_ini: str, file: UploadFile = File(...)):
    try:

        ruta_archivo = f"uploads/{id_ini}_{file.filename}"
        
        with open(ruta_archivo, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
            
        return facade.adjuntar_recurso_iniciativa(id_ini, ruta_archivo)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/iniciativas/{id_ini}")
def modificar(id_ini: str, data: ModificarIniciativa):
    try:
        return facade.modificar_iniciativa(id_ini, data.nuevo_contenido)
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/enviar/{id_ini}")
def enviar(id_ini: str):
    try:
        return facade.enviar_iniciativa(id_ini)
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))