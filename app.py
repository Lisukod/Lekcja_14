from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import accountant, json, os
from flask_sqlalchemy import SQLAlchemy
from flask_alembic import Alembic

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"

db = SQLAlchemy(app)


class Produkty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(120), unique=False, nullable=False)
    stan_mag = db.Column(db.Integer, unique=False, nullable=False)


class Saldo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wartosc_salda = db.Column(db.Integer, unique=False, nullable=False)


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(120), unique=False, nullable=False)
    pierwszy_param = db.Column(db.String(120), unique=False, nullable=False)
    drugi_param = db.Column(db.String(120), unique=False, nullable=False)
    trzeci_param = db.Column(db.String(120), unique=False, nullable=True)


sess = Session()
sess.init_app(app)
accountant.manager.main()


@app.route("/set/")
def set():
    session["key"] = "value"
    return "ok"


@app.route("/get/")
def get():
    return session.get("key", "not set")


@app.route("/")
def set_form():
    db.session.commit()
    return render_template(
        "index.html",
        saldo_value=db.session.query(Saldo).all()[0].wartosc_salda,
        storehouse=db.session.query(Produkty).all(),
    )


@app.route("/buy", methods=["POST"])
def update_buy():
    product_id = request.form["product_id"]
    product_amount = int(request.form["product_amount"])
    unit_price = int(request.form["unit_price"])
    db_saldo = db.session.query(Saldo).first()
    db_product = db.session.query(Produkty).filter_by(nazwa=product_id).first()
    print(db_product)
    if db_saldo.wartosc_salda - (product_amount * unit_price) < 0:
        messages = json.dumps(
            {
                "main": "Nie wystarczająca ilość środków by zakupić {} w ilości {} w cenie za sztukę {}".format(
                    product_id, product_amount, unit_price
                )
            }
        )
        session["messages"] = messages
        return redirect(url_for("form_error", messages=messages))
    if db_product is None:
        db.session.add(
            Produkty(
                nazwa=product_id,
                stan_mag=product_amount,
            )
        )
    else:
        db_product.stan_mag += product_amount
        db.session.add(db_product)

    db_saldo.wartosc_salda -= product_amount * unit_price
    db.session.add(db_saldo)
    db.session.add(
        History(
            nazwa="zakup",
            pierwszy_param=product_id,
            drugi_param=unit_price,
            trzeci_param=product_amount,
        )
    )
    db.session.commit()
    return redirect(url_for("set_form"))


@app.route("/sale", methods=["POST"])
def update_sale():
    product_id = request.form["product_id"]
    product_amount = int(request.form["product_amount"])
    unit_price = int(request.form["unit_price"])
    db_saldo = db.session.query(Saldo).first()
    db_product = db.session.query(Produkty).filter_by(nazwa=product_id).first()
    if db_product is None:
        messages = json.dumps(
            {
                "main": 'Produkt "{}" nie istnieje na magazynie'.format(
                    product_id
                )
            }
        )
        session["messages"] = messages
        return redirect(url_for("form_error", messages=messages))
    elif db_product.stan_mag - product_amount < 0:
        messages = json.dumps(
            {
                "main": 'Nie wystarczająca ilość produktu "{}" na magazynie'.format(
                    product_id
                )
            }
        )
        session["messages"] = messages
        return redirect(url_for("form_error", messages=messages))
    if product_amount < 0:
        messages = json.dumps(
            {"main": 'Ilość produktu "{}" mniejsza niż 0'.format(product_id)}
        )
        session["messages"] = messages
        return redirect(url_for("form_error", messages=messages))
    db_product.stan_mag -= product_amount
    db_saldo.wartosc_salda += product_amount * unit_price
    db.session.add(db_product)
    db.session.add(db_saldo)
    db.session.add(
        History(
            nazwa="sprzedaż",
            pierwszy_param=product_id,
            drugi_param=unit_price,
            trzeci_param=product_amount,
        )
    )
    db.session.commit()
    return redirect(url_for("set_form"))


@app.route("/saldo", methods=["POST"])
def update_saldo():
    comment = request.form["comment"]
    db_saldo = db.session.query(Saldo).first()
    db_saldo.wartosc_salda += int(request.form["saldo_value"])
    db.session.add(db_saldo)
    db.session.add(
        History(
            nazwa="saldo",
            pierwszy_param=db_saldo.wartosc_salda,
            drugi_param=comment,
        )
    )
    db.session.commit()
    return redirect(url_for("set_form"))


@app.route("/error")
def form_error():
    messages = request.args["messages"]
    messages = session["messages"]
    return render_template("error.html", messages=json.loads(messages))


@app.route("/history")
def set_logs():
    db_history = db.session.query(History).all()
    return render_template("history.html", logs=db_history)


alembic = Alembic()
alembic.init_app(app)
