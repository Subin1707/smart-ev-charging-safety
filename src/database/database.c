#ifndef _WIN32
#define _POSIX_C_SOURCE 200809L
#endif
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "database.h"
#include "logger.h"

#ifdef USE_LIBPQ
#include <libpq-fe.h>
#endif

static FILE *g_sql_file = NULL;
static char g_sql_path[256];
static int g_postgresql_connected = 0;
#ifdef USE_LIBPQ
static PGconn *g_pg_conn = NULL;
#endif

#ifndef USE_LIBPQ
/* SQL travels through stdin; vehicle/event strings never enter a shell command. */
static int docker_psql(const char *sql) {
#ifdef _WIN32
    FILE *pipe = _popen("docker exec -i smart_ev_database psql -v ON_ERROR_STOP=1 -U smart_ev_user -d smart_ev", "w");
#else
    FILE *pipe = popen("docker exec -i smart_ev_database psql -v ON_ERROR_STOP=1 -U smart_ev_user -d smart_ev", "w");
#endif
    if (!pipe) return 0;
    int written = fputs(sql, pipe) >= 0 && fputc('\n', pipe) != EOF;
#ifdef _WIN32
    int result = _pclose(pipe);
#else
    int result = pclose(pipe);
#endif
    return written && result == 0;
}
static void chen_sql_escaped(char *out, size_t out_size, const char *value) {
    size_t pos = 0;
    if (!value) value = "";

    while (*value && pos + 2 < out_size) {
        if (*value == '\'') out[pos++] = '\'';
        out[pos++] = *value++;
    }
    out[pos] = '\0';
}
#endif

int khoi_tao_database(const char *sql_dump_path) {
    if (sql_dump_path) {
        strncpy(g_sql_path, sql_dump_path, sizeof(g_sql_path) - 1);
        g_sql_path[sizeof(g_sql_path) - 1] = '\0';
    } else {
        strcpy(g_sql_path, "logs/database/persistence.sql");
    }

    g_sql_file = fopen(g_sql_path, "w");
    if (!g_sql_file) {
        printf("[DATABASE] Khong the tao file snapshot SQL: %s\n", g_sql_path);
        return 0;
    }

    fprintf(g_sql_file, "-- Smart EV Charging System SQL Persistence Dump\n");
    fprintf(g_sql_file, "BEGIN TRANSACTION;\n\n");
    fflush(g_sql_file);

    ghi_log(LOG_INFO, "Database persistence module khoi tao thanh cong (%s)", g_sql_path);
    return 1;
}

void thuc_thi_sql(const char *sql) {
    if (g_sql_file && sql) {
        fprintf(g_sql_file, "%s\n", sql);
        fflush(g_sql_file);
    }
}

void dong_database(void) {
    if (g_sql_file) {
        fprintf(g_sql_file, "\nCOMMIT;\n");
        fclose(g_sql_file);
        g_sql_file = NULL;
    }
}

int dong_bo_vao_postgresql(void) {
#ifdef USE_LIBPQ
    return g_postgresql_connected;
#else
    char cmd[512];
    snprintf(cmd, sizeof(cmd),
             "cmd /c \"docker exec -i smart_ev_database psql -U smart_ev_user -d smart_ev < \"%s\" > nul 2>&1\"",
             g_sql_path);

    int ret = system(cmd);
    if (ret == 0) {
        ghi_log(LOG_INFO, "[POSTGRESQL] Dong bo du lieu vao container smart_ev_database THANH CONG!");
        return 1;
    } else {
        ghi_log(LOG_WARNING, "[POSTGRESQL] Khong the tu dong nap vao Docker container (Ma loi: %d). File SQL da duoc luu tai %s",
                ret, g_sql_path);
        return 0;
    }
#endif
}

