# 🏪 Cafetería El Rincón Mexicano - Sistema NoSQL con MongoDB

## 📋 Descripción General

Este proyecto implementa un **sistema completo de gestión para una cafetería mexicana** utilizando tecnologías NoSQL modernas. El sistema permite gestionar productos, postres, categorías y realizar búsquedas avanzadas en tiempo real, todo desarrollado con **FastAPI**, **MongoDB** y **Docker**.

### 🎯 Objetivo Académico
Demostrar el uso de bases de datos NoSQL (MongoDB) en comparación con sistemas relacionales tradicionales, implementando características como:
- Auto-incremento de IDs en MongoDB (simulando comportamiento SQL)
- Búsquedas de texto completo
- Relaciones simples entre documentos
- API REST moderna con documentación automática
- Containerización con Docker

---

## 🗂️ Estructura del Proyecto

```
CARAMELITOAPIMONGO/
├── 📄 buscador.html          # Interfaz web para búsquedas
├── 🐳 docker-compose.yml     # Orquestación de contenedores
├── 🐍 main.py               # API FastAPI principal
├── 📦 requirements.txt      # Dependencias de Python
├── 🔄 reset-mongo.sh       # Script de reinicialización
├── 📁 mongo-init/
│   └── 🔧 mongo-init.js     # Script de inicialización de MongoDB
└── 📁 __pycache__/          # Cache de Python (auto-generado)
```

### 📁 Descripción de Archivos

| Archivo | Descripción | Función Principal |
|---------|-------------|-------------------|
| `buscador.html` | Interfaz web responsiva | Frontend para búsquedas en tiempo real |
| `docker-compose.yml` | Configuración Docker | Orquesta FastAPI, MongoDB y Mongo Express |
| `main.py` | API Backend | Lógica de negocio, endpoints y modelos |
| `requirements.txt` | Dependencias Python | Especifica librerías necesarias |
| `reset-mongo.sh` | Script de reset | Reinicializa completamente la BD |
| `mongo-init.js` | Inicialización BD | Crea índices, validaciones y funciones |

---

## 🚀 Instalación y Configuración

### Prerrequisitos
- **Docker** y **Docker Compose** instalados
- **Puerto 8090** (API), **27018** (MongoDB), **8082** (Mongo Express) disponibles

