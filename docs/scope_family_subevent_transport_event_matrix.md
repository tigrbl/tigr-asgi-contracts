# Scope Family Subevent Transport Event Matrix

Legend: R required, O optional, D derived/dependent, F forbidden. Each row has exactly one scope, one family, one subevent, and one transport event type. Empty transport event cells are explicit no-event mappings for that scope.

| Scope | Family | Subevent | Transport event | Direction | Scope supported | Event supported | Bindings | Protocols | rest | jsonrpc | http.stream | sse | websocket | webtransport |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| http | request | request.open | http.request | receive | yes | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | R | R | R | R | F | F |
| http | request | request.body_in | http.request | receive | yes | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | R | R | O | O | F | F |
| http | request | request.chunk_in | http.request | receive | yes | yes | http.stream | http.stream, https.stream | F | F | D | F | F | F |
| http | request | request.accept | http.request | receive | yes | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | O | O | O | O | F | F |
| http | request | request.close | http.request | receive | yes | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | R | R | R | R | F | F |
| http | request | request.disconnect | http.disconnect | receive | yes | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | O | O | O | O | F | F |
| http | request | response.open | http.response.start | send | yes | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | R | R | R | O | F | F |
| http | request | response.body_out | http.response.body | send | yes | yes | rest, jsonrpc, http.stream | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream | R | R | O | F | F | F |
| http | request | response.chunk_out | http.response.body | send | yes | yes | http.stream, sse | http.stream, https.stream, http.sse, https.sse | F | F | D | D | F | F |
| http | request | response.close | http.response.body | send | yes | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | O | O | O | O | F | F |
| http | request | response.emit_complete | transport.emit.complete | send | yes | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | R | R | R | R | F | F |
| http | session | session.open |  |  | yes | no | sse | http.sse, https.sse | F | F | F | R | F | F |
| http | session | session.accept |  |  | yes | no | sse | http.sse, https.sse | F | F | F | R | F | F |
| http | session | session.ready |  |  | yes | no | sse | http.sse, https.sse | F | F | F | R | F | F |
| http | session | session.heartbeat |  |  | yes | no | sse | http.sse, https.sse | F | F | F | O | F | F |
| http | session | session.sync |  |  | yes | no | sse | http.sse, https.sse | F | F | F | O | F | F |
| http | session | session.close |  |  | yes | no | sse | http.sse, https.sse | F | F | F | R | F | F |
| http | session | session.disconnect |  |  | yes | no | sse | http.sse, https.sse | F | F | F | O | F | F |
| http | session | session.emit_complete | transport.emit.complete | send | yes | yes | sse | http.sse, https.sse | F | F | F | O | F | F |
| http | message | message.in |  |  | no | no |  |  | F | F | F | F | F | F |
| http | message | message.decode |  |  | yes | no | jsonrpc | http.jsonrpc, https.jsonrpc | F | D | F | F | F | F |
| http | message | message.handle |  |  | no | no |  |  | F | F | F | F | F | F |
| http | message | message.out | http.response.body | send | yes | yes | sse | http.sse, https.sse | F | F | F | R | F | F |
| http | message | message.ack |  |  | no | no |  |  | F | F | F | F | F | F |
| http | message | message.nack |  |  | no | no |  |  | F | F | F | F | F | F |
| http | message | message.replay | http.response.body | send | yes | yes | sse | http.sse, https.sse | F | F | F | O | F | F |
| http | message | message.snapshot | http.response.body | send | yes | yes | sse | http.sse, https.sse | F | F | F | O | F | F |
| http | message | message.emit_complete | transport.emit.complete | send | yes | yes | sse | http.sse, https.sse | F | F | F | R | F | F |
| http | stream | stream.open | http.response.start | send | yes | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | O | O | R | R | F | F |
| http | stream | stream.chunk_in | http.request | receive | yes | yes | rest, jsonrpc, http.stream | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream | O | O | R | F | F | F |
| http | stream | stream.chunk_out | http.response.body | send | yes | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | O | O | R | R | F | F |
| http | stream | stream.flush | http.response.body | send | yes | yes | http.stream, sse | http.stream, https.stream, http.sse, https.sse | F | F | O | O | F | F |
| http | stream | stream.finalize | http.response.body | send | yes | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | O | O | R | O | F | F |
| http | stream | stream.abort | http.disconnect | receive | yes | yes | http.stream, sse | http.stream, https.stream, http.sse, https.sse | F | F | O | O | F | F |
| http | stream | stream.close | http.response.body | send | yes | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | O | O | R | R | F | F |
| http | stream | stream.emit_complete | transport.emit.complete | send | yes | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | O | O | R | R | F | F |
| http | datagram | datagram.in |  |  | no | no |  |  | F | F | F | F | F | F |
| http | datagram | datagram.handle |  |  | no | no |  |  | F | F | F | F | F | F |
| http | datagram | datagram.out |  |  | no | no |  |  | F | F | F | F | F | F |
| http | datagram | datagram.ack |  |  | no | no |  |  | F | F | F | F | F | F |
| http | datagram | datagram.emit_complete | transport.emit.complete | send | no | yes |  |  | F | F | F | F | F | F |
| websocket | request | request.open |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | request | request.body_in |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | request | request.chunk_in |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | request | request.accept |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | request | request.close |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | request | request.disconnect |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | request | response.open |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | request | response.body_out |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | request | response.chunk_out |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | request | response.close |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | request | response.emit_complete | transport.emit.complete | send | no | yes |  |  | F | F | F | F | F | F |
| websocket | session | session.open | websocket.connect | receive | yes | yes | websocket | ws, wss | F | F | F | F | R | F |
| websocket | session | session.accept | websocket.accept | send | yes | yes | websocket | ws, wss | F | F | F | F | R | F |
| websocket | session | session.ready | websocket.accept | send | yes | yes | websocket | ws, wss | F | F | F | F | R | F |
| websocket | session | session.heartbeat | websocket.send | send | yes | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | session | session.sync | websocket.send | send | yes | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | session | session.close | websocket.close | send | yes | yes | websocket | ws, wss | F | F | F | F | R | F |
| websocket | session | session.disconnect | websocket.disconnect | receive | yes | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | session | session.emit_complete | transport.emit.complete | send | yes | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | message | message.in | websocket.receive | receive | yes | yes | websocket | ws, wss | F | F | F | F | R | F |
| websocket | message | message.decode | websocket.receive | receive | yes | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | message | message.handle | websocket.receive | receive | yes | yes | websocket | ws, wss | F | F | F | F | R | F |
| websocket | message | message.out | websocket.send | send | yes | yes | websocket | ws, wss | F | F | F | F | R | F |
| websocket | message | message.ack | websocket.send | send | yes | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | message | message.nack | websocket.send | send | yes | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | message | message.replay | websocket.send | send | yes | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | message | message.snapshot | websocket.send | send | yes | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | message | message.emit_complete | transport.emit.complete | send | yes | yes | websocket | ws, wss | F | F | F | F | R | F |
| websocket | stream | stream.open |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | stream | stream.chunk_in |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | stream | stream.chunk_out |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | stream | stream.flush |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | stream | stream.finalize |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | stream | stream.abort |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | stream | stream.close |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | stream | stream.emit_complete | transport.emit.complete | send | no | yes |  |  | F | F | F | F | F | F |
| websocket | datagram | datagram.in |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | datagram | datagram.handle |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | datagram | datagram.out |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | datagram | datagram.ack |  |  | no | no |  |  | F | F | F | F | F | F |
| websocket | datagram | datagram.emit_complete | transport.emit.complete | send | no | yes |  |  | F | F | F | F | F | F |
| webtransport | request | request.open |  |  | no | no |  |  | F | F | F | F | F | F |
| webtransport | request | request.body_in |  |  | no | no |  |  | F | F | F | F | F | F |
| webtransport | request | request.chunk_in |  |  | no | no |  |  | F | F | F | F | F | F |
| webtransport | request | request.accept |  |  | no | no |  |  | F | F | F | F | F | F |
| webtransport | request | request.close |  |  | no | no |  |  | F | F | F | F | F | F |
| webtransport | request | request.disconnect |  |  | no | no |  |  | F | F | F | F | F | F |
| webtransport | request | response.open |  |  | no | no |  |  | F | F | F | F | F | F |
| webtransport | request | response.body_out |  |  | no | no |  |  | F | F | F | F | F | F |
| webtransport | request | response.chunk_out |  |  | no | no |  |  | F | F | F | F | F | F |
| webtransport | request | response.close |  |  | no | no |  |  | F | F | F | F | F | F |
| webtransport | request | response.emit_complete | transport.emit.complete | send | no | yes |  |  | F | F | F | F | F | F |
| webtransport | session | session.open | webtransport.connect | receive | yes | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | session | session.accept | webtransport.accept | send | yes | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | session | session.ready | webtransport.accept | send | yes | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | session | session.heartbeat | webtransport.stream.send | send | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | session | session.sync | webtransport.stream.send | send | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | session | session.close | webtransport.close | send | yes | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | session | session.disconnect | webtransport.disconnect | receive | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | session | session.emit_complete | transport.emit.complete | send | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.in | webtransport.stream.receive | receive | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.in | webtransport.datagram.receive | receive | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.decode | webtransport.stream.receive | receive | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.decode | webtransport.datagram.receive | receive | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.handle | webtransport.stream.receive | receive | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.handle | webtransport.datagram.receive | receive | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.out | webtransport.stream.send | send | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.ack | webtransport.stream.send | send | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.ack | webtransport.datagram.send | send | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.nack | webtransport.stream.send | send | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.nack | webtransport.datagram.send | send | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.replay | webtransport.stream.send | send | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.snapshot | webtransport.stream.send | send | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.emit_complete | transport.emit.complete | send | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | stream | stream.open | webtransport.stream.send | send | yes | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | stream | stream.chunk_in | webtransport.stream.receive | receive | yes | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | stream | stream.chunk_out | webtransport.stream.send | send | yes | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | stream | stream.flush | webtransport.stream.send | send | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | stream | stream.finalize | webtransport.stream.send | send | yes | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | stream | stream.abort | webtransport.close | send | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | stream | stream.close | webtransport.close | send | yes | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | stream | stream.emit_complete | transport.emit.complete | send | yes | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | datagram | datagram.in | webtransport.datagram.receive | receive | yes | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | datagram | datagram.handle | webtransport.datagram.receive | receive | yes | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | datagram | datagram.out | webtransport.datagram.send | send | yes | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | datagram | datagram.ack | webtransport.datagram.send | send | yes | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | datagram | datagram.emit_complete | transport.emit.complete | send | yes | yes | webtransport | webtransport | F | F | F | F | F | R |
| lifespan | request | request.open |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | request | request.body_in |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | request | request.chunk_in |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | request | request.accept |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | request | request.close |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | request | request.disconnect |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | request | response.open |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | request | response.body_out |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | request | response.chunk_out |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | request | response.close |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | request | response.emit_complete |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | session | session.open |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | session | session.accept |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | session | session.ready |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | session | session.heartbeat |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | session | session.sync |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | session | session.close |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | session | session.disconnect |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | session | session.emit_complete |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.in |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.decode |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.handle |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.out |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.ack |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.nack |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.replay |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.snapshot |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.emit_complete |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | stream | stream.open |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | stream | stream.chunk_in |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | stream | stream.chunk_out |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | stream | stream.flush |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | stream | stream.finalize |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | stream | stream.abort |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | stream | stream.close |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | stream | stream.emit_complete |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | datagram | datagram.in |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | datagram | datagram.handle |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | datagram | datagram.out |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | datagram | datagram.ack |  |  | no | no |  |  | F | F | F | F | F | F |
| lifespan | datagram | datagram.emit_complete |  |  | no | no |  |  | F | F | F | F | F | F |
