import logging
import os
import uuid

import braintree
import flask
app = flask.Flask(__name__)

braintree.Configuration.configure(
    braintree.Environment.Sandbox,
    'tbb7hb44zx28jhsh',
    os.environ.get('BRAINTREE_PUBLIC_KEY'),
    os.environ.get('BRAINTREE_PRIVATE_KEY'),
)

print 'Using public key:', os.environ.get('BRAINTREE_PUBLIC_KEY')
logging.captureWarnings(True)
log = logging.getLogger(__name__)


@app.route('/', methods=['GET'])
def form():
    return flask.render_template('cc.html')


@app.route('/token', methods=['GET'])
def token():
    client_token = braintree.ClientToken.generate({})
    print '[token] created:', client_token[:20], '...'
    return flask.jsonify(token=client_token)


@app.route('/purchase', methods=['POST'])
def purchase():
    nonce = flask.request.form['payment_method_nonce']

    result = braintree.Customer.create({
        'first_name': 'Charity',
        'last_name': 'Smith'
    })

    assert result.is_success, result
    print '[purchase] customer created:', result.customer.id

    result = braintree.PaymentMethod.create({
        'customer_id': result.customer.id,
        'payment_method_nonce': nonce
    })

    assert result.is_success, result
    mapping = {
        braintree.paypal_account.PayPalAccount: 'paypal',
        braintree.credit_card.CreditCard: 'credit'
    }
    try:
        payment_type = mapping[result.payment_method.__class__]
    except KeyError:
        raise ValueError('The payment account did not match a known type: {}'
                         .format(result.payment_method))

    print '[purchase] payment method type:', payment_type
    print '[purchase] payment method token:', result.payment_method.token

    result = braintree.Subscription.create({
        'payment_method_token': result.payment_method.token,
        'plan_id': 'past-due',
        'trial_period': False,
        'merchant_account_id': 'v2dbvygzr9zcrqmg',
        'id': str(uuid.uuid4()),
    })

    assert result.is_success, result
    print '[purchase] subscription created:', result.subscription.id
    return flask.render_template('done.html', success=result.is_success)


@app.route('/notification', methods=['GET'])
def notification_check():
    return braintree.WebhookNotification.verify(flask.request.args['bt_challenge'])


@app.route('/notification', methods=['POST'])
def notification_respond():
    webhook = braintree.WebhookNotification.parse(
        str(flask.request.form['bt_signature']),
        flask.request.form['bt_payload'])
    print '[notfication] kind: {0} for subscription: {1}'.format(
        webhook.kind, webhook.subscription.id)
    return flask.Response(status=200)

if __name__ == '__main__':
    app.run(debug=True)
