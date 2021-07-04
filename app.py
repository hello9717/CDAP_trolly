import MySQLdb
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_mysqldb import MySQL
import logging as logger
import json
from flask_cors import CORS

logger.basicConfig(level="DEBUG")
app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "trolly"
mysql = MySQL(app)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
CORS(app)


@app.route('/users')
def users():
    con = mysql.connection.cursor()
    sql = "SELECT * FROM users"
    con.execute(sql)
    res = con.fetchall()
    return render_template("admin/POS.html", datas=res)


@app.route('/welcome')
def welcome():
    return redirect('/products')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        con = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "SELECT * from users WHERE cardno=" + request.form['cardid']
        con.execute(sql)
        res = con.fetchone()
        con.close()
        session['session'] = request.form['cardid']
        session['Name'] = res["Name"]
        session['id'] = res["id"]
        return redirect('/welcome')

    return render_template("login.html")


@app.route('/admin/adduser', methods=['GET', 'POST'])
def addusers():
    if request.method == 'POST':
        name = request.form['name']
        cardid = request.form['cardid']
        con = mysql.connection.cursor()
        sql = "INSERT INTO users(id, Name, cardno) value (null,%s,%s)"
        con.execute(sql, [name, cardid])
        mysql.connection.commit()
        con.close()
        return redirect(url_for("hello_world"))
    return render_template("admin/add.html")


@app.route('/admin/addproduct', methods=['GET', 'POST'])
def addproduct():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        barcode = request.form['barcode']
        con = mysql.connection.cursor()
        sql = "INSERT INTO products(id, name, price, barcode) value (null,%s,%s,%s)"
        con.execute(sql, [name, price, barcode])
        mysql.connection.commit()
        con.close()
        return redirect(url_for("hello_world"))
    return render_template("admin/addproduct.html")


@app.route('/products', methods=['GET', 'POST'])
def products():
    # Get Products
    con = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "SELECT * FROM products"
    con.execute(sql)
    res = con.fetchall()
    con.close()

    # Get cart Products
    con = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql3 = "SELECT p.name, p.price, p.id, c.count FROM cart c JOIN products p on (c.productid=p.id and c.userid =" + str(
        session["id"]) + ")"
    con.execute(sql3)
    res2 = con.fetchall()
    con.close()

    # add To cart
    if request.method == 'POST':
        # Get Product ID
        con = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        GetIDSql = "SELECT id from products WHERE barcode=" + request.form['cardid']
        con.execute(GetIDSql)
        GetIDRes = con.fetchone()
        con.close()
        productid = GetIDRes["id"]
        userid = session["id"]

        # Get to cart Duplicate
        con = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        CartDuplicateSql = "SELECT * From Cart where userid=" + str(userid) + " And productid=" + str(productid)
        con.execute(CartDuplicateSql)
        CartDuplicateRes = con.fetchone()
        con.close()

        if CartDuplicateRes == None:
            con = mysql.connection.cursor()
            sql = "INSERT INTO cart(userid, productid) value (%s,%s)"
            con.execute(sql, [userid, productid])
            mysql.connection.commit()
            con.close()
        else:
            count = int(CartDuplicateRes["count"]) + 1
            con = mysql.connection.cursor()
            sql = "UPDATE cart SET count = " + str(count) + "  where userid=" + str(userid) + " And productid=" + str(
                productid)
            con.execute(sql)
            mysql.connection.commit()
            con.close()

    return render_template("products.html", datas=res, cart=res2)


@app.route('/product/<int:id>', methods=['GET', 'POST'])
def product(id):
    # Get Products
    con = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "SELECT * FROM products WHERE id=" + str(id)
    con.execute(sql)
    res = con.fetchone()
    con.close()

    # Get cart Products
    con = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql3 = "SELECT p.name, p.price, p.id, c.count FROM cart c JOIN products p on (c.productid=p.id and c.userid =" + str(
        session["id"]) + ")"
    con.execute(sql3)
    res2 = con.fetchall()
    con.close()

    # add To cart
    if request.method == 'POST':
        # Get Product ID
        con = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        GetIDSql = "SELECT id from products WHERE barcode=" + request.form['cardid']
        con.execute(GetIDSql)
        GetIDRes = con.fetchone()
        con.close()
        productid = GetIDRes["id"]
        userid = session["id"]

        # Get to cart Duplicate
        con = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        CartDuplicateSql = "SELECT * From Cart where userid=" + str(userid) + " And productid=" + str(productid)
        con.execute(CartDuplicateSql)
        CartDuplicateRes = con.fetchone()
        con.close()

        if CartDuplicateRes is None:
            con = mysql.connection.cursor()
            sql = "INSERT INTO cart(userid, productid) value (%s,%s)"
            con.execute(sql, [userid, productid])
            mysql.connection.commit()
            con.close()
        else:
            count = int(CartDuplicateRes["count"]) + 1
            con = mysql.connection.cursor()
            sql = "UPDATE cart SET count = " + str(count) + "  where userid=" + str(userid) + " And productid=" + str(
                productid)
            con.execute(sql)
            mysql.connection.commit()
            con.close()

    return render_template("product.html", datas=res, cart=res2)


@app.route('/api/map', methods=['GET'])
def api_map_get():
    con = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "SELECT * FROM map where status=true"
    con.execute(sql)
    res = con.fetchall()
    return jsonify(res)


@app.route('/api/map', methods=['POST'])
def apo_map_post():
    data = json.dumps(request.get_json())
    d = json.loads(data)
    con = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "INSERT INTO map(id, x, y, status,tileID) value (%s,%s,%s,%s,%s)"
    con.execute(sql, [d['id'], d['x'], d['y'], d['status'], d['tileID']])
    mysql.connection.commit()
    con.close()

    return data, 200


@app.route('/api/map/<int:x>/<int:y>', methods=['PUT'])
def apo_map_put(x, y):
    data = json.dumps(request.get_json())
    d = json.loads(data)
    con = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "UPDATE map SET status = " + str(d['status']) + " Where x= " + str(x) + " and y=" + str(y)
    con.execute(sql)
    mysql.connection.commit()
    con.close()
    return jsonify(x, y), 200


if __name__ == '__main__':
    logger.debug("Start")
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=True)
