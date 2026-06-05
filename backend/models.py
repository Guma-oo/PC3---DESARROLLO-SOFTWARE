from pydantic import BaseModel

class IniciativaCreate(BaseModel):
    titulo: str
    contenido: str

class ComentarioCreate(BaseModel):
    texto: str

class ModificarIniciativa(BaseModel):
    nuevo_contenido: str

class AdjuntoCreate(BaseModel):
    nombre_archivo: str