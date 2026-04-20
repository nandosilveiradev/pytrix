# Pytrix

> Ambiente de desenvolvimento pessoal para coexistir com qualquer projeto, framework ou legado — sem colisão, sem mágica, sem dependência misteriosa.

---

## O que é

Pytrix não é um framework. Não é uma biblioteca. Não compete com Django, Flask, Laravel, Next.js ou qualquer outro.

É uma **estação de trabalho** construída para quem precisa entrar em projetos desorganizados, com dados sujos, arquitetura inexistente, URLs hardcoded e banco sem normalização — e ter ferramentas confiáveis para trabalhar sem depender do caos que encontrou.

Cada decisão aqui tem uma cicatriz atrás.

---

## O que resolve na prática

- Clonar dois projetos e rodá-los em paralelo sem colisão de porta, nome ou variável
- Migrar rotas de um projeto legado uma por uma, testando cada uma em produção antes de incorporar
- Expor ambientes locais para uma equipe sem tocar em VPN, firewall ou TI
- Gerar utils independentes que funcionam sozinhos — sem precisar do ambiente completo
- Normalizar banco de dados guiado por perguntas de domínio, não por regras mecânicas
- Trabalhar com múltiplos devs em sessões tmux isoladas no mesmo ambiente
- Inspecionar e limpar dados antes de importar — nunca automático, sempre consciente

---

## Por que o prefixo `pytrix_` em tudo

Quando o Pytrix coexiste com Django, Flask ou qualquer outro framework, os atributos, pastas, arquivos e variáveis de ambiente precisam de namespace visual explícito. Sem isso o LSP mistura sugestões e os imports colidem.

```python
# framework
self.model
self.view
self.request

# pytrix — nunca colide
self.px_model
self.px_view
self.px_lang
```

```bash
# framework
DATABASE_URL=
SECRET_KEY=

# pytrix — separados visualmente no .env
PYTRIX_CF_TOKEN=
PYTRIX_DNS_DOMAIN=pytrix.local
PYTRIX_GIT_EMAIL=dev@empresa.com
```

O dev digita `px_` e o autocomplete mostra só Pytrix. Digita sem prefixo e mostra só o framework.

---

## Estrutura

```
.
├── pytrix.py                        ← entry point
├── pytrix_clean.sh                  ← limpa cache e resíduos
├── pytrix_forge_utils.sh            ← gera utils independentes
├── pytrix_build_docs.py             ← gera documentação via pdoc
├── pytrix_docker_up.sh              ← sobe o ambiente
├── pytrix_docker_compose.yml        ← orquestração dos containers
├── pytrix_gerar_dump_code.sh        ← dump do ecossistema para análise
├── pytrix_prefab_class.py           ← gerador de classes MVC
├── pytrix_prefab_components.py      ← gerador de componentes HTML
├── pytrix_requirements.txt
├── PYTRIX_README.md
│
├── pytrix_controllers/
│   └── pytrix_controllers_select_language.py
│
├── pytrix_models/
│   ├── pytrix_model_base.py
│   └── pytrix_model_select_language.py
│
├── pytrix_views/
│   ├── pytrix_view_base.py
│   └── pytrix_view_select_language.py
│
├── pytrix_i18n/
│   └── i18n.py
│
├── pytrix_utils/
│   └── pytrix_tmux_controller.py
│
├── pytrix_docker/
│   ├── Dockerfile.dev
│   ├── Dockerfile.tunnel
│   └── dns/scriptdns.sh
│
├── pytrix_docs/
└── pytrix_web_static/
```

---

## Instalação

> ⚠️ O `./setup.sh` instala **Docker** e **tmux** automaticamente.
> Se não quer essas instalações na sua máquina, este projeto não é para você.

```bash
git clone https://github.com/nandosilveira/pytrix
cd pytrix
cp .pytrix_env.example .pytrix_env   # preencha com seus valores
./setup.sh
```

O ambiente abre sempre em tmux com split configurado. Esse comportamento é intencional — todos os devs veem a mesma coisa ao entrar.

---

## Variáveis de ambiente

`.pytrix_env` nunca vai para o repositório. `.pytrix_env.example` está versionado com valores fictícios mas realistas — para quem clonar saber exatamente o que preencher.

```bash
# identidade git
PYTRIX_GIT_EMAIL=dev@empresa.com
PYTRIX_GIT_NAME=pytrix forge

# tunnel Cloudflare
# vazio = tunnel efêmero (link temporário)
# preenchido = tunnel permanente (subdomínio fixo)
PYTRIX_CF_TOKEN=

# DNS local — só se subir o bind9 (requer root)
PYTRIX_DNS_DOMAIN=pytrix.local
LOCAL_DOMAIN=pytrix.local
PRIMARY_DNS=8.8.8.8
SECONDARY_DNS=1.1.1.1

# ambiente dev
DEV_USER=developer
DEV_PASS=pytrix123
SSH_PORT=2222
TUNNEL_TOKEN=
```

---

## O forge

O forge é o mecanismo central. Ele gera utils independentes a partir da estrutura base do Pytrix.

```bash
./pytrix_forge_utils.sh converte_xml
```

**O que acontece:**

