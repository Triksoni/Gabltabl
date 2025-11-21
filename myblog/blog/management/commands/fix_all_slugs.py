# blog/management/commands/fix_all_slugs.py
from django.core.management.base import BaseCommand
from blog.models import Post
from django.template.defaultfilters import slugify

class Command(BaseCommand):
    help = 'Исправляет ВСЕ посты с пустыми или некорректными slug'

    def handle(self, *args, **options):
        posts = Post.objects.all()
        fixed_count = 0
        
        for post in posts:
            original_slug = post.slug
            needs_fix = False
            
            # Проверяем заголовок
            if not post.title or post.title.strip() == "":
                post.title = f"Пост {post.id}"
                needs_fix = True
                self.stdout.write(f'📝 Исправлен заголовок поста {post.id}')
            
            # Проверяем slug - если пустой, None или содержит только пробелы
            if not post.slug or str(post.slug).strip() == "":
                needs_fix = True
                self.stdout.write(f'🚨 Найден пост с пустым slug: ID {post.id}, заголовок: "{post.title}"')
            
            if needs_fix:
                # Генерируем новый slug
                base_slug = slugify(post.title)
                if not base_slug:
                    base_slug = f"post-{post.id}"
                
                unique_slug = base_slug
                counter = 1
                
                # Проверяем уникальность
                while Post.objects.filter(slug=unique_slug).exclude(pk=post.pk).exists():
                    unique_slug = f"{base_slug}-{counter}"
                    counter += 1
                
                post.slug = unique_slug
                post.save()
                fixed_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Исправлен пост: ID {post.id}, "{post.title}" -> "{post.slug}" (было: "{original_slug}")'))
            else:
                self.stdout.write(f'✓ Пост ID {post.id} в порядке: "{post.title}" -> "{post.slug}"')
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Исправлено постов: {fixed_count} из {posts.count()}'))
        
        # Проверим остались ли посты с пустыми slug
        problematic_posts = Post.objects.filter(slug__isnull=True) | Post.objects.filter(slug='')
        if problematic_posts.exists():
            self.stdout.write(self.style.ERROR(f'❌ Осталось проблемных постов: {problematic_posts.count()}'))
            for post in problematic_posts:
                self.stdout.write(self.style.ERROR(f'   ID {post.id}: "{post.title}" -> slug: "{post.slug}"'))