### 🛠️ Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd CARAMELITOAPIMONGO
   ```

2. **Dar permisos al script de reset** (Linux/macOS)
   ```bash
   chmod +x reset-mongo.sh
   ```

3. **Levantar los servicios**
   ```bash
   docker-compose up --build -d
   ```

4. **Verificar que todo funcione**
   ```bash
   # Esperar 15-20 segundos para que MongoDB inicialice
   curl http://localhost:8090/productos/
   ```

### 🔄 Reinicialización Completa
```bash
./reset-mongo.sh
```

---

## 🌐 Servicios y Puertos

| Servicio | URL | Puerto | Credenciales |
|----------|-----|--------|--------------|
| **API REST** | http://localhost:8090 | 8090 | - |
| **Documentación API** | http://localhost:8090/docs | 8090 | - |
| **Buscador Web** | http://localhost:8090/buscador | 8090 | - |
| **MongoDB** | mongodb://localhost:27018 | 27018 | admin/admin123 |
| **Mongo Express** | http://localhost:8082 | 8082 | admin/admin123 |

---

## 📊 Estructura de la Base de Datos

### 🏷️ Colecciones MongoDB

#### 1. **contadores** - Sistema de Auto-incremento
```javascript
{
  _id: ObjectId,
  collection_name: "productos",    // String
  sequence_value: 18              // Int (último ID usado)
}
```

#### 2. **categorias** - Categorías de productos
```javascript
{
  _id: 1,                         // Int (auto-incremento)
  nombre: "taco",                 // String
  descripcion: "Tacos variados"   // String
}
```

#### 3. **productos** - Productos de la cafetería
```javascript
{
  _id: 1,                         // Int (auto-incremento)
  nombre: "Taco de Pastor",       // String
  categoria: "taco",              // String
  descripcion: "Tortilla con...", // String
  precio: 18.0,                   // Float
  disponible: 1                   // Int (1=sí, 0=no)
}
```

#### 4. **postres** - Postres por rebanadas
```javascript
{
  _id: 1,                         // Int (auto-incremento)
  nombre: "Pastel de Chocolate",  // String
  descripcion: "Delicioso...",    // String
  categoria: "pastel",            // String
  rebanadas: 12,                  // Int
  precio_rebanada: 45.0,         // Float
  precio_total: 540.0,            // Float
  disponible: 1                   // Int (1=sí, 0=no)
}
```

---

## 🔌 API Endpoints

### 📍 Endpoints Principales

#### **Información General**
- `GET /` - Información de la API
- `GET /buscador` - Página web del buscador

#### **🏷️ Categorías**
- `GET /categorias/` - Listar todas las categorías
- `POST /categorias/` - Crear nueva categoría

#### **🌮 Productos**
- `GET /productos/` - Listar productos (paginado)
- `GET /productos/{id}` - Obtener producto específico
- `GET /productos/categoria/{categoria}` - Productos por categoría
- `POST /productos/` - Crear producto
- `PUT /productos/{id}` - Actualizar producto
- `DELETE /productos/{id}` - Eliminar producto

#### **🍰 Postres**
- `GET /postres/` - Listar postres (paginado)
- `GET /postres/{id}` - Obtener postre específico
- `GET /postres/categoria/{categoria}` - Postres por categoría
- `POST /postres/` - Crear postre
- `PUT /postres/{id}` - Actualizar postre
- `DELETE /postres/{id}` - Eliminar postre

#### **🔍 Búsquedas**
- `GET /buscar/{termino}` - Búsqueda global en productos y postres

#### **📊 Estadísticas y Administración**
- `GET /estadisticas/` - Estadísticas generales
- `GET /contadores/` - Estado de auto-incremento
- `GET /productos/{id}/misma-categoria` - Postres de misma categoría
- `GET /postres/{id}/misma-categoria` - Productos de misma categoría

### 📝 Ejemplos de Uso

#### Buscar productos con "taco"
```bash
curl http://localhost:8090/buscar/taco
```

#### Crear un nuevo producto
```bash
curl -X POST http://localhost:8090/productos/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Taco de Carnitas",
    "categoria": "taco",
    "descripcion": "Taco con carne de cerdo",
    "precio": 22.0,
    "disponible": 1
  }'
