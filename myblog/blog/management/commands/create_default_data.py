# blog/management/commands/create_default_data.py
from django.core.management.base import BaseCommand
from blog.models import Category, Tag
import uuid
from django.template.defaultfilters import slugify

class Command(BaseCommand):
    help = 'Создает категории и теги по умолчанию'

    def handle(self, *args, **options):
        categories = ['Программирование', 'Дизайн', 'Маркетинг', 'Путешествия', 'Кулинария']
        for cat_name in categories:
            category, created = Category.objects.get_or_create(name=cat_name)
            if created:
                category.slug = slugify(cat_name) + '-' + uuid.uuid4().hex[:6]
                category.save()
                self.stdout.write(self.style.SUCCESS(f'Создана категория: {cat_name}'))
        
        tags = ['django', 'python', 'web', 'development', 'design', 'cooking', 'travel']
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                tag.slug = slugify(tag_name) + '-' + uuid.uuid4().hex[:6]
                tag.save()
                self.stdout.write(self.style.SUCCESS(f'Создан тег: {tag_name}'))
        
        self.stdout.write(self.style.SUCCESS('Категории и теги по умолчанию созданы!'))