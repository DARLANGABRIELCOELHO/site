# rotas das páginas do sistema, cada página tem uma função específica para exibir informações e permitir a interação dos usuários com os dados do sistema. As páginas incluem:
# dashboard, clientes, tecnicos, vendas, garantia, laboratorio e catalogo. Cada página é responsável por exibir informações relevantes e permitir que os usuários realizem ações específicas relacionadas a cada área do sistema, como gerenciar clientes, técnicos, vendas, garantias, serviços em andamento e o catálogo de produtos disponíveis.
from component.sidebar import create_sidebar
from pages.dashboard import clientes_data, produtos, celulares, servicos, vendas, ordens_de_servico, tecnicos_data
from pages.laboratorio import ordens_de_servico
from pages.vendas import vendas, produtos, celulares, clientes_data
from pages.clientes import clientes_data
from pages.garantia import vendas, ordens_de_servico
from pages.catalogo import produtos, celulares, servicos
from pages.tecnicos import tecnicos_data
