from django.http import Http404


class BaseRepository:
    model = None

    def get_queryset(self):
        if self.model is None:
            raise ValueError("Repository model is not configured.")
        return self.model.objects.all()

    def list_all(self, *, order_by=None):
        queryset = self.get_queryset()
        if order_by:
            queryset = queryset.order_by(*order_by)
        return queryset

    def filter(self, *args, **kwargs):
        return self.get_queryset().filter(*args, **kwargs)

    def get(self, **kwargs):
        return self.get_queryset().get(**kwargs)

    def first(self, **kwargs):
        return self.get_queryset().filter(**kwargs).first()

    def create(self, **kwargs):
        return self.model.objects.create(**kwargs)

    def save(self, instance, *, update_fields=None):
        if update_fields:
            instance.save(update_fields=update_fields)
        else:
            instance.save()
        return instance

    def update(self, instance, **kwargs):
        for field, value in kwargs.items():
            setattr(instance, field, value)
        instance.save(update_fields=list(kwargs.keys()) if kwargs else None)
        return instance

    def delete(self, instance):
        instance.delete()

    def get_or_404(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist as exc:
            raise Http404(f"{self.model.__name__} not found.") from exc
