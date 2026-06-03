# Collaborator IA
Plataforma de recomendación de investigadores para colaboracion cientifica en IA en latinoamérica.

## Problema

Según el reporte ILIA 2024, entre los años 2018 y 2023 se registraron 23.850 colaboraciones científicas en el ámbito de la inteligencia artificial. De estas, un 50% correspondió a colaboraciones entre investigadores de América Latina y Europa, y un 13% a colaboraciones con Estados Unidos, mientras que solo un 8% se produjo entre investigadores de la propia región latinoamericana, lo que evidencia un desafío pendiente en términos de fortalecimiento de la colaboración regional. El principal problema detectado es la dificultad para encontrar otros investigadores trabajando en temas similares dentro de la región. 

## La solución

Este proyecto corresponde al desarrollo de una plataforma web que utiliza un sistema de recomendación con técnicas híbridas de contenido e Itemknn para generar recomendaciones personalizadas para el usuario sin requerir de perfiles en la DB sino que utilizando OpenAlex, un recopilatorio académico abierto.

La aplicación fue desarrollada usando React, Django Rest Framework y Postgresql, con un snapshot de OpenAlex reciente.


## Instalación

Se debe contar con el snapshot descargado en formato PostgreSQL de OpenAlex. Una vez hecho esto se debe ingresar la informacion de la DB para poder conectar en el archivo settings de la carpeta backend. Esta información se encuentra en la variable DATABASES.

Para poder ejecutar el backend de la aplicación primero se debe crear un ambiente virtual para poder instalar las librerias necesarias. 

``` cmd
python -m venv .venv
```

Para instalar las librerias correspondientes se utiliza el archivo requirements una vez activado el venv.

``` cmd
pip install -r requirements.txt
``` 

La aplicación utiliza la DB para poder traer la información final, sin embargo para optimizar consultas se hace un precalculo de las matrices de colaboración en archivos externos. Para poder generar estos archivos, se utiliza el script build_models.py asegurandose que la DB este conectada y tenga las vistas correctas definidas en models.

``` cmd
python build_models.py
```

No es necesario el uso de migraciones, ya que el sistema esta diseñado para acoplarse a la DB y no crear tablas adicionales, sin embargo puede ser útil a futuro si se agregan tablas propias de la plataforma al sistema.

Para poder ejecutar el backend, se utiliza el siguiente comando.

``` cmd
python manage.py runserver
``` 

El frontend esta desarrollado en react por lo que es necesario el uso de npm para manejar las librerias de nodejs. Para poder instalar estas librerias se utiliza el comando:

``` cmd
npm install
``` 

Para poder ejecutar la aplicación en modo desarrollador se utiliza el comando:

``` cmd
npm run dev
``` 

Para poder utilizar la solución completa es necesario tener ambos procesos funcionando de manera simultánea.

> **Nota:** Es importante que la información de conexión con la DB y las vistas y tablas definidas existan en la base de datos que se este utilizando.

> **Nota 2:** Conviene cambiar los enlaces al hacer fetch en el frontend si no se usa localhost como dominio de origen del backend.