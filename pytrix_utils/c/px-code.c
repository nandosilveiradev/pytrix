/*
 * PX-CODE v2.0  —  High-Performance Terminal Editor
 * ─────────────────────────────────────────────────
 * • Vim-plugin ecosystem  (auto-install via .env-px-code)
 * • Static RAM only       (zero malloc, ring/pool buffers)
 * • Double-buffer output  (1 MB write-batch, single flush)
 * • Multi-cursor          (Ctrl+Space / Ctrl+Shift+Space)
 * • Embedded terminal     (forkpty shell, Ctrl+T)
 * • File tree panel       (Ctrl+B)
 * • Syntax highlight      (C/C++, Python, JS/TS)
 * • Undo/Redo ring        (Ctrl+Z / Ctrl+Y, 1024 deep)
 * • Search                (Ctrl+F, live highlight)
 * • No command-mode       (always insert, Ctrl shortcuts)
 *
 * Build:
 *   Linux : gcc px-code.c -o px-code -lutil -O3 -march=native
 *   macOS : gcc px-code.c -o px-code -lutil -O3
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <poll.h>
#include <fcntl.h>
#include <dirent.h>
#include <signal.h>
#include <ctype.h>
#include <errno.h>
#include <pty.h>
#include <time.h>
#include <pwd.h>
#include <stdarg.h>

/* ══════════════════════════════════════════════════════════════
 * COMPILE-TIME CONSTANTS  (all buffers static, zero malloc)
 * ══════════════════════════════════════════════════════════════ */
#define PX_MAX_TABS      10
#define PX_MAX_LINES     8192
#define PX_LINE_LEN      1024
#define PX_MAX_CURSORS   32
#define PX_UNDO_DEPTH    1024
#define PX_MAX_PLUGINS   32
#define PX_PLUGIN_LEN    128
#define PX_TREE_MAX      512
#define PX_TREE_NAME     256
#define PX_SEARCH_LEN    256
#define PX_STATUS_LEN    256
#define PX_WBUF_SIZE     (1 << 20)   /* 1 MB write-batch buffer */
#define PX_TERM_ROWS     200
#define PX_TERM_COLS     512
#define PX_CLIP_SIZE     (PX_LINE_LEN * 32)
#define PX_ENV_FILE      ".env-px-code"
#define PX_PLUGIN_DIR    "/.px-code/plugins"
#define PX_VIM_PACK      "/.vim/pack/px-code/start"

/* ══════════════════════════════════════════════════════════════
 * KEY CODES
 * ══════════════════════════════════════════════════════════════ */
enum PxKey {
    KEY_NULL = 0,
    ARROW_UP = 1000, ARROW_DOWN, ARROW_LEFT, ARROW_RIGHT,
    KEY_HOME, KEY_END, KEY_PGUP, KEY_PGDN, KEY_DEL,
    KEY_F1, KEY_F2, KEY_F3, KEY_F4, KEY_F5,
    KEY_CTRL_TAB,    /* Ctrl+Tab      → next tab        */
    KEY_CTRL_STAB,   /* Shift+Tab     → prev tab        */
    KEY_CTRL_SPACE,  /* Ctrl+Space    → add cursor      */
    KEY_CTRL_SSPACE, /* (reserved)    → remove cursor   */
    KEY_ALT_S,       /* Alt+S         → save+sync       */
    KEY_CTRL_F,      KEY_CTRL_Z, KEY_CTRL_Y,
    KEY_CTRL_D,      KEY_CTRL_K,
    KEY_CTRL_B,      KEY_CTRL_T,
    KEY_CTRL_P,      KEY_CTRL_N,
    KEY_CTRL_W,      KEY_CTRL_G,
    KEY_CTRL_C,      KEY_CTRL_X, KEY_CTRL_V,
};
#define CTRL_KEY(k) ((k) & 0x1f)

/* ══════════════════════════════════════════════════════════════
 * CONFIGURATION
 * ══════════════════════════════════════════════════════════════ */
typedef struct {
    int  tab_size;
    int  auto_indent;
    int  insert_only;
    int  gutter_width;
    int  left_panel_pct;
    int  bottom_panel_pct;
    char c_flags[128];
    char py_interp[64];
    char plugins[PX_MAX_PLUGINS][PX_PLUGIN_LEN];
    int  plugin_count;
} PxConfig;

/* ══════════════════════════════════════════════════════════════
 * UNDO — static ring buffer of line snapshots
 * ══════════════════════════════════════════════════════════════ */
typedef struct {
    char line[PX_LINE_LEN];
    int  line_idx, cx, cy, tab_idx;
} UndoEntry;

typedef struct {
    UndoEntry entries[PX_UNDO_DEPTH];
    int head, cursor, count;
} UndoRing;

/* ══════════════════════════════════════════════════════════════
 * MULTI-CURSOR
 * ══════════════════════════════════════════════════════════════ */
typedef struct { int x, y; } MCursor;

/* ══════════════════════════════════════════════════════════════
 * FILE TREE
 * ══════════════════════════════════════════════════════════════ */
typedef struct {
    char name[PX_TREE_NAME];
    char path[PX_TREE_NAME];
    int  is_dir, depth;
} TreeNode;

/* ══════════════════════════════════════════════════════════════
 * TAB / EDITOR BUFFER
 * ══════════════════════════════════════════════════════════════ */
typedef struct {
    char    name[256];
    char    lines[PX_MAX_LINES][PX_LINE_LEN];
    int     nlines;
    int     cx, cy;
    int     scroll_r, scroll_c;
    MCursor mc[PX_MAX_CURSORS];
    int     mc_count;
    int     active, modified;
    char    clipboard[PX_CLIP_SIZE];
} PxTab;

/* ══════════════════════════════════════════════════════════════
 * TERMINAL PANEL — scrollback display buffer
 * ══════════════════════════════════════════════════════════════ */
typedef struct {
    int   fd;
    pid_t pid;
    char  lines[PX_TERM_ROWS][PX_TERM_COLS];
    int   nlines;           /* total lines received */
    int   visible, focused;
    int   rows, cols;
} PxTerm;

/* ══════════════════════════════════════════════════════════════
 * GLOBAL EDITOR STATE — entirely static, zero malloc
 * ══════════════════════════════════════════════════════════════ */
static struct {
    PxTab       tab[PX_MAX_TABS];
    int         cur;
    PxConfig    cfg;
    UndoRing    undo;
    PxTerm      term;
    struct termios orig_tios;
    int         rows, cols;
    /* File tree */
    int         tree_visible;
    TreeNode    tree[PX_TREE_MAX];
    int         tree_count, tree_sel;
    char        tree_root[256];
    /* Search */
    char        search[PX_SEARCH_LEN];
    int         search_on;
    /* Output write-batch buffer */
    char        wbuf[PX_WBUF_SIZE];
    int         wpos;
    /* Status bar */
    char        status[PX_STATUS_LEN];
    time_t      status_exp;
    /* Home dir */
    char        home[256];
    /* Resize flag */
    volatile int resized;
} E;

/* ══════════════════════════════════════════════════════════════
 * WRITE-BATCH BUFFER
 * Single 1MB buffer — one write() per frame, not per character
 * ══════════════════════════════════════════════════════════════ */
static inline void wb_putc(char c) {
    if (E.wpos < PX_WBUF_SIZE - 1) E.wbuf[E.wpos++] = c;
}
static void wb_puts(const char *s) {
    while (*s) wb_putc(*s++);
}
static void wb_printf(const char *fmt, ...) {
    char tmp[512];
    va_list ap;
    va_start(ap, fmt);
    int n = vsnprintf(tmp, sizeof(tmp), fmt, ap);
    va_end(ap);
    for (int i = 0; i < n && E.wpos < PX_WBUF_SIZE - 1; i++)
        E.wbuf[E.wpos++] = tmp[i];
}
static void wb_flush(void) {
    if (E.wpos > 0) {
        write(STDOUT_FILENO, E.wbuf, E.wpos);
        E.wpos = 0;
    }
}

