### Paso 1: Crear el clúster de Kubernetes

Entré a la consola de Google Cloud:
1. Fui a Kubernetes Engine > Clusters > Crear Clúster.

2. Configuré el clúster con:
   - Nombre: my-first-cluster-1
   - Zona: us-central1-c
   - Tipo de máquina: e2-medium
   - Cantidad de nodos: 2
   - Modo: Standard
   
![img.png](imagenes_README/img.png)
![img_2.png](imagenes_README/img_2.png)

Previamente creé una cuenta en Google Cloud e instalé y configué Google Cloud SDK.

### Paso 2: Conectarse al clúster con kubectl
Ejecuté el siguiente comando para obtener las credenciales de acceso:
![img_1.png](imagenes_README/img_1.png)

Verificación de la conexión al clúster y visualización de los nodos:
![img_3.png](imagenes_README/img_3.png)

### Paso 3: Desplegar una aplicación en el cluster
Se crea el archivo `deployment.yaml` para el despliegue:
![img_4.png](imagenes_README/img_4.png)

verificamos que los pods estén corriendo y el despliegue se haya hecho correctamente:
![img_5.png](imagenes_README/img_5.png)

Se crea el servicio para exponer la aplicación:
![img_6.png](imagenes_README/img_6.png)

Verificamos la ip aplicada al servicio previamente expuesto:
![img_7.png](imagenes_README/img_7.png)

### Paso 4: Escalar la Aplicación

Escalamiento del número de réplicas del deployment a 4:
![img_8.png](imagenes_README/img_8.png)

### Paso 5: Limpiar Recursos

Eliminé el deployment y el servicio:
![img_9.png](imagenes_README/img_9.png)


fin.