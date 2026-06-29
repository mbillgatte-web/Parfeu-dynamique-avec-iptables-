from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.

class Utilisateur(models.Model):
    STATUT_CHOICES = (
        ("superadmin", "Super Administrateur"),
        ("admin", "Administrateur"),
    )

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="admin")

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def verify_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email}) - {self.statut}"



class Regles(models.Model):
    id = models.AutoField(primary_key=True)
    chaine = models.CharField(max_length=255)
    protocol = models.CharField(max_length=10, choices=[
        ('tcp', 'TCP'),
        ('udp', 'UDP'),
        ('icmp', 'ICMP'),
        ('all', 'ALL'),
    ], default='all')
    port_source = models.IntegerField(null=True, blank=True)
    port_destination = models.IntegerField(null=True, blank=True)
    interface_dentree = models.CharField(max_length=100, null=True, blank=True)
    interface_sortie = models.CharField(max_length=100, null=True, blank=True)
    ip_source = models.GenericIPAddressField(null=True, blank=True)
    ip_destination = models.GenericIPAddressField(null=True, blank=True)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.id} - {self.chaine} - {self.protocol} - " \
               f"{self.port_source} - {self.port_destination} - {self.interface_dentree} - " \
               f"{self.interface_sortie} - {self.ip_source} - {self.ip_destination} - " \
               f"{self.description} - {self.date_creation}"



class Regles_Filter(Regles):
    ACTIONS = [
        ('ACCEPT', 'Accept'),
        ('DROP', 'Drop'),
        ('REJECT', 'Reject'),
        ('LOG', 'Log'),
    ]
    action = models.CharField(max_length=10, choices=ACTIONS)

    def __str__(self):
        # On réutilise __str__ du parent + on ajoute action
        return f"{super().__str__()} | Action: {self.action}"




class Regles_NAT(Regles):
    TYPE = [
        ('SNAT', 'Source NAT'),
        ('DNAT', 'Destination NAT'),
        ('MASQUERADE', 'Masquerade'),
    ]
    type = models.CharField(max_length=15, choices=TYPE)

    new_ip_source = models.GenericIPAddressField(null=True, blank=True)
    new_ip_destination = models.GenericIPAddressField(null=True, blank=True)
    new_port = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{super().__str__()} | Type: {self.type} | New IP Source: {self.new_ip_source} | New IP Destination: {self.new_ip_destination} | New Port: {self.new_port}"



class Regles_Mangle(Regles):
    ttl_value = models.IntegerField(null=True, blank=True, help_text="Nouvelle valeur du TTL")
    tos_value = models.CharField(max_length=50, null=True, blank=True, help_text="Valeur TOS ou DSCP")
    mark_value = models.IntegerField(null=True, blank=True, help_text="Marque appliquée au paquet")
    
    def __str__(self):
        return f"Mangle rule on {self.protocol}:{self.port_destiniation} → TTL={self.ttl_value}, TOS={self.tos_value}, MARK={self.mark_value}"





    


class Suggestions(models.Model):
    id = models.AutoField(primary_key=True)
    description_suggestion = models.TextField()
    date_declenchement = models.DateTimeField(auto_now_add=True)

    # Champs de règle "proposée"
    chaine = models.CharField(max_length=255, default='INPUT')
    protocol = models.CharField(max_length=10, choices=[
        ('tcp', 'TCP'),
        ('udp', 'UDP'),
        ('icmp', 'ICMP'),
        ('all', 'ALL'),
    ], default='all')
    port_source = models.IntegerField(null=True, blank=True)
    port_destination = models.IntegerField(null=True, blank=True)
    interface_dentree = models.CharField(max_length=100, null=True, blank=True)
    interface_sortie = models.CharField(max_length=100, null=True, blank=True)
    ip_source = models.GenericIPAddressField(null=True, blank=True)
    ip_destination = models.GenericIPAddressField(null=True, blank=True)
    action = models.CharField(max_length=10, choices=Regles_Filter.ACTIONS, default='ACCEPT')

    statut = models.CharField(max_length=20, choices=[
        ('proposee', 'Proposée'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
    ], default='proposee')

    def __str__(self):
        return f"[{self.statut}] Suggestion {self.id} : {self.description_suggestion}"
