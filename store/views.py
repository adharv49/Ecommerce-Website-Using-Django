from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, CartItem
from django.contrib.auth.decorators import login_required


from django.shortcuts import render


from .models import Product, Category, Wishlist

from django.db.models import Avg

def home(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    min_rating = request.GET.get('min_rating')

    # Start with category filter
    if selected_category:
        products = Product.objects.filter(category__name=selected_category)
    else:
        products = Product.objects.all()
    price_range = request.GET.get('price')

    if price_range:
        if price_range == '2000+':
            products = products.filter(price__gte=2000)
        else:
            min_price, max_price = price_range.split('-')
            products = products.filter(price__gte=min_price, price__lte=max_price)

    # Price filters
    

    # Rating filter
    if min_rating:
        try:
            min_rating = float(min_rating)
            products = products.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=min_rating)
        except ValueError:
            pass 
        '''
        filtered_products = []
        for product in products:
            avg = product.reviews.aggregate(avg=Avg('rating'))['avg']
            if avg and avg >= float(min_rating):
                filtered_products.append(product)
        products = filtered_products
        '''
    # Wishlist logic (unchanged)
    wishlist_items = []
    user_reviews = {}
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        user_reviews = {
            review.product_id: review
            for review in Review.objects.filter(user=request.user, product__in=products)
        }
    #products = products.prefetch_related('reviews')

    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'wishlist_items': wishlist_items,
        'user_reviews': user_reviews,
    })

# Add product to cart


# Cart page: show items and total


def cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    items = cart.items.all() if cart else []
    total = sum(item.subtotal for item in items)

    return render(request, 'store/cart.html', {
        'products': [item.product for item in items],
        'total': total
    })
# store/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from django.contrib import messages
from .models import Cart, CartItem

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart
    return None  # skip DB cart for anonymous users unless you want guest carts

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.info(request, f"{product.name} quantity updated in cart.")
    else:
        cart_item.quantity += 1
        messages.success(request, f"{product.name} added to your cart.")

    return redirect('home')

@login_required
def add_to_buy(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order, created = Order.objects.get_or_create(user=request.user)

    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if not created:
        order_item.quantity += 1
        order_item.save()
        messages.info(request, f"{product.name} quantity updated in checkout.")
    else:
        order_item.quantity += 1
        messages.success(request, f"{product.name} added to your checkout.")

    return redirect('home')
    product = get_object_or_404(Product, id=product_id)
    
    #total = sum(item.product.price * item.quantity for item in cart_items)
    #cart, created = Order.objects.get_or_create(user=request.user)
    order = Order.objects.filter(
    user=request.user,
    ).first()
    order_items = OrderItem.objects.get_or_create(order=order,product=product,defaults={'quantity': 1})
    #total = sum(item.price * item.quantity for item in order_items)

    #cart_item, created = OrderItem.objects.get_or_create(order=order, product=product)
    cart_item, created = OrderItem.objects.get_or_create(
    order=order,
    product=product,
    defaults={'quantity': 1}
    )
    

    #total = sum(item.product.price * item.quantity for item in cart_item)

    

    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.info(request, f"{product.name} quantity updated in checkout.")
    else:
        cart_item.quantity += 1
        messages.success(request, f"{product.name} added to your checkout.")

    return redirect('home')


@login_required
def cart_view(request):
    cart = Cart.objects.filter(user=request.user).first()

    if cart:
        items = cart.items.select_related('product')
        total = sum(item.subtotal for item in items)
    else:
        items = []
        total = 0

    return render(request, 'store/cart.html', {
        'items': items,
        'total': total
    })

from .models import Order, OrderItem  # Add Cart, CartItem, Product if not already imported

@login_required
def checkout_view(request):
    cart = Order.objects.filter(user=request.user).first()

    if cart:
        items = cart.items.select_related('product')
        total = sum(item.subtotal for item in items)
    else:
        items = []
        total = 0

    return render(request, 'store/checkout.html', {
        'items': items,
        'total': total
    })

from django.shortcuts import get_object_or_404, redirect
from .models import CartItem

def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart')
def remove_from_buy(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    item.delete()
    return redirect('checkout')
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Basic validations
        if not username or not password or not password2:
            messages.error(request, "All fields are required.")
            return redirect('register')

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        # Create the user
        user = User.objects.create_user(username=username, password=password)
        user.save()

        login(request, user)  # Log the user in
        return redirect('home')  # Change 'home' if needed

    return render(request, 'store/register.html')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def profile(request):
    return render(request, 'store/profile.html', {'user': request.user})


from .models import Wishlist, Product
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('home')

@login_required
def view_wishlist(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'store/wishlist.html', {'items': items})


from django.db.models import Q

def search(request):
    query = request.GET.get('query')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    ) if query else []
    
    return render(request, 'store/search_results.html', {'products': products, 'query': query})


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Wishlist, Product
@require_POST
def toggle_wishlist2(request,product_id):
    product_id = request.POST.get('product_id')
    product = Product.objects.get(id=product_id)
    user = request.user

    if not user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=403)

    wishlist_item, created = Wishlist.objects.get_or_create(user=user, product=product)

    if not created:
        wishlist_item.delete()
        return JsonResponse({'status': 'removed'})
    else:
        return JsonResponse({'status': 'added'})

