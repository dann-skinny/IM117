import os 
from flask import Flask, render_template, request, redirect, send_file, session, url_for 
from flask_mysqldb import MySQL 
from fpdf import FPDF 
###Todo lo de aquí abajo fue lo que se instalo y agrego para la grafica###
import matplotlib
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
matplotlib.use('Agg')
from sklearn.linear_model import LinearRegression 
import io 
import base64

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
##### Rutas del encargado de almacén #####
@app.route('/menu_almacen')
def menu_almacen():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM armas")
    armas = cur.fetchall()
    cur.close()
    return render_template('menu_almacen.html', armas=armas)

## Consulta de equipo ##
@app.route('/b_equipo', methods=['POST'])
def buscarA():
    nombre_arma = request.form.get('nombre_arma')  # Cambiado a 'arma'
    cursor = mysql.connection.cursor()

    # Consulta a la BD para obtener un envío por ID
    consulta = """SELECT * FROM armas WHERE nombre_arma = %s"""
    cursor.execute(consulta, (nombre_arma,))
    arma = cursor.fetchone()
    cursor.close()

    if not arma:
        mensaje = f"No se encontró ningún equipo con el nombre {nombre_arma}."
        return render_template('menu_almacen.html', mensaje=mensaje, arma=arma)

    # Si se encuentra el envío, se pasa a la plantilla con los detalles
    return render_template('menu_almacen.html', arma=arma)

## Agregar equipo ##
@app.route('/nuevo_equipo', methods=['POST'])
def nuevo_equipo():
    arma = request.form['nombre_arma']
    modelo = request.form['modelo']
    calibre = request.form['calibre']
    numSerie = request.form['numSerie']
    disparo = request.form['sistemaDisparo']
    materiales = request.form['materiales']
    peso = request.form['peso']
    costo = request.form['costo']
    
    cur = mysql.connection.cursor()
    escribir = """INSERT INTO armas (nombre_arma, modelo, calibre, numSerie, sistemaDisparo, materiales, peso, costo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    cur.execute(escribir, (arma, modelo, calibre, numSerie, disparo, materiales, peso, costo))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('menu_almacen'))

## Editar equipo ##
@app.route('/editar_equipo/<string:numSerie>', methods=['POST'])
def editar_equipo(numSerie):
    arma = request.form['nombre_arma']
    modelo = request.form['modelo']
    calibre = request.form['calibre']
    numSerie = request.form['numSerie']
    disparo = request.form['sistemaDisparo']
    materiales = request.form['materiales']
    peso = request.form['peso']
    costo = request.form['costo']

    cursor = mysql.connection.cursor()
    modificar = """UPDATE armas SET nombre_arma = %s, modelo = %s, calibre = %s, sistemaDisparo = %s, materiales = %s, peso = %s, costo = %s WHERE numSerie = %s"""
    cursor.execute(modificar, (arma, modelo, calibre, disparo, materiales, peso, costo, numSerie))
    mysql.connection.commit()
    cursor.execute("SELECT * FROM armas")
    cursor.close()

    return redirect(url_for('menu_almacen'))

@app.route('/cambiar_estadoA/<string:armas_numSerie>', methods=['POST'])
def cambiar_estadoA(armas_numSerie):
    nuevo_estado = request.form['estado']
    
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE armas
        SET estado = %s
        WHERE numSerie = %s
    """, (nuevo_estado, armas_numSerie))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('menu_almacen'))


##########################################################
##### Rutas del encargado de envios #####
@app.route('/menu_envios')
def menu_envios():
    # Obtener los envíos desde la base de datos
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM envios")
    envios = cur.fetchall()
    cur.close()
    
    # Renderizar la plantilla de gestión de envíos
    return render_template('menu_envios.html', envios=envios)

@app.route('/nuevo_envio', methods=['POST'])
def nuevo_envio():
    nombre_cliente = request.form['nombre_cliente']
    cantidad_arma = request.form['cantidad_arma']
    direccion = request.form['direccion']
    fecha = request.form['fecha']
    
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO envios (nombre_cliente, cantidad_arma, direccion, fecha)
        VALUES (%s, %s, %s, %s)
    """, (nombre_cliente, cantidad_arma, direccion, fecha))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('menu_envios'))


@app.route('/cambiar_estado/<int:envio_id>', methods=['POST'])
def cambiar_estado(envio_id):
    nuevo_estado = request.form['estado']
    
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE envios
        SET estado = %s
        WHERE id = %s
    """, (nuevo_estado, envio_id))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('menu_envios'))

