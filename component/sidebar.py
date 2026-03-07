# O arquivo sidebar.py é responsável por criar a barra lateral do sistema, que contém as rotas para as diferentes páginas do sistema. Ele define uma função create_sidebar() que retorna um dicionário com as rotas das páginas, permitindo que os usuários naveguem facilmente entre as diferentes seções do sistema.
def create_sidebar():
    menu_routes = {
        "dashboard": "/pages/dashboard.py",
        "laboratorio": "/pages/laboratorio.py",
        "vendas": "/pages/vendas.py",
        "clientes": "/pages/clientes.py",
        "garantia": "/pages/garantia.py",
        "catalogo": "/pages/catalogo.py",
        "tecnicos": "/pages/tecnicos.py",
    }
    return menu_routes
