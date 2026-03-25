from checklist.exception_handler import handle_repository_exceptions


class BaseRepository:
    model = None

    def get_queryset(self):
        if self.model is None:
            raise ValueError("Repository model is not configured.")
        return self.model.objects.all()

    @handle_repository_exceptions
    def list_all(self, *, order_by=None):
        queryset = self.get_queryset()
        if order_by:
            queryset = queryset.order_by(*order_by)
        return queryset

    @handle_repository_exceptions
    def filter(self, *args, **kwargs):
        return self.get_queryset().filter(*args, **kwargs)

    @handle_repository_exceptions
    def get(self, **kwargs):
        return self.get_queryset().get(**kwargs)

    @handle_repository_exceptions
    def first(self, **kwargs):
        return self.get_queryset().filter(**kwargs).first()

    @handle_repository_exceptions
    def create(self, **kwargs):
        return self.model.objects.create(**kwargs)

    @handle_repository_exceptions
    def save(self, instance, *, update_fields=None):
        if update_fields:
            instance.save(update_fields=update_fields)
        else:
            instance.save()
        return instance

    @handle_repository_exceptions
    def update(self, instance, **kwargs):
        for field, value in kwargs.items():
            setattr(instance, field, value)
        instance.save(update_fields=list(kwargs.keys()) if kwargs else None)
        return instance

    @handle_repository_exceptions
    def delete(self, instance):
        instance.delete()

    @handle_repository_exceptions
    def get_by_id(self, entity_id):
        return self.get_queryset().get(id=entity_id)
