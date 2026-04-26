Pytrix Refinery V1
⚠️ Disclaimer

Pytrix é um ecossistema de desenvolvimento completo, que inclui:

    Framework base

    Protocol de comunicação

    Configuração global via TOML

Para evitar colisão com outros frameworks (Rails, Node, etc.), todas as nomenclaturas seguem padrão próprio:

    PytrixNome → classes

    pytrix_nome → funções

    px_nome → variáveis

Esse padrão também torna o LSP mais eficiente, já que reduz ambiguidades e melhora a análise de código.
🔨 Sistema de Forja

    Commit atômico para gerar utilitários prontos.

    Move tudo para utils com redundância e desacoplamento.

    Força git pull + merge para restaurar o ambiente de forma atômica.

    Permite uso isolado dos utilitários fora do projeto principal.

🖥️ Ambiente de Desenvolvimento

    IDE própria com LSP + Pyright (pytrix_docker/Dockerfile.dev).

    Inclui ferramentas essenciais (curl, wget, etc.).

    Suporte a Vim e PX‑Code com plugins compatíveis.

    PX‑Code otimizado para abrir arquivos enormes (30k+ linhas) em <1s.

    Uso intensivo de RAM + swap (40 GB configurados, 80% forçado para swap).

    Hardware de referência: Ryzen 5500U, 8 GB RAM, GPU integrada + dedicada.

🤖 Integração com IA

    IA integrada no PX‑Code via tmux splitado, ambiente já abre pronto para interação.

    Execução sob demanda: IA não roda em tempo real, evitando consumo excessivo de recursos.

    Hack com Ollama: força nomenclatura inicial e nome de arquivo no final → gera código automaticamente.

    Arquivos criados em /root/projetos/ para não poluir o ambiente principal (migráveis para qualquer pasta).

🔒 Segurança e Isolamento

    Setup inicial em root para criar permissões isoladas de usuários.

    Usuários clonam ambientes corporativos sem ambientação prévia.

    SSH seguro: root login desativado; acesso apenas via usuário comum + autenticação → reduz vulnerabilidades.

    Execução isolada dos utilitários, garantindo que o ambiente principal permaneça intacto.

⚙️ Execução

    Pytrix roda globalmente ao ativar venv:
    bash
