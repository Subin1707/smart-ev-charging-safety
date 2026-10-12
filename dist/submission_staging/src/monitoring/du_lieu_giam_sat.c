#include "du_lieu_giam_sat.h"
#include "hang_so.h"
#include "trang_thai_xe.h"
#include "phat_hien_loi.h"
#include "su_kien_he_thong.h"
#ifdef _WIN32
#include <windows.h>
#endif

static int thay_the_snapshot(const char *duong_dan_tam, const char *duong_dan) {
#ifdef _WIN32
	return MoveFileExA(duong_dan_tam, duong_dan, MOVEFILE_REPLACE_EXISTING) ? 0 : -1;
#else
	return rename(duong_dan_tam, duong_dan);
#endif
}

static const char *trang_thai_xe_json(TrangThaiXe trang_thai) {
	switch (trang_thai) {
		case XE_CHO: return "WAITING";
		case XE_DA_KET_NOI: return "CONNECTED";
		case XE_DA_XAC_THUC: return "AUTHENTICATED";
		case XE_SAN_SANG: return "READY";
		case XE_DANG_SAC: return "CHARGING";
		case XE_DA_DAY: return "FULL";
		case XE_DUNG_SAC: return "STOPPED";
		case XE_DA_NGAT_KET_NOI: return "DISCONNECTED";
		case XE_LOI: return "FAULT";
		default: return "UNKNOWN";
	}
}

static const char *trang_thai_cong_json(TrangThaiCong trang_thai) {
	switch (trang_thai) {
		case CONG_RANH: return "IDLE";
		case CONG_DA_DAT: return "RESERVED";
		case CONG_DA_KET_NOI: return "CONNECTED";
		case CONG_SAN_SANG: return "READY";
		case CONG_DANG_SAC: return "CHARGING";
		case CONG_DUNG: return "STOPPED";
		case CONG_LOI: return "FAULT";
		default: return "UNKNOWN";
	}
}

static const XeDien *tim_xe_theo_id(const XeDien ds_xe[], int so_xe, int id) {
	if (!ds_xe || id < 0) return NULL;

	for (int i = 0; i < so_xe; i++) {
		if (ds_xe[i].id == id) return &ds_xe[i];
	}
	return NULL;
}

static int tim_port_cua_xe(const TramSac *tram, int vehicle_id) {
	if (!tram) return -1;

	for (int i = 0; i < SO_CONG_SAC; i++) {
		if (tram->cong[i].vehicle_id == vehicle_id) return tram->cong[i].id;
	}
	return 0;
}

static void xuat_snapshot_json_voi_trang_thai(FILE *output,
									int tick,
									const char *trang_thai_mo_phong,
									const TramSac *tram,
									const XeDien ds_xe[],
																int so_xe,
																const HangChoSac *queue,
																const KichBanMoPhong *kich_ban);

void xuat_snapshot_json(FILE *output,
						int tick,
						const TramSac *tram,
						const XeDien ds_xe[],
						int so_xe,
						const HangChoSac *queue,
						const KichBanMoPhong *kich_ban) {
	xuat_snapshot_json_voi_trang_thai(output, tick, "PAUSED", tram, ds_xe, so_xe, queue, kich_ban);
}