int ket_noi_postgresql(void) {
#ifdef USE_LIBPQ
    const char *host = getenv("DB_HOST");
    const char *port = getenv("DB_PORT");
    const char *name = getenv("DB_NAME");
    const char *user = getenv("DB_USER");
    const char *password = getenv("DB_PASSWORD");
    char conninfo[512];

    if (!host) host = "localhost";
    if (!port) port = "5433";
    if (!name) name = "smart_ev";
    if (!user) user = "smart_ev_user";
    if (!password) password = "smart_ev_password";

    snprintf(conninfo, sizeof(conninfo),
             "host=%s port=%s dbname=%s user=%s password=%s connect_timeout=5",
             host, port, name, user, password);
    g_pg_conn = PQconnectdb(conninfo);
    if (!g_pg_conn || PQstatus(g_pg_conn) != CONNECTION_OK) {
        fprintf(stderr, "[DATABASE] PostgreSQL connection failed: %s\n",
                g_pg_conn ? PQerrorMessage(g_pg_conn) : "allocation failed");
        if (g_pg_conn) PQfinish(g_pg_conn);
        g_pg_conn = NULL;
        g_postgresql_connected = 0;
        return 0;
    }
    g_postgresql_connected = 1;
    ghi_log(LOG_INFO, "[POSTGRESQL] Connected to %s:%s/%s.", host, port, name);
    return 1;
#else
    /* Native Docker integration is opt-in: an unhealthy daemon must not block
       the simulator during startup. Container builds use libpq above. */
    const char *enabled = getenv("SMART_EV_POSTGRES");
    g_postgresql_connected = enabled && strcmp(enabled, "1") == 0 && docker_psql("SELECT 1;");
    if (g_postgresql_connected) {
        ghi_log(LOG_INFO, "[POSTGRESQL] Ket noi truc tiep qua Docker psql thanh cong.");
    } else {
        ghi_log(LOG_WARNING, "[POSTGRESQL] Khong the ket noi truc tiep; RAM history van duoc duy tri.");
    }
    return g_postgresql_connected;
#endif
}

void ngat_ket_noi_postgresql(void) {
#ifdef USE_LIBPQ
    if (g_pg_conn) PQfinish(g_pg_conn);
    g_pg_conn = NULL;
#endif
    g_postgresql_connected = 0;
}

int database_dang_ket_noi(void) {
    return g_postgresql_connected;
}

int luu_su_kien_an_toan_postgresql(int tick,
                                    const char *ma_xe,
                                    int so_cong,
                                    const char *su_kien,
                                    const char *muc_do,
                                    const char *hanh_dong) {
    if (!g_postgresql_connected) return 0;

#ifdef USE_LIBPQ
    const char *values[6];
    char tick_text[16];
    char port_text[16];
    PGresult *result;
    snprintf(tick_text, sizeof(tick_text), "%d", tick);
    snprintf(port_text, sizeof(port_text), "%d", so_cong);
    values[0] = tick_text;
    values[1] = ma_xe ? ma_xe : "--";
    values[2] = port_text;
    values[3] = su_kien ? su_kien : "UNKNOWN";
    values[4] = muc_do ? muc_do : "INFO";
    values[5] = hanh_dong ? hanh_dong : "--";
    result = PQexecParams(g_pg_conn,
        "INSERT INTO su_kien_an_toan "
        "(tick, vehicle_code, port_number, event_type, severity, description) "
        "VALUES ($1, $2, $3, $4, $5, $6);",
        6, NULL, values, NULL, NULL, 0);
    if (PQresultStatus(result) != PGRES_COMMAND_OK) {
        fprintf(stderr, "[DATABASE] Safety event insert failed: %s\n",
                PQerrorMessage(g_pg_conn));
        PQclear(result);
        return 0;
    }
    PQclear(result);
    return 1;
#else
    char xe[96], port[32], event[160], level[64], action[160], sql[640];
    chen_sql_escaped(xe, sizeof(xe), ma_xe ? ma_xe : "--");
    snprintf(port, sizeof(port), "%d", so_cong);
    chen_sql_escaped(event, sizeof(event), su_kien ? su_kien : "UNKNOWN");
    chen_sql_escaped(level, sizeof(level), muc_do ? muc_do : "INFO");
    chen_sql_escaped(action, sizeof(action), hanh_dong ? hanh_dong : "--");
    snprintf(sql, sizeof(sql),
             "INSERT INTO su_kien_an_toan (tick, vehicle_code, port_number, event_type, severity, description) "
             "VALUES (%d, '%s', %s, '%s', '%s', '%s');",
             tick, xe, port, event, level, action);
    return docker_psql(sql);
#endif
}

