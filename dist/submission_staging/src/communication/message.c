#include <stdlib.h>
#include <string.h>
#include "message.h"

static int copy_field(char *destination, size_t destination_size,
					  const char *start, size_t length) {
	if (length == 0 || length >= destination_size) return 0;
	memcpy(destination, start, length);
	destination[length] = '\0';
	return 1;
}

int parse_protocol_message(const char *input, size_t input_length, ProtocolMessage *message) {
	const char *field_start;
	size_t field_length;
	int field = 0;

	if (!input || !message || input_length == 0 || input_length > 256) return 0;
	memset(message, 0, sizeof(*message));
	field_start = input;

	for (size_t i = 0; i <= input_length; i++) {
		if (i != input_length && input[i] != '|') continue;
		field_length = input + i - field_start;
		if (field == 0 && !copy_field(message->command, sizeof(message->command), field_start, field_length)) return 0;
		if (field == 1 && !copy_field(message->vehicle_id, sizeof(message->vehicle_id), field_start, field_length)) return 0;
		if (field == 2) {
			char port_text[12];
			if (!copy_field(port_text, sizeof(port_text), field_start, field_length)) return 0;
			message->port = atoi(port_text);
		}
		if (field == 3) {
			char power_text[24];
			if (!copy_field(power_text, sizeof(power_text), field_start, field_length)) return 0;
			message->power_kw = (float)atof(power_text);
		}
		field++;
		field_start = input + i + 1;
	}

	return field == 4;
}
