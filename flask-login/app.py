from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_muito_segura_aqui'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_form'

users_db = {}
user_id_counter = 0

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def get(user_id):
        for user_data in users_db.values():
            if str(user_data['id']) == str(user_id):
                return User(user_data['id'], user_data['username'], user_data['password_hash'])
        return None
 
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('home.html', username=current_user.username, logged_in=True)
    return render_template('home.html', logged_in=False)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        flash("Você já está logado(a). Redirecionando para a página inicial.", "info")
        return redirect(url_for('home'))

    global user_id_counter
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        senha2 = request.form['senha2']

        if not nome or not senha or not senha2:
            flash("Todos os campos são obrigatórios!", "danger")
            return render_template('login_cadastro.html')
        
        if senha != senha2:
            flash("As senhas não coincidem. Por favor, tente novamente.", "danger")
            return render_template('login_cadastro.html')

        if nome in users_db:
            flash("Este e-mail já está cadastrado. Por favor, use outro.", "danger")
            return render_template('login_cadastro.html')
        
  
        hashed_password = generate_password_hash(senha)
        user_id_counter += 1
        users_db[nome] = {'id': user_id_counter, 'username': nome, 'password_hash': hashed_password}
        
        flash("Usuário cadastrado com sucesso! Faça login.", "success")
        return redirect(url_for('login_form'))

    return render_template('login_cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login_form():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        
        user_data = users_db.get(nome)

        if user_data and check_password_hash(user_data['password_hash'], senha):
            user = User(user_data['id'], user_data['username'], user_data['password_hash'])
            login_user(user)
            flash(f"Bem-vindo(a), {nome}!", "success")
            return redirect(url_for('home'))
        else:
            flash("E-mail ou senha incorretos.", "danger")
    return render_template('login_form.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Você foi desconectado(a).", "info")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)