/* ══════════════════════════════════════════════════════════════
 * CONFIG PARSER  (.env-px-code)
 * ══════════════════════════════════════════════════════════════ */
static void cfg_defaults(void) {
    E.cfg.tab_size        = 4;
    E.cfg.auto_indent     = 1;
    E.cfg.insert_only     = 1;
    E.cfg.gutter_width    = 5;
    E.cfg.left_panel_pct  = 15;
    E.cfg.bottom_panel_pct= 20;
    strcpy(E.cfg.c_flags,  "-Wall -Wextra -O3");
    strcpy(E.cfg.py_interp,"python3");
}

static void cfg_trim(char *s) {
    char *p = s;
    while (isspace((unsigned char)*p) || *p == '"' || *p == '\'') p++;
    memmove(s, p, strlen(p) + 1);
    int n = strlen(s);
    while (n > 0 && (isspace((unsigned char)s[n-1]) || s[n-1] == '"' || s[n-1] == '\''))
        s[--n] = 0;
}

static void cfg_load(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) {
        /* Try home dir */
        char hp[512];
        snprintf(hp, sizeof(hp), "%s/%s", E.home, path);
        f = fopen(hp, "r");
        if (!f) return;
    }
    char line[512];
    while (fgets(line, sizeof(line), f)) {
        if (line[0] == '#' || line[0] == '\n') continue;
        char *eq = strchr(line, '=');
        if (!eq) continue;
        *eq = 0;
        char *key = line, *val = eq + 1;
        val[strcspn(val, "\n\r")] = 0;
        cfg_trim(key); cfg_trim(val);

        if      (!strcmp(key,"TAB_SIZE"))          E.cfg.tab_size         = atoi(val);
        else if (!strcmp(key,"AUTO_INDENT"))        E.cfg.auto_indent      = atoi(val);
        else if (!strcmp(key,"INSERT_ONLY_MODE"))   E.cfg.insert_only      = atoi(val);
        else if (!strcmp(key,"GUTTER_WIDTH"))       E.cfg.gutter_width     = atoi(val);
        else if (!strcmp(key,"LEFT_PANEL_SIZE"))    E.cfg.left_panel_pct   = atoi(val);
        else if (!strcmp(key,"BOTTOM_PANEL_SIZE"))  E.cfg.bottom_panel_pct = atoi(val);
        else if (!strcmp(key,"C_FLAGS"))            strncpy(E.cfg.c_flags,  val, 127);
        else if (!strcmp(key,"PY_INTERPRETER"))     strncpy(E.cfg.py_interp,val, 63);
        else if (!strcmp(key,"PLUGINS")) {
            char tmp[1024];
            strncpy(tmp, val, sizeof(tmp)-1);
            char *tok = strtok(tmp, ",");
            while (tok && E.cfg.plugin_count < PX_MAX_PLUGINS) {
                cfg_trim(tok);
                if (*tok) strncpy(E.cfg.plugins[E.cfg.plugin_count++], tok, PX_PLUGIN_LEN-1);
                tok = strtok(NULL, ",");
            }
        }
    }
    fclose(f);
}

/* ══════════════════════════════════════════════════════════════
 * PLUGIN MANAGER
 * Reads PLUGINS= from .env-px-code
 * Clones to ~/.px-code/plugins/ AND symlinks to ~/.vim/pack/
 * so both px-code AND vim share the same plugin tree.
 * ══════════════════════════════════════════════════════════════ */
static void plugin_install_all(void) {
    if (E.cfg.plugin_count == 0) return;

    char px_dir[512], vim_dir[512];
    snprintf(px_dir,  sizeof(px_dir),  "%s%s", E.home, PX_PLUGIN_DIR);
    snprintf(vim_dir, sizeof(vim_dir), "%s%s", E.home, PX_VIM_PACK);

    char cmd[1024];
    snprintf(cmd, sizeof(cmd), "mkdir -p '%s' '%s' 2>/dev/null", px_dir, vim_dir);
    system(cmd);

    for (int i = 0; i < E.cfg.plugin_count; i++) {
        const char *plug = E.cfg.plugins[i];
        const char *slash = strrchr(plug, '/');
        const char *name  = slash ? slash + 1 : plug;

        char dest[512];
        snprintf(dest, sizeof(dest), "%s/%s", px_dir, name);

        struct stat st;
        if (stat(dest, &st) != 0) {
            /* Not installed — git clone (shallow, fast) */
            snprintf(E.status, PX_STATUS_LEN, "Installing plugin: %s ...", name);
            wb_printf("\033[%d;1H\033[48;5;22m\033[97m  %s\033[K\033[m", E.rows, E.status);
            wb_flush();
            snprintf(cmd, sizeof(cmd),
                "git clone --depth=1 'https://github.com/%s' '%s' >/dev/null 2>&1",
                plug, dest);
            system(cmd);
        }

        /* Symlink into vim pack dir for native vim compatibility */
        char vdest[512];
        snprintf(vdest, sizeof(vdest), "%s/%s", vim_dir, name);
        if (stat(vdest, &st) != 0) {
            snprintf(cmd, sizeof(cmd), "ln -sf '%s' '%s' 2>/dev/null", dest, vdest);
            system(cmd);
        }
    }
    snprintf(E.status, PX_STATUS_LEN, "Plugins ready. (%d installed)", E.cfg.plugin_count);
    E.status_exp = time(NULL) + 4;
}

/* ══════════════════════════════════════════════════════════════
 * TTY SETUP
 * ══════════════════════════════════════════════════════════════ */
static void tty_raw(void) {
    tcgetattr(STDIN_FILENO, &E.orig_tios);
    struct termios raw = E.orig_tios;
    raw.c_iflag &= ~(BRKINT | ICRNL | INPCK | ISTRIP | IXON);
    raw.c_oflag &= ~OPOST;
    raw.c_cflag |=  CS8;
    raw.c_lflag &= ~(ECHO | ICANON | IEXTEN | ISIG);
    raw.c_cc[VMIN]  = 0;
    raw.c_cc[VTIME] = 1;
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw);
}

static void tty_restore(void) {
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &E.orig_tios);
}

static void update_size(void) {
    struct winsize ws;
    ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws);
    E.rows = ws.ws_row ? ws.ws_row : 24;
    E.cols = ws.ws_col ? ws.ws_col : 80;
}

/* ══════════════════════════════════════════════════════════════
 * KEY READER
 * Handles multi-byte escape sequences, Alt+key, Ctrl+key
 * ══════════════════════════════════════════════════════════════ */
