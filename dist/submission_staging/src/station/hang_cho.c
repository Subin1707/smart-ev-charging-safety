#include "hang_cho.h"

void khoi_tao_hang_cho(HangChoSac *queue) {
    if (!queue) return;

    queue->front = 0;
    queue->rear = 0;
    queue->count = 0;
}

int co_trong_hang_cho(const HangChoSac *queue, int vehicle_index) {
    if (!queue || vehicle_index < 0) return 0;

    for (int i = 0; i < queue->count; i++) {
        int index = (queue->front + i) % MAX_QUEUE;
        if (queue->vehicle_indexes[index] == vehicle_index) return 1;
    }
    return 0;
}

int them_vao_hang_cho(HangChoSac *queue, int vehicle_index) {
    if (!queue || vehicle_index < 0 || queue->count >= MAX_QUEUE
        || co_trong_hang_cho(queue, vehicle_index)) {
        return 0;
    }

    queue->vehicle_indexes[queue->rear] = vehicle_index;
    queue->rear = (queue->rear + 1) % MAX_QUEUE;
    queue->count++;
    return 1;
}

int lay_xe_dau_hang(HangChoSac *queue) {
    if (!queue || queue->count == 0) return -1;

    int vehicle_index = queue->vehicle_indexes[queue->front];
    queue->front = (queue->front + 1) % MAX_QUEUE;
    queue->count--;
    return vehicle_index;
}
