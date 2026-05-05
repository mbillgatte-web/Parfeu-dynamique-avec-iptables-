# superAdmin/Analyser_scapy.py (version corrigée)

from datetime import datetime, timedelta
from collections import defaultdict
from scapy.all import sniff, IP, TCP, ICMP, ARP

# -----------------------
# Initialisation Django
# -----------------------

from .models import Suggestions

# -----------------------
# Compteurs pour la détection
# -----------------------
traffic_counter = defaultdict(int)
syn_tracker = defaultdict(list)
icmp_tracker = defaultdict(list)
reseau_tracker = defaultdict(list)

# -----------------------
# Helper : extraire informations utiles du paquet
# -----------------------
def extract_info(pkt):
    """
    Retourne dict contenant :
      - proto: "ARP" | "IP" | "OTHER"
      - src, dst (IP ou ARP)
      - sport, dport (ports TCP/UDP si présents, sinon None)
      - tcp_flags (si TCP)
    """
    info = {
        "proto": "OTHER",
        "src": None,
        "dst": None,
        "sport": None,
        "dport": None,
        "tcp_flags": None
    }

    if ARP in pkt:
        info["proto"] = "ARP"
        info["src"] = pkt.psrc   # who sends the ARP request/reply
        info["dst"] = pkt.pdst
        return info

    if IP in pkt:
        info["proto"] = "IP"
        info["src"] = pkt[IP].src
        info["dst"] = pkt[IP].dst
        # TCP/UDP ports
        if TCP in pkt:
            info["sport"] = int(pkt[TCP].sport)
            info["dport"] = int(pkt[TCP].dport)
            info["tcp_flags"] = pkt[TCP].flags
        # (si tu veux UDP, ajoute UDP in pkt)
        return info

    return info

# -----------------------
# Fonction pour créer une suggestion
# -----------------------
def creer_suggestion(packet, anomalie_type, ip_src=None, ip_dst=None, sport=None, dport=None):
    chaine = "FORWARD"
    action = "DROP"  # Par défaut

    if anomalie_type == "icmp_anormal":
        action = "REJECT"
    elif anomalie_type in ["volume_anormal", "scan_reseau"]:
        action = "LOG"
    elif anomalie_type == "port_interdit":
        action = "DROP"
    elif anomalie_type == "syn_flood":
        action = "DROP"

    try:
        suggestion = Suggestions.objects.create(
            description_suggestion=f"Suspicion de {anomalie_type} détectée",
            chaine=chaine,
            protocol="tcp",
            port_source=sport,
            port_destination=dport,
            ip_source=ip_src,
            ip_destination=ip_dst,
            action=action,
            statut="proposee"
        )
        print(f"[SUGGESTION] {anomalie_type} détecté -> Suggestion créée (ID {suggestion.id}) pour {ip_src} -> {ip_dst}")
        return suggestion
    except Exception as e:
        print(f"[ERREUR DB] impossible de créer suggestion : {e}")
        return None

# -----------------------
# Fonction d'analyse d'un paquet Scapy
# -----------------------
def analyser_paquet(packet):
    now = datetime.now()
    info = extract_info(packet)

    # Debug console : affiche résumé + infos extraites
    print("[CAPTURE]", packet.summary())
    print(f"  --> extrait: proto={info['proto']} src={info['src']} dst={info['dst']} sport={info['sport']} dport={info['dport']} flags={info['tcp_flags']}")

    # Si ARP (utile pour nmap -sn sur LAN)
    if info["proto"] == "ARP" and info["src"]:
        # track pour détection scan réseau (ARP scan)
        ip_src = info["src"]
        ip_dst = info["dst"]
        reseau_tracker[ip_src].append((ip_dst, now))
        recent_ips = [p for p in reseau_tracker[ip_src] if now - p[1] < timedelta(seconds=10)]
        reseau_tracker[ip_src] = recent_ips
        unique = set([p[0] for p in recent_ips])
        if len(unique) > 5:
            creer_suggestion(packet, "scan_reseau", ip_src, ip_dst)
        return

    # Si IP
    if info["proto"] == "IP" and info["src"]:
        ip_src = info["src"]
        ip_dst = info["dst"]
        sport = info["sport"]
        dport = info["dport"]
        flags = info["tcp_flags"]

        # ICMP echo request (ping) -> type 8
        if ICMP in packet and packet[ICMP].type == 8:
            icmp_tracker[ip_src].append(now)
            recent = [t for t in icmp_tracker[ip_src] if now - t < timedelta(seconds=10)]
            icmp_tracker[ip_src] = recent
            if len(recent) > 20:
                creer_suggestion(packet, "icmp_anormal", ip_src, ip_dst, sport, dport)

        # SYN (flag SYN)
        if flags is not None:
            # méthode sûre : vérifier bit SYN
            try:
                syn_bit_set = bool(flags & 0x02)
            except Exception:
                # fallback si flags n'est pas bitmask mais str
                syn_bit_set = (str(flags).upper().find("S") != -1 and str(flags).upper().find("A") == -1)
            if syn_bit_set:
                syn_tracker[ip_src].append(now)
                recent_syn = [t for t in syn_tracker[ip_src] if now - t < timedelta(seconds=3)]
                syn_tracker[ip_src] = recent_syn
                if len(recent_syn) > 50:
                    creer_suggestion(packet, "syn_flood", ip_src, ip_dst, sport, dport)

        # Volume anormal
        traffic_counter[ip_src] += 1
        if traffic_counter[ip_src] > 100:
            creer_suggestion(packet, "volume_anormal", ip_src, ip_dst, sport, dport)
            traffic_counter[ip_src] = 0

        # Ports interdits (examiner dport et sport)
        if (dport in (21, 23, 445)) or (sport in (21, 23, 445)):
            creer_suggestion(packet, "port_interdit", ip_src, ip_dst, sport, dport)

        # Scan réseau (IP-level)
        reseau_tracker[ip_src].append((ip_dst, now))
        recent_ips = [p for p in reseau_tracker[ip_src] if now - p[1] < timedelta(seconds=10)]
        reseau_tracker[ip_src] = recent_ips
        unique_ips = set([p[0] for p in recent_ips])
        if len(unique_ips) > 5:
            creer_suggestion(packet, "scan_reseau", ip_src, ip_dst, sport, dport)

# -----------------------
# Lancement de la capture Scapy
# -----------------------
def lancer_capture():
    interfaces = ["ens33"]  # adapte selon ton interface
    print(f"[INFO] Capture Scapy démarrée sur {interfaces}...")
    for iface in interfaces:
        sniff(iface=iface, prn=analyser_paquet, store=False, lfilter=lambda p: (ARP in p) or (IP in p))

# Si tu veux exécuter directement pour debug
if __name__ == "__main__":
    lancer_capture()