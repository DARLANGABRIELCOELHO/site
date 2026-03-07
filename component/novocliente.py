# novocliente é a página onde os usuários podem adicionar um novo cliente ao sistema. Ele inclui um formulário para inserir informações como nome, número de contato, documento, endereço e observações. Após o preenchimento do formulário, os dados do cliente são salvos no banco de dados e o usuário é redirecionado para a página de clientes, onde o novo cliente pode ser visualizado na lista.
# ele é apenas o front para adicionar um novo cliente, a lógica de salvamento dos dados no banco de dados é tratada em outro módulo.
from data.database import clientes_data
from datetime import datetime
def novocliente():
    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone")
    documento = st.text_input("Documento")
    endereco = st.text_input("Endereço")
    observacoes = st.text_input("Observações")
    data_cadastro = datetime.now().strftime("%d/%m/%Y")
    if st.button("Salvar"):
        clientes_data.append({"nome": nome, "telefone": telefone, "documento": documento, "endereco": endereco, "observacoes": observacoes, "data_cadastro": data_cadastro})
        st.success("Cliente salvo com sucesso!")
        st.rerun()
def editarcliente():
    nome = st.text_input("Nome")
    telefone = st.text_input("Telefone")
    documento = st.text_input("Documento")
    endereco = st.text_input("Endereço")
    observacoes = st.text_input("Observações")
    data_cadastro = datetime.now().strftime("%d/%m/%Y")
    if st.button("Salvar"):
        clientes_data.append({"nome": nome, "telefone": telefone, "documento": documento, "endereco": endereco, "observacoes": observacoes, "data_cadastro": data_cadastro})
        st.success("Cliente salvo com sucesso!")
        st.rerun()  