import json
import re
import subprocess
from django.conf import settings

try:
    import anthropic
except ImportError:
    anthropic = None


SYSTEM_PROMPT = """Tu es un assistant IA spécialisé en sécurité réseau et administration de pare-feu iptables.
Tu es intégré dans une application web Django de gestion de pare-feu dynamique.

Ton rôle :
1. **Expliquer** les règles iptables existantes en langage simple et clair
2. **Suggérer** des règles iptables en réponse aux demandes de l'administrateur
3. **Analyser** les alertes et suggestions de sécurité
4. **Conseiller** sur les bonnes pratiques de sécurité réseau
5. **Exécuter** des actions réseau via les outils disponibles (scanner, autoriser/bloquer internet, lister les règles)

Contexte technique du projet :
- Machine Ubuntu (passerelle) : ens33 = WAN (accès internet), ens37 = 192.168.10.1 (LAN interne)
- Les machines clientes (Windows, etc.) sont sur le réseau 192.168.10.0/24
- Tables gérées : Filter (INPUT, OUTPUT, FORWARD), NAT (SNAT, DNAT, MASQUERADE), Mangle
- Actions disponibles : ACCEPT, DROP, REJECT, LOG
- Protocoles : TCP, UDP, ICMP, ALL

Quand l'utilisateur te demande d'exécuter une action (scanner le réseau, autoriser/bloquer internet, lister les règles),
utilise les outils (tools) disponibles pour l'effectuer directement. Après l'exécution, explique le résultat en français.

Réponds toujours en français. Sois concis mais précis. Utilise un langage accessible même pour un débutant."""


TOOLS_DEFINITION = [
    {
        "name": "scanner_reseau",
        "description": "Scanner le réseau local 192.168.10.0/24 pour trouver les machines connectées.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "autoriser_internet",
        "description": "Autoriser l'accès internet à une machine du réseau local en ajoutant une règle NAT MASQUERADE.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ip_address": {
                    "type": "string",
                    "description": "L'adresse IP de la machine à autoriser (ex: 192.168.10.2)"
                }
            },
            "required": ["ip_address"]
        }
    },
    {
        "name": "bloquer_internet",
        "description": "Bloquer l'accès internet d'une machine du réseau local en supprimant sa règle NAT MASQUERADE.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ip_address": {
                    "type": "string",
                    "description": "L'adresse IP de la machine à bloquer (ex: 192.168.10.2)"
                }
            },
            "required": ["ip_address"]
        }
    },
    {
        "name": "lister_regles",
        "description": "Lister toutes les règles iptables actuellement actives (tables filter et nat).",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
]


# =====================
# Fonctions des tools
# =====================

def tool_scanner_reseau():
    try:
        ping_cmd = "for i in $(seq 1 254); do ping -c 1 -W 1 192.168.10.$i > /dev/null 2>&1 & done; wait"
        subprocess.run(["bash", "-c", ping_cmd], timeout=30, capture_output=True)

        result = subprocess.run(
            ["ip", "neigh", "show", "dev", "ens37"],
            capture_output=True, text=True, timeout=5
        )

        if result.returncode != 0:
            return f"Erreur lors du scan: {result.stderr}"

        lines = result.stdout.strip().split("\n")
        hosts = []
        for line in lines:
            if not line.strip():
                continue
            parts = line.split()
            ip = parts[0]
            mac = parts[4] if len(parts) >= 5 else "inconnu"
            state = parts[-1] if parts else ""
            if state in ("REACHABLE", "STALE", "DELAY"):
                hosts.append(f"  - {ip} (MAC: {mac}, état: {state})")

        if hosts:
            return f"Machines détectées sur 192.168.10.0/24 :\n" + "\n".join(hosts)
        return "Aucune machine détectée sur le réseau 192.168.10.0/24."
    except subprocess.TimeoutExpired:
        return "Le scan réseau a expiré (timeout)."
    except Exception as e:
        return f"Erreur lors du scan réseau: {str(e)}"


