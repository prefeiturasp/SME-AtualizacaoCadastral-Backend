import environ
import unicodedata

from config.settings.base import URL_CONFIGS, MEDIA_URL

env = environ.Env()


def url_configs(variable, content):
    return env('REACT_APP_URL') + URL_CONFIGS[variable].format(**content)


def ofuscar_email(email):
    m = email.split('@')
    return f'{m[0][0]}{"*" * (len(m[0]) - 2)}{m[0][-1]}@{m[1]}'


def url(content):
    return env('SERVER_NAME') + MEDIA_URL + content


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii
