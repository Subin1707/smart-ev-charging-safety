#ifndef DATABASE_H
#define DATABASE_H

int khoi_tao_database(const char *sql_dump_path);
void dong_database(void);
void thuc_thi_sql(const char *sql);
int dong_bo_vao_postgresql(void);

int ket_noi_postgresql(void);
void ngat_ket_noi_postgresql(void);
int database_dang_ket_noi(void);
int luu_su_kien_an_toan_postgresql(int tick,
									const char *ma_xe,
									int so_cong,
									const char *su_kien,
									const char *muc_do,
									const char *hanh_dong);
void in_lich_su_su_kien_postgresql(void);

#endif /* DATABASE_H */
