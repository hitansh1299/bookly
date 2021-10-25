class UsernameError(Exception):
    def __str__(self) -> str:
        return "USERNAME TAKEN!"


class PhoneError(Exception):
    def __str__(self) -> str:
        return "Phone Number is Invalid!"


class AadharError(Exception):
    def __str__(self) -> str:
        return "Aadhar Number is Invalid!"

