from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cria usuário admin padrão'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        email = 'fabiano.freitas@gmail.com'
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'username': email, 'first_name': 'Fabiano', 'is_staff': True, 'is_superuser': True},
        )
        user.username = email
        user.set_password('260281xx')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        action = 'criado' if created else 'atualizado'
        self.stdout.write(self.style.SUCCESS(f'Admin {action}: {email}'))
