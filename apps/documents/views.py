from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import DocumentForm
from .models import Document
from apps.ai_engine.services.ai_service import generate_summary
import PyPDF2
import markdown
from django.contrib import messages

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user

            # Extract PDF text
            file = request.FILES['file']
            if not file.name.endswith('.pdf'):
                messages.error(request, "Only PDF files are allowed.")
                return redirect('upload_document')
            try:
                reader = PyPDF2.PdfReader(file)
                text = ""

                for page in reader.pages:
                    text += page.extract_text() or ""

            except Exception as e:
                messages.error(request, "Invalid or unsupported PDF file.")
                return redirect('upload_document')

            doc.extracted_text = text
            summary = generate_summary(text[:10000])  # limit text size
            summary = summary.replace("• -", "-").replace("•", "")
            summary = markdown.markdown(
                summary,
                extensions=['extra', 'nl2br']
            )
            doc.ai_summary = summary
            doc.save()

            messages.success(request, "Document uploaded successfully!")
            return redirect('document_list')
    else:
        form = DocumentForm()

    return render(request, 'documents/upload.html', {'form': form})


@login_required
def document_list(request):
    documents = Document.objects.all()
    return render(request, 'documents/list.html', {'documents': documents})

def view_summary(request, doc_id):
    doc = Document.objects.get(id=doc_id)
    return render(request, 'documents/summary.html', {'doc': doc})

@login_required
def delete_document(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    doc.delete()
    return redirect('document_list')