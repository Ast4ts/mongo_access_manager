from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import json

app = Flask(__name__)

# Загрузка конфигурации
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Главная страница
@app.route('/')
def index():
    return render_template('main.html')

# Панель управления MongoDB
@app.route('/mongodb_management')
def mongodb_management():
    mongo_servers = config['mongodb_servers']
    return render_template('mongodb_management.html', mongo_servers=mongo_servers)

# Управление пользователями MongoDB
@app.route('/manage_mongo', methods=['POST'])
def manage_mongo():
    server_idx = int(request.form['server'])
    username = request.form['username']
    password = request.form.get('password', None)
    roles = request.form.get('roles', '')
    action = request.form['action']
    
    mongo_server = config['mongodb_servers'][server_idx]
    client = MongoClient(mongo_server['uri'])
    db = client[mongo_server['db_name']]

    if action == 'add':
        db.command("createUser", username, pwd=password, roles=["readAnyDatabase"])
    elif action == 'remove':
        db.command("dropUser", username)
    elif action == 'add_role':
        roles_list = [role.strip() for role in roles.split(',')]
        db.command("grantRolesToUser", username, roles=[{"role": role, "db": mongo_server['db_name']} for role in roles_list])

    return redirect(url_for('mongodb_management'))
@app.route('/add_mongo_user', methods=['GET', 'POST'])
def add_mongo_user():
    mongo_servers = config['mongodb_servers']
    success_message = None

    if request.method == 'POST':
        server_idx = int(request.form['server'])
        username = request.form['username']
        password = request.form['password']
        
        mongo_server = mongo_servers[server_idx]
        client = MongoClient(mongo_server['uri'])
        db = client[mongo_server['db_name']]

        try:
            # Добавляем пользователя с ролью "readAnyDatabase"
            db.command("createUser", username, pwd=password, roles=[{'role': 'readAnyDatabase', 'db': 'admin'}])
            success_message = f"User '{username}' successfully added with role 'readAnyDatabase'."
        except Exception as e:
            print(f"Error adding user: {e}")
            success_message = f"Failed to add user '{username}'. Please try again."

    return render_template('add_mongo_user.html', mongo_servers=mongo_servers, success_message=success_message)



# Список пользователей MongoDB
@app.route('/list_mongo_users', methods=['GET', 'POST'])
def list_mongo_users():
    mongo_servers = config['mongodb_servers']  # Получаем список серверов из конфигурации
    users = []
    if request.method == 'POST':
        server_idx = int(request.form['server'])
        mongo_server = mongo_servers[server_idx]
        client = MongoClient(mongo_server['uri'])
        db = client[mongo_server['db_name']]

        try:
            users_info = db.command("usersInfo")
            users = users_info.get('users', [])
        except Exception as e:
            print(f"Error fetching users: {e}")

    return render_template('list_users.html', users=users, mongo_servers=mongo_servers)


# Добавление ролей пользователю MongoDB
@app.route('/add_roles_to_user')
def add_roles_to_user():
    mongo_servers = config['mongodb_servers']
    return render_template('add_roles_to_user.html', mongo_servers=mongo_servers)

if __name__ == '__main__':
    app.run(debug=True)
