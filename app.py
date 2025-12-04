# app.py
from flask import Flask, render_template, abort, request, session, redirect, url_for, flash
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a4c7e9f3b1d5c2e8a6f4d0c1b9a8e7d6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0'

# Simulação da base de dados de produtos - ATUALIZADA COM MAIS DETALHES
PRODUCTS = [
    {
        "id": 1, 
        "title": "Oxford Clássico Grey", 
        "price": "R$ 499,90", 
        "description": "Sapato social masculino em couro cinza. Elegância e conforto em um design atemporal.",
        "image_url": "https://via.placeholder.com/600x600/8D8D8D/FFFFFF?text=Oxford+Grey+Principal",
        # Detalhes específicos para a página de produto 
        "full_description": "O Oxford Clássico Grey é feito à mão com couro italiano premium. Sua sola de borracha injetada garante o conforto, enquanto o design minimalista confere um toque de sofisticação atemporal. Perfeito para o escritório ou eventos formais. Cuidado: Limpar apenas com pano úmido.",
        "sizes": ["38", "39", "40", "41", "42", "43"],
        "colors": [
            {"name": "Cinza", "hex": "#8D8D8D"},
            {"name": "Preto", "hex": "#333333"},
            {"name": "Caramelo", "hex": "#D2B48C"}
        ],
        "gallery": [
            "http://127.0.0.1:5000/static/img/produtos/sapato_1.png",
            "http://127.0.0.1:5000/static/img/produtos/sapato_1.png",
            "https://via.placeholder.com/150x150/CCCCCC/FFFFFF?text=Sola"
        ]
    },
    {
        "id": 2, 
        "title": "Bota Elegance Esmeralda", 
        "price": "R$ 679,00", 
        "description": "Bota feminina de salto alto na cor esmeralda.",
        "image_url": "https://via.placeholder.com/600x600/4A6D60/FFFFFF?text=Bota+Esmeralda+Principal"
        # Sem outros detalhes por enquanto
    },
    # ... (outros produtos) ...
]


@app.route('/')
def home():
    """Renderiza a página inicial."""
    return render_template('home.html', products=PRODUCTS)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Renderiza a página de detalhes de um produto específico."""
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    
    if product is None:
        abort(404) # Retorna erro 404 se o produto não for encontrado
        
    return render_template('product_detail.html', product=product)


@app.route('/search')
def search():
    # Lógica de pesquisa virá aqui
    return "Página de Resultados de Pesquisa"


# O endpoint dedicado as nossas coleções. 

@app.route('/collection')
def collection():
    """Renderiza a página de coleção com filtros opcionais."""
    
    # 1. Lógica Simples de Filtro (por exemplo, por categoria)
    category_filter = request.args.get('category')
    
    if category_filter and category_filter != 'all':
        # Simula filtragem no banco de dados
        filtered_products = [
            p for p in PRODUCTS 
            if p.get('category', 'all').lower() == category_filter.lower()
        ]
    else:
        filtered_products = PRODUCTS
        
    # Categorias para o menu de filtros (Definidas de forma simples)
    categories = ['All', 'Social', 'Casual', 'Bota', 'Esportivo']

    return render_template(
        'collection.html', 
        products=filtered_products,
        categories=categories,
        selected_category=category_filter or 'All'
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # SIMULAÇÃO DE LOGIN: Se e-mail e senha forem fornecidos, o login é bem-sucedido.
        if email and password:
            session['logged_in'] = True
            session['user_email'] = email
            # Redireciona para a Home Page
            return redirect(url_for('home'))
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Renderiza a página de cadastro e processa o formulário (futuramente)."""
    # Lógica de criação de usuário virá aqui
    if request.method == 'POST':
        # Simulação de processamento de cadastro
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        print(f"Novo Cadastro: {name}, Email: {email}")
        # Futuramente: validar e salvar novo usuário no banco de dados
        return redirect(url_for('login')) # Redireciona para o login após o cadastro
        
    return render_template('register.html')


# Uma rota destinada ao logout.

@app.route('/logout')
def logout():
    """Limpa a sessão do usuário e redireciona para a Home."""
    session.pop('logged_in', None)
    session.pop('user_email', None)
    return redirect(url_for('home'))


# Endpoint destinado ao perfil do usuário. 
@app.route('/profile')
def profile():
    if not session.get('logged_in'):
        return redirect(url_for('login')) 
    
    # Simulação dos dados do usuário logado e dados de pagamento
    user_data = {
        "name": "Lucas Souza",
        "email": session.get('user_email', 'usuario@exemplo.com'),
        "preferences": {
            "newsletter": True,
            "size_default": "41",
            "theme": "claro"
        },
        # NOVO: Dados de Pagamento Simulado
        "payment_methods": [
            {
                "id": 1, 
                "brand": "Visa", 
                "last_four": "0000", 
                "expiry": "00/00", 
                "default": True
            },
            {
                "id": 2, 
                "brand": "Mastercard", 
                "last_four": "0000", 
                "expiry": "00/00", 
                "default": False
            }
        ]
    }
    
    return render_template('profile.html', user=user_data)