void in_lich_su_su_kien_postgresql(void) {
#ifdef USE_LIBPQ
    PGresult *result;
    int rows;
#else
    const char *query_file = "logs/database/postgresql_history.txt";
    char cmd[900];
    FILE *file;
    char line[512];
    int total = 0;
#endif

    printf("\n=======================================================================\n");
    printf("                 POSTGRESQL SAFETY EVENT HISTORY\n");
    printf("=======================================================================\n");
    if (!g_postgresql_connected) {
        printf("[DATABASE] PostgreSQL chua ket noi.\n");
        printf("=======================================================================\n");
        return;
    }

#ifdef USE_LIBPQ
    result = PQexec(g_pg_conn,
                    "SELECT id, created_at, vehicle_code, event_type, severity "
                    "FROM su_kien_an_toan ORDER BY id;");
    if (PQresultStatus(result) != PGRES_TUPLES_OK) {
        printf("[DATABASE] Khong the truy van lich su PostgreSQL.\n");
        PQclear(result);
        printf("=======================================================================\n");
        return;
    }
    printf("%-4s %-20s %-9s %-20s %-10s\n", "ID", "TIME", "VEHICLE", "EVENT", "LEVEL");
    printf("-----------------------------------------------------------------------\n");
    rows = PQntuples(result);
    for (int i = 0; i < rows; i++) {
        printf("%-4s %-20s %-9s %-20s %-10s\n",
               PQgetvalue(result, i, 0), PQgetvalue(result, i, 1),
               PQgetvalue(result, i, 2), PQgetvalue(result, i, 3),
               PQgetvalue(result, i, 4));
    }
    PQclear(result);
    printf("-----------------------------------------------------------------------\n");
    printf("Total records: %d\n", rows);
    printf("=======================================================================\n");
    return;
#else
    snprintf(cmd, sizeof(cmd),
             "cmd /c \"docker exec smart_ev_database psql -U smart_ev_user -d smart_ev -At -F \\\"|\\\" -c \\\"SELECT id, created_at, vehicle_code, event_type, severity FROM su_kien_an_toan ORDER BY id;\\\" > %s 2> nul\"",
             query_file);
    if (system(cmd) != 0) {
        printf("[DATABASE] Khong the truy van lich su PostgreSQL.\n");
        printf("=======================================================================\n");
        return;
    }

    printf("%-4s %-20s %-9s %-20s %-10s\n", "ID", "TIME", "VEHICLE", "EVENT", "LEVEL");
    printf("-----------------------------------------------------------------------\n");
    file = fopen(query_file, "r");
    if (!file) {
        printf("[DATABASE] Khong doc duoc ket qua truy van.\n");
    } else {
        while (fgets(line, sizeof(line), file)) {
            char *cursor = line;
            char *fields[5];
            int field_count = 0;
            line[strcspn(line, "\r\n")] = '\0';
            while (field_count < 5 && (fields[field_count] = strtok(cursor, "|")) != NULL) {
                cursor = NULL;
                field_count++;
            }
            if (field_count == 5) {
                printf("%-4s %-20s %-9s %-20s %-10s\n",
                       fields[0], fields[1], fields[2], fields[3], fields[4]);
                total++;
            }
        }
        fclose(file);
    }
    printf("-----------------------------------------------------------------------\n");
    printf("Total records: %d\n", total);
    printf("=======================================================================\n");
#endif
}
