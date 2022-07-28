from project import User
from project.api import user_identity_lookup
from project import app

context = app.app_context()


def test_user_lookup():
    with context:
        user = User.query.filter_by(username='admin').first()
        assert user_identity_lookup(user) == 1

