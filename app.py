# app.py - Versão POO Refatorada
from flask import Flask, render_template, abort, request, session, redirect, url_for, flash
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import random


# ==================== MODELS ====================

class BaseModel(ABC):
    """Classe base abstrata para todos os modelos"""
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Converte o modelo para dicionário"""
        pass


class ProductModel(BaseModel):
    """Modelo de Produto com encapsulamento completo"""
    
    def __init__(self, id: int, title: str, price: str, description: str, 
                 image_url: str, full_description: str = "", sizes: List[str] = None,
                 colors: List[Dict] = None, gallery: List[str] = None, category: str = "all"):
        self._id = id
        self._title = title
        self._price = price
        self._description = description
        self._image_url = image_url
        self._full_description = full_description or description
        self._sizes = sizes or []
        self._colors = colors or []
        self._gallery = gallery or [image_url]
        self._category = category
    
    # Properties (getters)
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def price(self) -> str:
        return self._price
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def image_url(self) -> str:
        return self._image_url
    
    @property
    def full_description(self) -> str:
        return self._full_description
    
    @property
    def sizes(self) -> List[str]:
        return self._sizes.copy()
    
    @property
    def colors(self) -> List[Dict]:
        return self._colors.copy()
    
    @property
    def gallery(self) -> List[str]:
        return self._gallery.copy()
    
    @property
    def category(self) -> str:
        return self._category
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o produto para dicionário"""
        return {
            "id": self._id,
            "title": self._title,
            "price": self._price,
            "description": self._description,
            "image_url": self._image_url,
            "full_description": self._full_description,
            "sizes": self._sizes,
            "colors": self._colors,
            "gallery": self._gallery,
            "category": self._category
        }
    
    def __repr__(self) -> str:
        return f"ProductModel(id={self._id}, title='{self._title}', price='{self._price}')"


class CartItemModel(BaseModel):
    """Modelo de Item do Carrinho"""
    
    def __init__(self, product_id: int, title: str, price: str, size: str, quantity: int):
        self._product_id = product_id
        self._title = title
        self._price = price
        self._size = size
        self._quantity = quantity
    
    @property
    def product_id(self) -> int:
        return self._product_id
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def price(self) -> str:
        return self._price
    
    @property
    def size(self) -> str:
        return self._size
    
    @property
    def quantity(self) -> int:
        return self._quantity
    
    @quantity.setter
    def quantity(self, value: int):
        if value > 0:
            self._quantity = value
    
    def get_subtotal(self) -> float:
        """Calcula o subtotal do item"""
        price_value = float(self._price.replace('R$', '').replace(',', '.').strip())
        return price_value * self._quantity
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._product_id,
            "title": self._title,
            "price": self._price,
            "size": self._size,
            "quantity": self._quantity
        }


class OrderModel(BaseModel):
    """Modelo de Pedido"""
    
    def __init__(self, order_id: str, date: str, total: float, status: str,
                 tracking_code: str, item_list: List[str], history: List[Dict]):
        self._order_id = order_id
        self._date = date
        self._total = total
        self._status = status
        self._tracking_code = tracking_code
        self._item_list = item_list
        self._history = history
    
    @property
    def order_id(self) -> str:
        return self._order_id
    
    @property
    def date(self) -> str:
        return self._date
    
    @property
    def total(self) -> float:
        return self._total
    
    @property
    def status(self) -> str:
        return self._status
    
    @property
    def tracking_code(self) -> str:
        return self._tracking_code
    
    @property
    def item_list(self) -> List[str]:
        return self._item_list.copy()
    
    @property
    def history(self) -> List[Dict]:
        return self._history.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._order_id,
            "date": self._date,
            "total": self._total,
            "status": self._status,
            "tracking_code": self._tracking_code,
            "item_list": self._item_list,
            "history": self._history
        }


class UserModel(BaseModel):
    """Modelo de Usuário"""
    
    def __init__(self, email: str, name: str = "", preferences: Dict = None,
                 payment_methods: List[Dict] = None):
        self._email = email
        self._name = name
        self._preferences = preferences or {}
        self._payment_methods = payment_methods or []
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def preferences(self) -> Dict:
        return self._preferences.copy()
    
    @property
    def payment_methods(self) -> List[Dict]:
        return self._payment_methods.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "email": self._email,
            "name": self._name,
            "preferences": self._preferences,
            "payment_methods": self._payment_methods
        }


