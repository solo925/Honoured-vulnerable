"""
accounts/views.py
=================
INTENTIONAL VULNERABILITIES:
  [V-08] SQL Injection in login  – username is interpolated directly into raw SQL
  [V-09] Username enumeration    – different error messages for "no user" vs "wrong password"
  [V-10] Insecure password reset – token is just the username, trivially guessable
  [V-11] No rate-limiting        – unlimited login attempts (brute-force friendly)
  [V-12] Verbose registration error exposes whether a username already exists
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.db import connection


# ── [V-08] SQL Injection ──────────────────────────────────────────────────────
def login_view(request):
    """
    Classic SQL-injection login.

    Payload to bypass authentication (log in as any user without a password):
        Username:  admin'--
        Password:  anything

    Payload to dump all usernames (error-based, SQLite):
        Username:  ' OR 1=1--
    """
    error = None

    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        # ❌ VULNERABLE: f-string interpolation directly into SQL
        query = f"""
            SELECT id, username, password
            FROM accounts_user
            WHERE username = '{username}'
            AND   password = '{password}'
        """

        with connection.cursor() as cursor:
            try:
                cursor.execute(query)          # raw SQL, no parameterisation
                row = cursor.fetchone()
            except Exception as exc:
                # [V-01] DEBUG=True will render the full traceback in the browser
                raise exc

        if row:
            # Manually load and authenticate the Django user object
            from accounts.models import User
            try:
                user = User.objects.get(pk=row[0])
                user.backend = "django.contrib.auth.backends.ModelBackend"
                login(request, user)
                return redirect("/dashboard/")
            except User.DoesNotExist:
                pass

        # ── [V-09] Enumeration: message differs depending on failure mode ─────
        with connection.cursor() as c:
            c.execute(
                "SELECT 1 FROM accounts_user WHERE username = ?", [username]
            )
            if c.fetchone():
                error = "Incorrect password."          # user exists
            else:
                error = "No account with that username."  # user does not exist

    return render(request, "accounts/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("/accounts/login/")


# ── [V-10] Insecure password reset ───────────────────────────────────────────
def password_reset_view(request):
    """
    The 'reset token' is simply the username encoded in base64 – trivially
    reversible.  An attacker can generate a valid token for any known username
    and reset that account's password.
    """
    message = None

    if request.method == "POST":
        import base64
        username = request.POST.get("username", "")

        from accounts.models import User
        try:
            user = User.objects.get(username=username)
            # ❌ VULNERABLE: token = base64(username), not a cryptographic token
            token = base64.b64encode(username.encode()).decode()
            # In a real app this would be e-mailed.  Here we just display it.
            message = f"Your reset link: /accounts/reset/{token}/"
        except User.DoesNotExist:
            # ── [V-09] also present here: confirms whether username exists ────
            message = "No user found with that username."

    return render(request, "accounts/password_reset.html", {"message": message})


def password_reset_confirm_view(request, token):
    """
    Accepts the weak token, decodes the username, and sets whatever password
    the user submits – no complexity requirements (V-04).
    """
    import base64
    try:
        username = base64.b64decode(token.encode()).decode()
    except Exception:
        return render(request, "accounts/password_reset_confirm.html",
                      {"error": "Invalid token."})

    message = None
    if request.method == "POST":
        new_password = request.POST.get("password", "")
        from accounts.models import User
        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            message = "Password updated. You can now log in."
        except User.DoesNotExist:
            message = "User not found."

    return render(request, "accounts/password_reset_confirm.html",
                  {"message": message, "username": username})


# ── [V-12] Registration exposes username uniqueness ──────────────────────────
def register_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        from accounts.models import User
        if User.objects.filter(username=username).exists():
            error = f"The username '{username}' is already taken."  # enumeration
        else:
            # No password strength check (V-04)
            user = User.objects.create_user(username=username, password=password)
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, user)
            return redirect("/dashboard/")

    return render(request, "accounts/register.html", {"error": error})
