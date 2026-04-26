# Scope Family Subevent Matrix

Legend: R required, O optional, D derived/dependent, F forbidden. Each row has exactly one scope, one family, and one subevent.

| Scope | Family | Subevent | Direction | Transport events | Supported | Bindings | Protocols | rest | jsonrpc | http.stream | sse | websocket | webtransport |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| http | request | request.open | receive | http.request | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | R | R | R | R | F | F |
| http | request | request.body_in | receive | http.request | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | R | R | O | O | F | F |
| http | request | request.chunk_in | receive | http.request | yes | http.stream | http.stream, https.stream | F | F | D | F | F | F |
| http | request | request.accept | receive | http.request | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | O | O | O | O | F | F |
| http | request | request.close | receive | http.request | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | R | R | R | R | F | F |
| http | request | request.disconnect | receive | http.disconnect | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | O | O | O | O | F | F |
| http | request | response.open | send | http.response.start | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | R | R | R | O | F | F |
| http | request | response.body_out | send | http.response.body | yes | rest, jsonrpc, http.stream | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream | R | R | O | F | F | F |
| http | request | response.chunk_out | send | http.response.body | yes | http.stream, sse | http.stream, https.stream, http.sse, https.sse | F | F | D | D | F | F |
| http | request | response.close | send | http.response.body | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | O | O | O | O | F | F |
| http | request | response.emit_complete | send | transport.emit.complete | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | R | R | R | R | F | F |
| http | session | session.open |  |  | yes | sse | http.sse, https.sse | F | F | F | R | F | F |
| http | session | session.accept |  |  | yes | sse | http.sse, https.sse | F | F | F | R | F | F |
| http | session | session.ready |  |  | yes | sse | http.sse, https.sse | F | F | F | R | F | F |
| http | session | session.heartbeat |  |  | yes | sse | http.sse, https.sse | F | F | F | O | F | F |
| http | session | session.sync |  |  | yes | sse | http.sse, https.sse | F | F | F | O | F | F |
| http | session | session.close |  |  | yes | sse | http.sse, https.sse | F | F | F | R | F | F |
| http | session | session.disconnect |  |  | yes | sse | http.sse, https.sse | F | F | F | O | F | F |
| http | session | session.emit_complete | send | transport.emit.complete | yes | sse | http.sse, https.sse | F | F | F | O | F | F |
| http | message | message.in |  |  | no |  |  | F | F | F | F | F | F |
| http | message | message.decode |  |  | yes | jsonrpc | http.jsonrpc, https.jsonrpc | F | D | F | F | F | F |
| http | message | message.handle |  |  | no |  |  | F | F | F | F | F | F |
| http | message | message.out | send | http.response.body | yes | sse | http.sse, https.sse | F | F | F | R | F | F |
| http | message | message.ack |  |  | no |  |  | F | F | F | F | F | F |
| http | message | message.nack |  |  | no |  |  | F | F | F | F | F | F |
| http | message | message.replay | send | http.response.body | yes | sse | http.sse, https.sse | F | F | F | O | F | F |
| http | message | message.snapshot | send | http.response.body | yes | sse | http.sse, https.sse | F | F | F | O | F | F |
| http | message | message.emit_complete | send | transport.emit.complete | yes | sse | http.sse, https.sse | F | F | F | R | F | F |
| http | stream | stream.open | send | http.response.start | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | O | O | R | R | F | F |
| http | stream | stream.chunk_in | receive | http.request | yes | rest, jsonrpc, http.stream | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream | O | O | R | F | F | F |
| http | stream | stream.chunk_out | send | http.response.body | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | O | O | R | R | F | F |
| http | stream | stream.flush | send | http.response.body | yes | http.stream, sse | http.stream, https.stream, http.sse, https.sse | F | F | O | O | F | F |
| http | stream | stream.finalize | send | http.response.body | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | O | O | R | O | F | F |
| http | stream | stream.abort | receive | http.disconnect | yes | http.stream, sse | http.stream, https.stream, http.sse, https.sse | F | F | O | O | F | F |
| http | stream | stream.close | send | http.response.body | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | O | O | R | R | F | F |
| http | stream | stream.emit_complete | send | transport.emit.complete | yes | rest, jsonrpc, http.stream, sse | http.rest, https.rest, http.jsonrpc, https.jsonrpc, http.stream, https.stream, http.sse, https.sse | O | O | R | R | F | F |
| http | datagram | datagram.in |  |  | no |  |  | F | F | F | F | F | F |
| http | datagram | datagram.handle |  |  | no |  |  | F | F | F | F | F | F |
| http | datagram | datagram.out |  |  | no |  |  | F | F | F | F | F | F |
| http | datagram | datagram.ack |  |  | no |  |  | F | F | F | F | F | F |
| http | datagram | datagram.emit_complete | send | transport.emit.complete | no |  |  | F | F | F | F | F | F |
| websocket | request | request.open |  |  | no |  |  | F | F | F | F | F | F |
| websocket | request | request.body_in |  |  | no |  |  | F | F | F | F | F | F |
| websocket | request | request.chunk_in |  |  | no |  |  | F | F | F | F | F | F |
| websocket | request | request.accept |  |  | no |  |  | F | F | F | F | F | F |
| websocket | request | request.close |  |  | no |  |  | F | F | F | F | F | F |
| websocket | request | request.disconnect |  |  | no |  |  | F | F | F | F | F | F |
| websocket | request | response.open |  |  | no |  |  | F | F | F | F | F | F |
| websocket | request | response.body_out |  |  | no |  |  | F | F | F | F | F | F |
| websocket | request | response.chunk_out |  |  | no |  |  | F | F | F | F | F | F |
| websocket | request | response.close |  |  | no |  |  | F | F | F | F | F | F |
| websocket | request | response.emit_complete | send | transport.emit.complete | no |  |  | F | F | F | F | F | F |
| websocket | session | session.open | receive | websocket.connect | yes | websocket | ws, wss | F | F | F | F | R | F |
| websocket | session | session.accept | send | websocket.accept | yes | websocket | ws, wss | F | F | F | F | R | F |
| websocket | session | session.ready | send | websocket.accept | yes | websocket | ws, wss | F | F | F | F | R | F |
| websocket | session | session.heartbeat | send | websocket.send | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | session | session.sync | send | websocket.send | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | session | session.close | send | websocket.close | yes | websocket | ws, wss | F | F | F | F | R | F |
| websocket | session | session.disconnect | receive | websocket.disconnect | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | session | session.emit_complete | send | transport.emit.complete | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | message | message.in | receive | websocket.receive | yes | websocket | ws, wss | F | F | F | F | R | F |
| websocket | message | message.decode | receive | websocket.receive | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | message | message.handle | receive | websocket.receive | yes | websocket | ws, wss | F | F | F | F | R | F |
| websocket | message | message.out | send | websocket.send | yes | websocket | ws, wss | F | F | F | F | R | F |
| websocket | message | message.ack | send | websocket.send | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | message | message.nack | send | websocket.send | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | message | message.replay | send | websocket.send | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | message | message.snapshot | send | websocket.send | yes | websocket | ws, wss | F | F | F | F | O | F |
| websocket | message | message.emit_complete | send | transport.emit.complete | yes | websocket | ws, wss | F | F | F | F | R | F |
| websocket | stream | stream.open |  |  | no |  |  | F | F | F | F | F | F |
| websocket | stream | stream.chunk_in |  |  | no |  |  | F | F | F | F | F | F |
| websocket | stream | stream.chunk_out |  |  | no |  |  | F | F | F | F | F | F |
| websocket | stream | stream.flush |  |  | no |  |  | F | F | F | F | F | F |
| websocket | stream | stream.finalize |  |  | no |  |  | F | F | F | F | F | F |
| websocket | stream | stream.abort |  |  | no |  |  | F | F | F | F | F | F |
| websocket | stream | stream.close |  |  | no |  |  | F | F | F | F | F | F |
| websocket | stream | stream.emit_complete | send | transport.emit.complete | no |  |  | F | F | F | F | F | F |
| websocket | datagram | datagram.in |  |  | no |  |  | F | F | F | F | F | F |
| websocket | datagram | datagram.handle |  |  | no |  |  | F | F | F | F | F | F |
| websocket | datagram | datagram.out |  |  | no |  |  | F | F | F | F | F | F |
| websocket | datagram | datagram.ack |  |  | no |  |  | F | F | F | F | F | F |
| websocket | datagram | datagram.emit_complete | send | transport.emit.complete | no |  |  | F | F | F | F | F | F |
| webtransport | request | request.open |  |  | no |  |  | F | F | F | F | F | F |
| webtransport | request | request.body_in |  |  | no |  |  | F | F | F | F | F | F |
| webtransport | request | request.chunk_in |  |  | no |  |  | F | F | F | F | F | F |
| webtransport | request | request.accept |  |  | no |  |  | F | F | F | F | F | F |
| webtransport | request | request.close |  |  | no |  |  | F | F | F | F | F | F |
| webtransport | request | request.disconnect |  |  | no |  |  | F | F | F | F | F | F |
| webtransport | request | response.open |  |  | no |  |  | F | F | F | F | F | F |
| webtransport | request | response.body_out |  |  | no |  |  | F | F | F | F | F | F |
| webtransport | request | response.chunk_out |  |  | no |  |  | F | F | F | F | F | F |
| webtransport | request | response.close |  |  | no |  |  | F | F | F | F | F | F |
| webtransport | request | response.emit_complete | send | transport.emit.complete | no |  |  | F | F | F | F | F | F |
| webtransport | session | session.open | receive | webtransport.connect | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | session | session.accept | send | webtransport.accept | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | session | session.ready | send | webtransport.accept | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | session | session.heartbeat | send | webtransport.stream.send | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | session | session.sync | send | webtransport.stream.send | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | session | session.close | send | webtransport.close | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | session | session.disconnect | receive | webtransport.disconnect | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | session | session.emit_complete | send | transport.emit.complete | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.in | receive | webtransport.stream.receive, webtransport.datagram.receive | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.decode | receive | webtransport.stream.receive, webtransport.datagram.receive | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.handle | receive | webtransport.stream.receive, webtransport.datagram.receive | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.out | send | webtransport.stream.send | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.ack | send | webtransport.stream.send, webtransport.datagram.send | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.nack | send | webtransport.stream.send, webtransport.datagram.send | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.replay | send | webtransport.stream.send | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.snapshot | send | webtransport.stream.send | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | message | message.emit_complete | send | transport.emit.complete | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | stream | stream.open | send | webtransport.stream.send | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | stream | stream.chunk_in | receive | webtransport.stream.receive | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | stream | stream.chunk_out | send | webtransport.stream.send | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | stream | stream.flush | send | webtransport.stream.send | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | stream | stream.finalize | send | webtransport.stream.send | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | stream | stream.abort | send | webtransport.close | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | stream | stream.close | send | webtransport.close | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | stream | stream.emit_complete | send | transport.emit.complete | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | datagram | datagram.in | receive | webtransport.datagram.receive | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | datagram | datagram.handle | receive | webtransport.datagram.receive | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | datagram | datagram.out | send | webtransport.datagram.send | yes | webtransport | webtransport | F | F | F | F | F | R |
| webtransport | datagram | datagram.ack | send | webtransport.datagram.send | yes | webtransport | webtransport | F | F | F | F | F | O |
| webtransport | datagram | datagram.emit_complete | send | transport.emit.complete | yes | webtransport | webtransport | F | F | F | F | F | R |
| lifespan | request | request.open |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | request | request.body_in |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | request | request.chunk_in |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | request | request.accept |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | request | request.close |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | request | request.disconnect |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | request | response.open |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | request | response.body_out |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | request | response.chunk_out |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | request | response.close |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | request | response.emit_complete |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | session | session.open |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | session | session.accept |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | session | session.ready |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | session | session.heartbeat |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | session | session.sync |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | session | session.close |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | session | session.disconnect |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | session | session.emit_complete |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.in |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.decode |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.handle |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.out |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.ack |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.nack |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.replay |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.snapshot |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | message | message.emit_complete |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | stream | stream.open |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | stream | stream.chunk_in |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | stream | stream.chunk_out |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | stream | stream.flush |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | stream | stream.finalize |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | stream | stream.abort |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | stream | stream.close |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | stream | stream.emit_complete |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | datagram | datagram.in |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | datagram | datagram.handle |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | datagram | datagram.out |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | datagram | datagram.ack |  |  | no |  |  | F | F | F | F | F | F |
| lifespan | datagram | datagram.emit_complete |  |  | no |  |  | F | F | F | F | F | F |
