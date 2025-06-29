// Script de inicialización para MongoDB con Auto Incremento
// Este archivo se ejecuta automáticamente cuando se crea el contenedor

// Cambiar a la base de datos de la cafetería
db = db.getSiblingDB('cafeteria_db');

// Crear un usuario para la aplicación
db.createUser({
  user: 'cafeteria_user',
  pwd: 'cafeteria_pass',
  roles: [
    {
      role: 'readWrite',
      db: 'cafeteria_db'
    }
  ]
});

// ==================== ÍNDICES PARA CONTADORES ====================
db.contadores.createIndex({ "collection_name": 1 }, { unique: true });

print('✅ Índices de contadores creados');

// ==================== ÍNDICES PARA CATEGORÍAS ====================
db.categorias.createIndex({ "_id": 1 }, { unique: true });
db.categorias.createIndex({ "nombre": 1 }, { unique: true });
db.categorias.createIndex({ "descripcion": 1 });

print('✅ Índices de categorías creados');

// ==================== ÍNDICES PARA PRODUCTOS ====================
// Crear índices para mejorar el rendimiento
db.productos.createIndex({ "_id": 1 }, { unique: true });
db.productos.createIndex({ "nombre": 1 });
db.productos.createIndex({ "categoria": 1 });
db.productos.createIndex({ "precio": 1 });
db.productos.createIndex({ "disponible": 1 });

// Índice compuesto para búsquedas por categoría y disponibilidad
db.productos.createIndex({ "categoria": 1, "disponible": 1 });

// Índice de texto para búsquedas
db.productos.createIndex({
  "nombre": "text",
  "descripcion": "text",
  "categoria": "text"
}, {
  default_language: 'spanish',
  name: 'busqueda_texto_productos'
});

print('✅ Índices de productos creados');

// ==================== ÍNDICES PARA POSTRES ====================
// Índices simples para postres
db.postres.createIndex({ "_id": 1 }, { unique: true });
db.postres.createIndex({ "nombre": 1 });
db.postres.createIndex({ "categoria": 1 });
db.postres.createIndex({ "precio_rebanada": 1 });
db.postres.createIndex({ "precio_total": 1 });
db.postres.createIndex({ "rebanadas": 1 });
db.postres.createIndex({ "disponible": 1 });

// Índice compuesto para búsquedas por categoría
db.postres.createIndex({ "categoria": 1, "disponible": 1 });

// Índice de texto para búsquedas en postres
db.postres.createIndex({
  "nombre": "text",
  "descripcion": "text",
  "categoria": "text"
}, {
  default_language: 'spanish',
  name: 'busqueda_texto_postres'
});

print('✅ Índices de postres creados');

// ==================== VALIDACIONES DE ESQUEMA ====================

// Validación para contadores
db.runCommand({
  collMod: "contadores",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["collection_name", "sequence_value"],
      properties: {
        collection_name: {
          bsonType: "string",
          description: "Nombre de la colección debe ser string"
        },
        sequence_value: {
          bsonType: "int",
          minimum: 0,
          description: "Valor de secuencia debe ser entero positivo"
        }
      }
    }
  }
});

// Validación para productos con IDs enteros
db.runCommand({
  collMod: "productos",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "nombre", "categoria", "descripcion", "precio", "disponible"],
      properties: {
        _id: {
          bsonType: "int",
          minimum: 1,
          description: "ID debe ser entero positivo"
        },
        nombre: {
          bsonType: "string",
          maxLength: 100,
          description: "Nombre del producto debe ser string de máximo 100 caracteres"
        },
        categoria: {
          bsonType: "string",
          description: "Categoría debe ser string válido"
        },
        descripcion: {
          bsonType: "string",
          description: "Descripción debe ser string"
        },
        precio: {
          bsonType: "double",
          minimum: 0,
          description: "Precio debe ser positivo"
        },
        disponible: {
          bsonType: "int",
          minimum: 0,
          maximum: 1,
          description: "Disponible debe ser 0 o 1"
        }
      }
    }
  }
});

