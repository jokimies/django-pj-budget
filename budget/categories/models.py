import datetime
from decimal import Decimal
from django.utils.encoding import python_2_unicode_compatible

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

# django mptt
from mptt.models import MPTTModel, TreeForeignKey, TreeManager

#

class StandardMetadataMPTT(MPTTModel):
    """
    A basic (abstract) model for metadata.
    """
    created = models.DateTimeField(_('Created'), default=datetime.datetime.now)
    updated = models.DateTimeField(_('Updated'), default=datetime.datetime.now)
    is_deleted = models.BooleanField(_('Is deleted'), default=False, db_index=True)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        self.updated = datetime.datetime.now()
        super(StandardMetadataMPTT, self).save(*args, **kwargs)
    
    def delete(self):
        self.is_deleted = True
        self.save()


class ActiveManagerMPTT(TreeManager):
    def get_queryset(self):
        return super(ActiveManagerMPTT, self).get_queryset().filter(is_deleted=False)

class CategoryRootNodeManager(TreeManager):
    def get_queryset(self):
        return super(CategoryRootNodeManager, self).get_queryset().filter(level=0)

@python_2_unicode_compatible
class Category(StandardMetadataMPTT):
    """
    Categories are the means to loosely tie together the transactions and
    estimates.
    
    They are used to aggregate transactions together and compare them to the
    appropriate budget estimate. For the reasoning behind this, the docstring
    on the Transaction object explains this.
    """

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    name = models.CharField(_('Name'), max_length=128)
    slug = models.SlugField(_('Slug'), unique=True)
    
    objects = TreeManager()
    active = ActiveManagerMPTT()
    root_nodes = CategoryRootNodeManager()
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
    
    def __str__(self):
        return self.name
    

    def estimates_and_transactions(self, start_date, end_date, query = Q()):
        
        transactions = self.transactions.all()
        estimates = self.estimates.all()

def get_queryset_descendants(nodes, include_self=False): 
    """
    http://stackoverflow.com/questions/5722767/django-mptt-get-descendants-for-a-list-of-nodes
    """
    if not nodes: 
        return Category.objects.none() 
    filters = [] 
    for n in nodes: 
        lft, rght = n.lft, n.rght 
        if include_self: 
            lft -=1 
            rght += 1 
        filters.append(Q(tree_id=n.tree_id, lft__gt=lft, rght__lt=rght)) 
    # q = reduce(operator.or_, filters)
    # Removing reduce, as reduced from std library
    # (http://www.artima.com/weblogs/viewpost.jsp?thread=98196 )
    # Do it with for loop instead, just of everything together

    query = Q()
    for filter in filters:
        query |= filter
    return Category.objects.filter(query)
