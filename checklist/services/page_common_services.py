from django.core.paginator import Paginator


def paginate_items(items, page_number, per_page=10):
    paginator = Paginator(items, per_page)
    return paginator.get_page(page_number)
