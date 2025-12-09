#Projeto de POO (Loja de Sapatos)
from flask import Flask, render_template, request, session, redirect, url_for, flash, abort
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = '610c51de365d1158971307a6ea9202e417170240d94fb41936115aefd9fd5930' # Chave pra criptografar a sessão do usuário

# ==============================================================================
# 1. CLASSES (POO) - Aqui a gente define os objetos do sistema
# ==============================================================================

class Produto:
    """
    Essa classe serve de molde para criar os sapatos da loja.
    Cada sapato vai ter id, nome, preço, etc.
    Agora com ENCAPSULAMENTO: os dados ficam protegidos (com _ na frente).
    """
    def __init__(self, id, titulo, preco, descricao, url_imagem, descricao_completa, tamanhos, cores, galeria, categoria):
        # O underline (_) na frente diz que isso é "protegido", não deve mexer direto
        self._id = id
        self._titulo = titulo
        self._preco = preco
        self._descricao = descricao
        self._url_imagem = url_imagem
        self._descricao_completa = descricao_completa
        self._tamanhos = tamanhos
        self._cores = cores
        self._galeria = galeria
        self._categoria = categoria

    # Properties (Getters) - Permitem ler os dados protegidos de forma segura
    @property
    def id(self):
        return self._id

    @property
    def titulo(self):
        return self._titulo

    @property
    def preco(self):
        return self._preco

    @property
    def descricao(self):
        return self._descricao

    @property
    def url_imagem(self):
        return self._url_imagem

    @property
    def descricao_completa(self):
        return self._descricao_completa

    @property
    def tamanhos(self):
        return self._tamanhos

    @property
    def cores(self):
        return self._cores

    @property
    def galeria(self):
        return self._galeria

    @property
    def categoria(self):
        return self._categoria

    def para_dicionario(self):
        """
        Função que transforma o objeto Produto em um dicionário simples.
        A gente precisa disso porque o HTML (Jinja2) entende melhor dicionários do que objetos Python.
        """
        return {
            "id": self._id,
            "title": self._titulo,      # O template HTML usa 'title', então mantive assim
            "price": self._preco,
            "description": self._descricao,
            "image_url": self._url_imagem,
            "full_description": self._descricao_completa,
            "sizes": self._tamanhos,
            "colors": self._cores,
            "gallery": self._galeria,
            "category": self._categoria
        }

class ItemCarrinho:
    """
    Classe que representa um item que o usuário colocou no carrinho.
    Guarda qual é o produto, o tamanho escolhido e quantos ele quer levar.
    """
    def __init__(self, id_produto, titulo, preco, tamanho, quantidade):
        self.id_produto = id_produto
        self.titulo = titulo
        self.preco = preco
        self.tamanho = tamanho
        self.quantidade = quantidade

    def obter_subtotal(self):
        """
        Calcula quanto custa esse item (Preço x Quantidade).
        Ex: Se o sapato custa 100 e ele leva 2, retorna 200.
        """
        # Limpeza do preço: tira o 'R$' e troca vírgula por ponto pra virar número
        valor_numerico = float(self.preco.replace('R$', '').replace(',', '.').strip())
        return valor_numerico * self.quantidade

    def para_dicionario(self):
        return {
            "id": self.id_produto,
            "title": self.titulo,
            "price": self.preco,
            "size": self.tamanho,
            "quantity": self.quantidade
        }

class Pedido:
    """
    Classe para guardar os dados de uma venda finalizada.
    Tem o ID do pedido, o total pago, status de entrega, etc.
    """
    def __init__(self, id, data, total, status, codigo_rastreio, itens, historico):
        self.id = id
        self.data = data
        self.total = total
        self.status = status
        self.codigo_rastreio = codigo_rastreio
        self.itens = itens
        self.historico = historico

    def para_dicionario(self):
        return {
            "id": self.id,
            "date": self.data,
            "total": self.total,
            "status": self.status,
            "tracking_code": self.codigo_rastreio,
            "item_list": self.itens,
            "history": self.historico
        }

