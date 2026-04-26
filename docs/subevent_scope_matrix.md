# Subevent Scope Matrix

Legend: R required, O optional, D derived/dependent, F forbidden.

| Family | Subevent | Direction | Transport events | rest | jsonrpc | http.stream | sse | websocket | webtransport |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| request | request.open | receive | http.request | R | R | R | R | F | F |
| request | request.body_in | receive | http.request | R | R | O | O | F | F |
| request | request.chunk_in | receive | http.request | F | F | D | F | F | F |
| request | request.accept | receive | http.request | O | O | O | O | F | F |
| request | request.close | receive | http.request | R | R | R | R | F | F |
| request | request.disconnect | receive | http.disconnect | O | O | O | O | F | F |
| request | response.open | send | http.response.start | R | R | R | O | F | F |
| request | response.body_out | send | http.response.body | R | R | O | F | F | F |
| request | response.chunk_out | send | http.response.body | F | F | D | D | F | F |
| request | response.close | send | http.response.body | O | O | O | O | F | F |
| request | response.emit_complete | send | transport.emit.complete | R | R | R | R | F | F |
| session | session.open | receive | websocket.connect, webtransport.connect | F | F | F | R | R | R |
| session | session.accept | send | websocket.accept, webtransport.accept | F | F | F | R | R | R |
| session | session.ready | send | websocket.accept, webtransport.accept | F | F | F | R | R | R |
| session | session.heartbeat | send | websocket.send, webtransport.stream.send | F | F | F | O | O | O |
| session | session.sync | send | websocket.send, webtransport.stream.send | F | F | F | O | O | O |
| session | session.close | send | websocket.close, webtransport.close | F | F | F | R | R | R |
| session | session.disconnect | receive | websocket.disconnect, webtransport.disconnect | F | F | F | O | O | O |
| session | session.emit_complete | send | transport.emit.complete | F | F | F | O | O | O |
| message | message.in | receive | websocket.receive, webtransport.stream.receive, webtransport.datagram.receive | F | F | F | F | R | O |
| message | message.decode | receive | websocket.receive, webtransport.stream.receive, webtransport.datagram.receive | F | D | F | F | O | O |
| message | message.handle | receive | websocket.receive, webtransport.stream.receive, webtransport.datagram.receive | F | F | F | F | R | O |
| message | message.out | send | http.response.body, websocket.send, webtransport.stream.send | F | F | F | R | R | O |
| message | message.ack | send | websocket.send, webtransport.stream.send, webtransport.datagram.send | F | F | F | F | O | O |
| message | message.nack | send | websocket.send, webtransport.stream.send, webtransport.datagram.send | F | F | F | F | O | O |
| message | message.replay | send | http.response.body, websocket.send, webtransport.stream.send | F | F | F | O | O | O |
| message | message.snapshot | send | http.response.body, websocket.send, webtransport.stream.send | F | F | F | O | O | O |
| message | message.emit_complete | send | transport.emit.complete | F | F | F | R | R | O |
| stream | stream.open | send | http.response.start, webtransport.stream.send | O | O | R | R | F | R |
| stream | stream.chunk_in | receive | http.request, webtransport.stream.receive | O | O | R | F | F | R |
| stream | stream.chunk_out | send | http.response.body, webtransport.stream.send | O | O | R | R | F | R |
| stream | stream.flush | send | http.response.body, webtransport.stream.send | F | F | O | O | F | O |
| stream | stream.finalize | send | http.response.body, webtransport.stream.send | O | O | R | O | F | R |
| stream | stream.abort | receive/send | http.disconnect, webtransport.close | F | F | O | O | F | O |
| stream | stream.close | send | http.response.body, webtransport.close | O | O | R | R | F | R |
| stream | stream.emit_complete | send | transport.emit.complete | O | O | R | R | F | R |
| datagram | datagram.in | receive | webtransport.datagram.receive | F | F | F | F | F | R |
| datagram | datagram.handle | receive | webtransport.datagram.receive | F | F | F | F | F | R |
| datagram | datagram.out | send | webtransport.datagram.send | F | F | F | F | F | R |
| datagram | datagram.ack | send | webtransport.datagram.send | F | F | F | F | F | O |
| datagram | datagram.emit_complete | send | transport.emit.complete | F | F | F | F | F | R |
