from flask import Blueprint, render_template, url_for, request, session, flash, redirect,Request
from .models import City, Tour, Order
from datetime import datetime
from .forms import CheckoutForm
from . import db

main_bp = Blueprint('main', __name__)

# Home page
@main_bp.route('/')
def index():
    cities = db.session.scalars(db.select(City).order_by(City.id)).all()
    return render_template('index.html', cities=cities)

# View all the tours of a city
@main_bp.route('/tours/<int:city_id>')
def citytours(city_id):
    tours = db.session.scalars(db.select(Tour).where(Tour.city_id==city_id)).all()
    return render_template('citytours.html', tours=tours)


# Referred to as "Basket" to the user
@main_bp.route('/order', methods=['POST', 'GET'])
def order():
    tour_id = request.values.get('tour_id')
    print(f'Values: {tour_id}')
    # retrieve order if there is one
    if 'order_id' in session.keys():
        order = db.session.scalar(db.select(Order).where(Order.id==session['order_id']))
        # order will be None if order_id/session is stale
    else:
        # there is no order
        order = None

    # create new order if needed
    if order is None:
        order = Order(status=False, firstname='', surname='', email='', phone='', totalcost=0, date=datetime.now())
        try:
            db.session.add(order)
            db.session.commit()
            session['order_id'] = order.id
        except:
            print('Failed at creating a new order!')
            order = None
    
    # calculate total price
    total_price = 0
    if order is not None:
        for tour in order.tours:
            total_price += tour.price
    
    # are we adding an item?
    if tour_id is not None and order is not None:
        tour = db.session.scalar(db.select(Tour).where(Tour.id==tour_id))
        if tour not in order.tours:
            try:
                order.tours.append(tour)
                db.session.commit()
            except:
                return 'There was an issue adding the item to your basket'
            return redirect(url_for('main.order'))
        else:
            flash('There is already one of these in the basket')
            return redirect(url_for('main.order'))
    return render_template('order.html', order=order, total_price=total_price)

# Delete specific basket items
# Note this route cannot accept GET requests now
@main_bp.route('/deleteorderitem', methods=['POST'])
def deleteorderitem():
    id = request.form['id']
    if 'order_id' in session:
        order = db.get_or_404(Order, session['order_id'])
        tour_to_delete = db.session.scalar(db.select(Tour).where(Tour.id==id))
        try:
            order.tours.remove(tour_to_delete)
            db.session.commit()
            return redirect(url_for('main.order'))
        except:
            return 'Problem deleting item from order'
    return redirect(url_for('main.order'))

# Scrap basket
@main_bp.route('/deleteorder')
def deleteorder():
    if 'order_id' in session:
        del session['order_id']
        flash('All items deleted')
    return redirect(url_for('main.index'))

# Complete the order
@main_bp.route('/checkout', methods=['POST','GET'])
def checkout():
    form = CheckoutForm() 
    if 'order_id' in session:
        order = db.get_or_404(Order, session['order_id'])
        if form.validate_on_submit():
            order.status = True
            order.firstname = form.firstname.data
            order.surname = form.surname.data
            order.email = form.email.data
            order.phone = form.phone.data
            total_cost = 0
            for tour in order.tours:
                total_cost += tour.price
            order.totalcost = total_cost
            order.date = datetime.now()
            try:
                db.session.commit()
                del session['order_id']
                flash('Thank you! One of our team members will contact you soon...')
                return redirect(url_for('main.index'))
            except:
                return 'There was an issue completing your order'
    return render_template('checkout.html', form=form)














@main_bp.route('/Aboutus')
def Aboutus():
    # product page logic here
    return render_template('About-us.html')




@main_bp.route('/citytours_copy/<int:tour_id>')
def citytours_copy(tour_id):
    # Fetch the specific tour based on tour_id
    tour = db.session.query(Tour).filter(Tour.id == tour_id).first()

    if tour is not None:
        # If the tour is found, pass it to the template
        return render_template('test.html', tour=tour)
    else:
        # Handle the case where the tour is not found, for example, show an error message.
        return "Tour not found"
    
    
@main_bp.route('/Offers/<int:tour_id>')
def Offers(tour_id):
    # Fetch the specific tour based on tour_id
    tour = db.session.query(Tour).filter(Tour.id == tour_id).first()

    if tour is not None:
        # If the tour is found, pass it to the template
        return render_template('Offers.html', tour=tour)
    else:
        # Handle the case where the tour is not found, for example, show an error message.
        return "Tour not found"
    