def tool_autoriser_internet(ip_address):
    from .models import Regles_NAT
    if not re.match(r'^192\.168\.10\.\d{1,3}$', ip_address):
        return f"Erreur: adresse IP invalide ou hors du réseau local: {ip_address}"
    try:
        cmd = ["sudo", "/usr/sbin/iptables", "-t", "nat", "-A", "POSTROUTING",
               "-o", "ens33", "-s", ip_address, "-j", "MASQUERADE"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            Regles_NAT.objects.create(
                type="MASQUERADE",
                protocol="all",
                ip_source=ip_address,
                interface_sortie="ens33",
                description=f"Accès internet pour {ip_address} (via chatbot IA)"
            )
            return f"Règle MASQUERADE ajoutée avec succès pour {ip_address}. Cette machine a maintenant accès à internet."
        return f"Erreur lors de l'ajout de la règle: {result.stderr}"
    except Exception as e:
        return f"Erreur: {str(e)}"


def tool_bloquer_internet(ip_address):
    from .models import Regles_NAT
    if not re.match(r'^192\.168\.10\.\d{1,3}$', ip_address):
        return f"Erreur: adresse IP invalide ou hors du réseau local: {ip_address}"
    try:
        cmd = ["sudo", "/usr/sbin/iptables", "-t", "nat", "-D", "POSTROUTING",
               "-o", "ens33", "-s", ip_address, "-j", "MASQUERADE"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            Regles_NAT.objects.filter(
                type="MASQUERADE",
                ip_source=ip_address,
                interface_sortie="ens33"
            ).delete()
            return f"Règle MASQUERADE supprimée pour {ip_address}. Cette machine n'a plus accès à internet."
        return f"Erreur lors de la suppression: {result.stderr}"
    except Exception as e:
        return f"Erreur: {str(e)}"


def tool_lister_regles():
    try:
        output = ""
        r1 = subprocess.run(
            ["sudo", "/usr/sbin/iptables", "-L", "-n", "-v", "--line-numbers"],
            capture_output=True, text=True, timeout=10
        )
        output += "=== TABLE FILTER ===\n" + (r1.stdout if r1.returncode == 0 else r1.stderr)

        r2 = subprocess.run(
            ["sudo", "/usr/sbin/iptables", "-t", "nat", "-L", "-n", "-v", "--line-numbers"],
            capture_output=True, text=True, timeout=10
        )
        output += "\n=== TABLE NAT ===\n" + (r2.stdout if r2.returncode == 0 else r2.stderr)
        return output
    except Exception as e:
        return f"Erreur lors de la lecture des règles: {str(e)}"


TOOL_FUNCTIONS = {
    "scanner_reseau": lambda params: tool_scanner_reseau(),
    "autoriser_internet": lambda params: tool_autoriser_internet(params["ip_address"]),
    "bloquer_internet": lambda params: tool_bloquer_internet(params["ip_address"]),
    "lister_regles": lambda params: tool_lister_regles(),
}


# =====================
# Contexte et envoi
# =====================

def construire_contexte_regles(regles_filter, regles_nat, suggestions):
    contexte = "=== ÉTAT ACTUEL DU PARE-FEU ===\n\n"

    contexte += f"--- Règles Filter ({len(regles_filter)} règles) ---\n"
    for r in regles_filter:
        contexte += (
            f"  #{r.id} | {r.chaine} | {r.protocol} | "
            f"src={r.ip_source or '*'} | dst={r.ip_destination or '*'} | "
            f"sport={r.port_source or '*'} | dport={r.port_destination or '*'} | "
            f"action={r.action}\n"
        )

    contexte += f"\n--- Règles NAT ({len(regles_nat)} règles) ---\n"
    for r in regles_nat:
        contexte += (
            f"  #{r.id} | {r.type} | {r.protocol} | "
            f"src={r.ip_source or '*'} -> {r.new_ip_source or '*'} | "
            f"dst={r.ip_destination or '*'} -> {r.new_ip_destination or '*'}\n"
        )

    contexte += f"\n--- Suggestions/Alertes ({len(suggestions)} en attente) ---\n"
    for s in suggestions:
        contexte += (
            f"  #{s.id} | {s.description_suggestion} | "
            f"action={s.action} | statut={s.statut}\n"
        )

    return contexte


def envoyer_message_claude(message_utilisateur, historique, regles_filter, regles_nat, suggestions):
    if anthropic is None:
        raise ImportError("Le module 'anthropic' n'est pas installé. Exécutez : pip install anthropic")
    if not getattr(settings, "ANTHROPIC_API_KEY", ""):
        raise ValueError("ANTHROPIC_API_KEY n'est pas configurée. Définissez la variable d'environnement.")

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    contexte_regles = construire_contexte_regles(regles_filter, regles_nat, suggestions)

    messages = []
    for msg in historique:
        messages.append({"role": msg["role"], "content": msg["content"]})

    prompt_enrichi = f"{contexte_regles}\n\n--- Question de l'administrateur ---\n{message_utilisateur}"
    messages.append({"role": "user", "content": prompt_enrichi})

    max_iterations = 5
    for _ in range(max_iterations):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS_DEFINITION,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            result_text = ""
            for block in response.content:
                if block.type == "text":
                    result_text += block.text
            return result_text

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    if tool_name in TOOL_FUNCTIONS:
                        result = TOOL_FUNCTIONS[tool_name](tool_input)
                    else:
                        result = f"Outil inconnu: {tool_name}"

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            result_text = ""
            for block in response.content:
                if block.type == "text":
                    result_text += block.text
            return result_text or "Réponse incomplète du modèle."

    return "Erreur: trop d'appels d'outils consécutifs."
