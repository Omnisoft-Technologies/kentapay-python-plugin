from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from oscar.apps.payment.exceptions import PaymentError
from ecommerce.extensions.payment.views import BasePaymentCallbackView  # Import if needed for extension

from .processor import Kentapay

class CallbackView(BasePaymentCallbackView):  # Extend if possible for full integration
    def get(self, request):
        processor = Kentapay(request.site)
        basket = request.basket  # Assume basket is in session or query param
        try:
            handled_response = processor.handle_processor_response(request.GET, basket=basket)
            # Redirect to receipt page on success
            return HttpResponseRedirect('/checkout/receipt/')
        except PaymentError as e:
            logger.error(str(e))
            return HttpResponse('Payment Error', status=400)

class CancelView(View):
    def get(self, request):
        # Handle cancellation, redirect back to checkout
        return HttpResponseRedirect('/checkout/')
