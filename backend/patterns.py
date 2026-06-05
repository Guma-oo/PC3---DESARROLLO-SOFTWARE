import uuid
from pymongo import MongoClient


# FLYWEIGHT 
class EstadoIniciativaFlyweight:
    def __init__(self, nombre: str):
        self.nombre = nombre

class EstadoFactory:
    _estados = {}
    
    @staticmethod
    def get_estado(nombre: str) -> EstadoIniciativaFlyweight:
        if nombre not in EstadoFactory._estados:
            EstadoFactory._estados[nombre] = EstadoIniciativaFlyweight(nombre)
        return EstadoFactory._estados[nombre]

# COMPOSITE 
class ComponenteIniciativa:
    def renderizar(self) -> str:
        pass

class Articulo(ComponenteIniciativa):
    def __init__(self, texto: str):
        self.texto = texto
    def renderizar(self) -> str:
        return f"Artículo: {self.texto}"

class Capitulo(ComponenteIniciativa):
    def __init__(self, titulo: str):
        self.titulo = titulo
        self.hijos = []
    def agregar(self, componente: ComponenteIniciativa):
        self.hijos.append(componente)
    def renderizar(self) -> str:
        contenido = f"Capítulo: {self.titulo}\n"
        for hijo in self.hijos:
            contenido += f"  - {hijo.renderizar()}\n"
        return contenido


# DECORATOR 
class IniciativaInteractuable:
    def obtener_detalle(self) -> dict:
        pass

class IniciativaBase(IniciativaInteractuable):
    def __init__(self, id_ini: str, titulo: str, contenido: ComponenteIniciativa):
        self.id = id_ini
        self.titulo = titulo
        self.contenido_jerarquico = contenido
        self.firmas = 0
        self.estado = EstadoFactory.get_estado("Activa")
        self._comentarios = []
        self._adjuntos = []

    def obtener_detalle(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "contenido": self.contenido_jerarquico.renderizar() if hasattr(self.contenido_jerarquico, 'renderizar') else self.contenido_jerarquico,
            "firmas": self.firmas,
            "estado": self.estado.nombre,
            "comentarios": self._comentarios,
            "adjuntos": self._adjuntos
        }

class ComentarioDecorator(IniciativaInteractuable):
    def __init__(self, iniciativa: IniciativaBase, comentario: str):
        self.iniciativa = iniciativa
        self.iniciativa._comentarios.append(comentario)
    def obtener_detalle(self) -> dict:
        return self.iniciativa.obtener_detalle()

class AdjuntoDecorator(IniciativaInteractuable):
    def __init__(self, iniciativa: IniciativaBase, adjunto: str):
        self.iniciativa = iniciativa
        self.iniciativa._adjuntos.append(adjunto)
    def obtener_detalle(self) -> dict:
        return self.iniciativa.obtener_detalle()


# PROXY 
class IniciativaProxy:
    def __init__(self, iniciativa: IniciativaBase):
        self.iniciativa = iniciativa

    def modificar_contenido(self, nuevo_texto: str):
        if self.iniciativa.estado.nombre in ["Congelada", "Enviada"]:
            raise PermissionError("Acción denegada: La iniciativa está bloqueada o cerrada.")
        nuevo_capitulo = Capitulo("Capítulo Único Modificado")
        nuevo_capitulo.agregar(Articulo(nuevo_texto))
        self.iniciativa.contenido_jerarquico = nuevo_capitulo
        return True

    def enviar_congreso(self):
        if self.iniciativa.estado.nombre != "Congelada":
            raise PermissionError("Acción denegada: Solo se envían iniciativas congeladas.")
        self.iniciativa.estado = EstadoFactory.get_estado("Enviada")
        return True



class FirmaRENIEC:
    def validar_identidad_reniec(self) -> bool:
        return True 

class FirmaAdapter:
    def __init__(self, proveedor_externo):
        self.proveedor = proveedor_externo
    
    def firmar(self) -> bool:
        if isinstance(self.proveedor, FirmaRENIEC):
            return self.proveedor.validar_identidad_reniec()
        return False


class Notificador:
    def __init__(self, implementacion):
        self.implementacion = implementacion
    def enviar(self, mensaje: str):
        self.implementacion.enviar_mensaje(mensaje)

class NotificacionEmail:
    def enviar_mensaje(self, mensaje: str):
        print(f"[BRIDGE] Enviando Email: {mensaje}")

class NotificacionInterna:
    def enviar_mensaje(self, mensaje: str):
        print(f"[BRIDGE] Notificación de Sistema: {mensaje}")


