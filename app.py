from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import datetime
import os

app = Flask(__name__)
app.secret_key = "ferreteria_secret_key"

DB = "ferreteria_web.db"

def crear_base():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        password TEXT,
        rol TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        producto TEXT,
        cantidad TEXT,
        fecha TEXT
    )
    """)

    cursor.execute("SELECT * FROM usuarios WHERE usuario='ADMIN'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios VALUES (NULL,'ADMIN','1234','ADMIN')")

    conn.commit()
    conn.close()

crear_base()

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def validar_login():
    usuario = request.form["usuario"]
    password = request.form["password"]

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND password=?", (usuario,password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session["usuario"] = usuario
        session["rol"] = user[3]
        return redirect(url_for("panel"))
    else:
        return "Usuario o contraseña incorrectos"

@app.route("/panel")
def panel():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("panel.html", usuario=session["usuario"], rol=session["rol"])

@app.route("/crear_pedido", methods=["POST"])
def crear_pedido():
    if "usuario" not in session:
        return redirect(url_for("login"))

    producto = request.form["producto"]
    cantidad = request.form["cantidad"]
    fecha = str(datetime.datetime.now())

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pedidos VALUES (NULL,?,?,?,?)",
                   (session["usuario"],producto,cantidad,fecha))
    conn.commit()
    conn.close()

    return redirect(url_for("panel"))

@app.route("/historial")
def historial():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos")
    pedidos = cursor.fetchall()
    conn.close()
    return render_template("historial.html", pedidos=pedidos)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)