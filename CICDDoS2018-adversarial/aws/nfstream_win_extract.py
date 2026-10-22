#!/usr/bin/env python3
"""
NFStream custom plugin untuk ekstraksi Init Fwd/Bwd Win Byts (TCP window size).

NFStream default TIDAK mengekspos TCP window size. Plugin ini membaca raw IP
packet (packet.ip_packet) pada paket PERTAMA tiap arah, mem-parse TCP header,
dan mengambil field Window Size (offset 14-15 dari awal TCP header).

Menghasilkan 2 fitur baru pada flow.udps:
  - init_fwd_win_byts : TCP window paket pertama arah src->dst (Init Fwd Win Byts)
  - init_bwd_win_byts : TCP window paket pertama arah dst->src (Init Bwd Win Byts)

Nilai -1 jika arah tersebut tidak punya paket TCP (mis. UDP flow).
"""
from nfstream import NFPlugin


def _tcp_window_from_ip_packet(ip_packet, protocol):
    """Parse TCP window size (bytes) dari raw IP packet. Return -1 jika bukan TCP/invalid."""
    # protocol 6 = TCP
    if protocol != 6 or ip_packet is None:
        return -1
    try:
        b = ip_packet
        if len(b) < 20:
            return -1
        version = b[0] >> 4
        if version == 4:
            ihl = (b[0] & 0x0F) * 4
        elif version == 6:
            ihl = 40  # IPv6 fixed header (asumsi tanpa extension header)
        else:
            return -1
        tcp_off = ihl
        # TCP window size = byte ke-14 dan 15 dari TCP header (big-endian)
        if len(b) < tcp_off + 16:
            return -1
        window = (b[tcp_off + 14] << 8) | b[tcp_off + 15]
        return window
    except Exception:
        return -1


class InitWindowPlugin(NFPlugin):
    """Ekstrak Init Fwd/Bwd Win Byts dari TCP window paket pertama tiap arah."""

    def on_init(self, packet, flow):
        flow.udps.init_fwd_win_byts = -1
        flow.udps.init_bwd_win_byts = -1
        # Paket pertama flow selalu arah src->dst (direction 0)
        win = _tcp_window_from_ip_packet(packet.ip_packet, packet.protocol)
        if packet.direction == 0:
            flow.udps.init_fwd_win_byts = win
        else:
            flow.udps.init_bwd_win_byts = win

    def on_update(self, packet, flow):
        # Set window arah bwd saat paket dst->src pertama muncul
        if packet.direction == 1 and flow.udps.init_bwd_win_byts == -1:
            flow.udps.init_bwd_win_byts = _tcp_window_from_ip_packet(
                packet.ip_packet, packet.protocol)
        elif packet.direction == 0 and flow.udps.init_fwd_win_byts == -1:
            flow.udps.init_fwd_win_byts = _tcp_window_from_ip_packet(
                packet.ip_packet, packet.protocol)


if __name__ == "__main__":
    import sys
    from nfstream import NFStreamer
    src = sys.argv[1] if len(sys.argv) > 1 else "/tmp/probe3.pcap"
    streamer = NFStreamer(source=src, statistical_analysis=True,
                          udps=[InitWindowPlugin()])
    df = streamer.to_pandas()
    cols = ["src_ip", "dst_ip", "dst_port", "protocol",
            "udps.init_fwd_win_byts", "udps.init_bwd_win_byts"]
    have = [c for c in cols if c in df.columns]
    print("FLOWS", len(df))
    print(df[have].head(20).to_string())