static void xuat_snapshot_json_voi_trang_thai(FILE *output,
									int tick,
									const char *trang_thai_mo_phong,
									const TramSac *tram,
									const XeDien ds_xe[],
																int so_xe,
																const HangChoSac *queue,
																const KichBanMoPhong *kich_ban) {
	if (!output || !tram || !ds_xe || so_xe < 0) return;

	fprintf(output, "{\"tick\":%d,\"simulation\":{\"status\":\"%s\"},\"station\":{\"totalPower\":%.2f,\"maxPower\":%.2f,\"emergency\":%s},",
			tick,
			trang_thai_mo_phong ? trang_thai_mo_phong : "PAUSED",
			tram->cong_suat_hien_tai,
			tram->cong_suat_toi_da,
			tram->emergency ? "true" : "false");

	fprintf(output, "\"vehicles\":[");
	for (int i = 0; i < so_xe; i++) {
		const XeDien *xe = &ds_xe[i];
		int port = tim_port_cua_xe(tram, xe->id);
		char port_json[12] = "null";
		float power = port > 0 ? tram->cong[port - 1].cong_suat_kw : 0.0f;
		if (port > 0) snprintf(port_json, sizeof(port_json), "%d", port);
		const char *fault = NULL;
		if (port > 0 && tram->cong[port - 1].ma_loi != LOI_KHONG_CO) {
			fault = ten_ma_loi((MaLoiHeThong)tram->cong[port - 1].ma_loi);
		}

		if (i > 0) fprintf(output, ",");
		fprintf(output,
				"{\"id\":\"%s\",\"state\":\"%s\",\"soc\":%.2f,\"temperature\":%.2f,\"maxChargingPower\":%.2f,\"allocatedPower\":%.2f,\"port\":%s,\"assignedPort\":%s,\"connected\":%s,\"authenticated\":%s,\"fault\":%s}",
				xe->ma_xe,
				trang_thai_xe_json(xe->trang_thai),
				xe->pin.soc,
				xe->pin.nhiet_do,
				xe->cong_suat_sac_toi_da,
				power,
				port_json,
				xe->assigned_port > 0 ? port_json : "null",
				xe->da_ket_noi ? "true" : "false",
				xe->da_xac_thuc ? "true" : "false",
				fault ? "\"FAULT\"" : "null");
	}
	fprintf(output, "],\"ports\":[");

	for (int i = 0; i < SO_CONG_SAC; i++) {
		const CongSac *port = &tram->cong[i];
		const XeDien *xe = tim_xe_theo_id(ds_xe, so_xe, port->vehicle_id);

		if (i > 0) fprintf(output, ",");
		if (xe) {
			fprintf(output,
					"{\"id\":%d,\"state\":\"%s\",\"vehicleId\":\"%s\",\"power\":%.2f}",
					port->id,
					trang_thai_cong_json(port->trang_thai),
					xe->ma_xe,
					port->cong_suat_kw);
		} else {
			fprintf(output,
					"{\"id\":%d,\"state\":\"%s\",\"vehicleId\":null,\"power\":%.2f}",
					port->id,
					trang_thai_cong_json(port->trang_thai),
					port->cong_suat_kw);
		}
	}
	fprintf(output, "]");
	fprintf(output, ",\"queue\":{\"count\":%d,\"vehicles\":[",
				queue ? queue->count : 0);
	if (queue) {
		for (int i = 0; i < queue->count; i++) {
			int index = queue->vehicle_indexes[(queue->front + i) % MAX_QUEUE];
			if (i > 0) fprintf(output, ",");
			fprintf(output, "\"%s\"", ds_xe[index].ma_xe);
		}
	}
	fprintf(output, "]}");
	fprintf(output, ",\"scenario\":{\"name\":\"%s\",\"vehicleId\":\"%s\",\"status\":\"%s\",\"triggered\":%s},\"events\":[",
				kich_ban ? ten_kich_ban_scenario(kich_ban->loai) : "NORMAL",
				(kich_ban && kich_ban->vehicle_index >= 0 && kich_ban->vehicle_index < so_xe)
					? ds_xe[kich_ban->vehicle_index].ma_xe : "",
				(kich_ban && kich_ban->da_load) ? (kich_ban->da_kich_hoat ? "TRIGGERED" : "LOADED") : "IDLE",
				(kich_ban && kich_ban->da_kich_hoat) ? "true" : "false");
	const SuKienHeThong *su_kien = NULL;
	int so_su_kien = lay_su_kien_he_thong(&su_kien);
	for (int i = 0; i < so_su_kien; i++) {
		if (i > 0) fprintf(output, ",");
		fprintf(output,
				"{\"tick\":%d,\"type\":\"%s\",\"severity\":\"%s\",\"vehicleId\":\"%s\",\"code\":\"%s\",\"message\":\"%s\"}",
				su_kien[i].tick, su_kien[i].type, su_kien[i].severity,
				su_kien[i].vehicle_id, su_kien[i].code, su_kien[i].message);
	}
	fprintf(output, "],\"safetyChecks\":[");

	int soc_range = 1;
	int fault_zero_power = 1;
	int auth_before_charging = 1;
	int connected_before_charging = 1;
	int full_zero_power = 1;
	int port_fault_zero_power = 1;
	for (int i = 0; i < so_xe; i++) {
		int port = tim_port_cua_xe(tram, ds_xe[i].id);
		float power = port > 0 ? tram->cong[port - 1].cong_suat_kw : 0.0f;
		if (ds_xe[i].pin.soc < 0.0f || ds_xe[i].pin.soc > 100.0f) soc_range = 0;
		if (ds_xe[i].trang_thai == XE_LOI && power > 0.001f) fault_zero_power = 0;
		if (ds_xe[i].trang_thai == XE_DANG_SAC && !ds_xe[i].da_xac_thuc) auth_before_charging = 0;
		if (ds_xe[i].trang_thai == XE_DANG_SAC && !ds_xe[i].da_ket_noi) connected_before_charging = 0;
		if (ds_xe[i].pin.soc >= 100.0f && power > 0.001f) full_zero_power = 0;
		if (port > 0 && tram->cong[port - 1].trang_thai == CONG_LOI && power > 0.001f) port_fault_zero_power = 0;
	}
	int checks[] = {soc_range, tram->cong_suat_hien_tai <= tram->cong_suat_toi_da + 0.001f,
				   fault_zero_power, auth_before_charging, connected_before_charging,
				   tram->emergency ? tram->cong_suat_hien_tai <= 0.001f : 1,
				   full_zero_power, port_fault_zero_power};
		const char *check_ids[] = {"SOC_RANGE", "POWER_LIMIT", "FAULT_ZERO_POWER",
									   "AUTH_BEFORE_CHARGING", "CONNECTED_BEFORE_CHARGING",
									   "EMERGENCY_ZERO_POWER", "FULL_ZERO_POWER", "PORT_FAULT_ZERO_POWER"};
	for (size_t i = 0; i < sizeof(checks) / sizeof(checks[0]); i++) {
		if (i > 0) fprintf(output, ",");
		fprintf(output, "{\"id\":\"%s\",\"status\":\"%s\"}",
				check_ids[i], checks[i] ? "PASS" : "FAIL");
	}
	fprintf(output, "]}\n");
}