static int read_key(void) {
    char c;
    int n;
    while ((n = read(STDIN_FILENO, &c, 1)) == 0) {}
    if (n < 0) return KEY_NULL;

    if (c == '\033') {
        char seq[8] = {0};
        struct pollfd pfd = { STDIN_FILENO, POLLIN, 0 };
        if (poll(&pfd, 1, 50) <= 0) return '\033';

        if (read(STDIN_FILENO, &seq[0], 1) <= 0) return '\033';

        if (seq[0] == '[') {
            if (read(STDIN_FILENO, &seq[1], 1) <= 0) return '\033';
            if (seq[1] >= '0' && seq[1] <= '9') {
                if (read(STDIN_FILENO, &seq[2], 1) <= 0) return '\033';
                if (seq[2] == '~') {
                    switch (seq[1]) {
                        case '1': case '7': return KEY_HOME;
                        case '4': case '8': return KEY_END;
                        case '5': return KEY_PGUP;
                        case '6': return KEY_PGDN;
                        case '3': return KEY_DEL;
                    }
                }
                /* Ctrl+Tab: \033[I or similar depending on terminal */
            }
            switch (seq[1]) {
                case 'A': return ARROW_UP;
                case 'B': return ARROW_DOWN;
                case 'C': return ARROW_RIGHT;
                case 'D': return ARROW_LEFT;
                case 'H': return KEY_HOME;
                case 'F': return KEY_END;
                case 'Z': return KEY_CTRL_STAB;  /* Shift+Tab */
                case 'I': return KEY_CTRL_TAB;   /* Ctrl+Tab (some terms) */
            }
        } else if (seq[0] == 'O') {
            if (read(STDIN_FILENO, &seq[1], 1) <= 0) return '\033';
            switch (seq[1]) {
                case 'H': return KEY_HOME;
                case 'F': return KEY_END;
                case 'P': return KEY_F1;
                case 'Q': return KEY_F2;
                case 'R': return KEY_F3;
                case 'S': return KEY_F4;
            }
        }
        /* Alt+letter sequences */
        switch (seq[0]) {
            case 's': case 'S': return KEY_ALT_S;
        }
        return '\033';
    }

    /* Ctrl+letter mappings */
    switch ((unsigned char)c) {
        case 9:   return '\t';
        case 13:  return '\r';
        case 127: return 127;
        case CTRL_KEY('z'): return KEY_CTRL_Z;
        case CTRL_KEY('y'): return KEY_CTRL_Y;
        case CTRL_KEY('f'): return KEY_CTRL_F;
        case CTRL_KEY('b'): return KEY_CTRL_B;
        case CTRL_KEY('n'): return KEY_CTRL_N;
        case CTRL_KEY('w'): return KEY_CTRL_W;
        case CTRL_KEY('k'): return KEY_CTRL_K;
        case CTRL_KEY('d'): return KEY_CTRL_D;
        case CTRL_KEY('g'): return KEY_CTRL_G;
        case CTRL_KEY('p'): return KEY_CTRL_P;
        case CTRL_KEY('c'): return KEY_CTRL_C;
        case CTRL_KEY('x'): return KEY_CTRL_X;
        case CTRL_KEY('v'): return KEY_CTRL_V;
        case CTRL_KEY('t'): return KEY_CTRL_T;
        case CTRL_KEY(' '): return KEY_CTRL_SPACE;
        case CTRL_KEY('s'): return KEY_ALT_S;   /* also Ctrl+S */
        case CTRL_KEY('a'): return KEY_HOME;    /* Ctrl+A → line start */
        case CTRL_KEY('e'): return KEY_END;     /* Ctrl+E → line end   */
        case CTRL_KEY('u'): return KEY_CTRL_Z;  /* Ctrl+U → undo (vim) */
        case CTRL_KEY('r'): return KEY_CTRL_Y;  /* Ctrl+R → redo (vim) */
    }
    return (unsigned char)c;
}

/* ══════════════════════════════════════════════════════════════
 * UNDO RING
 * ══════════════════════════════════════════════════════════════ */
static void undo_push(void) {
    PxTab *t = &E.tab[E.cur];
    UndoEntry *e = &E.undo.entries[E.undo.head % PX_UNDO_DEPTH];
    strncpy(e->line, t->lines[t->cy], PX_LINE_LEN - 1);
    e->line_idx = t->cy;
    e->cx       = t->cx;
    e->cy       = t->cy;
    e->tab_idx  = E.cur;
    E.undo.head   = (E.undo.head + 1) % PX_UNDO_DEPTH;
    if (E.undo.count < PX_UNDO_DEPTH) E.undo.count++;
    E.undo.cursor = E.undo.head;
}

static void undo_do(void) {
    if (E.undo.count == 0) return;
    E.undo.cursor = (E.undo.cursor - 1 + PX_UNDO_DEPTH) % PX_UNDO_DEPTH;
    UndoEntry *e  = &E.undo.entries[E.undo.cursor];
    PxTab     *t  = &E.tab[e->tab_idx];
    strncpy(t->lines[e->line_idx], e->line, PX_LINE_LEN - 1);
    t->cx = e->cx; t->cy = e->cy;
    E.cur = e->tab_idx;
    E.undo.count--;
}

static void redo_do(void) {
    if (E.undo.cursor == E.undo.head) return;
    UndoEntry *e = &E.undo.entries[E.undo.cursor];
    E.undo.cursor = (E.undo.cursor + 1) % PX_UNDO_DEPTH;
    PxTab *t = &E.tab[e->tab_idx];
    t->cx = e->cx; t->cy = e->cy;
    E.cur = e->tab_idx;
}

/* ══════════════════════════════════════════════════════════════
 * FILE OPERATIONS
 * ══════════════════════════════════════════════════════════════ */
static int find_free_tab(void) {
    for (int i = 0; i < PX_MAX_TABS; i++)
        if (!E.tab[i].active) return i;
    return -1;
}

static void tab_init(int i, const char *name) {
    PxTab *t = &E.tab[i];
    memset(t, 0, sizeof(PxTab));
    strncpy(t->name, name, 255);
    t->nlines = 1;
    t->active = 1;
}

static void load_file(int idx, const char *path) {
    tab_init(idx, path);
    FILE *f = fopen(path, "r");
    if (!f) return;
    PxTab *t = &E.tab[idx];
    t->nlines = 0;
    while (t->nlines < PX_MAX_LINES &&
           fgets(t->lines[t->nlines], PX_LINE_LEN, f)) {
        t->lines[t->nlines][strcspn(t->lines[t->nlines], "\n\r")] = 0;
        t->nlines++;
    }
    if (t->nlines == 0) t->nlines = 1;
    fclose(f);
}

static void save_file(int idx) {
    PxTab *t = &E.tab[idx];
    if (!t->active) return;
    const char *path = t->name;
    if (path[0] == '[') {
        /* Auto-name unnamed buffer */
        static int unnamed_cnt = 0;
        char np[256];
        snprintf(np, sizeof(np), "unnamed_%d.txt", ++unnamed_cnt);
        strncpy(t->name, np, 255);
        path = t->name;
    }
    FILE *f = fopen(path, "w");
    if (!f) {
        snprintf(E.status, PX_STATUS_LEN, "Save error: %s", strerror(errno));
        E.status_exp = time(NULL) + 4;
        return;
    }
    for (int i = 0; i < t->nlines; i++)
        fprintf(f, "%s\n", t->lines[i]);
    fclose(f);
    t->modified = 0;
    snprintf(E.status, PX_STATUS_LEN, "Saved  %s", path);
    E.status_exp = time(NULL) + 3;
}

static void open_tab(const char *path) {
    for (int i = 0; i < PX_MAX_TABS; i++)
        if (E.tab[i].active && !strcmp(E.tab[i].name, path)) { E.cur = i; return; }
    int idx = find_free_tab();
    if (idx < 0) idx = 0;
    load_file(idx, path);
    E.cur = idx;
}

/* ══════════════════════════════════════════════════════════════
 * FILE TREE
 * ══════════════════════════════════════════════════════════════ */
