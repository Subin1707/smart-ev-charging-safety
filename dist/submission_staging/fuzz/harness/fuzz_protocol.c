#include <stdio.h>
#include <stdlib.h>
#include "message.h"
#include "protocol.h"

int fuzz_protocol_input(const unsigned char *data, size_t size) {
	ProtocolMessage message;
	int parsed = parse_protocol_message((const char *)data, size, &message);
	if (parsed) (void)protocol_message_is_safe(&message);
	return parsed;
}

#ifdef FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION
int LLVMFuzzerTestOneInput(const unsigned char *data, size_t size) {
	fuzz_protocol_input(data, size);
	return 0;
}
#else
int main(void) {
	unsigned char input[512];
	size_t size = fread(input, 1, sizeof(input), stdin);
	printf("parsed=%d\n", fuzz_protocol_input(input, size));
	return 0;
}
#endif
