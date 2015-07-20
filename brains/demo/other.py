import logging
import os
import sys
import uuid

import braintree
import flask
app = flask.Flask(__name__)

from requests.packages import urllib3
urllib3.disable_warnings()

braintree.Configuration.configure(
    braintree.Environment.Sandbox,
    'tbb7hb44zx28jhsh',
    os.environ.get('BRAINTREE_PUBLIC_KEY_MOFO'),
    os.environ.get('BRAINTREE_PRIVATE_KEY_MOFO'),
)

print 'Using public key:', os.environ.get('BRAINTREE_PUBLIC_KEY_MOFO')

def demo(customer):
    customer = braintree.Customer.find(customer)
    print '[customer] found:', customer.id

    card = customer.credit_cards[0]
    print '[paymethod] id:', card.token, card.card_type
    payment = braintree.PaymentMethod.find(card.token)


    print '[purchase] attempting transaction for $10'
    result = braintree.Transaction.sale({
        "amount": "10.00",
        "payment_method_token": payment.token,
        "options": {
            "submit_for_settlement": True
        }
    })

    assert result.is_success, result
    print '[purchase] transaction created:', result.transaction.id


if __name__=='__main__':
    demo(sys.argv[1])
