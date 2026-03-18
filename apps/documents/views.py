from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DocumentForm
from .models import Document
import PyPDF2
from apps.ai_engine.services.ai_service import generate_summary


@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user

            # Extract PDF text
            file = request.FILES['file']
            reader = PyPDF2.PdfReader(file)
            text = ""

            for page in reader.pages:
                text += page.extract_text() or ""

            doc.extracted_text = text
            summary = generate_summary(text[:3000])  # limit text size
            doc.ai_summary = summary
            doc.save()

            return redirect('document_list')
    else:
        form = DocumentForm()

    return render(request, 'documents/upload.html', {'form': form})


@login_required
def document_list(request):
    documents = Document.objects.all()
    return render(request, 'documents/list.html', {'documents': documents})