from flask import render_template, redirect, url_for, session, request, flash, current_app
from sqlalchemy.exc import IntegrityError

from ..models import *

from flask_login import login_required, current_user, logout_user, login_manager, LoginManager
from . import admin
from ..forms import BusinessForm, addmore, removefromcart, UpdateForm, ProductForm, \
    updatestatusform, update
from ..models import db
import secrets
from fileinput import filename
import os
from PIL import Image


def save_product_picture(file):
    size = (300, 300)
    images = []

    random_hex = secrets.token_hex(9)
    _, f_ex = os.path.splitext(file.filename)
    post_img_fn = random_hex + f_ex
    post_image_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_PRODUCTS'], post_img_fn)

    # Open the image
    img = Image.open(file)

    # Resize the image
    img.thumbnail(size)
    # Save the resized image
    img.save(post_image_path)
    return post_img_fn


def save_post_picture(form_picture):
    size = (300, 300)
    random_hex = secrets.token_hex(9)
    _, f_ex = os.path.splitext(form_picture.filename)
    post_img_fn = random_hex + f_ex

    post_image_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_POSTS'], post_img_fn)

    # Open the image
    img = Image.open(form_picture)

    # Resize the image
    img.thumbnail(size)

    # Save the resized image
    img.save(post_image_path)

    return post_img_fn


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@admin.route('/adminpage', methods=["POST", "GET"])
@login_required
def adminpage():
    username = current_user.username
    return render_template('admin/adminpage.html', username = username)

@admin.route('/reports', methods=["POST", "GET"])
@login_required
def reports():
    sales = Sales.query.all()
    return render_template('admin/reports.html', sales=sales)

@admin.route('/updateproduct/<int:item_id>', methods=['GET', 'POST'])
@login_required
def updateproduct(item_id):
    if not current_user.isadmin:
        return redirect(url_for('home'))
    form = update()
    if form.validate_on_submit():

        product = Product.query.filter_by(id=item_id).first()
        if product:
            product.productname = form.newname.data
            product.description = form.newdescription.data
            product.category = form.category.data
            product.price = form.newprice.data

        try:
            db.session.commit()
            return redirect(url_for('admin.products'))
        except IntegrityError:
            db.session.rollback()
            flash('Eish')
            return redirect(url_for('admin.products'))
    return render_template('admin/updateproduct.html', form=form, item_id=item_id)



@admin.route('/orders')
@login_required
def orders():
    form = updatestatusform()
    orders = Order.query.all()
    return render_template("admin/orders.html", form=form, orders=orders)


@admin.route('/orders/updatestatus/<int:order_id>', methods=['POST'])
@login_required
def updatestatus(order_id):
    form = updatestatusform()
    if form.validate_on_submit():
        newstatus = form.status.data
    orders = Order.query.get_or_404(order_id)
    orders.status = newstatus
    print('done updating')
    db.session.add(orders)
    db.session.commit()
    return redirect(url_for('admin.orders'))


@admin.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('admin.login'))



@admin.route('/addproducts', methods=["POST", "GET"])
@login_required
def addproducts():
    if not current_user.isadmin:
        return redirect(url_for('main.home'))

    form = ProductForm()
    if request.method == 'POST':
        if form.is_submitted():
            if form.validate_on_submit:
                product = Product(productname=form.product_name.data, price=form.product_price.data, quantity=form.product_quantity.data,
                                  description=form.product_description.data, usage=form.product_usage.data)
                file = form.product_pictures.data

                _image = save_product_picture(file)
                product.pictures = _image
                db.session.add(product)
                db.session.commit()
                print('picture saved')

                return redirect(url_for("admin.products"))
        else:
            flash("An error occured")
    return render_template("admin/addproducts.html", form=form)


@admin.route('/userorders/<int:order_id>', methods=['post', 'get'])
@login_required
def vieworders(order_id):
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    user_order = Order.query.filter_by(id=order_id).first()
    total = 0.00
    discount = 0.00
    gross_total = 0.00
    if user_order:

        gross_total = sum(item.product.price * item.quantity for item in user_order.order_items)
        if gross_total >=160:
            discount = round(0.15 * gross_total, 2)
            total -= discount
        else:
            total=gross_total
    else:
        flash('Order does no longer exist')
        db.session.delete(user_order)
        db.session.commit()
        return redirect(url_for('admin.orders'))
    return render_template('admin/vieworders.html', user_order=user_order, total=total)


@admin.route('/products')
@login_required
def products():
    if not current_user.isadmin:
        return redirect(url_for('main.home'))
    form2 = removefromcart()
    form3 = addmore()
    form = update()
    product = Product.query.all()
    status = ""
    for pro in product:
        if pro.quantity<5:
            status = " critical needs restock"
        elif pro.quantity == 0:
            status = "Out of stock"
        else:
            status = "In Stock_"
    return render_template('admin/products.html', product=product, status=status, form=form, form2=form2, form3=form3)


@admin.route('/accounts')
@login_required
def accounts():
    user1 = current_user.id
    user2 = User.query.filter_by(id=user1).first()
    if not user2.isadmin:
        flash('You do not have you are not priviledge to visit this site.')
        return redirect(url_for('main.home'))

    picture = 'sdsd.jpg'
    users = User.query.filter_by(isadmin=False).all()
    for user in users:
        if user.image_file is not None:
            picture = url_for('static', filename=('css/images/posts/' + user.image_file))
    return render_template('admin/accounts.html', users=users, picture=picture)

    
@admin.route('/remove_from_products/<int:item_id>', methods=['POST', 'GET'])
@login_required
def remove_from_products(item_id):
    product = Product.query.filter_by(id=item_id).first()
    if product:
        product.quantity -= 1
        db.session.add(product)
        if product.quantity <= 0:
            db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin.products'))


@admin.route('/add_products/<int:item_id>', methods=['POST', 'GET'])
@login_required
def add_products(item_id):
    product = Product.query.filter_by(id=item_id).first()
    if product:
        product.quantity += 1
        if product.quantity <= 0:
            db.session.delete(product)

    db.session.commit()
    return redirect(url_for('admin.products'))

