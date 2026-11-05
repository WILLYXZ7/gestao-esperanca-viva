from app.models import Atendimento, ItemDoacao

def test_login_fluxo_sucesso_e_falha(client):
    # GET tela de login
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Acesso Operacional' in response.data

    # POST com credenciais inválidas
    response_erro = client.post('/login', data={
        'email': 'regina.alves@esperancaviva.org',
        'password': 'SenhaInvalidaErrada'
    }, follow_redirects=True)
    assert b'E-mail ou senha incorretos' in response_erro.data

    # POST com credenciais válidas
    response_ok = client.post('/login', data={
        'email': 'regina.alves@esperancaviva.org',
        'password': 'Esperanca@2026'
    }, follow_redirects=True)
    assert response_ok.status_code == 200
    assert b'Atendimento Comunit' in response_ok.data

def test_rota_protegida_redireciona_anonimo(client):
    # Tentativa de acessar sem login
    response = client.get('/atendimento', follow_redirects=True)
    assert b'Acesso Operacional' in response.data
    assert b'login para acessar' in response.data

def test_atendimento_busca_e_registro(auth_client, app):
    # Buscar por Maria Aparecida
    resp_busca = auth_client.get('/atendimento?busca=Maria')
    assert resp_busca.status_code == 200
    assert b'Maria Aparecida da Silva' in resp_busca.data
    assert b'LIBERADA P/ RETIRADA' in resp_busca.data

    # Registrar entrega de cesta
    resp_post = auth_client.post('/atendimento/1/registrar', data={
        'observacoes': 'Entrega validada em teste automatizado'
    }, follow_redirects=True)
    assert resp_post.status_code == 200
    assert b'confirmada com sucesso' in resp_post.data

    # Tentar registrar novamente para a mesma família no mesmo mês (deve bloquear)
    resp_post_duplicado = auth_client.post('/atendimento/1/registrar', data={
        'observacoes': 'Tentativa duplicada'
    }, follow_redirects=True)
    assert b'BLOQUEADO' in resp_post_duplicado.data

def test_estoque_listagem_e_cadastro(auth_client, app):
    # Acessar listagem de estoque
    resp_estoque = auth_client.get('/estoque')
    assert resp_estoque.status_code == 200
    assert b'Leite Integral UHT' in resp_estoque.data
    assert b'CR' in resp_estoque.data  # CRÍTICO

    # Cadastrar nova doação
    resp_novo = auth_client.post('/estoque/novo', data={
        'nome_alimento': 'Macarrão Parafuso',
        'quantidade': '30',
        'unidade_medida': 'pacotes',
        'categoria': 'Não perecíveis',
        'data_validade': '2026-12-31'
    }, follow_redirects=True)
    assert resp_novo.status_code == 200
    assert b'Macarr' in resp_novo.data
