class OTPRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not request.session.get('otp_verified', False):
                # allow these pages WITHOUT OTP
                allowed = [
                    '/login/',
                    '/register/',
                    '/dashboard/',
                    '/verify-otp/',
                    '/logout/',
                ]
                if request.path not in allowed:
                    return redirect('dashboard')

        return self.get_response(request)
