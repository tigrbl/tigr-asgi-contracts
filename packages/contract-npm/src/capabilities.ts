export interface FamilyCapabilities {
  request?: boolean;
  session?: boolean;
  message?: boolean;
  stream_in?: boolean;
  stream_out?: boolean;
  datagram?: boolean;
  lifespan?: boolean;
}