static void tree_load(const char *root) {
    E.tree_count = 0;
    strncpy(E.tree_root, root, 255);
    DIR *d = opendir(root);
    if (!d) return;
    struct dirent *de;
    while ((de = readdir(d)) && E.tree_count < PX_TREE_MAX) {
        if (de->d_name[0] == '.') continue;
        TreeNode *n = &E.tree[E.tree_count++];
        strncpy(n->name, de->d_name, PX_TREE_NAME - 1);
        snprintf(n->path, PX_TREE_NAME, "%s/%s", root, de->d_name);
        n->is_dir = (de->d_type == DT_DIR);
        n->depth  = 0;
    }
    closedir(d);
    /* Sort: dirs first, then alphabetical */
    for (int i = 0; i < E.tree_count - 1; i++)
        for (int j = i + 1; j < E.tree_count; j++) {
            int swap = (E.tree[j].is_dir > E.tree[i].is_dir) ||
                       (E.tree[j].is_dir == E.tree[i].is_dir &&
                        strcmp(E.tree[j].name, E.tree[i].name) < 0);
            if (swap) { TreeNode tmp=E.tree[i]; E.tree[i]=E.tree[j]; E.tree[j]=tmp; }
        }
}

static void tree_open_sel(void) {
    if (E.tree_sel < 0 || E.tree_sel >= E.tree_count) return;
    TreeNode *n = &E.tree[E.tree_sel];
    if (n->is_dir) {
        tree_load(n->path);
        E.tree_sel = 0;
    } else {
        open_tab(n->path);
        E.tree_visible = 0;  /* auto-focus editor */
    }
}

/* ══════════════════════════════════════════════════════════════
 * TERMINAL PANEL  (forkpty embedded shell)
 * ══════════════════════════════════════════════════════════════ */

/* Strip VT100 escape sequences for our scrollback display */
static void strip_vt100(const char *in, char *out, int maxlen) {
    int j = 0;
    while (*in && j < maxlen - 1) {
        if (*in == '\033') {
            in++;
            if (*in == '[') {
                in++;
                while (*in && (*in < 0x40 || *in > 0x7e)) in++;
                if (*in) in++;
            } else if (*in == '(' || *in == ')') {
                in++;
                if (*in) in++;
            } else if (*in) in++;
            continue;
        }
        if ((unsigned char)*in >= 32 || *in == '\n' || *in == '\r' || *in == '\t')
            out[j++] = *in;
        in++;
    }
    out[j] = 0;
}

static void tpanel_open(void) {
    if (E.term.pid > 0) {
        E.term.visible = 1;
        E.term.focused = 1;
        return;
    }
    E.term.rows = (E.rows * E.cfg.bottom_panel_pct) / 100;
    if (E.term.rows < 3) E.term.rows = 3;
    E.term.cols = E.cols;

    struct winsize ws = { (unsigned short)E.term.rows,
                          (unsigned short)E.term.cols, 0, 0 };
    E.term.pid = forkpty(&E.term.fd, NULL, NULL, &ws);

    if (E.term.pid == 0) {
        /* Child: restore terminal and exec shell */
        const char *shell = getenv("SHELL");
        if (!shell) shell = "/bin/bash";
        setenv("TERM", "xterm-256color", 1);
        execlp(shell, shell, NULL);
        _exit(1);
    }
    fcntl(E.term.fd, F_SETFL, fcntl(E.term.fd, F_GETFL) | O_NONBLOCK);
    E.term.visible = 1;
    E.term.focused = 1;
    memset(E.term.lines, 0, sizeof(E.term.lines));
    E.term.nlines  = 1;
}

static void tpanel_close(void) {
    E.term.focused = 0;
    E.term.visible = 0;
}

static void tpanel_send(const char *data, int len) {
    if (E.term.fd > 0) write(E.term.fd, data, len);
}

/* Read output from pty and append to scrollback */
static void tpanel_poll(void) {
    if (E.term.fd <= 0) return;
    char raw[4096];
    int n = read(E.term.fd, raw, sizeof(raw) - 1);
    if (n <= 0) return;
    raw[n] = 0;

    char clean[4096];
    strip_vt100(raw, clean, sizeof(clean));

    /* Append to scrollback lines */
    char *p = clean;
    while (*p) {
        if (*p == '\n' || *p == '\r') {
            if (E.term.nlines < PX_TERM_ROWS - 1) E.term.nlines++;
            else {
                /* Scroll up: shift all lines */
                memmove(E.term.lines[0], E.term.lines[1],
                        sizeof(E.term.lines[0]) * (PX_TERM_ROWS - 1));
                E.term.lines[PX_TERM_ROWS - 1][0] = 0;
            }
            p++;
        } else {
            int cur = E.term.nlines - 1;
            int len = strlen(E.term.lines[cur]);
            if (len < PX_TERM_COLS - 2)
                E.term.lines[cur][len] = *p;
            p++;
        }
    }
}

/* ══════════════════════════════════════════════════════════════
 * SYNTAX HIGHLIGHTING
 * ══════════════════════════════════════════════════════════════ */
typedef enum { LANG_NONE=0, LANG_C, LANG_PY, LANG_JS } Lang;

static const char *kw_c1[] = {
    "if","else","while","for","do","switch","case","default","break","continue",
    "return","struct","enum","union","typedef","sizeof","void","int","char",
    "float","double","long","short","unsigned","signed","static","const",
    "extern","volatile","register","inline","auto","goto","restrict",NULL
};
static const char *kw_c2[] = {
    "NULL","true","false","TRUE","FALSE","uint8_t","uint16_t","uint32_t",
    "uint64_t","int8_t","int16_t","int32_t","int64_t","size_t","ssize_t",
    "FILE","EOF","stdin","stdout","stderr","STDIN_FILENO","STDOUT_FILENO",NULL
};
static const char *kw_py1[] = {
    "if","elif","else","while","for","in","not","and","or","is","def","class",
    "return","import","from","as","with","try","except","finally","raise",
    "pass","break","continue","lambda","yield","async","await","del",
    "global","nonlocal",NULL
};
static const char *kw_py2[] = {
    "True","False","None","self","cls","print","len","range","type",
    "int","str","float","list","dict","set","tuple","bool","open",NULL
};
static const char *kw_js1[] = {
    "if","else","while","for","do","switch","case","default","break","continue",
    "return","function","class","const","let","var","new","delete","typeof",
    "instanceof","in","of","try","catch","finally","throw","async","await",
    "import","export","from","extends","super","static",NULL
};
static const char *kw_js2[] = {
    "true","false","null","undefined","this","console","window","document",
    "Promise","Array","Object","String","Number","Boolean","JSON",NULL
};

static Lang detect_lang(const char *name) {
    const char *e = strrchr(name, '.');
    if (!e) return LANG_NONE;
    if (!strcmp(e,".c")||!strcmp(e,".h")||!strcmp(e,".cpp")||
        !strcmp(e,".cc")||!strcmp(e,".cxx")) return LANG_C;
    if (!strcmp(e,".py")) return LANG_PY;
    if (!strcmp(e,".js")||!strcmp(e,".ts")||
        !strcmp(e,".jsx")||!strcmp(e,".tsx")) return LANG_JS;
    return LANG_NONE;
}

