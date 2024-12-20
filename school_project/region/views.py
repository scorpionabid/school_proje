from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Region, RegionDocument, RegionNews

@login_required
def region_list(request):
    """
    Regionların siyahısı
    """
    regions = Region.objects.filter(is_active=True)
    
    # Pagination
    paginator = Paginator(regions, 10)
    page = request.GET.get('page')
    regions = paginator.get_page(page)
    
    context = {
        'regions': regions,
        'total_regions': Region.objects.count(),
        'active_regions': Region.objects.filter(is_active=True).count(),
    }
    return render(request, 'region/region_list.html', context)

@login_required
def region_detail(request, pk):
    """
    Region detalları
    """
    region = get_object_or_404(Region, pk=pk)
    context = {
        'region': region,
        'recent_documents': region.documents.all()[:5],
        'recent_news': region.news.filter(is_active=True)[:5],
    }
    return render(request, 'region/region_detail.html', context)

@login_required
def region_documents(request, pk):
    """
    Region sənədləri
    """
    region = get_object_or_404(Region, pk=pk)
    documents = region.documents.all()
    
    # Filter by document type
    doc_type = request.GET.get('type')
    if doc_type:
        documents = documents.filter(document_type=doc_type)
    
    # Pagination
    paginator = Paginator(documents, 20)
    page = request.GET.get('page')
    documents = paginator.get_page(page)
    
    context = {
        'region': region,
        'documents': documents,
        'document_types': RegionDocument.DOCUMENT_TYPES,
    }
    return render(request, 'region/region_documents.html', context)

@login_required
def region_news(request, pk):
    """
    Region xəbərləri
    """
    region = get_object_or_404(Region, pk=pk)
    news = region.news.filter(is_active=True)
    
    # Pagination
    paginator = Paginator(news, 10)
    page = request.GET.get('page')
    news = paginator.get_page(page)
    
    context = {
        'region': region,
        'news': news,
    }
    return render(request, 'region/region_news.html', context)

@login_required
def region_statistics(request, pk):
    """
    Region statistikası
    """
    region = get_object_or_404(Region, pk=pk)
    
    # Update statistics before showing
    region.update_statistics()
    
    context = {
        'region': region,
        'total_schools': region.total_schools,
        'total_students': region.total_students,
        'total_teachers': region.total_teachers,
    }
    return render(request, 'region/region_statistics.html', context)
