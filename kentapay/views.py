import logging
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.urls import reverse
from oscar.apps.payment.exceptions import PaymentError

from .processor import Kentapay  # Your processor class

logger = logging.getLogger(__name__)

class CallbackView(View):
    """
    Handle successful or failed payment callback/redirect from Kentapay.
    This is typically a GET request with query params.
    """
    def get(self, request, *args, **kwargs):
        # Retrieve the basket/order from session or query params
        # In real implementations, you might use request.GET.get('order_number') or basket ID
        # For simplicity, assume basket is attached via middleware/session
        basket = getattr(request, 'basket', None)  # This requires basket middleware

        if not basket:
            logger.error("No basket found in callback request")
            return HttpResponse("Invalid request - no basket found", status=400)

        processor = Kentapay(request.site)  # Or however you instantiate it

        try:
            # Pass request.GET (query params from Kentapay)
            handled_response = processor.handle_processor_response(request.GET, basket=basket)

            # On success: redirect to receipt/thank-you page
            # Adjust URL as needed (e.g., receipt view in ecommerce)
            return HttpResponseRedirect(reverse('checkout:thank-you') or '/checkout/receipt/')

        except PaymentError as e:
            logger.error(f"Kentapay callback failed: {str(e)}")
            # Redirect back to checkout with error message
            # You can add query param ?payment_error=1 or use messages framework
            return HttpResponseRedirect(reverse('basket:summary') or '/basket/')

        except Exception as e:
            logger.exception("Unexpected error in Kentapay callback")
            return HttpResponse("Payment processing error", status=500)


class CancelView(View):
    """
    Handle user cancellation (redirect back from Kentapay cancel URL).
    """
    def get(self, request, *args, **kwargs):
        # Optional: add flash message "Payment cancelled"
        return HttpResponseRedirect(reverse('basket:summary') or '/basket/')
