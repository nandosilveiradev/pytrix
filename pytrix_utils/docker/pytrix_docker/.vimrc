" =================================================
" 0. Configurações Globais (Leader Key)
" =================================================
let mapleader = ","          " Sua tecla de atalho agora é a vírgula

" =================================================
" 1. Gerenciamento de Plugins (vim-plug)
" =================================================
call plug#begin('/root/.vim/plugged')

" Inteligência e Autocomplete
Plug 'ycm-core/YouCompleteMe'
Plug 'prabirshrestha/vim-lsp'
Plug 'mattn/vim-lsp-settings'

" Snippets e IA
Plug 'SirVer/ultisnips'
Plug 'honza/vim-snippets'
Plug 'codota/tabnine-vim'

" Interface e Temas
Plug 'morhetz/gruvbox'
Plug 'tomasiser/vim-code-dark'

call plug#end()

" =================================================
" 2. Configurações Gerais e Indentação (PEP 8)
" =================================================
syntax on
filetype plugin indent on    " Essencial para o Pytrix reconhecer Python
set number
set relativenumber           " Ajuda a pular linhas mais rápido (ex: 5j)
set mouse=a
set cursorline
set termguicolors
set encoding=utf-8

" Padrão de 4 espaços (PEP 8)
set tabstop=4
set shiftwidth=4
set expandtab
set autoindent
set smartindent

" =================================================
" 3. Configuração do LSP (Python)
" =================================================
if executable('pylsp')
    au User lsp_setup call lsp#register_server({
        \ 'name': 'pylsp',
        \ 'cmd': {server_info->['pylsp']},
        \ 'allowlist': ['python'],
        \ })
endif

" Configurações do YouCompleteMe (YCM)
let g:ycm_python_interpreter_path = '/root/pytrix/venv/bin/python3'
let g:ycm_python_binary_path = '/root/pytrix/venv/bin/python3'
let g:ycm_confirm_extra_conf = 0
let g:ycm_collect_identifiers_from_tags_files = 1

" =================================================
" 4. Estética (Tema)
" =================================================
set background=dark
" Tenta carregar o gruvbox, se falhar mantém o padrão
silent! colorscheme gruvbox

" =================================================
" 5. Atalhos (Remapeados para não bugar o movimento)
" =================================================

function! s:on_lsp_buffer_enabled() abort
    " nmap <buffer> gd <plug>(lsp-definition)
    " nmap <buffer> K  <plug>(lsp-hover)
    " nmap <buffer> <f2> <plug>(lsp-rename)

    " Alternativa com Leader (Vírgula) se o K falhar na sua mão
    nmap <buffer> <leader>d <plug>(lsp-definition)
    nmap <buffer> K <plug>(lsp-hover)
    nmap <buffer> <leader>r <plug>(lsp-rename)
endfunction

augroup lsp_install
    au!
    autocmd User lsp_buffer_enabled call s:on_lsp_buffer_enabled()
augroup END

" Atalho rápido para salvar
nmap <leader>w :w<cr>