# ==================== REPOSITORIES ====================

class ProductRepository:
    """Repository para gerenciar produtos (padrão Repository)"""
    
    def __init__(self):
        self._products = self._initialize_products()
    
    def _initialize_products(self) -> List[ProductModel]:
        """Inicializa a lista de produtos"""
        return [
            ProductModel(
                id=1,
                title="Oxford Clássico Grey",
                price="R$ 499,90",
                description="Sapato social masculino em couro cinza. Elegância e conforto em um design atemporal.",
                image_url="https://via.placeholder.com/600x600/8D8D8D/FFFFFF?text=Oxford+Grey+Principal",
                full_description="O Oxford Clássico Grey é feito à mão com couro italiano premium. Sua sola de borracha injetada garante o conforto, enquanto o design minimalista confere um toque de sofisticação atemporal. Perfeito para o escritório ou eventos formais. Cuidado: Limpar apenas com pano úmido.",
                sizes=["38", "39", "40", "41", "42", "43"],
                colors=[
                    {"name": "Cinza", "hex": "#8D8D8D"},
                    {"name": "Preto", "hex": "#333333"},
                    {"name": "Caramelo", "hex": "#D2B48C"}
                ],
                gallery=[
                    "http://127.0.0.1:5000/static/img/produtos/sapato_1.png",
                    "http://127.0.0.1:5000/static/img/produtos/sapato_1.png",
                    "https://via.placeholder.com/150x150/CCCCCC/FFFFFF?text=Sola"
                ]
            ),
            ProductModel(
                id=2,
                title="Bota Elegance Esmeralda",
                price="R$ 679,00",
                description="Bota feminina de salto alto na cor esmeralda.",
                image_url="https://via.placeholder.com/600x600/4A6D60/FFFFFF?text=Bota+Esmeralda+Principal"
            )
        ]
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Retorna todos os produtos como dicionários"""
        return [product.to_dict() for product in self._products]
    
    def find_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Busca produto por ID"""
        for product in self._products:
            if product.id == product_id:
                return product.to_dict()
        return None
    
    def search_by_category(self, category: Optional[str]) -> List[Dict[str, Any]]:
        """Busca produtos por categoria"""
        if not category or category.lower() == 'all':
            return self.get_all()
        
        filtered = [
            product.to_dict() 
            for product in self._products 
            if product.category.lower() == category.lower()
        ]
        return filtered


class OrderRepository:
    """Repository para gerenciar pedidos"""
    
    def __init__(self):
        self._orders = self._initialize_orders()
    
    def _initialize_orders(self) -> List[OrderModel]:
        """Inicializa pedidos simulados"""
        return [
            OrderModel(
                order_id="PED-789012",
                date="2025-11-20",
                total=199.90,
                status="Entregue",
                tracking_code="BR123456789BR",
                item_list=["Tênis Casual", "Meia Esportiva"],
                history=[
                    {"time": "2025-11-20 15:30", "status": "Pagamento Confirmado"},
                    {"time": "2025-11-21 09:00", "status": "Preparando para Envio"},
                    {"time": "2025-11-22 14:45", "status": "Enviado para Transporte"},
                    {"time": "2025-11-25 10:20", "status": "Saiu para Entrega"},
                    {"time": "2025-11-25 15:00", "status": "Entregue"}
                ]
            ),
            OrderModel(
                order_id="PED-123456",
                date="2025-12-01",
                total=350.50,
                status="Em Transporte",
                tracking_code="BR987654321BR",
                item_list=["Bota de Couro"],
                history=[
                    {"time": "2025-12-01 18:00", "status": "Pagamento Confirmado"},
                    {"time": "2025-12-02 08:30", "status": "Preparando para Envio"},
                    {"time": "2025-12-02 14:00", "status": "Enviado para Transporte"},
                    {"time": "2025-12-03 10:00", "status": "Em Trânsito para a Unidade Regional"}
                ]
            )
        ]
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Retorna todos os pedidos"""
        return [order.to_dict() for order in self._orders]
    
    def find_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Busca pedido por ID"""
        for order in self._orders:
            if order.order_id == order_id:
                return order.to_dict()
        return None


# ==================== SERVICES ====================

