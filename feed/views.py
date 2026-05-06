import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, PostLike
from core.models import Notification


@login_required
def index(request):
    # For the feed, we only show approved posts
    posts = Post.objects.filter(is_approved=True).prefetch_related('comments', 'uploaded_by').order_by('-created_at')
    return render(request, 'feed/feed.html', {'posts': posts})



@login_required
@require_http_methods(['GET', 'POST'])
def api_posts(request):
    if request.method == 'GET':
        from core.models import Enrollment
        from django.db.models import Case, When, Value, IntegerField, Q

        # Pagination
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('limit', 20))

        # Get enrolled course IDs for the current user
        enrolled_course_ids = Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)

        # Show approved posts OR user's own drafts
        all_posts = Post.objects.filter(
            Q(is_approved=True, is_draft=False) | Q(uploaded_by=request.user)
        ).annotate(
            priority=Case(
                When(course_id__in=enrolled_course_ids, then=Value(1)),
                When(course__isnull=True, then=Value(2)),
                default=Value(3),
                output_field=IntegerField(),
            )
        ).prefetch_related('comments', 'uploaded_by').order_by('priority', '-created_at')

        total = all_posts.count()
        posts = list(all_posts[(page - 1) * per_page:page * per_page])

        # Get user's liked post IDs for this page
        user_liked_ids = set(PostLike.objects.filter(user=request.user, post__in=posts).values_list('post_id', flat=True))

        data = []
        for p in posts:
            comments = [{
                'id': c.id,
                'author': c.uploaded_by.get_full_name() or c.uploaded_by.email, 
                'text': c.text,
                'avatar_initials': f"{c.uploaded_by.first_name[0]}{c.uploaded_by.last_name[0]}" if c.uploaded_by.first_name and c.uploaded_by.last_name else "U",
                'can_edit': (c.uploaded_by == request.user),
                'can_delete': (c.uploaded_by == request.user or request.user.is_portal_admin),
            } for c in p.comments.all()]
            
            data.append({
                'id': p.id,
                'author': p.uploaded_by.get_full_name() or p.uploaded_by.email,
                'author_role': p.uploaded_by.get_role_display(),
                'avatar_initials': f"{p.uploaded_by.first_name[0]}{p.uploaded_by.last_name[0]}" if p.uploaded_by.first_name and p.uploaded_by.last_name else "U",
                'content': p.content,
                'media_url': p.media.url if p.media else None,
                'is_approved': p.is_approved,
                'is_draft': p.is_draft,
                'likes': p.likes,
                'user_liked': p.id in user_liked_ids,
                'comments': comments,
                'can_delete': (p.uploaded_by == request.user or request.user.is_portal_admin),
                'created_at': p.created_at.strftime("%b %d, %I:%M %p"),
            })
        return JsonResponse({'posts': data, 'has_more': (page * per_page) < total, 'total': total})

    # POST — create a new post
    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body)
            content = body.get('content', '')
            is_draft = body.get('is_draft', False)
        else:
            content = request.POST.get('content', '')
            is_draft = request.POST.get('is_draft') == 'true'
    except Exception:
        return JsonResponse({'error': 'Invalid request body'}, status=400)

    is_approved = True if (request.user.role == 'faculty' or request.user.is_portal_admin) and not is_draft else False

    post = Post.objects.create(
        uploaded_by=request.user,
        content=content,
        is_approved=is_approved,
        is_draft=is_draft,
        likes=0,
    )
    
    if not is_approved and not is_draft:
        from core.utils import notify_admins
        notify_admins(
            title="New Post Awaiting Review",
            message=f"{request.user.get_full_name() or request.user.email} published a feed post that requires approval.",
            notification_type="system",
            link="/core/moderation/"
        )

    
    if request.FILES.get('media'):
        post.media = request.FILES.get('media')
        post.save()

    message = 'Draft saved!' if is_draft else ('Post published!' if is_approved else 'Post submitted for admin review.')
    return JsonResponse({
        'id': post.id, 
        'message': message, 
        'is_approved': is_approved,
        'is_draft': post.is_draft,
        'author': post.uploaded_by.get_full_name() or post.uploaded_by.email,
        'avatar_initials': f"{post.uploaded_by.first_name[0]}{post.uploaded_by.last_name[0]}" if post.uploaded_by.first_name and post.uploaded_by.last_name else "U",
        'media_url': post.media.url if post.media else None
    }, status=201)



