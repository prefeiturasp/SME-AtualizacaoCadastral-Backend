# SME-AtualizacaoCadastral-Backend

## Executar o projeto com docker

- Clone o repositório
```console
git clone https://github.com/prefeiturasp/SME-AtualizacaoCadastral-Backend.git
```

- Entre no diretório criado
```console
cd SME-AtualizacaoCadastral-Backend
```

- Configure a instância com o .env
```console
cp env_sample .env
```

- Execute o docker usando o docker compose
```console
docker-compose -f local.yml up --build -d
```

- Rode as migrações
```console
make migrations
```

- Crie um super usuário
```console
make create_superuser
```

- Rode a aplicação
```console
make runserver
```

- Acesse a aplicação usando o browse
```console
http://localhost:8000
```