/* Fill attr[0..len] with ANSI fg color per character (0 = default) */
static void syntax_hl(const char *line, int len, int *attr, Lang lang) {
    if (lang == LANG_NONE || len == 0) return;
    const char **kw1 = (lang==LANG_PY)?kw_py1:(lang==LANG_JS)?kw_js1:kw_c1;
    const char **kw2 = (lang==LANG_PY)?kw_py2:(lang==LANG_JS)?kw_js2:kw_c2;
    int in_str = 0;
    char str_ch = 0;
    int i = 0;

    while (i < len) {
        /* Line comment */
        if (!in_str) {
            if (lang == LANG_C && line[i]=='/' && i+1<len && line[i+1]=='/') {
                for (int j=i;j<len;j++) attr[j]=90; break;
            }
            if ((lang==LANG_PY||lang==LANG_JS) && line[i]=='#') {
                for (int j=i;j<len;j++) attr[j]=90; break;
            }
            /* Preprocessor */
            if (lang==LANG_C && i==0 && line[0]=='#') {
                for (int j=0;j<len;j++) attr[j]=35; break;
            }
        }
        /* String */
        if (!in_str && (line[i]=='"' || line[i]=='\'')) {
            in_str=1; str_ch=line[i]; attr[i++]=32; continue;
        }
        if (in_str) {
            attr[i]=32;
            if (line[i]=='\\' && i+1<len) { attr[i+1]=32; i+=2; continue; }
            if (line[i]==str_ch) { i++; in_str=0; } else i++;
            continue;
        }
        /* Number */
        if (isdigit((unsigned char)line[i]) &&
            (i==0 || !isalnum((unsigned char)line[i-1]))) {
            while (i<len && (isalnum((unsigned char)line[i])||line[i]=='.'))
                attr[i++]=33;
            continue;
        }
        /* Word / keyword */
        if (isalpha((unsigned char)line[i]) || line[i]=='_') {
            int s=i;
            while (i<len && (isalnum((unsigned char)line[i])||line[i]=='_')) i++;
            int wl=i-s;
            if (wl < 64) {
                char w[64]; memcpy(w, line+s, wl); w[wl]=0;
                int matched=0;
                for (int k=0;kw1[k];k++) if (!strcmp(w,kw1[k])) {
                    for(int j=s;j<i;j++) attr[j]=34; matched=1; break;
                }
                if (!matched) for (int k=0;kw2[k];k++) if (!strcmp(w,kw2[k])) {
                    for(int j=s;j<i;j++) attr[j]=36; matched=1; break;
                }
                /* Function call */
                if (!matched && i<len && line[i]=='(')
                    for(int j=s;j<i;j++) attr[j]=33;
            }
            continue;
        }
        i++;
    }
}

/* ══════════════════════════════════════════════════════════════
 * EDITOR OPERATIONS
 * ══════════════════════════════════════════════════════════════ */
static void ed_clamp_cursor(PxTab *t) {
    if (t->cy < 0) t->cy = 0;
    if (t->cy >= t->nlines) t->cy = t->nlines - 1;
    int ll = (int)strlen(t->lines[t->cy]);
    if (t->cx < 0) t->cx = 0;
    if (t->cx > ll) t->cx = ll;
}

static void ed_insert(char c) {
    PxTab *t = &E.tab[E.cur];
    undo_push();
    int len = (int)strlen(t->lines[t->cy]);
    if (len >= PX_LINE_LEN - 2) return;
    memmove(t->lines[t->cy]+t->cx+1, t->lines[t->cy]+t->cx, len-t->cx+1);
    t->lines[t->cy][t->cx++] = c;
    t->modified = 1;
    /* Replicate on extra cursors */
    for (int i=0;i<t->mc_count;i++) {
        MCursor *mc = &t->mc[i];
        int ml = (int)strlen(t->lines[mc->y]);
        if (ml < PX_LINE_LEN - 2) {
            memmove(t->lines[mc->y]+mc->x+1, t->lines[mc->y]+mc->x, ml-mc->x+1);
            t->lines[mc->y][mc->x++] = c;
        }
    }
}

static void ed_tab(void) {
    for (int i=0;i<E.cfg.tab_size;i++) ed_insert(' ');
}

static void ed_newline(void) {
    PxTab *t = &E.tab[E.cur];
    if (t->nlines >= PX_MAX_LINES) return;
    undo_push();
    for (int i=t->nlines;i>t->cy+1;i--)
        memcpy(t->lines[i], t->lines[i-1], PX_LINE_LEN);
    char *tail = t->lines[t->cy]+t->cx;
    strncpy(t->lines[t->cy+1], tail, PX_LINE_LEN-1);
    *tail = 0;
    t->nlines++;
    /* Auto-indent */
    int indent = 0;
    if (E.cfg.auto_indent) {
        char *p = t->lines[t->cy];
        while ((*p==' '||*p=='\t') && indent<PX_LINE_LEN-2) { indent++; p++; }
        /* Extra indent after { */
        int prev_len = (int)strlen(t->lines[t->cy]);
        if (prev_len > 0 && t->lines[t->cy][prev_len-1] == '{')
            indent += E.cfg.tab_size;
        char tmp[PX_LINE_LEN];
        strncpy(tmp, t->lines[t->cy+1], PX_LINE_LEN-1);
        memset(t->lines[t->cy+1], ' ', indent);
        strncpy(t->lines[t->cy+1]+indent, tmp, PX_LINE_LEN-1-indent);
        t->cx = indent;
    } else {
        t->cx = 0;
    }
    t->cy++;
    t->modified = 1;
}

static void ed_backspace(void) {
    PxTab *t = &E.tab[E.cur];
    undo_push();
    if (t->cx > 0) {
        int len = (int)strlen(t->lines[t->cy]);
        memmove(t->lines[t->cy]+t->cx-1, t->lines[t->cy]+t->cx, len-t->cx+1);
        t->cx--;
        t->modified = 1;
    } else if (t->cy > 0) {
        int pl = (int)strlen(t->lines[t->cy-1]);
        int cl = (int)strlen(t->lines[t->cy]);
        if (pl+cl < PX_LINE_LEN-1) strcat(t->lines[t->cy-1], t->lines[t->cy]);
        for (int i=t->cy;i<t->nlines-1;i++) memcpy(t->lines[i],t->lines[i+1],PX_LINE_LEN);
        t->lines[t->nlines-1][0] = 0;
        t->nlines--;
        t->cy--;
        t->cx = pl;
        t->modified = 1;
    }
}

static void ed_del_forward(void) {
    PxTab *t = &E.tab[E.cur];
    int len = (int)strlen(t->lines[t->cy]);
    if (t->cx < len) {
        undo_push();
        memmove(t->lines[t->cy]+t->cx, t->lines[t->cy]+t->cx+1, len-t->cx);
        t->modified = 1;
    } else if (t->cy < t->nlines-1) {
        undo_push();
        if (len+(int)strlen(t->lines[t->cy+1]) < PX_LINE_LEN-1)
            strcat(t->lines[t->cy], t->lines[t->cy+1]);
        for (int i=t->cy+1;i<t->nlines-1;i++) memcpy(t->lines[i],t->lines[i+1],PX_LINE_LEN);
        t->nlines--;
        t->modified = 1;
    }
}

static void ed_del_line(void) {
    PxTab *t = &E.tab[E.cur];
    undo_push();
    strncpy(t->clipboard, t->lines[t->cy], PX_LINE_LEN);
    if (t->nlines > 1) {
        for (int i=t->cy;i<t->nlines-1;i++) memcpy(t->lines[i],t->lines[i+1],PX_LINE_LEN);
        t->lines[t->nlines-1][0]=0;
        t->nlines--;
        if (t->cy >= t->nlines) t->cy = t->nlines-1;
    } else {
        t->lines[0][0]=0;
    }
    t->cx=0; t->modified=1;
    snprintf(E.status, PX_STATUS_LEN, "Line deleted (paste with Ctrl+V)");
    E.status_exp = time(NULL)+2;
}

static void ed_dup_line(void) {
    PxTab *t = &E.tab[E.cur];
    if (t->nlines >= PX_MAX_LINES) return;
    for (int i=t->nlines;i>t->cy+1;i--) memcpy(t->lines[i],t->lines[i-1],PX_LINE_LEN);
    strncpy(t->lines[t->cy+1], t->lines[t->cy], PX_LINE_LEN-1);
    t->nlines++; t->cy++; t->modified=1;
}

