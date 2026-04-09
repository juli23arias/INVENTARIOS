import os
import django
from decimal import Decimal

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from usuarios.models import Usuario
from productos.models import Producto
from proveedores.models import Proveedor, Compra, DetalleCompra
from inventario.models import InventarioHistorial
from ventas.models import Venta, DetalleVenta

def run_seeder():
    print("Iniciando carga de datos iniciales ampliada...")

    # 1. Crear usuarios (Admin y Cajero)
    # Admin
    admin_user, created = Usuario.objects.get_or_create(username='admin', defaults={'email': 'admin@correo.com', 'rol': 'ADMIN'})
    admin_user.set_password('admin123')
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()

    # Cajero
    cajero_user, created = Usuario.objects.get_or_create(username='cajero', defaults={'email': 'cajero@correo.com', 'rol': 'CAJERO'})
    cajero_user.set_password('cajero123')
    cajero_user.save()

    print("[OK] Usuarios cargados.")

    # 2. Crear Proveedores (2 obligatorios)
    prov1, _ = Proveedor.objects.get_or_create(nombre='AgroInsumos S.A.', defaults={'contacto':'Carlos Pérez', 'telefono':'0991234567', 'email':'ventas@agroinsumos.com'})
    prov2, _ = Proveedor.objects.get_or_create(nombre='Distribuidora Herramientas', defaults={'contacto':'María López', 'telefono':'0987654321', 'email':'contacto@distri.com'})
    print("[OK] Proveedores cargados.")

    # 3. Crear Productos (5 obligatorios)
    productos_data = [
        {'nombre': 'Pala Tramontina', 'precio': '15.50', 'stock': 20, 'categoria': 'Herramientas', 'stock_minimo': 5},
        {'nombre': 'Fertilizante NPK 50kg', 'precio': '45.00', 'stock': 10, 'categoria': 'Fertilizantes', 'stock_minimo': 3},
        {'nombre': 'Machete Collin', 'precio': '8.25', 'stock': 50, 'categoria': 'Herramientas', 'stock_minimo': 10},
        {'nombre': 'Semillas de Maíz Trueno 1kg', 'precio': '5.00', 'stock': 100, 'categoria': 'Semillas', 'stock_minimo': 20},
        {'nombre': 'Bomba Fumigadora 20L', 'precio': '35.00', 'stock': 2, 'categoria': 'Equipos', 'stock_minimo': 3},
    ]

    prods = []
    for pd in productos_data:
        p, created = Producto.objects.get_or_create(
            nombre=pd['nombre'],
            defaults={
                'precio': Decimal(pd['precio']),
                'stock': pd['stock'],
                'categoria': pd['categoria'],
                'stock_minimo': pd['stock_minimo']
            }
        )
        prods.append(p)
        if created:
            # Movimiento de inventario 1: Ajuste manual inicial
            InventarioHistorial.objects.create(
                producto=p,
                tipo_movimiento='AJUSTE',
                cantidad=p.stock
            )
    print("[OK] Productos cargados.")

    # 4. Crear 2 Compras
    if Compra.objects.count() == 0:
        c1 = Compra.objects.create(proveedor=prov1)
        DetalleCompra.objects.create(compra=c1, producto=prods[1], cantidad=5, precio_compra=Decimal('40.00'))
        c1.detalles.first().producto.stock += 5
        c1.detalles.first().producto.save()
        InventarioHistorial.objects.create(producto=prods[1], tipo_movimiento='ENTRADA', cantidad=5)

        c2 = Compra.objects.create(proveedor=prov2)
        DetalleCompra.objects.create(compra=c2, producto=prods[0], cantidad=10, precio_compra=Decimal('12.00'))
        c2.detalles.first().producto.stock += 10
        c2.detalles.first().producto.save()
        InventarioHistorial.objects.create(producto=prods[0], tipo_movimiento='ENTRADA', cantidad=10)
        print("[OK] 2 Compras simuladas exitosamente.")

    # 5. Crear 2 Ventas
    if Venta.objects.count() == 0:
        v1 = Venta.objects.create(usuario=cajero_user)
        DetalleVenta.objects.create(venta=v1, producto=prods[3], cantidad=10, precio_unitario=prods[3].precio)
        v1.total = prods[3].precio * 10
        v1.save()
        prods[3].stock -= 10
        prods[3].save()
        InventarioHistorial.objects.create(producto=prods[3], tipo_movimiento='SALIDA', cantidad=10)

        v2 = Venta.objects.create(usuario=cajero_user)
        DetalleVenta.objects.create(venta=v2, producto=prods[2], cantidad=2, precio_unitario=prods[2].precio)
        v2.total = prods[2].precio * 2
        v2.save()
        prods[2].stock -= 2
        prods[2].save()
        InventarioHistorial.objects.create(producto=prods[2], tipo_movimiento='SALIDA', cantidad=2)
        print("[OK] 2 Ventas simuladas exitosamente.")

    print("\n--- BASE LATENTE REESTRUCTURADA ---")
    print("Todo listo y funcional.")

if __name__ == '__main__':
    run_seeder()
