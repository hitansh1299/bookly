class UsernameError(Exception):
    def __str__(self) -> str:
        return "USERNAME TAKEN!"