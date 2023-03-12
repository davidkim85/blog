from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from .forms import CommentForm, EmailPostForm
from .models import Post


# Create your views here.
def blogShow(request):
    posts = Post.objects.all()
    return render(request, 'blog/index.html', {'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()
    emailPost = EmailPostForm()
    sent = False;
    return render(request,
                  'blog/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form, 'sent': sent, 'emailPost': emailPost})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    emailPost = EmailPostForm()
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
        comments = post.comments.filter(active=True)
        form = CommentForm()

        return render(request,
                      'blog/detail.html',
                      {'post': post,
                       'comments': comments,
                       'form': form,'emailPost': emailPost})
    return render(request, 'blog/detail.html', {'post': post, 'form': form, 'comment': comment,'emailPost': emailPost})


@require_POST
def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comments = post.comments.filter(active=True)
    sent = False
    form = CommentForm()
    if request.method == 'POST':
        # Form was submitted
        emailPost = EmailPostForm(request.POST)
        if emailPost.is_valid():
            # Form fields passed validation
            cd = emailPost.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"Post that recommends to you"
            message = f"Read {post.title} at {post_url}\n\n"
            send_mail(subject, message, "poramok@gmail.com", [cd['email']])
            sent = True
    else:
        emailPost = EmailPostForm()
    return render(request, 'blog/detail.html', {'post': post, 'form': form, 'sent': sent,
                                                'emailPost': emailPost,'comments':comments})
