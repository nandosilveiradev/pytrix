#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int pytrix_validar_buffer(const char *px_path) {
    FILE *px_fp = fopen(px_path, "r");
    if (!px_fp) return 2;
    fseek(px_fp, -1, SEEK_END);
    char px_last_char = fgetc(px_fp);
    fclose(px_fp);
    return (px_last_char == '>') ? 0 : 10;
}

int main() {
    const char *px_url = "http://api-legado.com/data.xml"; 
    const char *px_file = "../../dados.xml";
    char px_cmd[512];
    snprintf(px_cmd, sizeof(px_cmd), "curl -s -L -o %s %s", px_file, px_url);
    if (system(px_cmd) != 0) return 1;
    return pytrix_validar_buffer(px_file);
}