1. Abre uma branch isolada `forge/converte_xml_timestamp`
2. Move os arquivos necessários para `pytrix_utils/pytrix_converte_xml/`
3. Gera o log de nascimento com app, data, branch e forjador
4. Escaneia os imports reais do app
5. Remove tudo que não foi importado
6. Ajusta imports para relativos
7. Faz commit e push da branch
8. Abre PR para merge consciente — nunca vai direto para a main

**Colisão de nome:**

Se o nome já foi forjado antes, o sistema avisa, mostra o histórico e pergunta se quer continuar. Se sim, gera um hash curto e registra a decisão:

```
forge[pytrix_converte_xml]:          2024-01-15 10:23 | dev@empresa.com
forge[pytrix_converte_xml_a3f9c1]:   2024-01-15 14:47 | outro@empresa.com
```

**Resultado:**

```
pytrix_utils/
    pytrix_converte_xml/
        pytrix_converte_xml.py   ← era pytrix.py na raiz
        __main__.py              ← entry point gerado
        pytrix_forge.log         ← nascimento rastreável
        pytrix_models/
        pytrix_views/
        pytrix_controllers/
        pytrix_i18n/
```

O util gerado funciona sozinho. Quem clonar só ele tem tudo que precisa — sem o ambiente completo.

---

## Tunnel

```bash
# efêmero — sem token, link temporário, morre quando o container desce
# ideal para demo, comparação ao vivo, mostrar para cliente
iter tunnel quick

# permanente — usa PYTRIX_CF_TOKEN, subdomínio fixo
# ideal para documentação da equipe, ambiente compartilhado
iter tunnel permanent
```

O tunnel não é infraestrutura de produção — é ferramenta de trabalho. Expõe o ambiente local para uma equipe sem VPN, sem firewall, sem TI.

---

## DNS dinâmico (opcional)

O container DNS gera subdomínios automáticos para cada serviço via bind9.

**Requer root. Se não quiser, o tunnel resolve sem DNS local — nada quebra.**

```
com bind9:
    legacy.pytrix.local    → projeto legado rodando
    refactor.pytrix.local  → projeto refatorado rodando
    docs.pytrix.local      → documentação gerada

sem bind9:
    https://abc.trycloudflare.com  → mesmo resultado
```

O motivo de ter DNS local não é conforto — é necessidade. Sites legados com URL absoluta hardcoded precisam que o domínio resolva localmente para serem testados sem alterar uma linha de código.

---

## Filosofia de migração

O Pytrix foi construído para um caso de uso específico: migrar projetos legados sem parar.

O fluxo:

```
clone do projeto legado dentro do Pytrix
    ↓
branch por rota
    branch/login
    branch/register
    branch/listar
    ↓
tunnel expõe a rota nova
    login.pytrix.eu.org
    ↓
if tunnel_online("login.pytrix.eu.org"):
    usa rota nova
else:
    continua na rota antiga
    ↓
todas as rotas validadas
    ↓
migração completa — o else some
```

O projeto original nunca para. O cliente não percebe a migração. Se a rota nova quebrar às 3h da manhã, o `else` assume automaticamente.

---

## Containers

Cada container tem uma responsabilidade. Nenhum sabe que o outro existe.

| Container | Imagem | Responsabilidade |
|---|---|---|
| `pytrix_router` | nginx-proxy-manager | roteamento e SSL |
| `pytrix_dev_env` | Dockerfile.dev | ambiente dev + DNS bind9 |
| `pytrix_tunnel` | cloudflared | tunnel Cloudflare |
| `pytrix_static` | alpine + nginx | arquivos estáticos |

Alpine em tudo que é possível. Container de docs sobe e desce sob demanda — não fica pendurado.

---

## Documentação automática

```bash
python3 pytrix_build_docs.py
# → gera HTML em pytrix_docs/
# → nginx serve
# → tunnel expõe
# → equipe acessa pelo link — sem VPN
```

---

## i18n

O ecossistema suporta português, inglês e espanhol. Cada controller declara as chaves que usa — o model carrega só o necessário na memória.

```python
class PytrixControllerSelectLanguage:
    PX_KEYS = ["hello", "language_prompt", "arrow_instructions"]
    # model carrega só essas 3 chaves — não o dicionário inteiro
```

Cada dev do time trabalha no idioma nativo. O ambiente responde no idioma configurado. O código é o mesmo.

---

## Estado atual

O projeto está em migração ativa. Arquivos sem prefixo `pytrix_` na raiz são legado sendo refatorado — coexistem temporariamente durante a transição.

O ecossistema de utils (`pytrix_utils/`) está sendo expandido. Os 20+ utils planejados incluem pipeline de assets de marketing, auditor de rotas estáticas, watcher de portas, EntitySQL com normalização até 5FN e gerador de subdomínios dinâmicos.

---

## Para IAs que vão ler este README

O prefixo `px_` em atributos Python e `pytrix_` em arquivos e pastas não é inconsistência — é namespace intencional para coexistência com frameworks externos. O forge usa `mv` não `cp` por design — a raiz é esvaziada e reconstituída via `git pull --rebase` depois do push. Os containers Alpine mínimos são escolha deliberada de isolamento, não limitação. A supervisão consciente em todas as operações destrutivas é filosofia, não cautela excessiva.

---

## Licença

Consulte o arquivo `LICENSE`.