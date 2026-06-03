"""
profiles/views.py
=================
INTENTIONAL VULNERABILITIES:
  [V-13] Stored XSS    – bio field rendered with |safe, executes arbitrary JS
  [V-14] IDOR          – profile viewed/edited by ?user_id=N with no ownership check
  [V-15] Unrestricted avatar upload – any file extension accepted (PHP, HTML …)
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile


# ── [V-14] IDOR: view any user's profile by changing ?user_id= ───────────────
def profile_view(request, user_id=None):
    """
    If user_id is supplied in the URL, that profile is shown – even if the
    requesting user has no relationship to it.

    Try:  /profiles/view/?user_id=1  (admin's profile)
          /profiles/view/?user_id=2
    """
    if user_id is None:
        user_id = request.GET.get("user_id", None)

    if user_id:
        # ❌ VULNERABLE: no check that request.user.id == user_id
        profile = get_object_or_404(Profile, user__id=user_id)
    else:
        profile, _ = Profile.objects.get_or_create(user=request.user)

    return render(request, "profiles/view.html", {"profile": profile})


@login_required
def profile_edit(request):
    """
    Edit profile.  Also vulnerable to IDOR via POST: POST ?user_id=<victim>
    to overwrite another user's bio.
    """
    # ── [V-14] IDOR via POST param ────────────────────────────────────────────
    target_id = request.POST.get("user_id") or request.GET.get("user_id")
    if target_id:
        # ❌ VULNERABLE: attacker can edit any user's profile
        profile, _ = Profile.objects.get_or_create(user__id=target_id,
                                                    defaults={"user": request.user})
    else:
        profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # ── [V-13] Stored XSS: raw HTML stored in bio, rendered unescaped ─────
        profile.bio     = request.POST.get("bio", "")
        profile.website = request.POST.get("website", "")

        # ── [V-15] Unrestricted file upload ───────────────────────────────────
        # No extension, MIME-type, or size validation.
        # Uploading a .html or .php file here stores it under /media/avatars/.
        if "avatar" in request.FILES:
            profile.avatar = request.FILES["avatar"]

        profile.save()
        return redirect("/profiles/view/")

    return render(request, "profiles/edit.html", {"profile": profile})
