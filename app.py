import os
from flask import Flask, json, jsonify, render_template, request, redirect, send_file, session, url_for
from flask_mysqldb import MySQL
import logging

app = Flask(__name__)
app.secret_key = 'clave_secreta'

##########################################################
##### Base de datos MySQL. #####
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root' # Cambiar contraseña dependiendo su MySQL
app.config['MYSQL_DB'] = 'im117'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

##########################################################
##### Rutas de inicio de sesión y cerrar sesión. #####
### Ruta de login. ###
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario,))
        user = cur.fetchone()
        cur.close()
        if user and user['password'] == password:
            session['user'] = user  
            if user['rol'] == 'almacen':
                return redirect(url_for('menu_almacen'))
            elif user['rol'] == 'mantenimiento':
                return redirect(url_for('menu_mantenimiento'))
            elif user['rol'] == 'ventas':
                return redirect(url_for('menu_ventas'))
            elif user['rol'] == 'proveedores':
                return redirect(url_for('menu_proveedores'))
            elif user['rol'] == 'envios':
                return redirect(url_for('menu_envios'))
        else:
            return "Nombre de usuario o contraseña incorrectos. Intente nuevamente."
    return render_template('index.html')

### Ruta de logout. ###
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)  
    return redirect(url_for('login')) 

###### Rutas del encargado de almacen. ######

### Ruta menú del encargado de almacen. ###
@app.route('/menu_almacen')
def menu_almacen():
    return render_template('menu_almacen.html')  

###### Rutas del encargado de envios. ######

### Ruta menú del encargado de envios. ###
@app.route('/menu_envios')
def menu_envios():
    return render_template('menu_envios.html')  

###### Rutas del encargado de mantenimiento y reparación. ######

### Ruta menú del encargado de matenimiento y reparación. ###
@app.route('/menu_mantenimiento')
def menu_mantenimiento():
    return render_template('menu_mantenimiento.html')  

### Ruta menú del encargado de proveedores. ###
@app.route('/menu_proveedores')
def menu_proveedores():
    return render_template('menu_proveedores.html')  

### Ruta menú del encargado de ventas. ###
@app.route('/menu_ventas')
def menu_ventas():
    return render_template('menu_ventas.html')  

if __name__ == '__main__':
    app.run(debug=True)