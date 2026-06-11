# Sistema NoSQL - Gestión Veterinaria 

Este proyecto es una aplicación web completa desarrollada para la gestión de una clínica veterinaria, utilizando tecnologías modernas de desarrollo web y una arquitectura de base de datos NoSQL de última generación.

## Características del Proyecto
* **Base de Datos en la Nube:** Conexión nativa a clúster remoto en **MongoDB Atlas** utilizando la versión más reciente (**MongoDB 8.0**).
* **Autenticación Segura:** Sistema de Login y Registro dinámico de usuarios con cifrado y hasheo de contraseñas mediante **Bcrypt**.
* **Protección de Credenciales:** Uso estricto de variables de entorno (`python-dotenv`) para ocultar cadenas de conexión e impedir la filtración de credenciales en el código fuente.
* **Modelado NoSQL Profesional:** * Relaciones referenciales directas mediante `ObjectId` operadas con pipelines de agregación (`$lookup`).
  * Mecanismo de **Borrado Lógico** (`activo: true/false`) para preservar el historial clínico de los pacientes sin destruir datos físicos.
  * Validaciones nativas de esquema de datos en el servidor de MongoDB.

##  Requisitos e Instalación

Para ejecutar este proyecto de forma local, asegúrate de tener instalado Python 3.10+ y ejecuta el siguiente comando en la terminal para instalar las dependencias necesarias:

```bash
pip install flask pymongo bcrypt python-dotenv

Ejecución
Configurar las variables de entorno en un archivo .env (MONGODB_URI y SECRET_KEY).

Ejecutar el script semilla para poblar la base de datos: python seed.py

Iniciar el servidor web: python app.py
