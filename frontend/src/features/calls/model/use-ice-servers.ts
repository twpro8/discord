// relative
import { getTurnCredentials } from "../api/get-turn-credentials";

/** Fetches the ICE server list for a call that's genuinely about to
 * start. Deliberately has no hardcoded fallback list here — the
 * backend's STUN_URLS/TURN_URLS settings are the single source of ICE
 * server config (see calls/application/turn_credentials.py); a fetch
 * failure means the app can't reach the backend at all (the same
 * backend the realtime WebSocket depends on), so a silent client-side
 * fallback wouldn't meaningfully help. Callers should treat a rejected
 * promise as a failed call-start attempt. */
export async function getIceServers(): Promise<RTCIceServer[]> {
  const { ice_servers } = await getTurnCredentials();
  return ice_servers;
}