static void ed_copy(void) {
    PxTab *t = &E.tab[E.cur];
    strncpy(t->clipboard, t->lines[t->cy], PX_LINE_LEN);
    snprintf(E.status, PX_STATUS_LEN, "Copied L%d", t->cy+1);
    E.status_exp = time(NULL)+2;
}

static void ed_paste(void) {
    PxTab *t = &E.tab[E.cur];
    if (!t->clipboard[0]) return;
    if (t->nlines >= PX_MAX_LINES) return;
    undo_push();
    for (int i=t->nlines;i>t->cy+1;i--) memcpy(t->lines[i],t->lines[i-1],PX_LINE_LEN);
    strncpy(t->lines[t->cy+1], t->clipboard, PX_LINE_LEN-1);
    t->nlines++; t->cy++; t->cx=0; t->modified=1;
}

static void ed_search_next(void) {
    PxTab *t = &E.tab[E.cur];
    if (!E.search[0]) return;
    for (int i=t->cy+1; i<t->nlines; i++) {
        char *found = strstr(t->lines[i], E.search);
        if (found) {
            t->cy = i;
            t->cx = found - t->lines[i];
            snprintf(E.status, PX_STATUS_LEN, "Found '%s' at L%d", E.search, i+1);
            E.status_exp = time(NULL)+3;
            return;
        }
    }
    /* Wrap */
    for (int i=0; i<=t->cy; i++) {
        char *found = strstr(t->lines[i], E.search);
        if (found) {
            t->cy = i;
            t->cx = found - t->lines[i];
            snprintf(E.status, PX_STATUS_LEN, "Wrapped → '%s' at L%d", E.search, i+1);
            E.status_exp = time(NULL)+3;
            return;
        }
    }
    snprintf(E.status, PX_STATUS_LEN, "Not found: '%s'", E.search);
    E.status_exp = time(NULL)+3;
}

static void ed_move(int key) {
    PxTab *t = &E.tab[E.cur];
    int ll;
    switch (key) {
        case ARROW_LEFT:
            if (t->cx>0) t->cx--;
            else if (t->cy>0) { t->cy--; t->cx=(int)strlen(t->lines[t->cy]); }
            break;
        case ARROW_RIGHT:
            ll=(int)strlen(t->lines[t->cy]);
            if (t->cx<ll) t->cx++;
            else if (t->cy<t->nlines-1) { t->cy++; t->cx=0; }
            break;
        case ARROW_UP:
            if (t->cy>0) {
                t->cy--;
                ll=(int)strlen(t->lines[t->cy]);
                if (t->cx>ll) t->cx=ll;
            }
            break;
        case ARROW_DOWN:
            if (t->cy<t->nlines-1) {
                t->cy++;
                ll=(int)strlen(t->lines[t->cy]);
                if (t->cx>ll) t->cx=ll;
            }
            break;
        case KEY_HOME: t->cx=0; break;
        case KEY_END:  t->cx=(int)strlen(t->lines[t->cy]); break;
        case KEY_PGUP: t->cy=(t->cy>20)?t->cy-20:0; ed_clamp_cursor(t); break;
        case KEY_PGDN: t->cy=(t->cy+20<t->nlines)?t->cy+20:t->nlines-1; ed_clamp_cursor(t); break;
    }
}

/* ══════════════════════════════════════════════════════════════
 * SEARCH PROMPT
 * ══════════════════════════════════════════════════════════════ */
static void prompt_search(void) {
    E.search[0] = 0;
    E.search_on = 1;
    for (;;) {
        wb_printf("\033[%d;1H\033[48;5;22m\033[97m  Search: %s_\033[K\033[m", E.rows, E.search);
        wb_flush();
        int k = read_key();
        if (k == '\r') { ed_search_next(); break; }
        if (k == '\033') { E.search[0]=0; E.search_on=0; break; }
        if (k==127 || k==KEY_CTRL_Z) {
            int n=(int)strlen(E.search);
            if (n>0) E.search[n-1]=0;
        } else if (k>=32 && k<127 && (int)strlen(E.search)<PX_SEARCH_LEN-1) {
            int n=(int)strlen(E.search);
            E.search[n]=(char)k; E.search[n+1]=0;
            ed_search_next();
        }
    }
}

/* ══════════════════════════════════════════════════════════════
 * RENDERER  — write-batch, single flush per frame
 * ══════════════════════════════════════════════════════════════ */
static void render_tabbar(int tree_w) {
    wb_puts("\033[1;1H\033[48;5;234m\033[K");
    /* Spacer for tree */
    for (int i=0;i<tree_w;i++) wb_putc(' ');
    for (int i=0;i<PX_MAX_TABS;i++) {
        if (!E.tab[i].active) continue;
        const char *nm = E.tab[i].name;
        const char *sl = strrchr(nm,'/');
        if (sl) nm=sl+1;
        if (i==E.cur) {
            wb_puts("\033[48;5;33m\033[97m");
            if (E.tab[i].modified) wb_puts(" ● ");
            else wb_puts("   ");
            wb_puts(nm);
            wb_puts("   \033[48;5;234m\033[90m");
        } else {
            wb_puts("\033[38;5;244m ");
            wb_puts(nm);
            wb_puts(" ");
        }
    }
    wb_puts("\033[m\r\n");
}

static void render_tree(int tree_w, int edit_h) {
    for (int row=0; row<edit_h; row++) {
        wb_printf("\033[%d;1H", row+2);
        if (row==0) {
            /* Tree header */
            wb_puts("\033[48;5;237m\033[38;5;75m");
            const char *rn = strrchr(E.tree_root,'/');
            char hdr[PX_TREE_NAME];
            snprintf(hdr, tree_w, " > %s", rn?rn+1:E.tree_root);
            hdr[tree_w-1]=0;
            wb_puts(hdr);
        } else {
            int ni = row-1;
            if (ni < E.tree_count) {
                TreeNode *n = &E.tree[ni];
                if (ni==E.tree_sel) wb_puts("\033[48;5;238m");
                else wb_puts("\033[48;5;235m");
                if (n->is_dir) wb_puts("\033[38;5;75m");
                else wb_puts("\033[38;5;252m");
                char entry[PX_TREE_NAME+4];
                snprintf(entry,sizeof(entry)," %s %s",n->is_dir?"▸":" ",n->name);
                entry[tree_w-1]=0;
                wb_puts(entry);
            } else {
                wb_puts("\033[48;5;235m");
            }
        }
        wb_puts("\033[K\033[m");
        /* Divider */
        wb_printf("\033[%d;%dH\033[90m│\033[m", row+2, tree_w+1);
    }
}

