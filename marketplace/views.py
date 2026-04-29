import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Listing, ChatMessage


@login_required
def index(request):
    return render(request, 'marketplace/marketplace.html')


@login_required
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def api_listings(request):
    if request.method == 'GET':
        qs = Listing.objects.all()
        
        # Regular users only see approved active listings
        # Regular users only see approved active listings OR their own
        if not request.user.is_portal_admin:
            from django.db.models import Q
            qs = qs.filter(Q(is_approved=True) | Q(uploaded_by=request.user))


        status = request.GET.get('status')
        listing_type = request.GET.get('type')
        if status:
            qs = qs.filter(status=status)
        if listing_type:
            qs = qs.filter(listing_type=listing_type)

        data = [{
            'id': l.id,
            'item_name': l.item_name,
            'uploaded_by': l.uploaded_by.get_full_name() or l.uploaded_by.email,
            'seller_contact': l.seller_contact,
            'price': str(l.price),
            'condition': l.get_condition_display(),
            'listing_type': l.get_listing_type_display(),
            'description': l.description,
            'status': l.status,
            'is_approved': l.is_approved,
            'can_edit': (l.uploaded_by == request.user or request.user.is_portal_admin),
            'image_url': l.image.url if l.image else None,
            'created_at': l.created_at.strftime("%b %d, %Y"),

        } for l in qs]
        return JsonResponse({'listings': data})

    # POST - Create new listing
    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body)
            item_name = body.get('item_name', '')
            seller_contact = body.get('seller_contact', '')
            price = body.get('price', 0)
            condition = body.get('condition', 'good')
            listing_type = body.get('listing_type', 'sell')
            description = body.get('description', '')
        else:
            item_name = request.POST.get('item_name', '')
            seller_contact = request.POST.get('seller_contact', '')
            price = request.POST.get('price', 0)
            condition = request.POST.get('condition', 'good')
            listing_type = request.POST.get('listing_type', 'sell')
            description = request.POST.get('description', '')
    except Exception:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    # Faculty members are automatically approved
    is_approved = True if request.user.role == 'faculty' or request.user.is_portal_admin else False

    listing = Listing.objects.create(
        uploaded_by=request.user,
        item_name=item_name,
        seller_name=request.user.get_full_name() or request.user.username,
        seller_contact=seller_contact,
        price=price,
        condition=condition,
        listing_type=listing_type,
        description=description,
        status='active',
        is_approved=is_approved
    )
    
    if not is_approved:
        from core.utils import notify_admins
        notify_admins(
            title="New Listing Awaiting Review",
            message=f"{request.user.get_full_name() or request.user.email} listed '{item_name}' which requires approval.",
            notification_type="system",
            link="/core/moderation/"
        )


    if request.FILES.get('image'):
        listing.image = request.FILES.get('image')
        listing.save()

    message = 'Listing published!' if is_approved else 'Listing submitted for admin review.'
    return JsonResponse({'id': listing.id, 'message': message, 'is_approved': is_approved}, status=201)


@login_required
@csrf_exempt
@require_http_methods(['GET', 'POST', 'PATCH', 'DELETE'])
def api_listing_detail(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'id': listing.id, 
            'item_name': listing.item_name,
            'uploaded_by': listing.uploaded_by.email, 
            'seller_contact': listing.seller_contact,
            'price': str(listing.price), 
            'condition': listing.get_condition_display(),
            'listing_type': listing.get_listing_type_display(), 
            'description': listing.description,
            'status': listing.status,
            'image_url': listing.image.url if listing.image else None
        })

    if request.method in ['POST', 'PATCH']:
        if listing.uploaded_by == request.user or request.user.is_portal_admin:
            try:
                body = json.loads(request.body)
                if 'status' in body:
                    listing.status = body['status']
                if 'item_name' in body: listing.item_name = body['item_name']
                if 'price' in body: listing.price = body['price']
                if 'description' in body: listing.description = body['description']
                if 'seller_contact' in body: listing.seller_contact = body['seller_contact']
                
                # Allow staff to approve
                if 'is_approved' in body and request.user.is_portal_admin:
                    val = body['is_approved']
                    listing.is_approved = val.lower() == 'true' if isinstance(val, str) else bool(val)
                
                listing.save()
                return JsonResponse({'status': 'updated', 'is_approved': listing.is_approved})

            except Exception:
                return JsonResponse({'error': 'Invalid data'}, status=400)
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.method == 'DELETE':
        if listing.uploaded_by == request.user or request.user.is_portal_admin:
            listing.delete()
            return JsonResponse({'status': 'deleted'})
        return JsonResponse({'error': 'Unauthorized'}, status=403)


@login_required
@csrf_exempt
@require_http_methods(['GET', 'POST'])
def api_chat(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    if request.method == 'GET':
        messages = [{
            'sender': m.sender.get_full_name() or m.sender.email, 
            'text': m.text, 
            'created_at': m.created_at.strftime("%I:%M %p")
        } for m in listing.messages.all()]
        return JsonResponse({'messages': messages})

    try:
        body = json.loads(request.body)
        text = body.get('text', '')
    except Exception:
        return JsonResponse({'error': 'Invalid data'}, status=400)

    msg = ChatMessage.objects.create(
        listing=listing,
        sender=request.user,
        text=text,
    )
    return JsonResponse({'id': msg.id, 'sender': msg.sender.get_full_name() or msg.sender.email, 'text': msg.text}, status=201)
