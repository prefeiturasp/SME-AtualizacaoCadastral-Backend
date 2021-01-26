from django.core import validators


phone_validation = validators.RegexValidator(
    regex=r"^\d{9}$",
    message="Necessário 9 digitos",
)

cpf_validation = validators.RegexValidator(
    regex=r"^\d{11}$",
    message="Necessário 11 digitos",
)

email_validation = validators.RegexValidator(
    regex=r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$",
    message="Necessário e-mail valido",
)

nome_validation = validators.RegexValidator(
    regex=r"^[a-zA-Z]+$",
    message="Não é permitido número",
)
