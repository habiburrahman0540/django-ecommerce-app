from django.contrib import admin,messages
from django.db.models.query import QuerySet
from . import models
from django.db.models import Count
# Register your models here.

class InventoryFilter(admin.SimpleListFilter):
      title = 'Inventory'
      parameter_name = 'inventory'
      
      def lookups(self, request, model_admin):
          return [('<10','Law')]
      
      def queryset(self, request, queryset: QuerySet):
          if self.value() == '<10':
              return queryset.filter(inventory__lt = 10)

    
 
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    search_fields = ['title']
    actions = ['clear_inventory']
    list_display = [ 'title','description','unit_price','inventory_status','collection']
    list_per_page = 10
    list_filter =['collection','last_update',InventoryFilter]
    @admin.display(ordering='inventory')
    def inventory_status(self,product):
        if product.inventory < 10:
            return 'Law'
        return 'ok'
    
    
    @admin.action(description='Clear Product inventory')
    def clear_inventory (self, request , queryset):
       update_query = queryset.update(inventory=0)
       self.message_user(
           request,
           f'{update_query} Product cleared successfully.',
           messages.ERROR
           )
       
       
       
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','products_count']
    search_fields = ['title']
    @admin.display(ordering='products_count')
    def products_count(self,collection):
        return collection.products_count
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count = Count('product')
        )
    
    
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','email','phone','membership']
    list_display_links = ['first_name','last_name','email','phone']
    list_per_page = 10
    list_select_related=['user']
    ordering =['user__first_name','user__last_name']
    search_fields = ['first_name__istartswith','last_name__istartswith']
    list_editable = ['membership']
    
    
@admin.register(models.Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['street','city','customer']
    

class orderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    model = models.OrderItem
    extra = 0
    min_num = 1
    max_num = 10
    
@admin.register(models.Order)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ['placed_at','customer']
    autocomplete_fields = ['customer']
    inlines = [orderItemInline]


@admin.register(models.Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['id','description','discount']
 