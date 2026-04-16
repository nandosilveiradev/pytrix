#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>

void pytrix_menu() {
    struct dirent *px_entry;
    DIR *px_dir = opendir("./pytrix_utils/c/");
    int px_count = 1;
    printf("\n--- [ Pytrix Brain Watcher - Menu Dinâmico ] ---\n");
    if (px_dir) {
        while ((px_entry = readdir(px_dir)) != NULL) {
            if (px_entry->d_name[0] != '.' && strstr(px_entry->d_name, ".c") == NULL) {
                printf("[%d] %s\n", px_count++, px_entry->d_name);
            }
        }
        closedir(px_dir);
    }
    printf("[0] Retornar ao Fluxo Python\nOpção: ");
}

int main() {
    int px_op;
    char px_bin[128];
    while(1) {
        pytrix_menu();
        scanf("%d", &px_op);
        if (px_op == 0) break;
        printf("Digite o nome do binário para executar: ");
        scanf("%s", px_bin);
        char px_cmd[256];
        snprintf(px_cmd, sizeof(px_cmd), "./pytrix_utils/c/%s", px_bin);
        system(px_cmd);
    }
    return 0;
}
