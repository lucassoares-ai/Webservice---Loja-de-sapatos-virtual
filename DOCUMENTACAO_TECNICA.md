# Documentação Técnica Completa - Sistema de Loja de Sapatos Virtual

## Sumário
1.  [Introdução e Objetivos](#1-introdução-e-objetivos)
2.  [Arquitetura do Sistema](#2-arquitetura-do-sistema)
3.  [Tecnologias Utilizadas](#3-tecnologias-utilizadas)
4.  [Análise Detalhada do Código (Models)](#4-análise-detalhada-do-código-models)
    *   [Classe Produto (Encapsulada)](#41-classe-produto-encapsulada)
    *   [Classe ItemCarrinho (Simples)](#42-classe-itemcarrinho-simples)
    *   [Classe Pedido (Histórico)](#43-classe-pedido-histórico)
    *   [Classe Loja (Gerenciador)](#44-classe-loja-gerenciador)
5.  [Catálogo Exaustivo de Endpoints e Rotas](#5-catálogo-exaustivo-de-endpoints-e-rotas)
    *   [Conceito de Endpoint](#51-conceito-de-endpoint)
    *   [Rotas Públicas](#52-rotas-públicas)
    *   [Rotas de Compra (Carrinho/Checkout)](#53-rotas-de-compra-carrinhocheckout)
    *   [Rotas de Usuário (Área Logada)](#54-rotas-de-usuário-área-logada)
6.  [Frontend e Templates (Jinja2)](#6-frontend-e-templates-jinja2)
7.  [Gerenciamento de Sessão e Segurança](#7-gerenciamento-de-sessão-e-segurança)
8.  [Glossário Técnico](#8-glossário-técnico)

---

## 1. Introdução e Objetivos

Este documento serve como o manual técnico definitivo para o projeto "Loja de Sapatos Virtual". O sistema foi desenvolvido como um projeto acadêmico para demonstrar a aplicação prática de conceitos de **Programação Orientada a Objetos (POO)** em um ambiente web real.

O objetivo não é apenas criar uma loja funcional, mas sim criar um código que sirva de exemplo de como estruturar classes, métodos e atributos de forma inteligente, equilibrando rigor técnico (encapsulamento) com simplicidade prática.

---

## 2. Arquitetura do Sistema

O sistema segue uma arquitetura **Monolítica Modular** baseada no padrão **MVC (Model-View-Controller)**, adaptada para o framework Flask.

### 2.1. O Padrão Híbrido de Encapsulamento
Uma das decisões de design mais importantes deste projeto foi o uso de um **Encapsulamento Híbrido**. Em vez de aplicar regras rígidas de POO em todo lugar (o que tornaria o código verboso e difícil de ler), aplicamos o encapsulamento onde ele traz mais valor:

1.  **Classes Críticas (`Loja`, `Produto`)**:
    *   Estas classes representam o "coração" e os dados mestres do sistema.
    *   **Regra**: Atributos são protegidos (`_atributo`) e acessados apenas via métodos ou properties (`@property`).
    *   **Por quê?**: Para garantir a integridade. Não queremos que um erro de programação altere o preço de um produto ou apague a lista de vendas acidentalmente.

2.  **Classes de Transferência (`ItemCarrinho`, `Pedido`)**:
    *   Estas classes representam dados passageiros ou registros históricos imutáveis.
    *   **Regra**: Atributos são públicos (acesso direto).
    *   **Por quê?**: Para simplificar. Um item no carrinho é apenas um agrupamento de dados (nome, preço, quantidade). Criar getters e setters para isso seria apenas "ruído" no código.

---

## 3. Tecnologias Utilizadas

*   **Python 3.x**: A linguagem base. Escolhida por sua clareza e poder.
*   **Flask**: Um "micro-framework" web. Ele é responsável por receber as requisições do navegador e decidir qual função Python deve rodar.
*   **Jinja2**: O motor de templates. Ele permite misturar HTML com lógica Python (como loops `for` e condicionais `if`) para criar páginas dinâmicas.
*   **Werkzeug**: Biblioteca utilitária que roda por baixo do Flask, lidando com a parte "chata" do protocolo HTTP.

---

## 4. Análise Detalhada do Código (Models)

Nesta seção, dissecamos cada classe definida no arquivo `app.py`.

### 4.1. Classe `Produto` (Encapsulada)
Esta classe é o molde para todos os sapatos vendidos na loja.

**Atributos Protegidos:**
*   `_id`: Identificador único (ex: 1).
*   `_titulo`: Nome comercial (ex: "Oxford Clássico").
*   `_preco`: Valor formatado (ex: "R$ 499,90").
*   `_descricao`: Texto curto para vitrine.
*   `_url_imagem`: Caminho da foto principal.
*   `_tamanhos`: Lista de strings (ex: `["38", "39"]`).

**Properties (`@property`):**
Para cada atributo protegido, existe um método decorado com `@property`.
*   **Função**: Permitir o acesso de leitura (`produto.titulo`) sem permitir a escrita direta (`produto.titulo = "Novo"` daria erro).
*   **Benefício**: Cria uma interface pública segura. O mundo externo pode *ver* o produto, mas não pode *alterá-lo*.

**Método `para_dicionario()`:**
*   **Função**: Converte o objeto complexo `Produto` em um dicionário Python simples (`dict`).
*   **Por que é necessário?**: O Flask/Jinja2 prefere trabalhar com dicionários ao renderizar HTML. Esse método faz a "tradução" do objeto POO para um formato serializável.

### 4.2. Classe `ItemCarrinho` (Simples)
Representa uma escolha do usuário. É criado quando ele clica em "Adicionar ao Carrinho".

**Atributos Públicos:**
*   `id_produto`, `titulo`, `preco`, `tamanho`, `quantidade`.
*   **Nota**: Não há `_` aqui. O acesso é direto (`item.quantidade`).

**Método `obter_subtotal()`:**
*   **Lógica**: Pega o preço (string "R$ 100,00"), limpa os caracteres não numéricos, converte para `float` e multiplica pela quantidade.
*   **Uso**: Fundamental para calcular o valor total do carrinho na rota `/cart`.

### 4.3. Classe `Pedido` (Histórico)
Representa uma venda concluída. É um "retrato" do passado.

**Atributos Públicos:**
*   `id`: Código gerado (ex: "PED-999").
*   `data`: Data da compra.
*   `status`: Estado atual (ex: "Em Transporte").
*   `historico`: Lista de eventos para o rastreamento.

### 4.4. Classe `Loja` (Gerenciador)
Esta é a classe mais importante. Ela atua como o **Banco de Dados em Memória**.

**Atributos Protegidos:**
*   `_produtos`: Uma lista (`list`) que contém todos os objetos `Produto` disponíveis.
*   `_pedidos`: Uma lista (`list`) que guarda todos os objetos `Pedido` já realizados.

**Métodos de Acesso:**
*   `listar_produtos()`: Retorna a lista `_produtos`. É a única forma oficial de ver o catálogo.
*   `buscar_produto(id)`: Percorre a lista `_produtos` um por um (`for p in self._produtos`) até achar aquele com o ID correspondente. Retorna `None` se não achar.
*   `buscar_por_categoria(categoria)`: Usa uma *List Comprehension* para criar uma nova lista contendo apenas os produtos que batem com a categoria solicitada.
*   `criar_novo_pedido(total)`:
    1.  Gera um ID aleatório.
    2.  Cria um objeto `Pedido`.
    3.  Adiciona esse objeto na lista `_pedidos`.
    4.  Retorna o ID para ser mostrado ao usuário.

---

## 5. Catálogo Exaustivo de Endpoints e Rotas

### 5.1. Conceito de Endpoint
Um **Endpoint** é um ponto de acesso específico na API ou no site. Pense nele como uma "função que pode ser chamada pela internet".
*   **Rota**: É o endereço URL (ex: `/carrinho`).
*   **Método**: É a ação HTTP (GET para ler, POST para enviar dados).

Abaixo, explicamos **cada linha** de lógica de **cada rota** do sistema.

### 5.2. Rotas Públicas

#### Rota: Home
*   **URL**: `GET /`
*   **Função Python**: `home()`
*   **Explicação Detalhada**:
    1.  O usuário acessa `www.site.com/`.
    2.  O Flask chama a função `home()`.
    3.  A função chama `loja.listar_produtos()` para obter a lista bruta de objetos.
    4.  Executa um loop (`[p.para_dicionario() for p in ...]`) para converter todos os objetos em dicionários.
    5.  Chama `render_template('inicio.html', products=...)`, enviando essa lista para o HTML.
    6.  O HTML desenha um "card" para cada produto da lista.

#### Rota: Detalhes do Produto
*   **URL**: `GET /product/<int:product_id>`
*   **Função Python**: `product_detail(product_id)`
*   **Parâmetro**: `<int:product_id>` diz ao Flask para capturar o número da URL e passar como argumento para a função.
*   **Lógica**:
    1.  Chama `loja.buscar_produto(product_id)`.
    2.  **Verificação de Erro**: Se a loja retornar `None` (produto não existe), a função executa `abort(404)`, que mostra a página de "Erro: Não Encontrado".
    3.  Se achou, renderiza `detalhes_produto.html` passando os dados do produto.

#### Rota: Coleção (Filtros)
*   **URL**: `GET /collection`
*   **Função Python**: `collection()`
*   **Query String**: O usuário pode acessar `/collection?category=Bota`.
*   **Lógica**:
    1.  `request.args.get('category')`: O Flask olha para a URL e tenta pegar o valor de "category".
    2.  Chama `loja.buscar_por_categoria(categoria)`.
    3.  Se a categoria for vazia ou "All", a loja devolve tudo. Se for "Bota", devolve só botas.
    4.  Renderiza a página `colecao.html` com a lista filtrada.

### 5.3. Rotas de Compra (Carrinho/Checkout)

#### Rota: Ver Carrinho
*   **URL**: `GET /cart`
*   **Função Python**: `cart()`
*   **Conceito de Sessão**: O carrinho não está no banco de dados da loja. Ele está na **Sessão** (`session`), que é um espaço de memória temporário exclusivo de cada usuário.
*   **Lógica**:
    1.  `session.get('cart', [])`: Tenta pegar o carrinho da sessão. Se não existir (primeira visita), cria uma lista vazia `[]`.
    2.  **Cálculo de Totais**: A função itera sobre cada item do carrinho, limpando o preço (tirando "R$") e multiplicando pela quantidade.
    3.  Define o frete (R$ 25,00 fixo se tiver itens, R$ 0,00 se vazio).
    4.  Renderiza `carrinho.html` passando os itens e os totais calculados.

#### Rota: Adicionar ao Carrinho
*   **URL**: `POST /add_to_cart/<int:product_id>`
*   **Método POST**: Obrigatório, pois estamos alterando o estado do servidor (adicionando dados).
*   **Lógica**:
    1.  Recebe os dados do formulário HTML: `request.form.get('size')` e `quantity`.
    2.  Busca o produto original na `Loja` para garantir que o preço e nome estão corretos (segurança contra fraudes no frontend).
    3.  Cria um dicionário representando o novo item.
    4.  Adiciona esse dicionário à lista `session['cart']`.
    5.  **Importante**: Executa `session.modified = True` (implícito ao reatribuir) para garantir que o Flask salve o cookie atualizado no navegador.
    6.  Redireciona (`redirect`) o usuário para a página do carrinho.

#### Rota: Remover do Carrinho
*   **URL**: `POST /remove_from_cart/<int:product_id>/<size>`
*   **Lógica**:
    1.  Recupera a lista do carrinho.
    2.  Usa uma *List Comprehension* com filtro negativo: "Crie uma nova lista com todos os itens, **exceto** aquele que tem esse ID E esse Tamanho".
    3.  Salva a nova lista na sessão.
    4.  Redireciona para o carrinho.

#### Rota: Checkout
*   **URL**: `GET /checkout`
*   **Segurança**: Verifica `if not session.get('cart')`. Se o carrinho estiver vazio, impede o acesso ao checkout e manda de volta para o carrinho.
*   **Dados Mockados**: Como não temos um sistema de usuários completo com banco de dados, criamos um dicionário `usuario` "fake" com endereços e cartões de exemplo, apenas para preencher a tela e demonstrar o layout.

#### Rota: Simular Pagamento
*   **URL**: `GET /simulate_payment`
*   **Objetivo**: Fingir que fomos ao banco e cobramos o cartão.
*   **Lógica**:
    1.  Recalcula o total final.
    2.  Salva esse total em `session['last_order_total']`. Precisamos salvar isso porque, na próxima etapa, vamos limpar o carrinho, e perderíamos a informação de quanto foi pago.
    3.  Redireciona para `/order_success`.

#### Rota: Sucesso do Pedido
*   **URL**: `GET /order_success`
*   **Ação Final**:
    1.  Recupera o total salvo no passo anterior.
    2.  Chama `loja.criar_novo_pedido(total)`. Isso efetiva a compra no sistema da loja.
    3.  **Limpeza**: `session['cart'] = []`. Isso é crucial. Se não fizermos isso, os itens continuam no carrinho mesmo depois de pagos.
    4.  Mostra a tela de agradecimento com o número do pedido gerado.

### 5.4. Rotas de Usuário (Área Logada)

#### Rota: Login
*   **URL**: `GET` e `POST` `/login`
*   **Lógica Híbrida**:
    *   Se for **GET**: Apenas mostra o formulário de login.
    *   Se for **POST**:
        1.  Pega email e senha.
        2.  Define `session['logged_in'] = True`. Essa é a "chave" que abre as portas das áreas restritas.
        3.  Redireciona para a Home.

#### Rota: Meus Pedidos
*   **URL**: `GET /orders`
*   **Proteção**:
    1.  Verifica `if not session.get('logged_in')`.
    2.  Se não estiver logado, redireciona para `/login`.
*   **Exibição**: Chama `loja.listar_pedidos()` e mostra a tabela.

#### Rota: Rastreamento
*   **URL**: `GET /track/<order_id>`
*   **Lógica**:
    1.  Recebe o ID do pedido (ex: "PED-123").
    2.  Itera sobre a lista de pedidos da loja.
    3.  Se encontrar o pedido, renderiza a página de rastreio.
    4.  Se não encontrar, volta para a lista de pedidos.

---

## 6. Frontend e Templates (Jinja2)

O Flask usa o **Jinja2** para criar o HTML. Não escrevemos HTML estático; escrevemos "receitas" de HTML.

### Herança de Templates (`base.html`)
Todas as páginas começam com `{% extends "base.html" %}`.
*   O `base.html` contém o cabeçalho (menu), o rodapé e os links CSS.
*   As outras páginas apenas preenchem o "miolo" (`{% block content %}`).
*   Isso evita repetir código. Se quisermos mudar o menu, mudamos só no `base.html` e o site todo atualiza.

### Loops e Condicionais
*   **Loops**: `{% for p in products %}` cria um bloco de HTML para cada produto na lista. É assim que a vitrine é montada.
*   **Condicionais**: `{% if session['logged_in'] %}` decide se mostra o botão "Sair" ou o botão "Login" no menu.

---

## 7. Gerenciamento de Sessão e Segurança

### O que é a Sessão?
A web é "stateless" (sem memória). O servidor esquece quem você é assim que entrega a página.
Para lembrar (manter o carrinho, manter o login), usamos a **Sessão**.

### Como funciona no Flask?
1.  O Flask cria um dicionário (`session`).
2.  Ele serializa esse dicionário em uma string.
3.  Ele **assina criptograficamente** essa string usando a `app.secret_key`.
4.  Ele envia isso para o navegador como um **Cookie**.
5.  O navegador manda esse cookie de volta em cada clique.
6.  O Flask verifica a assinatura (para garantir que o usuário não alterou os dados) e restaura o dicionário.

### Segurança
A chave `app.secret_key` definida no código (`610c51...`) é fundamental. Se alguém descobrir essa chave, pode forjar cookies e se passar por qualquer usuário. Por isso, em produção, ela deve ser mantida em segredo absoluto.

---

## 8. Glossário Técnico

*   **API (Application Programming Interface)**: Conjunto de rotas que permitem que sistemas conversem.
*   **Backend**: O código que roda no servidor (Python).
*   **Frontend**: O código que roda no navegador (HTML/CSS).
*   **Deploy**: O ato de colocar o site no ar (na internet).
*   **Mock**: Dados falsos usados para teste.
*   **Payload**: Os dados úteis enviados em uma requisição (ex: o tamanho do sapato).
*   **Query String**: A parte da URL após o `?` usada para filtros.
*   **Status Code**: Código numérico que diz se deu certo (200), se não achou (404) ou se deu erro (500).

---
*Documentação gerada para fins acadêmicos - Projeto Loja de Sapatos Virtual 2025.*

---

## 9. Arquitetura de Frontend e Estilização (CSS)

O projeto não utiliza apenas um arquivo CSS gigante. Em vez disso, adotamos uma **Arquitetura Modular de Estilos**.

### 9.1. Estrutura de Arquivos
Dentro da pasta `static/styles/`, temos:

*   **`main.css`**: O arquivo base. Define:
    *   Reset de CSS (para garantir consistência entre navegadores).
    *   Variáveis de Cores (Root Variables).
    *   Tipografia (Fontes).
    *   Layout do Cabeçalho (Header) e Rodapé (Footer).
*   **`cart.css`**: Estilos específicos da tabela do carrinho e resumo de valores.
*   **`checkout.css`**: Estilização do formulário de pagamento e seleção de endereço.
*   **`product_detail.css`**: Layout da página de produto (Grid de imagens, seleção de tamanho).
*   **`collection.css`**: Layout da vitrine e da barra lateral de filtros.

### 9.2. Decisões de Design
*   **Flexbox**: Utilizado extensivamente para alinhamento de itens (ex: centralizar o conteúdo do cabeçalho, alinhar os cards de produtos).
*   **Grid Layout**: Usado na galeria de produtos para criar um layout responsivo que se adapta a diferentes tamanhos de tela.
*   **Variáveis CSS**:
    ```css
    :root {
        --primary-color: #333;
        --accent-color: #50C878; /* Verde Esmeralda */
        --text-color: #555;
        --light-bg: #f9f9f9;
    }
    ```
    Isso permite mudar a cor principal do site inteiro alterando apenas uma linha.

---

## 10. Guia de Testes Manuais (QA)

Para garantir que o sistema está funcionando antes da apresentação, siga este roteiro de testes.

### Cenário 1: Fluxo de Compra Feliz
1.  Acesse a **Home**. Verifique se as imagens carregam.
2.  Clique em um produto. Verifique se a página de **Detalhes** abre.
3.  Selecione Tamanho "40" e Quantidade "2".
4.  Clique em **Adicionar ao Carrinho**.
5.  Verifique se foi redirecionado para o **Carrinho**.
6.  Confirme o subtotal: (Preço x 2).
7.  Clique em **Finalizar Compra**.
8.  Verifique se os endereços de exemplo aparecem.
9.  Clique em **Pagar Agora**.
10. Verifique a tela de **Sucesso** e anote o ID do pedido.

### Cenário 2: Gestão de Carrinho
1.  Adicione o Produto A (Tam 38).
2.  Adicione o Produto A (Tam 40).
3.  Adicione o Produto B.
4.  Vá para o Carrinho. Deve haver 3 linhas.
5.  Remova o Produto A (Tam 38).
6.  Verifique se o Produto A (Tam 40) continua lá. (Isso testa a lógica de remoção por ID+Tamanho).

### Cenário 3: Área do Usuário
1.  Tente acessar `/orders` sem estar logado. Deve ir para Login.
2.  Faça login com qualquer email.
3.  Acesse `/orders` novamente. Deve ver a lista.
4.  Clique em "Rastrear" em um pedido antigo. Deve ver a timeline.

---

## 11. Roteiro de Melhorias Futuras (Roadmap)

Este projeto é uma base sólida (MVP). Para transformá-lo em um produto comercial real, os seguintes passos seriam necessários:

### 11.1. Banco de Dados Real (SQL)
*   **Atual**: Dados em memória (perdem-se ao reiniciar).
*   **Futuro**: Implementar **PostgreSQL** ou **MySQL**.
*   **Ferramenta**: Usar **SQLAlchemy** (ORM) para mapear as classes `Produto` e `Pedido` para tabelas no banco.

### 11.2. Autenticação Robusta
*   **Atual**: Login simulado com flag na sessão.
*   **Futuro**: Implementar **Flask-Login** e hash de senhas com **Bcrypt**.
*   **Funcionalidade**: Permitir cadastro real, recuperação de senha por email.

### 11.3. Pagamento Real
*   **Atual**: Simulação ("Pagar Agora").
*   **Futuro**: Integração com API de pagamento (Stripe, Mercado Pago ou Pagar.me).
*   **Fluxo**: O botão de checkout abriria um modal seguro da operadora de cartão.

### 11.4. Painel Administrativo (Admin)
*   **Atual**: Produtos são adicionados via código.
*   **Futuro**: Criar uma rota `/admin` onde o dono da loja pode:
    *   Cadastrar novos produtos (com upload de fotos).
    *   Alterar preços.
    *   Mudar status dos pedidos (de "Pago" para "Enviado").

---

## 12. Solução de Problemas Comuns (Troubleshooting)

### Erro: "Address already in use"
*   **Causa**: Você tentou rodar o `app.py` mas ele já está rodando em outra janela.
*   **Solução**: Procure o terminal onde ele está rodando e aperte `Ctrl+C`. Ou use `killall python3`.

### Erro: Imagens não carregam
*   **Causa**: Caminho incorreto ou cache do navegador.
*   **Solução**: Verifique se as imagens estão na pasta `static/img/produtos/`. Tente abrir a imagem direto na URL (ex: `localhost:5000/static/img/produtos/foto.png`).

### Erro: Alterei o CSS mas nada mudou
*   **Causa**: O navegador guardou o CSS antigo em cache para ser mais rápido.
*   **Solução**: Aperte `Ctrl + Shift + R` (Hard Reload) para forçar o navegador a baixar o CSS novo.

---