from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from .models import Product, Wishlist  # Adjust import paths as needed

@require_POST
def toggle_wishlist_detail(request, product_id):
    # Check if user is logged in
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=403)

    product = get_object_or_404(Product, id=product_id)
    user = request.user

    try:
        Wishlist.objects.get(user=user, product=product).delete()
        return JsonResponse({'status': 'removed'})
    except Wishlist.DoesNotExist:
        Wishlist.objects.create(user=user, product=product)
        return JsonResponse({'status': 'added'})
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=403)

    # Get product and user
    product = get_object_or_404(Product, id=product_id)
    user = request.user

    # Toggle logic
    wishlist_item, created = Wishlist.objects.get_or_create(user=user, product=product)

    if not created:
        # Product already in wishlist — remove it
        wishlist_item.delete()
        messages.success(request, f"❌ Removed '{product.name}' from wishlist.")
    else:
        # Product wasn't in wishlist — added now
        messages.success(request, f"✅ Added '{product.name}' to wishlist.")

    # Redirect back to the previous page
    return redirect(request.META.get('HTTP_REFERER', 'home'))

'''
@require_POST
def toggle_wishlist_detail(request,product_id):
    product = get_object_or_404(Product, id=product_id)
    product_id = request.POST.get('product_id')
    #product = Product.objects.get(id=product_id)
    user = request.user

    if not user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=403)

    wishlist_item, created = Wishlist.objects.get_or_create(user=user, product=product)

    
    if not created:
        #remove_from_wishlist(request, product_id)
        wishlist_item.delete()
        redirect('home')
        #return render(request, 'store/product_detail.html', {
        #'product': product,})
      #  return JsonResponse({'status': 'removed'})
      
        
    else:
        add_to_wishlist(request, product_id)
        #return render(request, 'store/product_detail.html', {
        #'product': product,'status':'added'})
       # return JsonResponse({'status': 'added'})
        
  
    return redirect(request.META.get('HTTP_REFERER', 'home'))
    redirect('home')
      
'''     
    
from django.views.decorators.http import require_POST

@require_POST
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('wishlist')

from django.contrib.auth.decorators import login_required

from django.db import IntegrityError

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Review

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')

        # Check for existing review
        review, created = Review.objects.get_or_create(product=product, user=request.user,defaults={'rating': rating, 'comment': comment})
        review.rating = rating
        review.comment = comment
        review.save()

        if created:
            messages.success(request, "Review submitted successfully.")
        else:
            messages.success(request, "Your review has been updated.")

    return redirect('home')


@login_required
def delete_review(request, product_id):
    review = get_object_or_404(Review, product_id=product_id, user=request.user)
    review.delete()
    messages.success(request, "Your review has been deleted.")
    return redirect('home')


# views.py
from django.shortcuts import render
from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})
def product_details(request, pk):
   # product = get_object_or_404(Product, pk=pk)
    #product = get_object_or_404(Product, id=product_id)
    product = get_object_or_404(Product, pk=pk)
    wishlist_items = []
    user_reviews = {}

    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        user_reviews = {
            review.product_id: review
            for review in Review.objects.filter(user=request.user, product=product)
        }

    return render(request, 'store/product_detail.html', {
        'product': product,
        'wishlist_items': wishlist_items,
        'user_reviews': user_reviews,
    })
    #return render(request, 'product_detail.html', {'product': product})
    
    


from django.shortcuts import redirect
from django.contrib.auth import logout


def custom_logout(request):
    logout(request)
    return redirect('home')  # or 'login'




   




