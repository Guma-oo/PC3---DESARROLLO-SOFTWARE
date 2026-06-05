# Voz del Ciudadano - Proyecto Universitario
**Autor:** Sánchez Longa Erick Joel

*Nota:*  El límite de "25,000 firmas" ha sido ajustado a **5 firmas** mediante la variable `limite_firmas` en la configuración del Facade. Hice esto mas que todo para poder probar el programa.

## Instalación y Ejecución

### Requisitos previos
- Python 3.8 o superior.

### 1. Ejecutar el Backend
Abra una terminal en la raíz del proyecto y ejecuta:

```bash
cd backend
pip install fastapi pydantic uvicorn
uvicorn main:app --reload