# Endpoint destinado a página do carrinho 

@app.route('/cart')
def cart():
    """Renderiza a página do carrinho, exibindo os itens da sessão."""
    cart_items = session.get('cart', [])
    
    # Calcular o subtotal
    subtotal = sum(float(item['price'].replace('R$', '').replace(',', '.')) * item['quantity'] for item in cart_items)
    
    # Simulação de frete (Exemplo fixo)
    shipping_cost = 25.00
    total = subtotal + shipping_cost

    return render_template(
        'cart.html', 
        cart_items=cart_items,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        total=total
    )


# Endpoint destinado a adição de produtos ao carrinho

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    """Adiciona um produto (com tamanho e quantidade) ao carrinho na sessão."""
    
    # 1. Obter dados do formulário
    selected_size = request.form.get('size')
    quantity = int(request.form.get('quantity', 1)) 
    
    # 2. Encontrar o produto no nosso "banco de dados"
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)

    if product is None:
        abort(404)
        
    # 3. Inicializar ou obter o carrinho da sessão
    cart_items = session.get('cart', [])
    
    # 4. Criar o novo item
    new_item = {
        'id': product['id'],
        'title': product['title'],
        'price': product['price'], # Manter o formato string 'R$ X' por enquanto
        'size': selected_size,
        'quantity': quantity
    }
    
    # 5. Adicionar item (Lógica de unificação simplificada: apenas adiciona um novo item)
    # Em uma implementação real, você verificaria se o item (ID+Tamanho) já existe para atualizar a quantidade.
    
    cart_items.append(new_item)
    
    # 6. Salvar o carrinho de volta na sessão
    session['cart'] = cart_items
    
    # 7. Redirecionar para a visualização do carrinho
    return redirect(url_for('cart'))


# Endpoint da simulação do pagamento 


@app.route('/simulate_payment')
def simulate_payment():
    """Simula o processamento do pagamento e salva o total para a página de sucesso."""
    
    cart_items = session.get('cart', [])
    if not cart_items:
        return redirect(url_for('cart')) 
        
    # Recalcula o total (em ambiente real, este cálculo seria mais seguro)
    subtotal_val = sum(float(item['price'].replace('R$', '').replace(',', '.')) * item['quantity'] for item in cart_items)
    shipping_cost = 25.00
    total_val = subtotal_val + shipping_cost
    
    # ⚠️ Salva o total na sessão para ser usado na próxima página
    session['last_order_total'] = total_val
    
    # Simula o processamento (poderia haver uma lógica de erro aqui)
    return redirect(url_for('order_success'))
 
# Endpoint da página de checkout

# app.py (Adicione esta nova rota)
# Certifique-se de que 'redirect' e 'url_for' estão nos seus imports

@app.route('/checkout')
def checkout():
    """Renderiza a página de finalização de compra (Checkout)."""
    
    # 1. Requer Carrinho e Login
    cart_items = session.get('cart', [])
    if not cart_items:
        # Se o carrinho estiver vazio, redireciona para a página do carrinho
        return redirect(url_for('cart')) 
    
    # Simulação dos dados necessários para o Checkout (Dados do usuário logado)
    user_data = {
        # Endereços simulados (Para seleção de frete)
        "addresses": [
            {"id": 1, "label": "Casa", "street": "Rua das Flores, 123", "city": "São Paulo", "zip": "01000-000", "default": True},
            {"id": 2, "label": "Trabalho", "street": "Av. Principal, 500", "city": "Rio de Janeiro", "zip": "20000-000", "default": False}
        ],
        # Formas de pagamento (Reutiliza os dados do perfil)
        "payment_methods": [
            {"id": 1, "brand": "Visa", "last_four": "1234", "expiry": "12/28", "default": True},
            {"id": 2, "brand": "Mastercard", "last_four": "9876", "expiry": "05/26", "default": False}
        ]
    }
    
    # 2. Cálculo do Resumo (Reutilizado da rota /cart, mas adaptado para valores numéricos)
    subtotal_val = sum(float(item['price'].replace('R$', '').replace(',', '.')) * item['quantity'] for item in cart_items)
    shipping_cost = 25.00 # Simulação de frete fixo
    total_val = subtotal_val + shipping_cost

    return render_template(
        'checkout.html', 
        cart_items=cart_items,
        user=user_data,
        subtotal=subtotal_val,
        shipping_cost=shipping_cost,
        total=total_val
    )