@login_required
@require_http_methods(['POST'])
def api_like_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    like, created = PostLike.objects.get_or_create(post=post, user=request.user)
    if created:
        post.likes += 1
        post.save()
        if post.uploaded_by != request.user:
            Notification.objects.create(
                recipient=post.uploaded_by,
                sender=request.user,
                notification_type='system',
                title='Post Liked',
                message=f'{request.user.get_full_name() or request.user.email} liked your post.',
                link='/feed/'
            )
    else:
        like.delete()
        post.likes = max(0, post.likes - 1)
        post.save()

    return JsonResponse({'likes': post.likes, 'user_liked': created})



@login_required
@require_http_methods(['GET', 'POST', 'PATCH', 'DELETE'])
def api_post_detail(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    if request.method == 'GET':
        comments = [{'id': c.id, 'author': c.uploaded_by.email, 'text': c.text} for c in post.comments.all()]
        return JsonResponse({
            'id': post.id, 
            'author': post.uploaded_by.get_full_name() or post.uploaded_by.email, 
            'content': post.content,
            'media_url': post.media.url if post.media else None,
            'is_approved': post.is_approved, 
            'is_draft': post.is_draft,
            'likes': post.likes, 
            'comments': comments
        })

    if request.method in ['POST', 'PATCH']:
        try:
            if request.content_type == 'application/json':
                body = json.loads(request.body)
            else:
                body = request.POST

            # Authorization check
            if post.uploaded_by != request.user and not request.user.is_portal_admin:
                return JsonResponse({'error': 'Unauthorized'}, status=403)
                
            if 'content' in body:
                post.content = body['content']

            if 'is_approved' in body and request.user.is_portal_admin:
                post.is_approved = body['is_approved']
            
            if 'is_draft' in body:
                val = body['is_draft']
                post.is_draft = val.lower() == 'true' if isinstance(val, str) else bool(val)
                if not post.is_draft:
                    post.is_approved = True if request.user.role == 'faculty' or request.user.is_portal_admin else False
            
            if request.FILES.get('media'):
                post.media = request.FILES.get('media')

            post.save()
            return JsonResponse({'status': 'updated'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


    if request.method == 'DELETE':
        if post.uploaded_by == request.user or request.user.is_portal_admin:
            if post.uploaded_by != request.user:
                Notification.objects.create(
                    recipient=post.uploaded_by,
                    sender=request.user,
                    notification_type='system',
                    title='Your Post was Removed',
                    message='An administrator has removed your post.',
                    link='/feed/'
                )
            post.delete()
            return JsonResponse({'status': 'deleted'})
        return JsonResponse({'error': 'Unauthorized'}, status=403)


@login_required
@require_http_methods(['POST'])
def api_comments(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body)
            text = body.get('text', '')
        else:
            text = request.POST.get('text', '')
    except Exception:
        return JsonResponse({'error': 'Invalid request body'}, status=400)

    comment = Comment.objects.create(
        post=post,
        uploaded_by=request.user,
        text=text,
    )
    
    if post.uploaded_by != request.user:
        Notification.objects.create(
            recipient=post.uploaded_by,
            sender=request.user,
            notification_type='system',
            title='New Comment on your Post',
            message=f'{request.user.get_full_name() or request.user.email} commented on your post: "{text[:50]}..."',
            link='/feed/'
        )
        
    return JsonResponse({
        'id': comment.id, 
        'author': comment.uploaded_by.get_full_name() or comment.uploaded_by.email, 
        'text': comment.text,
        'avatar_initials': f"{comment.uploaded_by.first_name[0]}{comment.uploaded_by.last_name[0]}" if comment.uploaded_by.first_name and comment.uploaded_by.last_name else "U",
        'can_edit': True,
        'can_delete': True,
    }, status=201)


@login_required
@require_http_methods(['PATCH', 'DELETE'])
def api_comment_detail(request, comment_id):
    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    if request.method == 'PATCH':
        if comment.uploaded_by != request.user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        try:
            body = json.loads(request.body)
            if 'text' in body:
                comment.text = body['text']
                comment.save()
            return JsonResponse({'status': 'updated', 'text': comment.text})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    if request.method == 'DELETE':
        if comment.uploaded_by == request.user or request.user.is_portal_admin:
            if comment.uploaded_by != request.user:
                Notification.objects.create(
                    recipient=comment.uploaded_by,
                    sender=request.user,
                    notification_type='system',
                    title='Your Comment was Removed',
                    message='An administrator has removed your comment.',
                    link='/feed/'
                )
            comment.delete()
            return JsonResponse({'status': 'deleted'})
        return JsonResponse({'error': 'Unauthorized'}, status=403)

