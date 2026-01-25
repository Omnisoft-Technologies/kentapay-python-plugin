import logging
import requests
from decimal import Decimal

from django.urls import reverse
from ecommerce.extensions.payment.processors import BasePaymentProcessor, HandledProcessorResponse
from ecommerce.extensions.payment.exceptions import ProcessorResponseError

logger = logging.getLogger(__name__)

class Kentapay(BasePaymentProcessor):
    NAME = 'kentapay'
    TITLE = 'Kentapay'

    def get_transaction_parameters(self, basket, request=None, use_client_side_checkout=False, **kwargs):
        """Generate parameters for redirect to Kentapay payment page."""
        order_number = basket.order_number if basket.order_number else 'TEMP-' + str(basket.id)
        params = {
            'amount': str(basket.total_incl_tax),
            'currency': basket.currency,
            'order_id': order_number,
            'callback_url': request.build_absolute_uri(reverse('kentapay:callback')),
            'cancel_url': request.build_absolute_uri(reverse('kentapay:cancel')),
            # Add any Kentapay-specific params like merchant_id from self.configuration
            'merchant_id': self.configuration.get('merchant_id', ''),
        }

        # Placeholder: Post to Kentapay to get a session/token (replace with real API)
        response = requests.post('https://api.kentapay.com/initiate', data=params)
        if response.status_code != 200:
            raise ProcessorResponseError('Failed to initiate Kentapay transaction')

        data = response.json()
        payment_page_url = data.get('payment_url', 'https://kentapay.com/pay')  # Fallback

        return {'payment_page_url': payment_page_url}

    def handle_processor_response(self, response, basket=None):
        """Handle callback from Kentapay."""
        transaction_id = response.get('txid')
        status = response.get('status')
        amount = Decimal(response.get('amount', '0'))

        if status != 'success' or amount != basket.total_incl_tax:
            logger.error(f'Kentapay payment failed for basket {basket.id}: {response}')
            raise ProcessorResponseError('Payment verification failed')

        # Placeholder: Verify signature or call Kentapay API to confirm (replace with real verification)
        verify_response = requests.get(f'https://api.kentapay.com/verify/{transaction_id}')
        if verify_response.json().get('verified') != True:
            raise ProcessorResponseError('Transaction not verified')

        self.record_processor_response(response, transaction_id=transaction_id, basket=basket)
        return HandledProcessorResponse(
            transaction_id=transaction_id,
            total=basket.total_incl_tax,
            currency=basket.currency,
            card_number='XXXX',  # Masked
            card_type='Kentapay',
        )

    def issue_credit(self, order_number, basket, reference_number, amount, currency):
        """Issue a refund via Kentapay."""
        params = {
            'reference_number': reference_number,
            'amount': str(amount),
            'currency': currency,
            # Add credentials from self.configuration
        }

        # Placeholder: Call Kentapay refund API (replace with real endpoint)
        response = requests.post('https://api.kentapay.com/refund', data=params)
        if response.status_code != 200:
            raise ProcessorResponseError('Refund failed')

        data = response.json()
        return data.get('refund_id')