// Validación para postres con IDs enteros
db.runCommand({
  collMod: "postres",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "nombre", "descripcion", "categoria", "rebanadas", "precio_rebanada", "precio_total", "disponible"],
      properties: {
        _id: {
          bsonType: "int",
          minimum: 1,
          description: "ID debe ser entero positivo"
        },
        nombre: {
          bsonType: "string",
          maxLength: 100,
          description: "Nombre del postre debe ser string de máximo 100 caracteres"
        },
        categoria: {
          bsonType: "string",
          description: "Categoría debe ser string válido"
        },
        descripcion: {
          bsonType: "string",
          description: "Descripción debe ser string"
        },
        rebanadas: {
          bsonType: "int",
          minimum: 1,
          description: "Rebanadas debe ser positivo"
        },
        precio_rebanada: {
          bsonType: "double",
          minimum: 0,
          description: "Precio por rebanada debe ser positivo"
        },
        precio_total: {
          bsonType: "double",
          minimum: 0,
          description: "Precio total debe ser positivo"
        },
        disponible: {
          bsonType: "int",
          minimum: 0,
          maximum: 1,
          description: "Disponible debe ser 0 o 1"
        }
      }
    }
  }
});

// Validación para categorías con IDs enteros
db.runCommand({
  collMod: "categorias",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "nombre", "descripcion"],
      properties: {
        _id: {
          bsonType: "int",
          minimum: 1,
          description: "ID debe ser entero positivo"
        },
        nombre: {
          bsonType: "string",
          maxLength: 50,
          description: "Nombre de categoría debe ser string de máximo 50 caracteres"
        },
        descripcion: {
          bsonType: "string",
          description: "Descripción debe ser string"
        }
      }
    }
  }
});

print('✅ Validaciones de esquema aplicadas');

// ==================== FUNCIONES DE AUTO INCREMENTO ====================

// Función para obtener el siguiente ID
db.system.js.save({
  _id: "getNextSequence",
  value: function(collectionName) {
    var result = db.contadores.findAndModify({
      query: { collection_name: collectionName },
      update: { $inc: { sequence_value: 1 } },
      new: true,
      upsert: true
    });
    return result.sequence_value;
  }
});

// Función para verificar integridad de IDs
db.system.js.save({
  _id: "verificarIntegridadIDs",
  value: function() {
    var colecciones = ["productos", "postres", "categorias"];
    var resultado = {};
    
    colecciones.forEach(function(coleccion) {
      var count = db[coleccion].count();
      var maxId = db[coleccion].findOne({}, {_id: 1}, {sort: {_id: -1}});
      var contador = db.contadores.findOne({collection_name: coleccion});
      
      resultado[coleccion] = {
        total_documentos: count,
        max_id: maxId ? maxId._id : 0,
        contador_actual: contador ? contador.sequence_value : 0,
        integridad: (maxId && contador) ? (maxId._id === contador.sequence_value) : false
      };
    });
    
    return resultado;
  }
});

print('✅ Funciones de auto incremento creadas');

print('✅ Base de datos MongoDB inicializada correctamente con sistema de auto incremento');

// Mostrar resumen de colecciones
print('\n📊 RESUMEN DE COLECCIONES:');
print('- contadores: Sistema de auto incremento para IDs');
print('- categorias: Categorías de productos y postres (IDs: 1, 2, 3...)');
print('- productos: Productos de la cafetería (IDs: 1, 2, 3...)');
print('- postres: Postres disponibles por rebanadas (IDs: 1, 2, 3...)');

print('\n🔢 SISTEMA DE AUTO INCREMENTO:');
print('- IDs inician en 1 para cada colección');
print('- Incremento automático al insertar nuevos documentos');
print('- Función getNextSequence() disponible');
print('- Función verificarIntegridadIDs() para auditoría');

print('\n🔍 FUNCIONALIDADES:');
print('- Búsqueda de texto completo en productos y postres');
print('- Relaciones por categoría entre productos y postres');
print('- Índices optimizados para consultas rápidas');
print('- Validaciones de esquema para integridad de datos');
print('- IDs secuenciales como en bases de datos relacionales');

print('\n✨ MongoDB NoSQL con Auto Incremento configurado correctamente!');