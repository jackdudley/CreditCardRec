from src.model.user import User
from src.repository.user_repository import UserRepository
from src.repository.authorized_user_repository import AuthorizedUserRepository

class UserService():
    def get_user_data() -> User:
        return Us