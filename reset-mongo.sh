#!/bin/bash

echo "🔄 Reinicializando MongoDB..."

# Detener contenedores
echo "📦 Deteniendo contenedores..."
docker-compose down

# Eliminar volúmenes para empezar limpio
echo "🗑️ Eliminando volúmenes..."
docker-compose down -v

# Limpiar sistema
echo "🧹 Limpiando sistema..."
docker system prune -f

# Reconstruir
echo "🔨 Reconstruyendo contenedores..."
docker-compose up --build -d

echo "⏳ Esperando que los servicios estén listos..."
sleep 15

echo ""
echo "🎉 ¡MongoDB reinicializado!"
echo ""
echo "📊 Servicios disponibles:"
echo "  - API: http://localhost:8080"
echo "  - Documentación: http://localhost:8080/docs"
echo "  - Buscador: http://localhost:8080/buscador"
echo "  - Mongo Express: http://localhost:8082 (admin/admin123)"
echo ""
echo "🔧 Verificar datos:"
echo "  curl http://localhost:8080/productos/"
echo "  curl http://localhost:8080/postres/"
echo "  curl http://localhost:8080/categorias/"