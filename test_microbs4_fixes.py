
# test_microbs4_fixes.py - Prueba para verificar las correcciones
from microbs4 import MicroBS4

def test_find_all_expanded():
    """
    Prueba con HTML expandido para verificar búsquedas más completas
    """
    # HTML con más variedad de elementos y clases
    html = '''
    <div class="container main-container">
        <header class="header">
            <h1 class="title">Título de la página</h1>
            <nav class="navigation">
                <ul class="menu">
                    <li class="menu-item active"><a href="#home">Inicio</a></li>
                    <li class="menu-item"><a href="#about">Acerca de</a></li>
                    <li class="menu-item"><a href="#services">Servicios</a></li>
                    <li class="menu-item"><a href="#contact">Contacto</a></li>
                </ul>
            </nav>
        </header>
        
        <main class="content">
            <section class="item section featured">
                <h2 class="section-title">Artículo destacado</h2>
                <p class="text">Este es un artículo destacado.</p>
                <div class="item multi class test highlight">Item con múltiples clases destacado</div>
            </section>
            
            <section class="item section">
                <h2 class="section-title">Sección regular</h2>
                <div class="card-container">
                    <div class="card item">Item 1</div>
                    <div class="card item">Item 2</div>
                    <div class="card item">Item 3</div>
                    <div class="card item selected">Item 4 (seleccionado)</div>
                    <div class="card item">Item 5</div>
                </div>
            </section>
            
            <aside class="sidebar item">
                <div class="widget">
                    <h3 class="widget-title">Enlaces</h3>
                    <ul class="links">
                        <li class="link-item"><a href="#link1">Enlace 1</a></li>
                        <li class="link-item"><a href="#link2">Enlace 2</a></li>
                        <li class="link-item"><a href="#link3">Enlace 3</a></li>
                    </ul>
                </div>
                <div class="widget item multi class test">
                    <h3 class="widget-title">Categorías</h3>
                    <ul class="categories">
                        <li class="category-item">Categoría 1</li>
                        <li class="category-item selected">Categoría 2</li>
                        <li class="category-item">Categoría 3</li>
                    </ul>
                </div>
            </aside>
        </main>
        
        <footer class="footer">
            <div class="footer-content">
                <div class="copyright item">© 2025 MicroBS4</div>
                <div class="social-links">
                    <a href="#twitter" class="social-link item">Twitter</a>
                    <a href="#facebook" class="social-link item multi class test">Facebook</a>
                    <a href="#instagram" class="social-link item">Instagram</a>
                </div>
            </div>
        </footer>
    </div>
    '''
    
    print("=== PRUEBA DE BÚSQUEDA CON HTML EXPANDIDO ===")
    soup = MicroBS4(html)
    
    # Lista de pruebas a realizar
    test_cases = [
        {"tag": "div", "class_name": "item", "expected_count": "múltiples", "description": "divs con clase 'item'"},
        {"tag": "div", "class_name": "multi", "expected_count": 3, "description": "divs con clase 'multi'"},
        {"tag": "div", "class_name": "test", "expected_count": 3, "description": "divs con clase 'test'"},
        {"tag": "div", "class_name": "highlight", "expected_count": 1, "description": "divs con clase 'highlight'"},
        {"tag": "li", "class_name": "selected", "expected_count": 1, "description": "elementos li seleccionados"},
        {"tag": "a", "class_name": "social-link", "expected_count": 3, "description": "enlaces sociales"},
        {"tag": "a", "class_name": "multi", "expected_count": 1, "description": "enlaces con múltiples clases"},
        {"tag": "section", "class_name": "featured", "expected_count": 1, "description": "secciones destacadas"},
        {"tag": "h2", "class_name": None, "expected_count": 2, "description": "todos los h2"},
        {"tag": "ul", "class_name": None, "expected_count": 3, "description": "todas las listas ul"}
    ]
    
    # Ejecutar cada prueba y mostrar resultados
    for i, test in enumerate(test_cases, 1):
        tag = test["tag"]
        class_name = test["class_name"]
        expected = test["expected_count"]
        desc = test["description"]
        
        # Realizar la búsqueda
        results = soup.find_all(tag, class_name=class_name)
        
        # Mostrar resultados
        print(f"\n{i}. Búsqueda de {desc}:")
        print(f"   Encontrados: {len(results)}")
        
        # Verificar cantidad esperada
        if expected == "múltiples":
            if len(results) > 1:
                print(f"   ✓ CORRECTO: Se encontraron múltiples elementos ({len(results)})")
            else:
                print(f"   ✗ ERROR: Se esperaban múltiples elementos, pero se encontraron {len(results)}")
        else:
            if len(results) == expected:
                print(f"   ✓ CORRECTO: Se encontraron exactamente {expected} elementos")
            else:
                print(f"   ✗ ERROR: Se encontraron {len(results)} elementos cuando deberían ser {expected}")
        
        # Mostrar los primeros elementos encontrados (máximo 3)
        print("   Elementos encontrados (muestra):")
        for j, item in enumerate(results[:3], 1):
            # Extraer texto simplificado
            text = item.get_text().strip()
            if len(text) > 40:
                text = text[:37] + "..."
            print(f"     - {j}. {text}")
        
        # Si hay más elementos, mostrar cuántos más
        if len(results) > 3:
            print(f"     (y {len(results) - 3} más...)")
    
    # Verificación adicional para elementos anidados
    print("\nVerificación de búsqueda anidada:")
    
    # Primero encontrar un contenedor
    sidebar = soup.find("aside", class_name="sidebar")
    if sidebar:
        print("✓ Encontrada la barra lateral")
        
        # Buscar elementos dentro de ese contenedor
        widgets = sidebar.find_all("div", class_name="widget")
        print(f"  - Widgets en la barra lateral: {len(widgets)}")
        
        # Buscar elementos li dentro de la barra lateral
        items = sidebar.find_all("li")
        print(f"  - Elementos de lista en la barra lateral: {len(items)}")
        
        # Buscar elementos específicos por selector
        categories = sidebar.select(".category-item")
        print(f"  - Categorías seleccionadas: {len(categories)}")
        
        # Buscar elemento seleccionado dentro de la barra lateral
        selected = sidebar.find("li", class_name="selected")
        if selected:
            print(f"  - Elemento seleccionado: '{selected.get_text().strip()}'")
    else:
        print("✗ No se encontró la barra lateral")
    
    print("\nPrueba completada.")

# Ejecutar la prueba
if __name__ == "__main__":
    test_find_all_expanded()
