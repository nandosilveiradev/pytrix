I18N = {
    "bloco": "####################################################################################################",
    "hello": {
        "pt": "### Seja bem Vindo!",
        "en": "### Welcome!",
        "es": "### ¡Bienvenido!"
    },
    "language_prompt": {
        "pt": "Selecione o idioma:",
        "en": "Select language:",
        "es": "Seleccione el idioma:"
    },
    "arrow_instructions": {
        "pt": "Use as setas!",
        "en": "Use the arrow keys!",
        "es": "¡Usa las flechas!"
    },
    "language_choices_codes": ["pt", "en", "es"],
    "language_choices_labels": ["Português", "English", "Español"],
    "language_view": {
        "pt": "Idioma",
        "en": "Language",
        "es": "Idioma"

    },
    # -> Nomes dos bancos ############################################################################################
    "postgres": "POSTGRES",
    "mysql": "MYSQL",
    "sqlite": "SQLITE",
    #################################################################################################################
    "ask_mode_intro": {
        "pt": "Selecione o modo de operação. \nEssa escolha define como o programa vai funcionar.",
        "en": "Select the operation mode. \nThis choice defines how the program will work.",
        "es": "Seleccione el modo de operación. \nEsta elección define cómo funcionará el programa."
    },
    "mode_options_labels": {
        "pt": "1) Conectar ao servidor remoto\n2) Conectar ao servidor local\n3) Apenas gerar arquivos localmente sem servidor",
        "en": "1) Connect to the remote server\n2) Connect to the local server\n3) Only generate files locally without server",
        "es": "1) Conectar al servidor remoto\n2) Conectar al servidor local\n3) Solo generar archivos localmente sin servidor"
    },

   "server_questions": {
        "pt": "Informe os dados de conexão ao servidor:",
        "en": "Enter the server connection data:"
    },
    "ask_test_con_remote_host": {
    "pt": "Digite a url do host para conexão remota",
    "en": ""
    },
    "ask_test_con_remote_port": {
        "pt" : "Digite a porta de conexão: ",
        "en" : ""
    },
    "ask_test_con_remote_user": {
        "pt" : "Digite a usuário de conexão: ",
       "en" : ""
    },
    "ask_test_con_remote_password": {
        "pt" : "Digite a usuário de conexão: ",
        "en" : ""
    },
    "ask_test_con_remote_intro": {
        "pt" : "conexão efetuada com sucesso!\n ",
        "en" : ""
    },
    "ask_name_db_choice": {
        "pt" : "[] vazio",
        "en" : "[] void"
    }
    ,"ask_create_name_db": {
        "pt": "Digite o nome do banco de dados.\nO nome não pode ter caractere especial, !@#$%*(), \nacentuação '`~^, e todas as letras devem estar em minúsculas. \nCaso a palavra seja composta, utilize underline para separá-las.",
        "en": "Enter the database name.\nThe name cannot contain special characters, !@#$%*(), \naccentuation '`~^, and all letters must be in lowercase. \nIf the word is compound, use an underscore to separate them."
    },
    "ask_remote_menu": {
        "pt": "Criar Banco de dados.\nListar Banco de dados.\nEntrar no banco de dados.\nSair desse servidor remoto.",
        "en": "Create database.\nList databases.\nEnter a database.\nExit this remote server."
    },
    "ask_db_name": {
        "pt": "Digite o nome do banco de dados: ",
        "en": "Enter the database name: "
    },
    "confirm_db_create": {
        "pt": "O banco foi criado com sucesso: ",
        "en": "The database was created successfully: "
    },
    "error_db_create": {
        "pt": "Houve um erro na tentativa de criar o banco de dados!",
        "en": "An error occurred while trying to create the database!"
    },
    "title_entity_menu": {
        "pt": "Menu | Gerenciador de entidades/tabelas",
        "en": "Menu | Entity/Table Manager"
    },
    "ask_entity_menu": {
        "pt": "Listar entidades/tabelas geradas.\nCriar uma nova entidade/tabela.\nFazer normalização da primeira forma normal (1FN).\nFazer normalização da segunda forma normal (2FN).\nFazer normalização da terceira forma normal (3FN).\nBCNF → refinamento da terceira forma normal (3FN).",
        "en": "List generated entities/tables.\nCreate a new entity/table.\nPerform First Normal Form (1NF).\nPerform Second Normal Form (2NF).\nPerform Third Normal Form (3NF).\nBCNF → refinement of Third Normal Form (3NF)."
    },

    "local_selected": {
        "pt": "Modo local selecionado. Os arquivos serão gerados aqui.",
        "en": "Local mode selected. Files will be generated here."
    },
    "connection_success": {
        "pt": "Conexão estabelecida com sucesso!",
        "en": "Connection established successfully!"
    },
    "connection_failed": {
        "pt": "Falha na conexão com o banco de dados.",
        "en": "Failed to connect to the database."
    },
    "ask_entity_name": {
        "pt": "Digite o nome da entidade (Enter para terminar):",
        "en": "Enter entity name (press Enter to finish):"
    },
    "ask_attribute_name": {
        "pt": "Digite o nome do atributo (Enter para terminar):",
        "en": "Enter attribute name (press Enter to finish):"
    },
    "ask_attribute_type": {
        "pt": "Digite o tipo do atributo:",
        "en": "Enter attribute type:"
    },
    "ask_length_value": {
        "pt": "Digite o tamanho (1 a 255):",
        "en": "Enter length (1 to 255):"
    },
    "ask_precision_value": {
        "pt": "Digite a precisão (ex: 10):",
        "en": "Enter precision (e.g. 10):"
    },
    "ask_scale_value": {
        "pt": "Digite a escala (ex: 2):",
        "en": "Enter scale (e.g. 2):"
    },
    "ask_not_null": {
        "pt": "Esse atributo pode ser NULL? (s/n):",
        "en": "Can this attribute be NULL? (y/n):"
    },
    "ask_unique": {
        "pt": "Esse atributo deve ser UNIQUE? (s/n):",
        "en": "Should this attribute be UNIQUE? (y/n):"
    },
    "ask_primary_key": {
        "pt": "Esse atributo deve ser PRIMARY KEY? (s/n):",
        "en": "Should this attribute be PRIMARY KEY? (y/n):"
    },
    "ask_auto_increment": {
        "pt": "Esse atributo deve ser AUTO INCREMENT? (s/n):",
        "en": "Should this attribute be AUTO INCREMENT? (y/n):"
    },
    "ask_more_entities": {
        "pt": "Deseja criar outra entidade? (s/n):",
        "en": "Do you want to create another entity? (y/n):"
    },
    "invalid_option": {
        "pt": "Opção inválida, tente novamente.",
        "en": "Invalid option, please try again."
    },
    "empty_entity_name": {
        "pt": "O nome da entidade não pode ser vazio.",
        "en": "Entity name cannot be empty."
    },
    "empty_attribute_name": {
        "pt": "O nome do atributo não pode ser vazio.",
        "en": "Attribute name cannot be empty."
    },
    "entity_created": {
        "pt": "Entidade criada com sucesso!",
        "en": "Entity created successfully!"
    },
    "sql_generated": {
        "pt": "Arquivo(s) SQL gerado(s) com sucesso.",
        "en": "SQL file(s) generated successfully."
    },
    "exit_program": {
        "pt": "Encerrando o programa.",
        "en": "Exiting the program."
    },
    "goodbye": {
        "pt": "Obrigado por usar o Entity SQL Terminal!",
        "en": "Thank you for using Entity SQL Terminal!"
    },
    "attribute_list_done": {
        "pt": "Lista de atributos concluída.",
        "en": "Attribute list completed."
    }
}