int ghi_snapshot_json(const char *duong_dan,
					  int tick,
					  const TramSac *tram,
					  const XeDien ds_xe[],
					  int so_xe,
					  const HangChoSac *queue,
					  const KichBanMoPhong *kich_ban) {
	if (!duong_dan) return 0;

	char duong_dan_tam[512];
	snprintf(duong_dan_tam, sizeof(duong_dan_tam), "%s.tmp", duong_dan);
	FILE *output = fopen(duong_dan_tam, "w");
	if (!output) return 0;

	xuat_snapshot_json(output, tick, tram, ds_xe, so_xe, queue, kich_ban);
	fclose(output);
	if (thay_the_snapshot(duong_dan_tam, duong_dan) != 0) return 0;
	return 1;
}

int ghi_snapshot_json_voi_trang_thai(const char *duong_dan,
								  int tick,
								  const char *trang_thai_mo_phong,
								  const TramSac *tram,
								  const XeDien ds_xe[],
								  int so_xe,
								  const HangChoSac *queue,
								  const KichBanMoPhong *kich_ban) {
	if (!duong_dan) return 0;

	char duong_dan_tam[512];
	snprintf(duong_dan_tam, sizeof(duong_dan_tam), "%s.tmp", duong_dan);
	FILE *output = fopen(duong_dan_tam, "w");
	if (!output) return 0;

	xuat_snapshot_json_voi_trang_thai(output, tick, trang_thai_mo_phong, tram, ds_xe, so_xe, queue, kich_ban);
	fclose(output);
	if (thay_the_snapshot(duong_dan_tam, duong_dan) != 0) return 0;
	return 1;
}
