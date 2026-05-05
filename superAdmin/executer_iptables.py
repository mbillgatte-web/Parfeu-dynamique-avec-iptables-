import subprocess
import logging

# Configurer un logger simple
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_iptables_command(cmd):
    """Exécute la commande iptables via sudo et gère les erreurs."""
    try:
        full_cmd = ["sudo", "/usr/sbin/iptables"] + cmd
        result = subprocess.run(full_cmd, check=True, capture_output=True, text=True)
        logger.info(f"Commande exécutée avec succès: {' '.join(full_cmd)}")
        if result.stdout:
            logger.info(f"Sortie: {result.stdout.strip()}")
        return True, None
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur iptables: {' '.join(e.cmd)} | Code retour: {e.returncode}")
        if e.stderr:
            logger.error(f"Détails erreur: {e.stderr.strip()}")
        return False, f"Erreur iptables: {e.stderr.strip() if e.stderr else e.returncode}"
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        return False, str(e)



# TABLE FILTER


def executer_ajout_filter(rule):
  
     # Choix de l'option en fonction de la priorité
    action_ajout = "-I" if getattr(rule, "ajouter_en_priorite", False) else "-I"

    cmd = [action_ajout, rule.chaine.upper()]

    # Protocole
    proto = rule.protocol.lower()
    if proto != "all":
        cmd += ["-p", proto]

    # Interfaces
    if getattr(rule, "interface_dentree", None):
        cmd += ["-i", rule.interface_dentree]
    if getattr(rule, "interface_sortie", None):
        cmd += ["-o", rule.interface_sortie]

    # IP source/destination
    if getattr(rule, "ip_source", None):
        cmd += ["-s", rule.ip_source]
    if getattr(rule, "ip_destination", None):
        cmd += ["-d", rule.ip_destination]

    # Ports seulement pour TCP/UDP
    if proto in ["tcp", "udp"]:
        if getattr(rule, "port_source", None):
            cmd += ["--sport", str(rule.port_source)]
        if getattr(rule, "port_destination", None):
            cmd += ["--dport", str(rule.port_destination)]

    # Action finale
    cmd += ["-j", rule.action.upper()]

    return run_iptables_command(cmd)




def executer_ajout_prioriter_filter(rule):
      
     # Choix de l'option en fonction de la priorité
    action_ajout = "-I" if getattr(rule, "ajouter_en_priorite", False) else "-I"

    cmd = [action_ajout, rule.chaine.upper()]

    # Protocole
    proto = rule.protocol.lower()
    if proto != "all":
        cmd += ["-p", proto]

    # Interfaces
    if getattr(rule, "interface_dentree", None):
        cmd += ["-i", rule.interface_dentree]
    if getattr(rule, "interface_sortie", None):
        cmd += ["-o", rule.interface_sortie]

    # IP source/destination
    if getattr(rule, "ip_source", None):
        cmd += ["-s", rule.ip_source]
    if getattr(rule, "ip_destination", None):
        cmd += ["-d", rule.ip_destination]

    # Ports seulement pour TCP/UDP
    if proto in ["tcp", "udp"]:
        if getattr(rule, "port_source", None):
            cmd += ["--sport", str(rule.port_source)]
        if getattr(rule, "port_destination", None):
            cmd += ["--dport", str(rule.port_destination)]

    # Action finale
    cmd += ["-j", rule.action.upper()]

    return run_iptables_command(cmd)










def executer_supprimer_filter(rule):
    """Suppression règle table filter (identique à l'ajout mais avec -D)"""
    cmd = ["-D", rule.chaine.upper()]

    proto = rule.protocol.lower()
    if proto != "all":
        cmd += ["-p", proto]

    if getattr(rule, "interface_dentree", None):
        cmd += ["-i", rule.interface_dentree]
    if getattr(rule, "interface_sortie", None):
        cmd += ["-o", rule.interface_sortie]

    if getattr(rule, "ip_source", None):
        cmd += ["-s", rule.ip_source]
    if getattr(rule, "ip_destination", None):
        cmd += ["-d", rule.ip_destination]

    if proto in ["tcp", "udp"]:
        if getattr(rule, "port_source", None):
            cmd += ["--sport", str(rule.port_source)]
        if getattr(rule, "port_destination", None):
            cmd += ["--dport", str(rule.port_destination)]

    cmd += ["-j", rule.action.upper()]

    return run_iptables_command(cmd)