class Loja:
    """
    Essa é a classe principal que gerencia tudo.
    Ela guarda a lista de produtos e pedidos na memória (já que não usamos banco de dados real).
    AQUI MANTEMOS O ENCAPSULAMENTO: As listas são protegidas (_).
    """
    def __init__(self):
        # Lista de produtos (simulando um banco de dados)
        # Protegida com _ para que só a classe Loja mexa nela
        self._produtos = [
            Produto(
                id=1,
                titulo="Oxford Clássico Grey",
                preco="R$ 499,90",
                descricao="Sapato social masculino em couro cinza. Elegância e conforto.",
                url_imagem="http://127.0.0.1:5000/static/img/produtos/sapato1foto1.png",
                descricao_completa="O Oxford Clássico Grey é feito à mão com couro italiano premium. Design minimalista e sofisticado.",
                tamanhos=["38", "39", "40", "41", "42", "43"],
                cores=[{"name": "Cinza", "hex": "#8D8D8D"}, {"name": "Preto", "hex": "#333333"}],
                galeria=[
                    "http://127.0.0.1:5000/static/img/produtos/sapato1foto2.png",
                    "http://127.0.0.1:5000/static/img/produtos/sapato1foto3.png",
                    "http://127.0.0.1:5000/static/img/produtos/sapato1foto4.png"
                ],
                categoria="Social"
            ),
            Produto(
                id=2,
                titulo="Bota Elegance Esmeralda",
                preco="R$ 679,00",
                descricao="Bota feminina de salto alto na cor esmeralda.",
                url_imagem="http://127.0.0.1:5000/static/img/produtos/sapato2foto1.png",
                descricao_completa="Bota de cano médio com acabamento em camurça premium.",
                tamanhos=["35", "36", "37", "38"],
                cores=[{"name": "Esmeralda", "hex": "#50C878"}],
                galeria=[],
                categoria="Bota"
            )
        ]
        
        # Lista protegida de pedidos
        self._pedidos = [
            Pedido("PED-789012", "2025-11-20", 199.90, "Entregue", "BR123456789BR", ["Tênis Casual"], [{"time": "2025-11-20", "status": "Entregue"}]),
            Pedido("PED-123456", "2025-12-01", 350.50, "Em Transporte", "BR987654321BR", ["Bota de Couro"], [{"time": "2025-12-01", "status": "Enviado"}])
        ]

    def listar_produtos(self):
        """Método público para acessar a lista de produtos (Encapsulamento)"""
        return self._produtos

    def listar_pedidos(self):
        """Método público para acessar a lista de pedidos (Encapsulamento)"""
        return self._pedidos

    def buscar_produto(self, id):
        """Varre a lista de produtos procurando um com o ID igual ao solicitado"""
        for p in self._produtos:
            if p.id == id:
                return p
        return None

    def buscar_por_categoria(self, categoria):
        """Filtra a lista de produtos pela categoria (ex: só mostra botas)"""
        if not categoria or categoria.lower() == 'all':
            return self._produtos
        # List comprehension: cria uma nova lista só com os produtos da categoria certa
        return [p for p in self._produtos if p.categoria.lower() == categoria.lower()]

    def criar_novo_pedido(self, total):
        """Gera um novo pedido quando o usuário termina de pagar"""
        novo_id = f"PED-{random.randint(100000, 999999)}"
        novo_pedido = Pedido(
            id=novo_id,
            data=datetime.now().strftime("%Y-%m-%d"),
            total=total,
            status="Pagamento Confirmado",
            codigo_rastreio=f"BR{random.randint(100000000, 999999999)}BR",
            itens=[], # Por enquanto a lista de itens começa vazia
            historico=[{"time": datetime.now().strftime("%Y-%m-%d %H:%M"), "status": "Pagamento Aprovado"}]
        )
        self._pedidos.append(novo_pedido)
        return novo_id

# Instância da loja para ser usada nas rotas
loja = Loja()


# ==============================================================================
# 2. ROTAS (FLASK) - Aqui definimos as URLs do site
# ==============================================================================

