#ifndef HANG_CHO_H
#define HANG_CHO_H

#define MAX_QUEUE 20

typedef struct {
    int vehicle_indexes[MAX_QUEUE];
    int front;
    int rear;
    int count;
} HangChoSac;

void khoi_tao_hang_cho(HangChoSac *queue);
int them_vao_hang_cho(HangChoSac *queue, int vehicle_index);
int lay_xe_dau_hang(HangChoSac *queue);
int co_trong_hang_cho(const HangChoSac *queue, int vehicle_index);

#endif
