# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, session
from flask_login import login_required, login_user, logout_user

from areason.extensions import login_manager, csrf_protect
from areason.public.forms import LoginForm
from areason.user.forms import RegisterForm
from areason.public.forms import ContactForm
from areason.user.models import User
from areason.utils import flash_errors, send_html_email
from datetime import datetime

import stripe

stripe_keys = {
    'secret_key': 'sk_test_Xpu6wCBVWoj3Rrhg1tWvc9RV',
    'publishable_key': 'sk_test_Xpu6wCBVWoj3Rrhg1tWvc9RV'
}

stripe.api_key = stripe_keys['secret_key']

blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    """Home page."""
    year = datetime.utcnow().year

    return render_template('index.html', year=year)


@blueprint.route('/confirm', methods=['GET', 'POST'])
@blueprint.route('/confirm/<modify>', methods=['GET', 'POST'])
@csrf_protect.exempt
def confirm(modify=None):
    if modify:
        session['purchase'] = request.get_json()
        return jsonify({'result': 'success'}), 200
    return render_template('public/confirm.html', purchase=session.get('purchase', None))


@blueprint.route('/pay', methods=['GET', 'POST'])
def pay():
    amount = session.get('purchase', None).get('totals', None)['stripeTotal']
    print(amount)
    customer = stripe.Customer.create(
        email=request.form.get('stripeEmail', None),
        source=request.form.get('stripeToken', None),
        shipping={
            'address': {
                'line1': request.form.get('stripeShippingAddressLine1', None),
                'city': request.form.get('stripeShippingAddressCity', None),
                'postal_code': request.form.get('stripeShippingAddressZip', None),
                'state': request.form.get('stripeShippingAddressState', None),
            },
            'name': request.form.get('stripeShippingName', None)
        }
    )
    items = ''
    for item in session.get('purchase', None).get('cart', None):
        string = '{} ({}) Qty: {}, '.format(item['item'], item['option'], item['quantity'])
        items += string

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Coffee Purchase',
        metadata={
            'items': items,
            'shipping': session.get('purchase', None).get('totals', None)['shippingTotal'],
            'tax': session.get('purchase', None).get('totals', None)['taxTotal'],
        }
    )

    session['purchase']['customer'] = {
        'name': request.form.get('stripeShippingName', None),
        'email': request.form.get('stripeEmail', None),
        'address': '{} {}, {} {}'.format(request.form.get('stripeShippingAddressLine1', None),
                                         request.form.get('stripeShippingAddressCity', None),
                                         request.form.get('stripeShippingAddressState', None),
                                         request.form.get('stripeShippingAddressZip', None))
    }

    html = render_template('public/order_email.html', purchase=session.get('purchase', None))
    send_html_email('A Reason for Living <admin@areasonforliving.com>', 'New Coffee Order', ['aaron@areasonforliving.com', 'sales@imprintcoffeeroasting.com'], 'dan@danwins.com', html)

    result = 'Successfully paid! We will ship your order soon.'
    return render_template('public/finish.html', result=result)


@blueprint.route('/support')
def gimme5():
    """About page."""
    return render_template('public/gimme5.html')

@blueprint.route('/qr')
def qr():
    """About page."""
    return redirect('https://www.youtube.com/watch?v=SctSa3SvIBE')

@blueprint.route('/be-a-prayer-partner')
def prayer_partner():
    flash('Send me an email and ask to join our newsletter! We need your prayers!')
    return redirect(url_for('public.contact'))

@blueprint.route('/where-weve-been')
def where_weve_been():
    """About page."""
    return render_template('public/where_weve_been.html')

@blueprint.route('/what-we-do')
def what_we_do():
    """About page."""
    return render_template('public/what_we_do.html')

@blueprint.route('/about')
def about():
    """About page."""
    return render_template('public/about.html')

@blueprint.route('/success')
def success():
    """About page."""
    # html = """
    # <html>
    #     <p>Someone paid you money via your donation page.</p>
    # </html>
    # """
    # send_html_email('{} <{}>'.format('Admin', 'admin@areasonforliving.com'), 'You got a payment', 'aaron@areasonforliving.com', 'dan@danwins.com', html)
    return render_template('public/success.html')

@blueprint.route('/checkout-succeeded', methods=['GET', 'POST'])
def stripe_webhook():
    """About page."""
    print(request.data, request.form, request.args)
    html = """
    <html>
        <p>Data: {}</p>
        <p>Form: {}</p>
        <p>Someone paid you money via your donation page.</p>
    </html>
    """.format(request.data, request.form)
    send_html_email('{} <{}>'.format('Admin', 'admin@areasonforliving.com'), 'You got a payment', 'aaron@areasonforliving.com', 'dan@danwins.com', html)
    return render_template('public/success.html')

@blueprint.route('/canceled')
def canceled():
    """About page."""
    return render_template('public/cancel.html')


@blueprint.route('/evangelists')
def evangelists():
    """About page."""
    return render_template('public/evangelists.html')


@blueprint.route('/beliefs')
def beliefs():
    """About page."""
    return render_template('public/beliefs.html')


@blueprint.route('/resources')
def resources():
    """About page."""
    return render_template('public/resources.html')


@blueprint.route('/coffee')
def coffee():
    """About page."""
    return render_template('public/coffee.html')


@blueprint.route('/contact', methods=['GET', 'POST'])
def contact():
    """About page."""
    form = ContactForm()
    if form.validate_on_submit():
        message = form.message.data
        name = form.name.data
        email = form.email.data
        html = render_template('public/contact_email.html', message=message, name=name)
        send_html_email('{} <{}>'.format(name, email), 'Website Contact Form', 'aaron@areasonforliving.com', 'dan@danwins.com', html)
    return render_template('public/contact.html', form=form)


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """Register new user."""
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        User.create(username=form.username.data, email=form.email.data, password=form.password.data, active=True)
        flash('Thank you for registering. You can now log in.', 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)
