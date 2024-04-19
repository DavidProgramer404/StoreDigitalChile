from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

# Crear la aplicación Flask
app = Flask(__name__)
app.secret_key = 'password'  # Clave secreta para la sesión

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'password'

# Inicializar la extensión SQLAlchemy con la aplicación Flask
db = SQLAlchemy(app)

# Inicializar el administrador de inicio de sesión de Flask
login_manager = LoginManager()
login_manager.init_app(app)

# Definir el modelo de la tabla User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

    # Método para establecer la contraseña
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Método para verificar la contraseña
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Definir el modelo de la tabla Product
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)

# Configurar la función para cargar un usuario desde la base de datos
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# Rutas
@app.route('/')
def home():
    products = Product.query.all()  # Obtener todos los productos de la base de datos
    return render_template('home.html', products=products)  # Pasar los productos a la plantilla HTML


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)  # Iniciar sesión del usuario
            return redirect(url_for('home'))
        else:
            return 'Usuario o contraseña incorrectos'
    return render_template('login.html')

@app.route("/logout")
@login_required  # El usuario debe estar autenticado para acceder a esta ruta
def logout():
    logout_user()  # Cerrar sesión del usuario
    return redirect(url_for('home'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Verificar si el nombre de usuario ya está en uso
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return 'El nombre de usuario ya está en uso'

        # Verificar si las contraseñas coinciden
        if password != confirm_password:
            return 'Las contraseñas no coinciden'

        # Crear un nuevo usuario
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))  # Redirigir al usuario al inicio de sesión

    return render_template('register.html')

@app.route('/create_product', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        # Crear un nuevo producto y guardarlo en la base de datos
        new_product = Product(name=name, description=description, price=price)
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('home'))  # Redirigir a la página de inicio después de crear el producto

    return render_template('create_product.html')



# Crear todas las tablas definidas en los modelos
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)


try:
    db.session.add(new_product)
    db.session.commit()
except Exception as e:
    print("Error al guardar en la base de datos:", e)
