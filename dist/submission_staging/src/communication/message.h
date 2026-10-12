#ifndef MESSAGE_H
#define MESSAGE_H

#include <stddef.h>

typedef struct {
	char command[16];
	char vehicle_id[20];
	int port;
	float power_kw;
} ProtocolMessage;

int parse_protocol_message(const char *input, size_t input_length, ProtocolMessage *message);

#endif /* MESSAGE_H */
