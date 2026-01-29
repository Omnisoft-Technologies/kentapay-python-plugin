import logging
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.urls import reverse
from oscar.apps.payment.exceptions import PaymentError

from .processor import Kentapay

logger = logging.getLogger(__name__)

class CallbackView(View):
    def get(self, request, *args, **kwargs):
        basket = getattr(request, 'basket', None)  # Assumes basket middleware

        if not basket:
            logger.error("No basket in callback request")
            return HttpResponse("Invalid request - no basket", status=400)

        processor = Kentapay(request.site)

        try:
            handled_response = processor.handle_processor_response(request.GET, basket=basket)
            # Success → receipt page
            return HttpResponseRedirect(reverse('checkout:thank-you') or '/checkout/receipt/')
        except PaymentError as e:
            logger.error(f"Kentapay callback error: {e}")
            return HttpResponseRedirect(reverse('basket:summary') or '/basket/')
        except Exception as e:
            logger.exception("Unexpected Kentapay callback error")
            return HttpResponse("Payment error", status=500)


class CancelView(View):
    def get(self, request, *args, **kwargs):
        # User cancelled → back to basket
        return HttpResponseRedirect(reverse('basket:summary') or '/basket/')