class AuthenticationService:
    """Serviço de autenticação"""
    
    @staticmethod
    def login(email: str, password: str) -> bool:
        """Realiza login do usuário"""
        if email and password:
            session['logged_in'] = True
            session['user_email'] = email
            return True
        return False
    
    @staticmethod
    def logout():
        """Realiza logout do usuário"""
        session.pop('logged_in', None)
        session.pop('user_email', None)
    
    @staticmethod
    def is_authenticated() -> bool:
        """Verifica se usuário está autenticado"""
        return session.get('logged_in', False)
    
    @staticmethod
    def get_current_user_email() -> str:
        """Retorna email do usuário atual"""
        return session.get('user_email', 'usuario@exemplo.com')


class UserService:
    """Serviço para operações de usuário"""
    
    @staticmethod
    def get_profile_data() -> Dict[str, Any]:
        """Retorna dados do perfil do usuário"""
        user = UserModel(
            email=AuthenticationService.get_current_user_email(),
            name="Lucas Souza",
            preferences={
                "newsletter": True,
                "size_default": "41",
                "theme": "claro"
            },
            payment_methods=[
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
        )
        return user.to_dict()
    
    @staticmethod
    def get_checkout_data() -> Dict[str, Any]:
        """Retorna dados para checkout"""
        return {
            "addresses": [
                {"id": 1, "label": "Casa", "street": "Rua das Flores, 123", "city": "São Paulo", "zip": "01000-000", "default": True},
                {"id": 2, "label": "Trabalho", "street": "Av. Principal, 500", "city": "Rio de Janeiro", "zip": "20000-000", "default": False}
            ],
            "payment_methods": [
                {"id": 1, "brand": "Visa", "last_four": "1234", "expiry": "12/28", "default": True},
                {"id": 2, "brand": "Mastercard", "last_four": "9876", "expiry": "05/26", "default": False}
            ]
        }


class CartService:
    """Serviço para gerenciar carrinho de compras"""
    
    def __init__(self, product_repository: ProductRepository):
        self._product_repository = product_repository
    
    def get_items(self) -> List[Dict[str, Any]]:
        """Retorna itens do carrinho"""
        return session.get('cart', [])
    
    def add_item(self, product_id: int, size: str, quantity: int) -> bool:
        """Adiciona item ao carrinho"""
        product = self._product_repository.find_by_id(product_id)
        if not product:
            return False
        
        cart_item = CartItemModel(
            product_id=product['id'],
            title=product['title'],
            price=product['price'],
            size=size,
            quantity=quantity
        )
        
        cart_items = self.get_items()
        cart_items.append(cart_item.to_dict())
        session['cart'] = cart_items
        return True
    
    def clear(self):
        """Limpa o carrinho"""
        session.pop('cart', None)
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo do carrinho"""
        cart_items = self.get_items()
        subtotal = sum(
            float(item['price'].replace('R$', '').replace(',', '.').strip()) * item['quantity'] 
            for item in cart_items
        )
        shipping_cost = 25.00
        total = subtotal + shipping_cost
        
        return {
            "items": cart_items,
            "subtotal": subtotal,
            "shipping_cost": shipping_cost,
            "total": total
        }


class OrderService:
    """Serviço para gerenciar pedidos"""
    
    def __init__(self, order_repository: OrderRepository, cart_service: CartService):
        self._order_repository = order_repository
        self._cart_service = cart_service
    
    def get_all_orders(self) -> List[Dict[str, Any]]:
        """Retorna todos os pedidos do usuário"""
        return self._order_repository.get_all()
    
    def find_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Busca pedido por ID"""
        return self._order_repository.find_by_id(order_id)
    
    def process_payment(self) -> Optional[float]:
        """Processa pagamento"""
        cart_summary = self._cart_service.get_summary()
        if not cart_summary["items"]:
            return None
        
        total_val = cart_summary["total"]
        session['last_order_total'] = total_val
        return total_val
    
    def create_order(self) -> tuple[str, float]:
        """Cria novo pedido"""
        total_paid = session.pop('last_order_total', 150.00)
        order_id = f"PED-{random.randint(100000, 999999)}"
        self._cart_service.clear()
        return order_id, total_paid


# ==================== CONTROLLERS ====================

class BaseController:
    """Controlador base com métodos comuns"""
    
    def __init__(self, auth_service: AuthenticationService):
        self._auth_service = auth_service
    
    def require_authentication(self):
        """Verifica se usuário está autenticado, redireciona se não"""
        if not self._auth_service.is_authenticated():
            return redirect(url_for('login'))
        return None


class ProductController(BaseController):
    """Controlador de produtos"""
    
    def __init__(self, product_repository: ProductRepository, auth_service: AuthenticationService):
        super().__init__(auth_service)
        self._product_repository = product_repository
    
    def index(self):
        """Página inicial com produtos"""
        products = self._product_repository.get_all()
        return render_template('home.html', products=products)
    
    def detail(self, product_id: int):
        """Detalhes do produto"""
        product = self._product_repository.find_by_id(product_id)
        if product is None:
            abort(404)
        return render_template('product_detail.html', product=product)
    
    def collection(self):
        """Coleção de produtos com filtro"""
        category_filter = request.args.get('category')
        filtered_products = self._product_repository.search_by_category(category_filter)
        categories = ['All', 'Social', 'Casual', 'Bota', 'Esportivo']
        
        return render_template(
            'collection.html',
            products=filtered_products,
            categories=categories,
            selected_category=category_filter or 'All'
        )
    
    def search(self):
        """Busca de produtos"""
        query = request.args.get('q', '')
        # Por enquanto, redireciona para a coleção completa
        # Pode ser expandido para busca real no futuro
        return redirect(url_for('collection'))


class AuthController(BaseController):
    """Controlador de autenticação"""
    
    def login(self):
        """Página de login"""
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            if self._auth_service.login(email, password):
                return redirect(url_for('home'))
        return render_template('login.html')
    
    def register(self):
        """Página de registro"""
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            print(f"Novo Cadastro: {name}, Email: {email}")
            return redirect(url_for('login'))
        return render_template('register.html')
    
    def logout(self):
        """Logout"""
        self._auth_service.logout()
        return redirect(url_for('home'))


class UserController(BaseController):
    """Controlador de usuário"""
    
    def __init__(self, user_service: UserService, auth_service: AuthenticationService):
        super().__init__(auth_service)
        self._user_service = user_service
    
    def profile(self):
        """Perfil do usuário"""
        auth_check = self.require_authentication()
        if auth_check:
            return auth_check
        
        user_data = self._user_service.get_profile_data()
        return render_template('profile.html', user=user_data)


class CartController(BaseController):
    """Controlador de carrinho"""
    
    def __init__(self, cart_service: CartService, user_service: UserService, 
                 auth_service: AuthenticationService):
        super().__init__(auth_service)
        self._cart_service = cart_service
        self._user_service = user_service
    
    def view_cart(self):
        """Visualizar carrinho"""
        cart_summary = self._cart_service.get_summary()
        return render_template(
            'cart.html',
            cart_items=cart_summary['items'],
            subtotal=cart_summary['subtotal'],
            shipping_cost=cart_summary['shipping_cost'],
            total=cart_summary['total']
        )
    
    def add_to_cart(self, product_id: int):
        """Adicionar ao carrinho"""
        selected_size = request.form.get('size')
        quantity = int(request.form.get('quantity', 1))
        
        if self._cart_service.add_item(product_id, selected_size, quantity):
            return redirect(url_for('cart'))
        abort(404)
    
    def checkout(self):
        """Página de checkout"""
        cart_items = self._cart_service.get_items()
        if not cart_items:
            return redirect(url_for('cart'))
        
        user_data = self._user_service.get_checkout_data()
        cart_summary = self._cart_service.get_summary()
        
        return render_template(
            'checkout.html',
            cart_items=cart_items,
            user=user_data,
            subtotal=cart_summary['subtotal'],
            shipping_cost=cart_summary['shipping_cost'],
            total=cart_summary['total']
        )


class OrderController(BaseController):
    """Controlador de pedidos"""
    
    def __init__(self, order_service: OrderService, auth_service: AuthenticationService):
        super().__init__(auth_service)
        self._order_service = order_service
    
    def simulate_payment(self):
        """Simula pagamento"""
        total_val = self._order_service.process_payment()
        if total_val is None:
            return redirect(url_for('cart'))
        return redirect(url_for('order_success'))
    
    def order_success(self):
        """Página de sucesso do pedido"""
        auth_check = self.require_authentication()
        if auth_check:
            return auth_check
        
        order_id, total_paid = self._order_service.create_order()
        
        return render_template(
            'order_success.html',
            order_id=order_id,
            total_paid=total_paid,
            user_email=session.get('user_email', 'usuario@exemplo.com')
        )
    
    def list_orders(self):
        """Lista pedidos do usuário"""
        auth_check = self.require_authentication()
        if auth_check:
            return auth_check
        
        user_orders = self._order_service.get_all_orders()
        return render_template('orders.html', orders=user_orders)
    
    def track_detail(self, order_id: str):
        """Detalhes de rastreamento"""
        auth_check = self.require_authentication()
        if auth_check:
            return auth_check
        
        order = self._order_service.find_order(order_id)
        if order is None:
            return redirect(url_for('orders'))
        return render_template('track_detail.html', order=order)


class ContactController(BaseController):
    """Controlador de contato"""
    
    def contact(self):
        """Página de contato"""
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            subject = request.form.get('subject')
            message = request.form.get('message')
            
            print("--- NOVO CONTATO RECEBIDO ---")
            print(f"Nome: {name}")
            print(f"E-mail: {email}")
            print(f"Assunto: {subject}")
            print(f"Mensagem: {message[:50]}...")
            print("-----------------------------")
            
            flash('Sua mensagem foi enviada com sucesso! Responderemos em breve.', 'success')
            return redirect(url_for('contact'))
        
        return render_template('contact.html')


# ==================== APPLICATION ====================

class ShoeStoreApp:
    """Aplicação principal da loja de sapatos"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'a4c7e9f3b1d5c2e8a6f4d0c1b9a8e7d6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0'
        
        # Inicializa repositórios
        self._product_repository = ProductRepository()
        self._order_repository = OrderRepository()
        
        # Inicializa serviços
        self._auth_service = AuthenticationService()
        self._user_service = UserService()
        self._cart_service = CartService(self._product_repository)
        self._order_service = OrderService(self._order_repository, self._cart_service)
        
        # Inicializa controladores
        self._product_controller = ProductController(self._product_repository, self._auth_service)
        self._auth_controller = AuthController(self._auth_service)
        self._user_controller = UserController(self._user_service, self._auth_service)
        self._cart_controller = CartController(self._cart_service, self._user_service, self._auth_service)
        self._order_controller = OrderController(self._order_service, self._auth_service)
        self._contact_controller = ContactController(self._auth_service)
        
        # Registra rotas
        self._register_routes()
    
    def _register_routes(self):
        """Registra todas as rotas da aplicação"""
        # Rotas de produtos
        self.app.add_url_rule('/', 'home', self._product_controller.index)
        self.app.add_url_rule('/product/<int:product_id>', 'product_detail', self._product_controller.detail)
        self.app.add_url_rule('/collection', 'collection', self._product_controller.collection)
        self.app.add_url_rule('/search', 'search', self._product_controller.search)
        
        # Rotas de autenticação
        self.app.add_url_rule('/login', 'login', self._auth_controller.login, methods=['GET', 'POST'])
        self.app.add_url_rule('/register', 'register', self._auth_controller.register, methods=['GET', 'POST'])
        self.app.add_url_rule('/logout', 'logout', self._auth_controller.logout)
        
        # Rotas de usuário
        self.app.add_url_rule('/profile', 'profile', self._user_controller.profile)
        
        # Rotas de carrinho
        self.app.add_url_rule('/cart', 'cart', self._cart_controller.view_cart)
        self.app.add_url_rule('/add_to_cart/<int:product_id>', 'add_to_cart', self._cart_controller.add_to_cart, methods=['POST'])
        self.app.add_url_rule('/checkout', 'checkout', self._cart_controller.checkout)
        
        # Rotas de pedidos
        self.app.add_url_rule('/simulate_payment', 'simulate_payment', self._order_controller.simulate_payment)
        self.app.add_url_rule('/order_success', 'order_success', self._order_controller.order_success)
        self.app.add_url_rule('/orders', 'orders', self._order_controller.list_orders)
        self.app.add_url_rule('/track/<string:order_id>', 'track', self._order_controller.track_detail)
        
        # Rotas de contato
        self.app.add_url_rule('/contact', 'contact', self._contact_controller.contact, methods=['GET', 'POST'])
    
    def run(self, *args, **kwargs):
        """Executa a aplicação"""
        self.app.run(*args, **kwargs)


# ==================== ENTRY POINT ====================

if __name__ == '__main__':
    store_app = ShoeStoreApp()
    store_app.run(debug=True)
