from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import accountant, json, os

app = Flask(__name__)
app.secret_key = os.urandom(24)
sess = Session()
sess.init_app(app)
accountant.manager.main()

@app.route('/set/')
def set():
    session['key'] = 'value'
    return 'ok'

@app.route('/get/')
def get():
    return session.get('key', 'not set')

@app.route('/')
def set_form(): 
    return render_template("index.html", saldo_value=accountant.manager.saldo, storehouse=accountant.manager.storehouse)

@app.route('/buy', methods=["POST"])
def update_buy():
    product_id = request.form["product_id"]
    product_amount = int(request.form["product_amount"])
    unit_price = int(request.form["unit_price"]) 
    if accountant.manager.saldo - (product_amount*unit_price) < 0:
        messages = json.dumps({"main":"Nie wystarczająca ilość środków by zakupić {} w ilości {} w cenie za sztukę {}".format(product_id, product_amount, unit_price)})
        session['messages'] = messages
        return redirect(url_for("form_error", messages=messages))
    accountant.manager.buy_fun(product_id, unit_price, product_amount, "out.txt")
    return redirect(url_for("set_form"))

@app.route('/sale', methods=["POST"])
def update_sale():
    product_id = request.form["product_id"]
    product_amount = int(request.form["product_amount"])
    unit_price = int(request.form["unit_price"]) 
    if product_id not in accountant.manager.storehouse:
        messages = json.dumps({"main":"Produkt \"{}\" nie istnieje na magazynie".format(product_id)})
        session['messages'] = messages
        return redirect(url_for("form_error", messages=messages))  
    elif accountant.manager.storehouse[product_id] - product_amount < 0:
        messages = json.dumps({"main":"Nie wystarczająca ilość produktu \"{}\" na magazynie".format(product_id)})
        session['messages'] = messages
        return redirect(url_for("form_error", messages=messages))
    if product_amount < 0:
        messages = json.dumps({"main":'Ilość produktu "{}" mniejsza niż 0'.format(product_id)})
        session['messages'] = messages
        return redirect(url_for("form_error", messages=messages))
    accountant.manager.sale_fun(product_id, unit_price, product_amount, "out.txt")
    return redirect(url_for("set_form"))

@app.route('/saldo', methods=["POST"])
def update_saldo():
    accountant.manager.saldo_fun(int(request.form["saldo_value"]), request.form["comment"])
    return redirect(url_for("set_form"))

@app.route('/error')
def form_error():
    messages = request.args['messages']
    messages = session['messages']
    return render_template("error.html", messages=json.loads(messages))

@app.route('/history')
def set_logs():
    return render_template("history.html", logs=accountant.manager.logs)