def executer_modifier_filter(old_rule, new_rule):
    """Modifier une règle filter (supprimer puis ajouter)"""
    success, error = executer_supprimer_filter(old_rule)
    if not success:
        return success, f"Impossible de supprimer l'ancienne règle: {error}"
    return executer_ajout_filter(new_rule)



# TABLE NAT


def _get_nat_chain(rule):
    """Retourne la chaîne NAT appropriée"""
    if rule.type.upper() in ["SNAT", "MASQUERADE"]:
        return "POSTROUTING"
    elif rule.type.upper() == "DNAT":
        return "PREROUTING"
    else:
        return "OUTPUT"


def executer_ajouter_nat(rule):
    """Ajout d'une règle NAT"""
    chain = _get_nat_chain(rule)
    cmd = ["-t", "nat", "-A", chain]

    proto = rule.protocol.lower()
    if proto != "all":
        cmd += ["-p", proto]

    # Interfaces
    if chain == "PREROUTING" and getattr(rule, "interface_dentree", None):
        cmd += ["-i", rule.interface_dentree]
    if chain == "POSTROUTING" and getattr(rule, "interface_sortie", None):
        cmd += ["-o", rule.interface_sortie]

    # IP source/destination
    if getattr(rule, "ip_source", None):
        cmd += ["-s", rule.ip_source]
    if getattr(rule, "ip_destination", None):
        cmd += ["-d", rule.ip_destination]

    # Ports TCP/UDP
    if proto in ["tcp", "udp"]:
        if getattr(rule, "port_source", None):
            cmd += ["--sport", str(rule.port_source)]
        if getattr(rule, "port_destination", None):
            cmd += ["--dport", str(rule.port_destination)]

    # Action NAT
    if rule.type.upper() == "SNAT":
        target = rule.new_ip_source
        if getattr(rule, "new_port", None):
            target += f":{rule.new_port}"
        cmd += ["-j", "SNAT", "--to-source", target]

    elif rule.type.upper() == "DNAT":
        target = rule.new_ip_destination
        if getattr(rule, "new_port", None):
            target += f":{rule.new_port}"
        cmd += ["-j", "DNAT", "--to-destination", target]

    elif rule.type.upper() == "MASQUERADE":
        cmd += ["-j", "MASQUERADE"]

    return run_iptables_command(cmd)


def executer_supprimer_nat(rule):
 
    chain = _get_nat_chain(rule)
    cmd = ["-t", "nat", "-D", chain]

    proto = rule.protocol.lower()
    if proto != "all":
        cmd += ["-p", proto]

    if chain == "PREROUTING" and getattr(rule, "interface_dentree", None):
        cmd += ["-i", rule.interface_dentree]
    if chain == "POSTROUTING" and getattr(rule, "interface_sortie", None):
        cmd += ["-o", rule.interface_sortie]

    if getattr(rule, "ip_source", None):
        cmd += ["-s", rule.ip_source]
    if getattr(rule, "ip_destination", None):
        cmd += ["-d", rule.ip_destination]

    if proto in ["tcp", "udp"]:
        if getattr(rule, "port_source", None):
            cmd += ["--sport", str(rule.port_source)]
        if getattr(rule, "port_destination", None):
            cmd += ["--dport", str(rule.port_destination)]

    if rule.type.upper() == "SNAT":
        target = rule.new_ip_source
        if getattr(rule, "new_port", None):
            target += f":{rule.new_port}"
        cmd += ["-j", "SNAT", "--to-source", target]

    elif rule.type.upper() == "DNAT":
        target = rule.new_ip_destination
        if getattr(rule, "new_port", None):
            target += f":{rule.new_port}"
        cmd += ["-j", "DNAT", "--to-destination", target]

    elif rule.type.upper() == "MASQUERADE":
        cmd += ["-j", "MASQUERADE"]

    return run_iptables_command(cmd)


def executer_modifier_nat(old_rule, new_rule):
    
    success, error = executer_supprimer_nat(old_rule)
    if not success:
        return success, f"Impossible de supprimer l'ancienne règle NAT: {error}"
    return executer_ajouter_nat(new_rule)