@app.route('/order_success')
def order_success():
    """Página de confirmação de pedido após o checkout (simulação)."""
    
    # Requer login
    if not session.get('logged_in'):
        return redirect(url_for('login')) 

    # 1. Simulação do processo de Finalização:
    
    # ⚠️ Em um ambiente real, o valor total seria pego do POST do checkout
    # ou calculado com base no pedido salvo no banco de dados.
    # Aqui, usaremos um valor fixo ou um valor do último cálculo de checkout.
    
    # Recupera o total, ou usa um fallback
    # Vamos simular um total salvo na sessão, ou usar um valor padrão:
    total_paid = session.pop('last_order_total', 150.00) 
    
    # Gera um ID de pedido único (simulado)
    order_id = f"PED-{random.randint(100000, 999999)}"
    
    # 2. Ação Crucial: Limpa o carrinho após a "compra"
    # Este é o passo que realmente finaliza a transação para o usuário.
    session.pop('cart', None) 
    
    # 3. Renderiza a página de sucesso
    return render_template(
        'order_success.html', 
        order_id=order_id,
        total_paid=total_paid,
        user_email=session.get('user_email', 'usuario@exemplo.com')
    )

# Alguns produtos simlados

# app.py (Simulação de Dados de Pedidos)
# Você pode colocar isso perto da definição do PRODUCTS

# app.py (Simulação de Dados de Pedidos - ATUALIZADO)

SIMULATED_ORDERS = [
    {
        "id": "PED-789012", 
        "date": "2025-11-20", 
        "total": 199.90, 
        "status": "Entregue",
        "tracking_code": "BR123456789BR",
        "item_list": ["Tênis Casual", "Meia Esportiva"], # <-- CORREÇÃO AQUI
        "history": [
            {"time": "2025-11-20 15:30", "status": "Pagamento Confirmado"},
            {"time": "2025-11-21 09:00", "status": "Preparando para Envio"},
            {"time": "2025-11-22 14:45", "status": "Enviado para Transporte"},
            {"time": "2025-11-25 10:20", "status": "Saiu para Entrega"},
            {"time": "2025-11-25 15:00", "status": "Entregue"}
        ]
    },
    {
        "id": "PED-123456", 
        "date": "2025-12-01", 
        "total": 350.50, 
        "status": "Em Transporte",
        "tracking_code": "BR987654321BR",
        "item_list": ["Bota de Couro"], # <-- CORREÇÃO AQUI
        "history": [
            {"time": "2025-12-01 18:00", "status": "Pagamento Confirmado"},
            {"time": "2025-12-02 08:30", "status": "Preparando para Envio"},
            {"time": "2025-12-02 14:00", "status": "Enviado para Transporte"},
            {"time": "2025-12-03 10:00", "status": "Em Trânsito para a Unidade Regional"}
        ]
    }
]

@app.route('/orders')
def orders():
    """Exibe a lista de pedidos do usuário logado."""
    if not session.get('logged_in'):
        return redirect(url_for('login')) 
    
    # Em um ambiente real, você filtraria a lista pelo ID do usuário
    user_orders = SIMULATED_ORDERS 
    
    return render_template('orders.html', orders=user_orders)


@app.route('/track/<string:order_id>')
def track(order_id):
    """Exibe os detalhes e o histórico de rastreio de um pedido específico."""
    if not session.get('logged_in'):
        return redirect(url_for('login')) 

    # Encontra o pedido pelo ID simulado
    order = next((o for o in SIMULATED_ORDERS if o['id'] == order_id), None)
    
    if order is None:
        # Se o ID não for encontrado, redireciona para a lista de pedidos ou mostra 404
        return redirect(url_for('orders'))
        
    return render_template('track_detail.html', order=order)

# Endpoint da página de contato. 

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Renderiza o formulário de contato e processa o envio."""
    
    if request.method == 'POST':
        # 1. Capturar os dados do formulário
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # 2. Simulação de processamento (Aqui você enviaria o e-mail)
        
        # Exemplo: Imprime no console do Flask para visualização
        print("--- NOVO CONTATO RECEBIDO ---")
        print(f"Nome: {name}")
        print(f"E-mail: {email}")
        print(f"Assunto: {subject}")
        print(f"Mensagem: {message[:50]}...") # Limita a mensagem para o log
        print("-----------------------------")
        
        # 3. Feedback para o usuário e redirecionamento
        # Usaremos 'flash' para mostrar uma mensagem de sucesso
        flash('Sua mensagem foi enviada com sucesso! Responderemos em breve.', 'success')
        return redirect(url_for('contact'))
        
    # GET: Renderiza a página
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)