#ifndef TELEMETRY_REPOSITORY_H
#define TELEMETRY_REPOSITORY_H

void luu_telemetry(int session_id, int tick, const char *ma_xe, int port_id, float soc, float temp, float power, const char *state);

#endif /* TELEMETRY_REPOSITORY_H */
