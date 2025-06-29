from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from beanie import Document, init_beanie
from pydantic import BaseModel, Field
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Modelo para Contadores (para auto incremento)
class Contador(Document):
    collection_name: str = Field(..., unique=True)
    sequence_value: int = Field(default=0)
    
    class Settings:
        name = "contadores"

# Modelo de Categorías (MongoDB Document)
class Categoria(Document):
    id: int = Field(..., alias="_id")
    nombre: str = Field(..., max_length=50)
    descripcion: str
    
    class Settings:
        name = "categorias"

# Modelo de Productos (MongoDB Document) con ID auto incremental
class Producto(Document):
    id: int = Field(..., alias="_id")
    nombre: str = Field(..., max_length=100)
    categoria: str  # Nombre de la categoría
    descripcion: str
    precio: float
    disponible: int = Field(default=1, description="1 = disponible, 0 = no disponible")
    
    class Settings:
        name = "productos"

# Modelo de Postres (MongoDB Document) con ID auto incremental
class Postre(Document):
    id: int = Field(..., alias="_id")
    nombre: str = Field(..., max_length=100)
    descripcion: str
    categoria: str  # Nombre de la categoría
    rebanadas: int = Field(..., gt=0)
    precio_rebanada: float = Field(..., gt=0)
    precio_total: float = Field(..., gt=0)
    disponible: int = Field(default=1, description="1 = disponible, 0 = no disponible")
    
    class Settings:
        name = "postres"

# Función para obtener el siguiente ID
async def get_next_sequence_value(collection_name: str) -> int:
    """Obtiene el siguiente valor de secuencia para una colección"""
    contador = await Contador.find_one(Contador.collection_name == collection_name)
    
    if not contador:
        # Crear contador si no existe
        contador = Contador(collection_name=collection_name, sequence_value=1)
        await contador.insert()
        return 1
    else:
        # Incrementar y actualizar
        nuevo_valor = contador.sequence_value + 1
        await contador.update({"$set": {"sequence_value": nuevo_valor}})
        return nuevo_valor

# Esquemas Pydantic para Categorías
class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: str

class CategoriaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    
    class Config:
        from_attributes = True

# Esquemas Pydantic para Productos
class ProductoCreate(BaseModel):
    nombre: str = Field(..., max_length=100)
    categoria: str
    descripcion: str
    precio: float = Field(..., gt=0)
    disponible: Optional[int] = Field(default=1, ge=0, le=1)

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    categoria: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = Field(None, gt=0)
    disponible: Optional[int] = Field(None, ge=0, le=1)

class ProductoResponse(BaseModel):
    id: int
    nombre: str
    categoria: str
    descripcion: str
    precio: float
    disponible: int
    
    class Config:
        from_attributes = True