###### Ruta para la consulta de envios por ID. ######
@app.route('/b_envio', methods=['POST'])
def buscarE():
    envio_id = request.form.get('id')
    cursor = mysql.connection.cursor()

    # Consulta a la BD para obtener un envío por ID
    consulta = """SELECT * FROM envios WHERE id = %s"""
    cursor.execute(consulta, (envio_id,))
    envio = cursor.fetchone()
    cursor.close()

    if not envio:
        mensaje = f"No se encontró ningún envío con el ID {envio_id}."
        return render_template('menu_envios.html', mensaje=mensaje, envio=envio)

    # Si se encuentra el envío, se pasa a la plantilla con los detalles
    return render_template('menu_envios.html', envio=envio)

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
    cur = mysql.connection.cursor()

    query = """
        SELECT armas.nombre_arma AS nombre_arma, SUM(ventas.cantidad) AS total_cantidad
        FROM ventas
        INNER JOIN armas ON ventas.numSerie = armas.numSerie
        GROUP BY armas.nombre_arma
        ORDER BY total_cantidad DESC
    """
    cur.execute(query)
    resultados = cur.fetchall()
    cur.close()

    if resultados:
        arma_mas_vendida = resultados[0]['nombre_arma']
        arma_menos_vendida = resultados[-1]['nombre_arma']
    else:
        arma_mas_vendida = "No hay ventas registradas"
        arma_menos_vendida = "No hay ventas registradas"

    return render_template('menu_ventas.html', arma_mas_vendida=arma_mas_vendida, arma_menos_vendida=arma_menos_vendida)

@app.route('/nuevo_reporteV')
def nuevo_reporteV():
    return render_template('reporte_ventas.html')

###Ruta para generar el reporte de ventas ###
@app.route('/generar_reporte_ventas', methods=['POST'])
def generar_reporte_ventas():
    fecha_inicio = request.form['fecha_inicio']
    fecha_fin = request.form['fecha_fin']

    # Consulta a la base de datos
    cur = mysql.connection.cursor()
    query = """
        SELECT * FROM ventas 
        WHERE fecha BETWEEN %s AND %s
    """
    cur.execute(query, (fecha_inicio, fecha_fin))
    registros = cur.fetchall()
    
    # Calcular el total de ventas
    total_ventas = sum([registro['total'] for registro in registros])
    
    cur.close()

    # Generar el PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(200, 10, 'Reporte de Ventas', 0, 1, 'C')
    pdf.ln(10)

    # Agregar encabezados
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(10, 12, 'ID', 1, 0, 'C')
    pdf.cell(20, 12, 'Fecha', 1, 0, 'C')
    pdf.cell(25, 12, 'Num Serie', 1, 0, 'C')
    pdf.cell(20, 12, 'Cantidad', 1, 0, 'C')
    pdf.cell(27, 12, 'Precio Unitario', 1, 0, 'C')
    pdf.cell(20, 12, 'Total', 1, 0, 'C')
    pdf.cell(32, 12, 'Metodo Pago', 1, 0, 'C')
    pdf.ln()

    # Agregar datos
    pdf.set_font('Arial', '', 8)
    for registro in registros:
        pdf.cell(10, 12, str(registro['id_venta']), 1, 0, 'C')
        pdf.cell(20, 12, registro['fecha'].strftime('%Y-%m-%d') if registro['fecha'] else 'N/A', 1, 0, 'C')
        pdf.cell(25, 12, registro['numSerie'] if registro['numSerie'] else 'N/A', 1, 0, 'C')
        pdf.cell(20, 12, str(registro['cantidad']), 1, 0, 'C')
        pdf.cell(27, 12, str(registro['precio_unitario']), 1, 0, 'C')
        pdf.cell(20, 12, str(registro['total']), 1, 0, 'C')
        pdf.cell(32, 12, registro['metodo_pago'] if registro['metodo_pago'] else 'N/A', 1, 0, 'C')
        pdf.ln()

    # Agregar el total de ventas
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(200, 12, f'Total de Ventas: ${total_ventas:.2f}', 0, 1, 'C')

    # Guardar PDF temporalmente
    pdf_path = 'reporte_ventas.pdf'
    pdf.output(pdf_path)

    # Enviar PDF al usuario
    return send_file(pdf_path, as_attachment=True)

###Ruta y proceso para generar la grafica###
@app.route('/generar_grafica', methods=['POST'])
def generar_grafica():
    try:
        year = request.form['year']

        # Consulta a la base de datos para obtener los datos de ventas
        cur = mysql.connection.cursor()
        query = """
            SELECT fecha, total FROM ventas
            WHERE YEAR(fecha) = %s
        """
        cur.execute(query, (year,))
        registros = cur.fetchall()
        cur.close()

        # Verificar si hay datos para el año especificado
        if not registros:
            return render_template('grafica_ventas.html', error=f"No hay datos disponibles para el año {year}", year=year)

        # Convertir los registros en un DataFrame de pandas
        data = pd.DataFrame(registros, columns=['fecha', 'total'])

        # Convertir la columna 'fecha' a datetime
        data['fecha'] = pd.to_datetime(data['fecha'])

        # Extraer el mes de la columna 'fecha'
        data['mes'] = data['fecha'].dt.month

        # Agrupar los datos por mes y sumar las ventas
        monthly_sales = data.groupby('mes')['total'].sum().reset_index()

        # Generar la gráfica
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(monthly_sales['mes'], monthly_sales['total'], marker='o', linestyle='-', color='b')
        ax.set_title(f'Ventas Mensuales - {year}')
        ax.set_xlabel('Mes')
        ax.set_ylabel('Total de Ventas')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'])
        ax.grid(True)

        # Guardar la gráfica en un objeto en memoria
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()

        # Cerrar la figura
        plt.close(fig)

        return render_template('grafica_ventas.html', graph_url=graph_url, year=year)

    except Exception as e:
        # Manejo de errores generales
        return render_template('grafica_ventas.html', error=f"Ocurrió un error: {str(e)}", year=year)

if __name__ == '__main__':
    app.run(debug=True)
