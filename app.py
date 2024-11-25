import os
from flask import Flask, render_template, request, redirect, send_file, session, url_for
from flask_mysqldb import MySQL
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = 'clave_secreta'

##########################################################
##### Configuración de la base de datos MySQL. #####
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'  # Cambiar contraseña según configuración
app.config['MYSQL_DB'] = 'im117'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

##########################################################
##### Rutas de inicio de sesión y logout. #####
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

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

###### Rutas del encargado de mantenimiento y reparación. ######
@app.route('/menu_mantenimiento')
def menu_mantenimiento():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM mantenimiento")
    datos = cur.fetchall()
    cur.close()
    return render_template('menu_mantenimiento.html', datos=datos)

@app.route('/nueva_solicitud')
def nueva_solicitud():
    return render_template('reporte_mantenimiento.html')

@app.route('/generar_reporte', methods=['POST'])
def generar_reporte():
    fecha_inicio = request.form['fecha_inicio']
    fecha_fin = request.form['fecha_fin']

    # Consulta a la base de datos
    cur = mysql.connection.cursor()
    query = """
        SELECT * FROM mantenimiento 
        WHERE fecha BETWEEN %s AND %s
    """
    cur.execute(query, (fecha_inicio, fecha_fin))
    registros = cur.fetchall()
    cur.close()

    # Generar el PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(200, 10, 'Reporte de Mantenimiento', 0, 1, 'C')
    pdf.ln(10)

    # Agregar encabezados
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(10, 10, 'ID', 1)
    pdf.cell(26, 10, 'Nombre Arma', 1)
    pdf.cell(35, 10, 'Tipo Servicio', 1)
    pdf.cell(85, 10, 'Descripcion Falla', 1)
    pdf.cell(20, 10, 'Fecha', 1)
    pdf.ln()

    # Agregar datos
    pdf.set_font('Arial', '', 8)
    for registro in registros:
        pdf.cell(10, 10, str(registro['id']), 1)
        pdf.cell(26, 10, registro['nombreA'] if registro['nombreA'] else 'N/A', 1)
        pdf.cell(35, 10, registro['tipoServicio'] if registro['tipoServicio'] else 'N/A', 1)
        pdf.cell(85, 10, registro['descripcionFalla'] if registro['descripcionFalla'] else 'N/A', 1)
        pdf.cell(20, 10, registro['fecha'].strftime('%Y-%m-%d') if registro['fecha'] else 'N/A', 1)
        pdf.ln()

    # Guardar PDF temporalmente
    pdf_path = 'reporte_mantenimiento.pdf'
    pdf.output(pdf_path)

    # Enviar PDF al usuario
    return send_file(pdf_path, as_attachment=True)

##########################################################
##### Rutas del encargado de almacen #####
@app.route('/menu_almacen')
def menu_almacen():
    return render_template('menu_almacen.html')

##########################################################
##### Rutas del encargado de envios #####
@app.route('/menu_envios')
def menu_envios():
    return render_template('menu_envios.html')

##########################################################
###### Rutas del encargado de proveedores. ######
@app.route('/menu_proveedores')
def menu_proveedores():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM pedidos")  
    pedidos = cur.fetchall()
    cur.close()
    return render_template('menu_proveedores.html', pedidos=pedidos)

###### Modal para registrar un nuevo pedido a proveedores. ######
@app.route('/nuevo_pedido', methods=['POST'])
def nuevo_pedido():
    equipo = request.form['equipo']
    cantidad = request.form['cantidad']
    proveedor = request.form['proveedor']
    fecha = request.form['fecha']
    comentarios = request.form['comentarios']

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO pedidos (equipo, cantidad, proveedor, fecha, comentarios)
        VALUES (%s, %s, %s, %s, %s)
    """, (equipo, cantidad, proveedor, fecha, comentarios))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('menu_proveedores'))

###### Ruta para la consulta de pedidos por ID. ######
@app.route('/buscar', methods=['POST'])
def buscar():
    pedido_id = request.form.get('id')
    cursor = mysql.connection.cursor()

    # Consulta a la BD para obtener un pedido por ID
    consulta = """SELECT * FROM pedidos WHERE id = %s"""
    cursor.execute(consulta, (pedido_id,))
    pedido = cursor.fetchone()
    cursor.close()

    if not pedido:
        mensaje = f"No se encontró ningún pedido con el ID {pedido_id}."
        return render_template('menu_proveedores.html', mensaje=mensaje, pedido=pedido)

    # Si se encuentra el pedido, se pasa a la plantilla con los detalles
    return render_template('menu_proveedores.html', pedido=pedido)

##########################################################
##### Rutas del encargado de ventas. #####
@app.route('/menu_ventas')
def menu_ventas():
    return render_template('menu_ventas.html')

if __name__ == '__main__':
    app.run(debug=True)
