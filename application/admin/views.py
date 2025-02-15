from flask import render_template, redirect, url_for, request, flash, current_app
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, extract
from ..models import User, Product, Sales, Order, Cart
from datetime import datetime,timedelta
from flask_login import login_required, current_user, logout_user,  LoginManager
from . import admin
from ..forms import addmore, removefromcart, UpdateForm, ProductForm, \
    updatestatusform, update
from ..models import db
import os
import secrets
from PIL import Image
from flask import current_app


def save_product_picture(file):
    # Set the desired size for resizing
    size = (300, 300)

    # Generate a random hex string for the filename
    random_hex = secrets.token_hex(9)

    # Get the file extension
    _, f_ex = os.path.splitext(file.filename)

    # Generate the final filename (random + extension)
    post_img_fn = random_hex + f_ex

    # Define the path to save the file (UPLOAD_PRODUCTS should be configured in your Flask app)
    post_image_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_PRODUCTS'], post_img_fn)

    try:
        # Open the image
        img = Image.open(file)

        # Resize the image to fit within the size (thumbnail)
        img.thumbnail(size)

        # Save the resized image
        img.save(post_image_path)

        return post_img_fn  # Return the filename to store in the database
    except Exception as e:
        # If an error occurs during image processing, handle it
        print(f"Error saving image: {e}")
        return None

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.newlogin'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@admin.route('/adminpage', methods=["POST", "GET"])
@login_required
def adminpage():
    # Get today's date
    today = datetime.utcnow()
    current_month = today.month
    current_year = today.year
    # Calculate the start of the current month (first day of the month)
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Calculate the end of the current month (last day of the month)
    next_month = today.replace(day=28) + timedelta(days=4)  # this gets us to the next month
    end_of_month = next_month.replace(day=1) - timedelta(days=1)  # last day of the current month

    # Query to calculate total sales in the current month
    total_sales = db.session.query(func.sum(Sales.price * Sales.quantity)) \
        .filter(Sales.date_ >= start_of_month, Sales.date_ <= end_of_month) \
        .scalar()

    # If no sales are found, return 0
    total_sales = total_sales if total_sales else 0.0
    pending_orders = len(Order.query.filter_by(status = 'Pending').all())
    if not pending_orders:
        pending_orders = 0
    order_count = len(Order.query.filter(
        extract('month', Order.create_at) == current_month,
        extract('year', Order.create_at) == current_year,
        (Order.status == 'Completed' or Order.status == "Delivered")).all())  # Filter by status
    username = current_user.username
    user_count = len(User.query.filter_by(isadmin=False).all())
    return render_template('admin/adminpage.html', username = username, total_sales=total_sales,
                           current_year=today.year, current_month=today.strftime('%B'), order_count=order_count,
                           user_count=user_count, pending_orders=pending_orders)

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

            return redirect(url_for('admin.products'))
    return render_template('admin/updateproduct.html', form=form, item_id=item_id)

@admin.route('/orders')
@login_required
def orders():
    form = updatestatusform()
    orders = Order.query.filter_by(status="Pending").all()
    approved_order = Order.query.filter_by(status="Approved for processing").all()

    #total = sum(item.product.price * item.quantity for item in orders.order_items)
    return render_template("admin/orders.html", form=form, orders=orders, approved_order=approved_order)

@admin.route('/delivered')
@login_required
def delivered_orders():
    form = updatestatusform()
    orders = Order.query.filter_by(status="Delivered").all()
    #total = sum(item.product.price * item.quantity for item in orders.order_items)
    return render_template("admin/delivered.html", form=form, orders=orders)

@admin.route('/cancelled')
@login_required
def cancelled_orders():
    form = updatestatusform()
    orders = Order.query.filter_by(status="Cancelled").all()
    #total = sum(item.product.price * item.quantity for item in orders.order_items)
    return render_template("admin/cancelled.html", form=form, orders=orders)


@admin.route('/orders/updatestatus/<int:order_id>', methods=['POST'])
@login_required
def updatestatus(order_id):
    global newstatus
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
    return redirect(url_for('auth.newlogin'))



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
            flash("An error occurred")
    return render_template("admin/addproducts.html", form=form)


@admin.route('/userorders/<int:order_id>', methods=['post', 'get'])
@login_required
def vieworders(order_id):
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    user_order = Order.query.filter_by(id=order_id).first()
    total = 0.00
    if user_order:

        gross_total = sum(item.product.price * item.quantity for item in user_order.order_items)

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
    # Query non-admin users with pagination
    non_admin_users = User.query.filter_by(isadmin=False).all()
    return render_template('admin/accounts.html', non_admin_users=non_admin_users)

    
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

