from django.shortcuts import get_object_or_404
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,UpdateModelMixin
from rest_framework.response import Response
from .models import Product,Collection,OrderItem,Review,Cart,CartItem,Customer
from .serializers import ProductSerializer,CustomerSerializer,CollectionSerializer,ReviewSerializer,CartSerializer,CartItemSerializer,AddCartItemSerializer,UpdateCartItemSerializer
from store import serializers
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from .pagination import DefaultPagination
from .permissions import IsAdminOrReadOnly
# Create your views here.
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class =  ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend ,SearchFilter,OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title','description']
    pagination_class = DefaultPagination
    ordering_fields = ['unit_price','last_update']
    
    def get_serializer_context(self):
        return {'request': self.request}
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error':"Product cannot be deleted."},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy( request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('product')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = DefaultPagination
    def destroy(self, request, *args, **kwargs):
        if collection.products.count() > 0:
            return Response({'error':'Collection cannot be deleted.'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy( request, *args, **kwargs)

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        return Review.objects.filter(product_id = self.kwargs['product_pk'])
    
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

class CartViewSet(CreateModelMixin,DestroyModelMixin,RetrieveModelMixin, GenericViewSet ):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
class CartItemViewSet(ModelViewSet):
    http_method_names =['get','post','patch','delete']
    def get_serializer_class(self):
        if self.request.method == 'POST': 
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}
    def get_queryset(self):
        return CartItem.objects.filter(cart_id= self.kwargs['cart_pk']).select_related('product')


class CustomerViewSet(CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,GenericViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False,methods=['GET','PUT'])
    def me(self,request):
        (customer,created) = Customer.objects.get_or_create(user_id=request.user.id)
        if request.method == 'GET':
            serializers = CustomerSerializer(customer)
            return Response(serializers.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer,data=request.data)
            serializer.is_valid(raise_exception =True)
            serializer.save()
            return Response(serializer.data)