```

#### Obtener estadísticas
```bash
curl http://localhost:8090/estadisticas/
```

---

## 💻 Tecnologías Utilizadas

### **Backend**
- **FastAPI** 0.104.1 - Framework web moderno y rápido
- **Beanie** 1.23.6 - ODM para MongoDB con Pydantic
- **Motor** 3.3.1 - Driver asíncrono de MongoDB
- **Pydantic** 2.5.0 - Validación de datos
- **Uvicorn** 0.23.2 - Servidor ASGI

### **Base de Datos**
- **MongoDB** 7.0 - Base de datos NoSQL
- **Mongo Express** 1.0.0 - Interfaz web para MongoDB

### **DevOps**
- **Docker** & **Docker Compose** - Containerización
- **CORS** - Configurado para desarrollo

### **Frontend**
- **HTML5** con CSS3 moderno
- **JavaScript** (Vanilla) para interactividad
- **Responsive Design** - Compatible con móviles

---

## ✨ Características Técnicas Destacadas

### 🔢 **Auto-incremento en MongoDB**
- Simula comportamiento de bases de datos relacionales
- IDs secuenciales (1, 2, 3...) en lugar de ObjectIds
- Sistema de contadores para cada colección
- Función `getNextSequence()` personalizada

### 🔍 **Búsqueda Avanzada**
- Búsqueda de texto completo con MongoDB Text Search
- Búsqueda insensible a mayúsculas/minúsculas
- Índices optimizados para rendimiento
- Búsqueda simultánea en múltiples campos

### 🔗 **Relaciones Simples**
- Relaciones por categoría entre productos y postres
- Endpoints para encontrar elementos relacionados
- Agregaciones para estadísticas

### 🛡️ **Validaciones y Esquemas**
- Validaciones a nivel de base de datos con MongoDB Schema Validation
- Validaciones de API con Pydantic
- Tipos de datos estrictos
- Campos requeridos y opcionales

### 📱 **Interfaz Responsiva**
- Diseño moderno con gradientes y animaciones
- Compatible con dispositivos móviles
- Búsqueda en tiempo real
- Tabla de resultados interactiva

---

## 🧪 Datos de Prueba

El sistema incluye datos de ejemplo para testing:

### **Categorías** (9 categorías)
- torta, cuernito, quesadilla, taco, baguette, bebida, postre, pastel, postre_frio

### **Productos** (18 productos de ejemplo)
- Tortas: Jamón, Milanesa, Cubana
- Tacos: Pastor, Suadero, Barbacoa
- Quesadillas: Queso, Hongos, Tinga
- Bebidas: Café Americano, Horchata, Limonada
- Y más...

### **Postres** (8 postres de ejemplo)
- Pastel de Chocolate, Cheesecake de Fresa, Tres Leches
- Tarta de Manzana, Red Velvet, Tiramisú
- Y más...

---

## 🔧 Comandos Útiles

### **Verificar estado de servicios**
```bash
docker-compose ps
```

### **Ver logs en tiempo real**
```bash
docker-compose logs -f fastapi
docker-compose logs -f mongo
```

### **Conectar a MongoDB directamente**
```bash
docker exec -it caramelitoapimongo_mongo_1 mongosh -u admin -p admin123
```

### **Detener servicios**
```bash
docker-compose down
```

### **Limpiar volúmenes (CUIDADO: borra datos)**
```bash
docker-compose down -v
```

---

## 📈 Casos de Uso

1. **Gestión de Inventario**: CRUD completo de productos y postres
2. **Sistema de Búsqueda**: Búsqueda rápida por nombre, descripción o categoría
3. **Análisis de Ventas**: Estadísticas por categoría y precios
4. **Relaciones de Productos**: Encontrar productos similares por categoría
5. **Administración**: Monitoreo de contadores y estado de BD

---

## 🎓 Valor Académico

Este proyecto demuestra:

### **Conceptos de Bases de Datos NoSQL**
- Flexibilidad de esquemas
- Documentos anidados vs. tablas relacionales
- Índices de texto completo
- Agregaciones y pipelines

### **Comparación SQL vs. NoSQL**
- Auto-incremento simulado en MongoDB
- Relaciones por referencia vs. joins
- Validaciones a nivel de aplicación vs. BD

### **Arquitectura Moderna**
- APIs REST con documentación automática
- Containerización con Docker
- Separación de responsabilidades
- Patrones de diseño (ODM, Repository Pattern)

### **Desarrollo Full-Stack**
- Backend con FastAPI
- Frontend responsivo
- Base de datos NoSQL
- DevOps con Docker

---

## 📞 Soporte y Documentación

- **Documentación API**: http://localhost:8090/docs (Swagger UI automático)
- **Redoc**: http://localhost:8090/redoc (Documentación alternativa)
- **MongoDB Compass**: Conectar a `mongodb://admin:admin123@localhost:27018/cafeteria_db`

---

## 📝 Notas Importantes

1. **Persistencia**: Los datos se mantienen en volúmenes Docker
2. **Seguridad**: Configurado para desarrollo, NO para producción
3. **Performance**: Optimizado con índices MongoDB
4. **Compatibilidad**: Probado en Linux, macOS y Windows con Docker

---

**Desarrollado por**: [Sinuhé Vidals Sibaja y Samantha Betanzo Bolaños]  
**Universidad**: [Universidad Tecnológica de la Mixteca]  
**Materia**: [Base de Datos]  
**Fecha**: [28 de Junio del 2025]

---

*Este proyecto demuestra la implementación práctica de sistemas NoSQL modernos aplicados a casos de uso reales del sector alimentario.*
