#ifndef PROTOCOL_H
#define PROTOCOL_H

#include "message.h"

int protocol_message_is_safe(const ProtocolMessage *message);

#endif /* PROTOCOL_H */