@app.route('/')
def home():
    """Rota da Página Inicial (Home)"""
    # Pega todos os produtos da loja e manda pro HTML
    # USANDO O MÉTODO DE ACESSO (ENCAPSULAMENTO)
    lista_produtos = [p.para_dicionario() for p in loja.listar_produtos()]
    return render_template('inicio.html', products=lista_produtos)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Rota que mostra os detalhes de um produto específico"""
    produto = loja.buscar_produto(product_id)
    if not produto:
        abort(404) # Se não achar o produto, dá erro 404
    return render_template('detalhes_produto.html', product=produto.para_dicionario())

@app.route('/collection')
def collection():
    """Rota da página de Coleção (onde tem os filtros)"""
    categoria = request.args.get('category') # Pega a categoria da URL (ex: ?category=Bota)
    produtos_filtrados = loja.buscar_por_categoria(categoria)
    lista_final = [p.para_dicionario() for p in produtos_filtrados]
    
    return render_template(
        'colecao.html', 
        products=lista_final, 
        categories=['All', 'Social', 'Casual', 'Bota'],
        selected_category=categoria or 'All'
    )

@app.route('/cart')
def cart():
    """Rota do Carrinho de Compras"""
    # Pega o carrinho da sessão do usuário (se não tiver, cria uma lista vazia)
    carrinho_sessao = session.get('cart', [])
    
    # Calcula o total somando item por item
    subtotal = 0
    for item in carrinho_sessao:
        preco = float(item['price'].replace('R$', '').replace(',', '.').strip())
        subtotal += preco * item['quantity']
    
    frete = 25.00 if subtotal > 0 else 0
    total = subtotal + frete
    
    return render_template(
        'carrinho.html',
        cart_items=carrinho_sessao,
        subtotal=subtotal,
        shipping_cost=frete,
        total=total
    )

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Rota que recebe o formulário de 'Adicionar ao Carrinho'"""
    produto = loja.buscar_produto(product_id)
    if not produto:
        abort(404)
        
    tamanho = request.form.get('size')
    quantidade = int(request.form.get('quantity', 1))
    
    # Cria o dicionário do item
    novo_item = {
        "id": produto.id,
        "title": produto.titulo,
        "price": produto.preco,
        "size": tamanho,
        "quantity": quantidade
    }
    
    # Adiciona na lista da sessão
    carrinho = session.get('cart', [])
    carrinho.append(novo_item)
    session['cart'] = carrinho
    
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>/<size>', methods=['POST'])
def remove_from_cart(product_id, size):
    """Rota para remover um item do carrinho"""
    carrinho = session.get('cart', [])
    # Recria a lista do carrinho, excluindo o item que o usuário clicou pra remover
    carrinho = [item for item in carrinho if not (item['id'] == product_id and item['size'] == size)]
    session['cart'] = carrinho
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    """Rota da página de Finalizar Compra (Checkout)"""
    if not session.get('cart'):
        return redirect(url_for('cart'))
        
    # Dados de exemplo do usuário (endereço, cartão) pra preencher a tela
    usuario = {
        "addresses": [{"id": 1, "label": "Casa", "street": "Rua Exemplo, 123", "city": "São Paulo", "zip": "01000-000", "default": True}],
        "payment_methods": [{"id": 1, "brand": "Mastercard", "last_four": "1234", "default": True}]
    }
    
    # Recalcula totais
    carrinho = session.get('cart', [])
    subtotal = sum([float(i['price'].replace('R$', '').replace(',', '.').strip()) * i['quantity'] for i in carrinho])
    total = subtotal + 25.00
    
    return render_template('finalizar_compra.html', cart_items=carrinho, user=usuario, subtotal=subtotal, shipping_cost=25.00, total=total)

@app.route('/simulate_payment')
def simulate_payment():
    """Rota que finge que processou o pagamento"""
    # Calcula total para salvar na sessão e mostrar na tela de sucesso
    carrinho = session.get('cart', [])
    subtotal = sum([float(i['price'].replace('R$', '').replace(',', '.').strip()) * i['quantity'] for i in carrinho])
    session['last_order_total'] = subtotal + 25.00
    
    return redirect(url_for('order_success'))

@app.route('/order_success')
def order_success():
    """Rota da tela de Sucesso (Pedido Confirmado)"""
    total = session.get('last_order_total', 0)
    novo_id = loja.criar_novo_pedido(total)
    
    # Esvazia o carrinho depois que comprou
    session['cart'] = []
    
    return render_template('pedido_sucesso.html', order_id=novo_id, total_paid=total, user_email=session.get('user_email', 'cliente@email.com'))

@app.route('/orders')
def orders():
    """Rota de Meus Pedidos"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # USANDO O MÉTODO DE ACESSO (ENCAPSULAMENTO)
    lista_pedidos = [p.para_dicionario() for p in loja.listar_pedidos()]
    return render_template('pedidos.html', orders=lista_pedidos)

@app.route('/track/<order_id>')
def track(order_id):
    """Rota de Rastreamento"""
    # USANDO O MÉTODO DE ACESSO (ENCAPSULAMENTO)
    for p in loja.listar_pedidos():
        if p.id == order_id:
            return render_template('detalhes_rastreamento.html', order=p.para_dicionario())
    return redirect(url_for('orders'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de Login"""
    if request.method == 'POST':
        session['logged_in'] = True
        session['user_email'] = request.form.get('email')
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Rota de Sair (Logout)"""
    session.clear() # Limpa a sessão (desloga o usuário)
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Rota de Cadastro"""
    if request.method == 'POST':
        return redirect(url_for('login'))
    return render_template('registrar.html')

@app.route('/profile')
def profile():
    """Rota de Perfil"""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    usuario = {
        "name": "Usuário Teste",
        "email": session.get('user_email'),
        "preferences": {"size_default": "40", "newsletter": True, "theme": "claro"},
        "payment_methods": [{"brand": "Visa", "last_four": "4242", "expiry": "12/28", "default": True}]
    }
    return render_template('perfil.html', user=usuario)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Rota de Contato"""
    if request.method == 'POST':
        flash('Mensagem enviada com sucesso!', 'success')
        return redirect(url_for('contact'))
    return render_template('contato.html')

@app.route('/search')
def search():
    """Rota de Busca (Redireciona para coleção)"""
    return redirect(url_for('colecao'))

if __name__ == '__main__':
    app.run(debug=True)
