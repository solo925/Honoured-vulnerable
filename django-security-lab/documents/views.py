"""
documents/views.py
==================
INTENTIONAL VULNERABILITIES:
  [V-20] Unrestricted file upload – no MIME / extension check; .html, .exe accepted
  [V-21] Path traversal in download – filename taken from DB without sanitisation,
          allowing ../../../etc/passwd style reads when combined with os.path.join
  [V-22] IDOR on download – any authenticated user can download any document by ID
  [V-23] Insecure direct file read – open() called with user-controlled path
"""

import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Document


@login_required
def upload_document(request):
    """
    Upload any file without restriction.

    [V-20] Try uploading:
      - a .html file containing <script>alert(1)</script>
        → browse to /media/documents/<name>.html to trigger XSS
      - a .exe, .php, or .py file to test extension blocking (there is none)
    """
    error = None
    if request.method == "POST":
        title = request.POST.get("title", "untitled")
        f     = request.FILES.get("file")
        if f:
            doc = Document(
                owner=request.user,
                title=title,
                # ❌ VULNERABLE: original filename stored, used later in download
                original_filename=f.name,
            )
            doc.file = f      # no validation
            doc.save()
            return redirect("/documents/list/")
        error = "No file selected."

    return render(request, "documents/upload.html", {"error": error})


@login_required
def list_documents(request):
    # Shows only the current user's documents – but download has no such guard
    docs = Document.objects.filter(owner=request.user)
    return render(request, "documents/list.html", {"documents": docs})


# ── [V-22] IDOR + [V-21] Path traversal ─────────────────────────────────────
@login_required
def download_document(request, doc_id):
    """
    [V-22] Any logged-in user can download any document by changing doc_id.
           There is no ownership check.

    [V-21] Path traversal: the 'file' GET parameter (if supplied) is joined
           directly to MEDIA_ROOT with os.path.join, allowing:
               /documents/download/1/?file=../../db.sqlite3
               /documents/download/1/?file=../../config/settings.py
               /documents/download/1/?file=../../../etc/passwd
    """
    doc = get_object_or_404(Document, pk=doc_id)

    # ── [V-22] No ownership check ─────────────────────────────────────────────
    # Secure version would be: get_object_or_404(Document, pk=doc_id, owner=request.user)

    # ── [V-21] Path traversal ─────────────────────────────────────────────────
    override_path = request.GET.get("file")
    if override_path:
        # ❌ VULNERABLE: user controls the path
        file_path = os.path.join(settings.MEDIA_ROOT, override_path)
    else:
        file_path = doc.file.path

    try:
        with open(file_path, "rb") as fh:
            data = fh.read()
    except FileNotFoundError:
        raise Http404("File not found.")
    except PermissionError:
        raise Http404("Permission denied.")

    response = HttpResponse(data, content_type="application/octet-stream")
    # ❌ VULNERABLE: original_filename not sanitised (header injection possible)
    response["Content-Disposition"] = (
        f'attachment; filename="{doc.original_filename}"'
    )
    return response


@login_required
def delete_document(request, doc_id):
    """[V-22] IDOR: any user can delete any document."""
    doc = get_object_or_404(Document, pk=doc_id)
    # ❌ No ownership check
    doc.delete()
    return redirect("/documents/list/")
