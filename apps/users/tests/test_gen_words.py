import pytest
from apps.users.utils.gen_words import generate_random_username

@pytest.mark.django_db  # Añade este decorador para habilitar el acceso a la base de datos
def test_generate_random_username():
    # Prueba la generación de un nombre de usuario aleatorio
    username = generate_random_username()
    assert isinstance(username, str)
    assert len(username) > 0