static void render_editor(int tree_w, int edit_h, int edit_w) {
    PxTab *t = &E.tab[E.cur];
    Lang   lang = detect_lang(t->name);

    /* Scroll clamp */
    if (t->cy < t->scroll_r) t->scroll_r = t->cy;
    if (t->cy >= t->scroll_r+edit_h) t->scroll_r = t->cy-edit_h+1;
    if (t->cx < t->scroll_c) t->scroll_c = t->cx;
    if (t->cx >= t->scroll_c+edit_w) t->scroll_c = t->cx-edit_w+1;

    static int attr_buf[PX_LINE_LEN];

    for (int row=0; row<edit_h; row++) {
        int fr = row+t->scroll_r;
        int col_offset = tree_w + (E.tree_visible ? 1 : 0);
        wb_printf("\033[%d;%dH", row+2, col_offset+1);

        /* Gutter */
        if (fr < t->nlines) {
            if (fr == t->cy)
                wb_printf("\033[38;5;252m%*d \033[90m│\033[m ",
                          E.cfg.gutter_width-1, fr+1);
            else
                wb_printf("\033[38;5;239m%*d \033[90m│\033[m ",
                          E.cfg.gutter_width-1, fr+1);
        } else {
            wb_printf("\033[38;5;237m%*s \033[90m│\033[m ",
                      E.cfg.gutter_width-1, "~");
        }

        /* Content */
        if (fr < t->nlines) {
            const char *line = t->lines[fr];
            int llen = (int)strlen(line);
            memset(attr_buf, 0, sizeof(int)*llen);
            syntax_hl(line, llen, attr_buf, lang);

            /* Find search match on this line */
            int hl_s=-1, hl_e=-1;
            if (E.search_on && E.search[0]) {
                const char *found = strstr(line, E.search);
                if (found) { hl_s=found-line; hl_e=hl_s+(int)strlen(E.search); }
            }

            int prev_attr = -99;
            for (int c=t->scroll_c; c<llen && (c-t->scroll_c)<edit_w; c++) {
                if (c>=hl_s && c<hl_e) {
                    if (prev_attr != -1) { wb_puts("\033[43m\033[30m"); prev_attr=-1; }
                } else {
                    if (attr_buf[c] != prev_attr) {
                        if (attr_buf[c]==0) wb_puts("\033[m");
                        else wb_printf("\033[%dm", attr_buf[c]);
                        prev_attr = attr_buf[c];
                    }
                }
                wb_putc(line[c]);
            }
            wb_puts("\033[m");
        }
        wb_puts("\033[K");
    }
}

static void render_term_panel(int term_h) {
    if (!E.term.visible || term_h < 2) return;
    int start = E.rows - term_h;

    /* Header bar */
    wb_printf("\033[%d;1H", start);
    if (E.term.focused)
        wb_puts("\033[48;5;22m\033[97m  ▶ TERMINAL  [Ctrl+T to unfocus]\033[K\033[m");
    else
        wb_puts("\033[48;5;236m\033[90m  ▷ terminal  [Ctrl+T to focus]\033[K\033[m");

    /* Display scrollback */
    int display_h = term_h - 1;
    int first = (E.term.nlines > display_h) ? E.term.nlines - display_h : 0;
    for (int row=0; row<display_h; row++) {
        wb_printf("\033[%d;1H", start+1+row);
        wb_puts("\033[48;5;232m\033[38;5;252m");
        int li = first + row;
        if (li < E.term.nlines) {
            char safe[PX_TERM_COLS+1];
            strncpy(safe, E.term.lines[li], E.cols);
            safe[E.cols]=0;
            wb_puts(safe);
        }
        wb_puts("\033[K\033[m");
    }
}

static void render_statusbar(void) {
    PxTab *t = &E.tab[E.cur];
    const char *lnames[] = {"", "C/C++", "Python", "JS/TS"};
    Lang lang = detect_lang(t->name);

    wb_printf("\033[%d;1H", E.rows);
    wb_puts("\033[48;5;238m\033[97m");

    const char *nm = t->name;
    const char *sl = strrchr(nm,'/');
    if (sl) nm=sl+1;

    wb_printf("  PX-CODE  │  %s%s  │  L%d:C%d  │  %s  ",
        t->modified ? "● " : "",
        nm,
        t->cy+1, t->cx+1,
        lnames[lang]);

    /* Status message (timed) */
    if (time(NULL) < E.status_exp && E.status[0]) {
        wb_puts("\033[38;5;226m│  ");
        wb_puts(E.status);
        wb_puts("  \033[97m");
    } else if (E.term.focused) {
        wb_puts("\033[38;5;82m│  TERMINAL MODE  \033[97m");
    } else if (t->mc_count > 0) {
        wb_printf("\033[38;5;214m│  %d CURSORS  \033[97m", t->mc_count+1);
    }

    wb_puts("\033[K\033[m");

    /* Right-aligned hints */
    const char *hint = "  Alt+S:Save  Ctrl+F:Search  Ctrl+T:Terminal  Ctrl+B:Tree  ";
    int hlen = (int)strlen(hint);
    if (E.cols > hlen + 30)
        wb_printf("\033[%d;%dH\033[48;5;235m\033[38;5;244m%s\033[m",
                  E.rows, E.cols - hlen + 1, hint);
}

static void render(void) {
    update_size();

    int tree_w  = E.tree_visible ? (E.cols * E.cfg.left_panel_pct / 100) : 0;
    int term_h  = E.term.visible  ? (E.rows * E.cfg.bottom_panel_pct / 100) : 0;
    if (term_h < 2 && E.term.visible) term_h = 2;
    int edit_h  = E.rows - 2 - term_h;   /* 2 = tabbar + statusbar */
    int edit_w  = E.cols - tree_w - (E.tree_visible?1:0) - E.cfg.gutter_width - 2;
    if (edit_h < 1) edit_h = 1;
    if (edit_w < 10) edit_w = 10;

    wb_puts("\033[?25l");  /* hide cursor during redraw */

    render_tabbar(tree_w);
    if (E.tree_visible) render_tree(tree_w, edit_h);
    render_editor(tree_w, edit_h, edit_w);
    if (E.term.visible) render_term_panel(term_h);
    render_statusbar();

    /* Position cursor */
    if (!E.term.focused) {
        PxTab *t = &E.tab[E.cur];
        int sr = (t->cy - t->scroll_r) + 2;
        int sc = tree_w + (E.tree_visible?2:0) + E.cfg.gutter_width + 2 + (t->cx - t->scroll_c);
        if (sr >= 2 && sr < 2+edit_h && sc >= 1 && sc <= E.cols)
            wb_printf("\033[%d;%dH", sr, sc);
    }

    wb_puts("\033[?25h");
    wb_flush();
}

/* ══════════════════════════════════════════════════════════════
 * INPUT HANDLER
 * ══════════════════════════════════════════════════════════════ */