# Esquemas Pydantic para Postres
class PostreCreate(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: str
    categoria: str
    rebanadas: int = Field(..., gt=0)
    precio_rebanada: float = Field(..., gt=0)
    precio_total: float = Field(..., gt=0)
    disponible: Optional[int] = Field(default=1, ge=0, le=1)

class PostreUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    rebanadas: Optional[int] = Field(None, gt=0)
    precio_rebanada: Optional[float] = Field(None, gt=0)
    precio_total: Optional[float] = Field(None, gt=0)
    disponible: Optional[int] = Field(None, ge=0, le=1)

class PostreResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    categoria: str
    rebanadas: int
    precio_rebanada: float
    precio_total: float
    disponible: int
    
    class Config:
        from_attributes = True

# Crear la app FastAPI
app = FastAPI(
    title="API Cafetería El Rincón Mexicano - MongoDB con Auto Incremento",
    description="API NoSQL para gestionar productos y postres con IDs auto incrementales",
    version="2.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Función para inicializar datos de ejemplo
async def init_sample_data():
    """Inicializa la base de datos con categorías, productos y postres de ejemplo"""
    
    # Verificar si ya existen categorías
    count_categorias = await Categoria.count()
    
    if count_categorias == 0:
        # Inicializar contadores
        await Contador.delete_all()  # Limpiar contadores existentes
        
        # Crear contadores para cada colección
        contadores = [
            Contador(collection_name="categorias", sequence_value=0),
            Contador(collection_name="productos", sequence_value=0),
            Contador(collection_name="postres", sequence_value=0)
        ]
        await Contador.insert_many(contadores)
        
        # Crear categorías con IDs secuenciales
        categorias_data = [
            {"nombre": "torta", "descripcion": "Tortas tradicionales mexicanas"},
            {"nombre": "cuernito", "descripcion": "Cuernitos y croissants horneados"},
            {"nombre": "quesadilla", "descripcion": "Quesadillas de tortilla de maíz"},
            {"nombre": "taco", "descripcion": "Tacos variados"},
            {"nombre": "baguette", "descripcion": "Baguettes gourmet"},
            {"nombre": "bebida", "descripcion": "Bebidas frías y calientes"},
            {"nombre": "postre", "descripcion": "Postres individuales"},
            {"nombre": "pastel", "descripcion": "Pasteles completos y por rebanada"},
            {"nombre": "postre_frio", "descripcion": "Postres fríos y gelatinas"}
        ]
        
        categorias_iniciales = []
        for i, cat_data in enumerate(categorias_data, 1):
            categoria = Categoria(id=i, **cat_data)
            categorias_iniciales.append(categoria)
        
        await Categoria.insert_many(categorias_iniciales)
        # Actualizar contador de categorías
        await Contador.find_one(Contador.collection_name == "categorias").update({"$set": {"sequence_value": len(categorias_data)}})
        
        print("✅ Categorías de ejemplo insertadas correctamente")
    
    # Verificar si ya existen productos
    count_productos = await Producto.count()
    
    if count_productos == 0:
        productos_data = [
            # Tortas
            {"nombre": "Torta de Jamón", "categoria": "torta", "descripcion": "Torta con jamón, queso, aguacate, jitomate y lechuga en pan telera", "precio": 45.0},
            {"nombre": "Torta de Milanesa", "categoria": "torta", "descripcion": "Torta con milanesa de res empanizada, aguacate, jitomate, lechuga y frijoles", "precio": 60.0},
            {"nombre": "Torta Cubana", "categoria": "torta", "descripcion": "Torta con jamón, queso, milanesa, salchicha, chorizo, huevo, aguacate y frijoles", "precio": 85.0},
            
            # Cuernitos
            {"nombre": "Cuernito de Jamón y Queso", "categoria": "cuernito", "descripcion": "Croissant horneado relleno de jamón y queso gouda derretido", "precio": 38.0},
            {"nombre": "Cuernito 3 Quesos", "categoria": "cuernito", "descripcion": "Croissant horneado relleno de queso manchego, gouda y philadelphia", "precio": 42.0},
            
            # Quesadillas
            {"nombre": "Quesadilla de Queso", "categoria": "quesadilla", "descripcion": "Tortilla de maíz hecha a mano rellena de queso Oaxaca", "precio": 25.0},
            {"nombre": "Quesadilla de Hongos", "categoria": "quesadilla", "descripcion": "Tortilla de maíz hecha a mano rellena de hongos guisados y queso", "precio": 30.0},
            {"nombre": "Quesadilla de Tinga", "categoria": "quesadilla", "descripcion": "Tortilla de maíz hecha a mano rellena de tinga de pollo y queso", "precio": 35.0},
            
            # Tacos
            {"nombre": "Taco de Pastor", "categoria": "taco", "descripcion": "Tortilla de maíz con carne de cerdo marinada en adobo y piña", "precio": 18.0},
            {"nombre": "Taco de Suadero", "categoria": "taco", "descripcion": "Tortilla de maíz con carne de res suadero, cilantro y cebolla", "precio": 20.0},
            {"nombre": "Taco de Barbacoa", "categoria": "taco", "descripcion": "Tortilla de maíz con carne de barbacoa de borrego, cilantro y cebolla", "precio": 25.0},
            
            # Baguettes
            {"nombre": "Baguette Italiano", "categoria": "baguette", "descripcion": "Pan baguette con jamón serrano, queso provolone, tomate y pesto", "precio": 65.0},
            {"nombre": "Baguette de Pollo", "categoria": "baguette", "descripcion": "Pan baguette con pollo a la plancha, queso manchego, lechuga y jitomate", "precio": 60.0},
            
            # Bebidas
            {"nombre": "Café Americano", "categoria": "bebida", "descripcion": "Café de grano recién molido, 12 oz", "precio": 30.0},
            {"nombre": "Agua de Horchata", "categoria": "bebida", "descripcion": "Agua fresca de arroz con canela y vainilla, 16 oz", "precio": 25.0},
            {"nombre": "Limonada", "categoria": "bebida", "descripcion": "Limonada natural con un toque de menta, 16 oz", "precio": 28.0},
            
            # Postres individuales
            {"nombre": "Rebanada de Pastel de Chocolate", "categoria": "postre", "descripcion": "Rebanada individual de pastel de chocolate con ganache", "precio": 45.0},
            {"nombre": "Flan Individual", "categoria": "postre", "descripcion": "Porción individual de flan napolitano con caramelo", "precio": 35.0}
        ]
        
        productos_iniciales = []
        for i, prod_data in enumerate(productos_data, 1):
            producto = Producto(id=i, **prod_data)
            productos_iniciales.append(producto)
        
        await Producto.insert_many(productos_iniciales)
        # Actualizar contador de productos
        await Contador.find_one(Contador.collection_name == "productos").update({"$set": {"sequence_value": len(productos_data)}})
        
        print("✅ Productos de ejemplo insertados correctamente")
    
    # Verificar si ya existen postres
    count_postres = await Postre.count()
    
    if count_postres == 0:
        postres_data = [
            {"nombre": "Pastel de Chocolate", "descripcion": "Delicioso pastel de chocolate con ganache de chocolate oscuro y decorado con fresas", "categoria": "pastel", "rebanadas": 12, "precio_rebanada": 45.0, "precio_total": 540.0},
            {"nombre": "Cheesecake de Fresa", "descripcion": "Tarta de queso cremosa con base de galleta y cobertura de fresas naturales", "categoria": "pastel", "rebanadas": 10, "precio_rebanada": 50.0, "precio_total": 500.0},
            {"nombre": "Pastel Tres Leches", "descripcion": "Esponjoso pastel bañado en tres tipos de leche con crema chantilly y canela", "categoria": "pastel", "rebanadas": 16, "precio_rebanada": 35.0, "precio_total": 560.0},
            {"nombre": "Tarta de Manzana", "descripcion": "Clásica tarta de manzana con masa crujiente y manzanas caramelizadas", "categoria": "pastel", "rebanadas": 8, "precio_rebanada": 40.0, "precio_total": 320.0},
            {"nombre": "Pastel de Zanahoria", "descripcion": "Húmedo pastel de zanahoria con nueces y betún de queso crema", "categoria": "pastel", "rebanadas": 12, "precio_rebanada": 42.0, "precio_total": 504.0},
            {"nombre": "Tiramisú", "descripcion": "Postre italiano con capas de bizcocho bañado en café, mascarpone y cacao", "categoria": "postre_frio", "rebanadas": 9, "precio_rebanada": 55.0, "precio_total": 495.0},
            {"nombre": "Pastel Red Velvet", "descripcion": "Suave pastel de terciopelo rojo con betún de queso crema", "categoria": "pastel", "rebanadas": 14, "precio_rebanada": 48.0, "precio_total": 672.0},
            {"nombre": "Flan Napolitano Familiar", "descripcion": "Flan casero de tamaño familiar con caramelo y vainilla", "categoria": "postre_frio", "rebanadas": 10, "precio_rebanada": 25.0, "precio_total": 250.0}
        ]
        
        postres_iniciales = []
        for i, postre_data in enumerate(postres_data, 1):
            postre = Postre(id=i, **postre_data)
            postres_iniciales.append(postre)
        
        await Postre.insert_many(postres_iniciales)
        # Actualizar contador de postres
        await Contador.find_one(Contador.collection_name == "postres").update({"$set": {"sequence_value": len(postres_data)}})
        
        print("✅ Postres de ejemplo insertados correctamente")

# Inicialización de la base de datos
@app.on_event("startup")
async def startup_event():
    """Configurar la conexión a MongoDB al iniciar la aplicación"""
    
    # Obtener la URL de MongoDB desde variables de entorno
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    print(f"🔗 Conectando a MongoDB: {mongodb_url}")
    
    # Conectar a MongoDB
    client = AsyncIOMotorClient(mongodb_url)
    
    # Inicializar Beanie con la base de datos y modelos
    await init_beanie(
        database=client.cafeteria_db,
        document_models=[Contador, Categoria, Producto, Postre]
    )
    
    # Inicializar datos de ejemplo
    await init_sample_data()
    
    print("✅ Conexión a MongoDB establecida con IDs auto incrementales")

# Funciones helper para convertir documentos a response
def producto_to_response(producto: Producto) -> dict:
    """Convierte un documento Producto a diccionario para ProductoResponse"""
    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "categoria": producto.categoria,
        "descripcion": producto.descripcion,
        "precio": producto.precio,
        "disponible": producto.disponible
    }

def postre_to_response(postre: Postre) -> dict:
    """Convierte un documento Postre a diccionario para PostreResponse"""
    return {
        "id": postre.id,
        "nombre": postre.nombre,
        "descripcion": postre.descripcion,
        "categoria": postre.categoria,
        "rebanadas": postre.rebanadas,
        "precio_rebanada": postre.precio_rebanada,
        "precio_total": postre.precio_total,
        "disponible": postre.disponible
    }

# Endpoint raíz
@app.get("/")
async def read_root():
    return {
        "message": "Bienvenido a la API NoSQL de Cafetería El Rincón Mexicano",
        "database": "MongoDB",
        "version": "2.1.0",
        "puerto": "8080",
        "auto_increment": "✅ IDs secuenciales activados"
    }

# Endpoint para servir el buscador HTML
@app.get("/buscador")
async def get_buscador():
    """Sirve la página HTML del buscador"""
    if os.path.exists("buscador.html"):
        return FileResponse("buscador.html")
    else:
        raise HTTPException(status_code=404, detail="Archivo buscador.html no encontrado")

# ==================== ENDPOINTS PARA CATEGORÍAS ====================

@app.get("/categorias/", response_model=List[CategoriaResponse], tags=["categorias"])
async def listar_categorias():
    """Obtiene todas las categorías disponibles."""
    categorias = await Categoria.find_all().to_list()
    return [{"id": c.id, "nombre": c.nombre, "descripcion": c.descripcion} for c in categorias]

@app.post("/categorias/", response_model=CategoriaResponse, tags=["categorias"])
async def crear_categoria(categoria: CategoriaCreate):
    """Crea una nueva categoría."""
    nuevo_id = await get_next_sequence_value("categorias")
    nueva_categoria = Categoria(id=nuevo_id, **categoria.dict())
    await nueva_categoria.insert()
    return {"id": nueva_categoria.id, "nombre": nueva_categoria.nombre, "descripcion": nueva_categoria.descripcion}

# ==================== ENDPOINTS PARA PRODUCTOS ====================

@app.get("/productos/", response_model=List[ProductoResponse], tags=["productos"])
async def listar_productos(skip: int = 0, limit: int = 100):
    """Obtiene todos los productos disponibles en la cafetería."""
    productos = await Producto.find_all().skip(skip).limit(limit).to_list()
    return [producto_to_response(p) for p in productos]

@app.get("/productos/{producto_id}", response_model=ProductoResponse, tags=["productos"])
async def obtener_producto(producto_id: int):
    """Obtiene un producto específico por su ID."""
    producto = await Producto.find_one(Producto.id == producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto_to_response(producto)

@app.get("/productos/categoria/{categoria}", response_model=List[ProductoResponse], tags=["productos"])
async def obtener_productos_por_categoria(categoria: str):
    """Obtiene todos los productos de una categoría específica."""
    productos = await Producto.find(Producto.categoria == categoria).to_list()
    return [producto_to_response(p) for p in productos]

@app.post("/productos/", response_model=ProductoResponse, tags=["productos"])
async def crear_producto(producto: ProductoCreate):
    """Crea un nuevo producto en la base de datos."""
    nuevo_id = await get_next_sequence_value("productos")
    nuevo_producto = Producto(id=nuevo_id, **producto.dict())
    await nuevo_producto.insert()
    return producto_to_response(nuevo_producto)

@app.put("/productos/{producto_id}", response_model=ProductoResponse, tags=["productos"])
async def actualizar_producto(producto_id: int, producto_update: ProductoUpdate):
    """Actualiza un producto existente."""
    producto = await Producto.find_one(Producto.id == producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    update_data = producto_update.dict(exclude_unset=True)
    if update_data:
        await producto.update({"$set": update_data})
        producto = await Producto.find_one(Producto.id == producto_id)
    
    return producto_to_response(producto)

@app.delete("/productos/{producto_id}", tags=["productos"])
async def eliminar_producto(producto_id: int):
    """Elimina un producto de la base de datos."""
    producto = await Producto.find_one(Producto.id == producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    nombre_producto = producto.nombre
    await producto.delete()
    
    return {"message": f"Producto '{nombre_producto}' eliminado correctamente"}

# ==================== ENDPOINTS PARA POSTRES ====================

@app.get("/postres/", response_model=List[PostreResponse], tags=["postres"])
async def listar_postres(skip: int = 0, limit: int = 100):
    """Obtiene todos los postres disponibles en la cafetería."""
    postres = await Postre.find_all().skip(skip).limit(limit).to_list()
    return [postre_to_response(p) for p in postres]

@app.get("/postres/{postre_id}", response_model=PostreResponse, tags=["postres"])
async def obtener_postre(postre_id: int):
    """Obtiene un postre específico por su ID."""
    postre = await Postre.find_one(Postre.id == postre_id)
    if postre is None:
        raise HTTPException(status_code=404, detail="Postre no encontrado")
    return postre_to_response(postre)

@app.get("/postres/categoria/{categoria}", response_model=List[PostreResponse], tags=["postres"])
async def obtener_postres_por_categoria(categoria: str):
    """Obtiene todos los postres de una categoría específica."""
    postres = await Postre.find(Postre.categoria == categoria).to_list()
    return [postre_to_response(p) for p in postres]

@app.post("/postres/", response_model=PostreResponse, tags=["postres"])
async def crear_postre(postre: PostreCreate):
    """Crea un nuevo postre en la base de datos."""
    nuevo_id = await get_next_sequence_value("postres")
    nuevo_postre = Postre(id=nuevo_id, **postre.dict())
    await nuevo_postre.insert()
    return postre_to_response(nuevo_postre)

@app.put("/postres/{postre_id}", response_model=PostreResponse, tags=["postres"])
async def actualizar_postre(postre_id: int, postre_update: PostreUpdate):
    """Actualiza un postre existente."""
    postre = await Postre.find_one(Postre.id == postre_id)
    if postre is None:
        raise HTTPException(status_code=404, detail="Postre no encontrado")
    
    update_data = postre_update.dict(exclude_unset=True)
    if update_data:
        await postre.update({"$set": update_data})
        postre = await Postre.find_one(Postre.id == postre_id)
    
    return postre_to_response(postre)

@app.delete("/postres/{postre_id}", tags=["postres"])
async def eliminar_postre(postre_id: int):
    """Elimina un postre de la base de datos."""
    postre = await Postre.find_one(Postre.id == postre_id)
    if postre is None:
        raise HTTPException(status_code=404, detail="Postre no encontrado")
    
    nombre_postre = postre.nombre
    await postre.delete()
    
    return {"message": f"Postre '{nombre_postre}' eliminado correctamente"}

# ==================== ENDPOINTS DE BÚSQUEDA ====================

@app.get("/buscar/{termino}", tags=["busqueda"])
async def buscar_global(termino: str):
    """
    Busca un término en productos y postres (nombre, descripción y categoría).
    La búsqueda es case-insensitive.
    """
    # Búsqueda en productos usando regex (insensible a mayúsculas)
    productos = await Producto.find({
        "$or": [
            {"nombre": {"$regex": termino, "$options": "i"}},
            {"descripcion": {"$regex": termino, "$options": "i"}},
            {"categoria": {"$regex": termino, "$options": "i"}}
        ]
    }).to_list()
    
    # Búsqueda en postres usando regex (insensible a mayúsculas)
    postres = await Postre.find({
        "$or": [
            {"nombre": {"$regex": termino, "$options": "i"}},
            {"descripcion": {"$regex": termino, "$options": "i"}},
            {"categoria": {"$regex": termino, "$options": "i"}}
        ]
    }).to_list()
    
    # Formatear resultados para que coincidan con el buscador HTML
    resultados = {
        "termino_busqueda": termino,
        "productos": [
            {
                "tipo": "Producto",
                "id": p.id,  # Ahora es entero
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "categoria": p.categoria,
                "precio": f"${p.precio:.2f}",
                "disponible": "Sí" if p.disponible else "No"
            }
            for p in productos
        ],
        "postres": [
            {
                "tipo": "Postre",
                "id": p.id,  # Ahora es entero
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "categoria": p.categoria,
                "precio_rebanada": f"${p.precio_rebanada:.2f}",
                "precio_total": f"${p.precio_total:.2f}",
                "rebanadas": p.rebanadas,
                "disponible": "Sí" if p.disponible else "No"
            }
            for p in postres
        ],
        "total_resultados": len(productos) + len(postres)
    }
    
    return resultados

# ==================== ENDPOINTS DE RELACIONES (SIMPLES) ====================

@app.get("/productos/{producto_id}/misma-categoria", response_model=List[PostreResponse], tags=["relaciones"])
async def obtener_postres_misma_categoria(producto_id: int):
    """Obtiene todos los postres de la misma categoría que un producto"""
    producto = await Producto.find_one(Producto.id == producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    postres = await Postre.find(Postre.categoria == producto.categoria).to_list()
    return [postre_to_response(p) for p in postres]

@app.get("/postres/{postre_id}/misma-categoria", response_model=List[ProductoResponse], tags=["relaciones"])
async def obtener_productos_misma_categoria(postre_id: int):
    """Obtiene todos los productos de la misma categoría que un postre"""
    postre = await Postre.find_one(Postre.id == postre_id)
    if postre is None:
        raise HTTPException(status_code=404, detail="Postre no encontrado")
    
    productos = await Producto.find(Producto.categoria == postre.categoria).to_list()
    return [producto_to_response(p) for p in productos]

# ==================== ENDPOINTS DE ESTADÍSTICAS ====================

@app.get("/estadisticas/", tags=["estadísticas"])
async def obtener_estadisticas():
    """Obtiene estadísticas generales de productos y postres."""
    # Estadísticas de productos por categoría
    pipeline_productos = [
        {
            "$group": {
                "_id": "$categoria",
                "total_productos": {"$sum": 1},
                "precio_promedio": {"$avg": "$precio"},
                "precio_minimo": {"$min": "$precio"},
                "precio_maximo": {"$max": "$precio"}
            }
        },
        {
            "$sort": {"total_productos": -1}
        }
    ]
    
    estadisticas_productos = await Producto.aggregate(pipeline_productos).to_list()
    total_productos = await Producto.count()
    total_postres = await Postre.count()
    
    # Estadísticas de postres por categoría
    pipeline_postres = [
        {
            "$group": {
                "_id": "$categoria",
                "total_postres": {"$sum": 1},
                "precio_promedio_rebanada": {"$avg": "$precio_rebanada"},
                "precio_promedio_total": {"$avg": "$precio_total"}
            }
        },
        {
            "$sort": {"total_postres": -1}
        }
    ]
    
    estadisticas_postres = await Postre.aggregate(pipeline_postres).to_list()
    
    return {
        "resumen": {
            "total_productos": total_productos,
            "total_postres": total_postres,
            "total_categorias": len(set([p["_id"] for p in estadisticas_productos] + [p["_id"] for p in estadisticas_postres]))
        },
        "estadisticas_productos": estadisticas_productos,
        "estadisticas_postres": estadisticas_postres
    }

# ==================== ENDPOINT PARA VER CONTADORES ====================

@app.get("/contadores/", tags=["administración"])
async def obtener_contadores():
    """Obtiene los valores actuales de los contadores de auto incremento"""
    contadores = await Contador.find_all().to_list()
    return {
        "contadores": [
            {
                "coleccion": c.collection_name,
                "proximo_id": c.sequence_value + 1,
                "ultimo_id_usado": c.sequence_value
            }
            for c in contadores
        ]
    }

# Punto de entrada para ejecutar la aplicación
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)