#  FACADE 
class SistemaVozCiudadanaFacade:
    def __init__(self):
        # Conexión a Mongo
        self.uri = "mongodb+srv://erickslonga24_db_user:<TU_PASSWORD_AQUI>@todolistcluster.hrygcsc.mongodb.net/?appName=TodoListCluster"
        self.client = MongoClient(self.uri)
        self.db = self.client["voz_ciudadana_db"]
        self.collection = self.db["iniciativas"]
        self.limite_firmas = 5 

    def crear_iniciativa(self, titulo: str, contenido_texto: str) -> dict:
        id_ini = str(uuid.uuid4())[:8]
        capitulo = Capitulo("Disposiciones Generales")
        capitulo.agregar(Articulo(contenido_texto))
        
        iniciativa = IniciativaBase(id_ini, titulo, capitulo)
        detalle = iniciativa.obtener_detalle()
        
        # Persistencia en MongoDB
        self.collection.insert_one(detalle)
        detalle.pop("_id", None)
        return detalle

    def listar_iniciativas(self) -> list:
        iniciativas = []
        for doc in self.collection.find():
            doc.pop("_id", None)
            iniciativas.append(doc)
        return iniciativas

    def firmar_iniciativa(self, id_ini: str) -> dict:
        doc = self.collection.find_one({"id": id_ini})
        if not doc:
            raise ValueError("Iniciativa no encontrada")
        
        if doc["estado"] in ["Congelada", "Enviada"]:
            raise PermissionError("No se puede firmar una iniciativa cerrada.")

        adaptador = FirmaAdapter(FirmaRENIEC())
        if adaptador.firmar():
            nuevas_firmas = doc["firmas"] + 1
            nuevo_estado = doc["estado"]
            
            if nuevas_firmas >= self.limite_firmas:
                nuevo_estado = "Congelada"
                notificador = Notificador(NotificacionInterna())
                notificador.enviar(f"Iniciativa {id_ini} CONGELADA (Meta alcanzada).")
                
            self.collection.update_one(
                {"id": id_ini},
                {"$set": {"firmas": nuevas_firmas, "estado": nuevo_estado}}
            )
            
        doc = self.collection.find_one({"id": id_ini})
        doc.pop("_id", None)
        return doc

    def comentar_iniciativa(self, id_ini: str, texto: str) -> dict:
        doc = self.collection.find_one({"id": id_ini})
        if not doc:
            raise ValueError("Iniciativa no encontrada")
        
      
        iniciativa_obj = IniciativaBase(doc["id"], doc["titulo"], doc["contenido"])
        iniciativa_obj.firmas = doc["firmas"]
        iniciativa_obj.estado = EstadoFactory.get_estado(doc["estado"])
        iniciativa_obj._comentarios = doc["comentarios"]
        iniciativa_obj._adjuntos = doc["adjuntos"]
        
      
        decorado = ComentarioDecorator(iniciativa_obj, texto)
        nuevo_detalle = decorado.obtener_detalle()
        
        self.collection.update_one(
            {"id": id_ini},
            {"$set": {"comentarios": nuevo_detalle["comentarios"]}}
        )
        return nuevo_detalle

    def adjuntar_recurso_iniciativa(self, id_ini: str, nombre_archivo: str) -> dict:
        doc = self.collection.find_one({"id": id_ini})
        if not doc:
            raise ValueError("Iniciativa no encontrada")
            
        if doc["estado"] in ["Congelada", "Enviada"]:
            raise PermissionError("No se pueden adjuntar recursos a una iniciativa cerrada o congelada.")
            
        iniciativa_obj = IniciativaBase(doc["id"], doc["titulo"], doc["contenido"])
        iniciativa_obj.firmas = doc["firmas"]
        iniciativa_obj.estado = EstadoFactory.get_estado(doc["estado"])
        iniciativa_obj._comentarios = doc["comentarios"]
        iniciativa_obj._adjuntos = doc["adjuntos"]
        
       
        decorado = AdjuntoDecorator(iniciativa_obj, nombre_archivo)
        nuevo_detalle = decorado.obtener_detalle()
        
        self.collection.update_one(
            {"id": id_ini},
            {"$set": {"adjuntos": nuevo_detalle["adjuntos"]}}
        )
        return nuevo_detalle

    def modificar_iniciativa(self, id_ini: str, nuevo_texto: str) -> dict:
        doc = self.collection.find_one({"id": id_ini})
        if not doc:
            raise ValueError("Iniciativa no encontrada")
            
        iniciativa_obj = IniciativaBase(doc["id"], doc["titulo"], doc["contenido"])
        iniciativa_obj.estado = EstadoFactory.get_estado(doc["estado"])
        
        
        proxy = IniciativaProxy(iniciativa_obj)
        proxy.modificar_contenido(nuevo_texto)
        
        nuevo_detalle = iniciativa_obj.obtener_detalle()
        
        self.collection.update_one(
            {"id": id_ini},
            {"$set": {"contenido": nuevo_detalle["contenido"]}}
        )
        return nuevo_detalle

    def enviar_iniciativa(self, id_ini: str) -> dict:
        doc = self.collection.find_one({"id": id_ini})
        if not doc:
            raise ValueError("Iniciativa no encontrada")
            
        iniciativa_obj = IniciativaBase(doc["id"], doc["titulo"], doc["contenido"])
        iniciativa_obj.estado = EstadoFactory.get_estado(doc["estado"])
        
        proxy = IniciativaProxy(iniciativa_obj)
        proxy.enviar_congreso()
        
        self.collection.update_one(
            {"id": id_ini},
            {"$set": {"estado": "Enviada"}}
        )
        
        notificador = Notificador(NotificacionEmail())
        notificador.enviar(f"Iniciativa {id_ini} ENVIADA AL CONGRESO.")
        
        doc = self.collection.find_one({"id": id_ini})
        doc.pop("_id", None)
        return doc

facade = SistemaVozCiudadanaFacade()