static void handle_key(int key) {
    /* If terminal panel has focus, forward all input to shell */
    if (E.term.focused && E.term.visible) {
        if (key == KEY_CTRL_T) { tpanel_close(); return; }
        char buf[8] = {0}; int bl = 0;
        switch (key) {
            case ARROW_UP:    strcpy(buf,"\033[A"); bl=3; break;
            case ARROW_DOWN:  strcpy(buf,"\033[B"); bl=3; break;
            case ARROW_RIGHT: strcpy(buf,"\033[C"); bl=3; break;
            case ARROW_LEFT:  strcpy(buf,"\033[D"); bl=3; break;
            case KEY_HOME:    strcpy(buf,"\033[H"); bl=3; break;
            case KEY_END:     strcpy(buf,"\033[F"); bl=3; break;
            case KEY_PGUP:    strcpy(buf,"\033[5~"); bl=4; break;
            case KEY_PGDN:    strcpy(buf,"\033[6~"); bl=4; break;
            case '\r':  buf[0]='\r'; bl=1; break;
            case '\t':  buf[0]='\t'; bl=1; break;
            case 127:   buf[0]=127;  bl=1; break;
            default:
                if (key>0 && key<256) { buf[0]=(char)key; bl=1; }
                break;
        }
        if (bl>0) tpanel_send(buf, bl);
        return;
    }

    /* File tree focus */
    if (E.tree_visible && key == ARROW_UP && E.tree_sel > 0 &&
        E.tab[E.cur].cx == 0 && E.tab[E.cur].cy == 0) { /* optional: tree nav when at top */ }

    PxTab *t = &E.tab[E.cur];

    switch (key) {
        /* ── Movement ── */
        case ARROW_UP: case ARROW_DOWN: case ARROW_LEFT: case ARROW_RIGHT:
        case KEY_HOME: case KEY_END: case KEY_PGUP: case KEY_PGDN:
            ed_move(key); break;

        /* ── Tab switching ── */
        case KEY_CTRL_TAB:
            { int s=E.cur;
              do { E.cur=(E.cur+1)%PX_MAX_TABS; } while (!E.tab[E.cur].active && E.cur!=s); }
            break;
        case KEY_CTRL_STAB:
            { int s=E.cur;
              do { E.cur=(E.cur-1+PX_MAX_TABS)%PX_MAX_TABS; } while (!E.tab[E.cur].active && E.cur!=s); }
            break;

        /* ── Save ── */
        case KEY_ALT_S:
            save_file(E.cur); break;

        /* ── Undo / Redo ── */
        case KEY_CTRL_Z: undo_do(); break;
        case KEY_CTRL_Y: redo_do(); break;

        /* ── Copy / Cut / Paste ── */
        case KEY_CTRL_C: ed_copy(); break;
        case KEY_CTRL_X: ed_copy(); ed_del_line(); break;
        case KEY_CTRL_V: ed_paste(); break;

        /* ── Line ops ── */
        case KEY_CTRL_K: ed_del_line(); break;
        case KEY_CTRL_D: ed_dup_line(); break;

        /* ── Multi-cursor ── */
        case KEY_CTRL_SPACE: {
            if (t->mc_count < PX_MAX_CURSORS) {
                t->mc[t->mc_count].x = t->cx;
                t->mc[t->mc_count].y = t->cy;
                t->mc_count++;
                snprintf(E.status, PX_STATUS_LEN, "Cursor %d added", t->mc_count+1);
                E.status_exp = time(NULL)+2;
            }
            break;
        }
        case KEY_CTRL_SSPACE:
            if (t->mc_count > 0) t->mc_count--;
            break;

        /* ── Search ── */
        case KEY_CTRL_F: prompt_search(); break;

        /* ── Panels ── */
        case KEY_CTRL_T:
            if (!E.term.visible) tpanel_open();
            else { E.term.focused = !E.term.focused; }
            break;
        case KEY_CTRL_B:
            E.tree_visible = !E.tree_visible;
            if (E.tree_visible && E.tree_count == 0) tree_load(".");
            break;

        /* ── New/close tab ── */
        case KEY_CTRL_N: {
            int idx = find_free_tab();
            if (idx >= 0) { tab_init(idx, "[Novo]"); E.cur = idx; }
            break;
        }
        case KEY_CTRL_W:
            if (t->modified) {
                snprintf(E.status,PX_STATUS_LEN,"Unsaved! Alt+S to save, Ctrl+W again to discard");
                E.status_exp = time(NULL)+4;
                t->modified = 0; /* second press will close */
                break;
            }
            t->active = 0;
            for (int i=0;i<PX_MAX_TABS;i++) if (E.tab[i].active) { E.cur=i; break; }
            break;

        /* ── Goto line ── */
        case KEY_CTRL_G: {
            char gbuf[32] = {0};
            int gpos = 0;
            for(;;) {
                wb_printf("\033[%d;1H\033[48;5;22m\033[97m  Goto line: %s_\033[K\033[m",
                          E.rows, gbuf);
                wb_flush();
                int k = read_key();
                if (k=='\r') {
                    int ln = atoi(gbuf)-1;
                    if (ln>=0 && ln<t->nlines) { t->cy=ln; t->cx=0; }
                    break;
                }
                if (k=='\033') break;
                if (k==127 && gpos>0) gbuf[--gpos]=0;
                else if (isdigit(k) && gpos<10) { gbuf[gpos++]=(char)k; gbuf[gpos]=0; }
            }
            break;
        }

        /* ── Text input ── */
        case '\r':  ed_newline(); break;
        case 127:   ed_backspace(); break;
        case KEY_DEL: ed_del_forward(); break;
        case '\t':  ed_tab(); break;

        default:
            if (key >= 32 && key < 127) ed_insert((char)key);
            break;
    }
    (void)t;
}

/* ══════════════════════════════════════════════════════════════
 * SIGNAL HANDLERS
 * ══════════════════════════════════════════════════════════════ */
static void sig_winch(int s) { (void)s; E.resized=1; }
static void sig_exit(int s) {
    (void)s;
    tty_restore();
    write(STDOUT_FILENO, "\033[?1049l\033[?25h", 14);
    _exit(0);
}

/* ══════════════════════════════════════════════════════════════
 * MAIN
 * ══════════════════════════════════════════════════════════════ */
int main(int argc, char **argv) {
    /* Home dir */
    const char *home = getenv("HOME");
    if (!home) {
        struct passwd *pw = getpwuid(getuid());
        home = (pw && pw->pw_dir) ? pw->pw_dir : "/tmp";
    }
    strncpy(E.home, home, 255);

    /* Config */
    cfg_defaults();
    cfg_load(PX_ENV_FILE);

    /* Plugin auto-install (non-interactive) */
    plugin_install_all();

    /* Open files from argv */
    int loaded = 0;
    for (int i=1; i<argc && loaded<PX_MAX_TABS; i++) {
        load_file(loaded++, argv[i]);
    }
    if (loaded == 0) tab_init(0, "[Novo]");

    /* Terminal setup */
    update_size();
    tty_raw();

    /* Signals */
    signal(SIGWINCH, sig_winch);
    signal(SIGTERM,  sig_exit);
    signal(SIGINT,   sig_exit);
    signal(SIGCHLD,  SIG_IGN);

    /* Alternate screen buffer */
    write(STDOUT_FILENO, "\033[?1049h\033[H\033[?25l", 19);

    /* Initial file tree */
    E.tree_visible = 1;
    tree_load(".");

    /* ── MAIN LOOP ── */
    static time_t last_esc = 0;
    for (;;) {
        if (E.resized) { update_size(); E.resized=0; }
        tpanel_poll();   /* drain pty output */
        render();

        /* Poll: stdin + pty fd with 100ms timeout */
        struct pollfd pfds[2];
        pfds[0].fd     = STDIN_FILENO;
        pfds[0].events = POLLIN;
        pfds[1].fd     = (E.term.fd > 0) ? E.term.fd : -1;
        pfds[1].events = POLLIN;

        int np = poll(pfds, 2, 100);
        if (np < 0) continue;

        if (pfds[1].revents & POLLIN) tpanel_poll();
        if (!(pfds[0].revents & POLLIN)) continue;

        int key = read_key();

        /* ESC: double-tap to quit */
        if (key == '\033') {
            PxTab *t = &E.tab[E.cur];
            /* Cancel multi-cursor first */
            if (t->mc_count > 0) { t->mc_count=0; continue; }
            /* Unfocus terminal */
            if (E.term.focused) { E.term.focused=0; continue; }
            /* Cancel search */
            if (E.search_on) { E.search_on=0; E.search[0]=0; continue; }
            /* Double-ESC = quit */
            time_t now = time(NULL);
            if (now - last_esc < 1) break;
            last_esc = now;
            snprintf(E.status, PX_STATUS_LEN, "ESC again to quit | Alt+S to save");
            E.status_exp = time(NULL)+3;
            continue;
        }

        handle_key(key);
    }

    /* ── CLEANUP ── */
    if (E.term.pid > 0) { kill(E.term.pid, SIGTERM); waitpid(E.term.pid, NULL, 0); }
    tty_restore();
    write(STDOUT_FILENO, "\033[?1049l\033[?25h\033[2J\033[H", 23);
    return 0;
}
