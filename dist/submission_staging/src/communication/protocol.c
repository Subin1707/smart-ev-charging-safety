#include <string.h>
#include "protocol.h"

int protocol_message_is_safe(const ProtocolMessage *message) {
	if (!message) return 0;
	if (strcmp(message->command, "CONNECT") != 0 &&
		strcmp(message->command, "AUTH") != 0 &&
		strcmp(message->command, "START") != 0 &&
		strcmp(message->command, "STOP") != 0 &&
		strcmp(message->command, "EMERGENCY") != 0) return 0;
	if (message->port < 0 || message->port > 5) return 0;
	if (message->power_kw < 0.0f || message->power_kw > 22.0f) return 0;
	return 1;
}
