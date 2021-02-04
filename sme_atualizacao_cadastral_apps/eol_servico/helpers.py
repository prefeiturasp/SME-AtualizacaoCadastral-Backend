def ajusta_cpf(cpf):
    if cpf:
        return f'{int(cpf):0>11}'
    return ''
