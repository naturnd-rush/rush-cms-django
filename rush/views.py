from django.contrib import messages
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render


def rush_login_view(request):
    """
    GET --> Render the RUSH Admin login page.
    POST --> Submit login form data and redirect to admin homepage.
    """

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/admin/")
        else:
            messages.error(request, "Invalid username or password")

    form = AdminAuthenticationForm(request)
    return render(
        request=request,
        template_name="admin/rush_login_page.html",
        context={
            "form": form,
            "site_header": "RUSH Admin",
        },
    )
