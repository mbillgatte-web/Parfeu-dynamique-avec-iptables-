import json

from django import http
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .models import *
from django.utils.timezone import now
from django.utils.timesince import timesince
from django.contrib import messages
from .executer_iptables import *
from .chatbot_ia import envoyer_message_claude


# Dictionnaire pour changer la couleur de l'icône selon l'action
ICON_MAP = {
    "ACCEPT": {"bg": "bg-green-100", "text": "text-green-500", "icon": "fas fa-check-circle"},
    "DROP": {"bg": "bg-red-100", "text": "text-red-500", "icon": "fas fa-exclamation-triangle"},
    "REJECT": {"bg": "bg-yellow-100", "text": "text-yellow-500", "icon": "fas fa-ban"},
    "LOG": {"bg": "bg-blue-100", "text": "text-blue-500", "icon": "fas fa-info-circle"},
}

# Create your views here.


def connexion(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = Utilisateur.objects.get(email=email)
        except Utilisateur.DoesNotExist:
            return render(request, "superAdmin/connexion.html", {"error": "Email introuvable"})

        if not user.verify_password(password):
            return render(request, "superAdmin/connexion.html", {"error": "Mot de passe incorrect"})

        request.session['user_id'] = user.id
        request.session['user_email'] = user.email
        request.session['user_statut'] = user.statut

        return redirect("dashboard")

    return render(request, "superAdmin/connexion.html")



def Dashboard(request):
    total_nat_rules = Regles_NAT.objects.count()
    total_filter_rules = Regles_Filter.objects.count()
    total_suggestions = Suggestions.objects.count()
    total_rules = total_nat_rules + total_filter_rules

    suggestions = Suggestions.objects.order_by('-date_declenchement')[:10]

    # Ajouter les propriétés d'icône à chaque suggestion
    for s in suggestions:
        s.icon_props = ICON_MAP.get(s.action, ICON_MAP["REJECT"])

    context = {
        'total_nat_rules': total_nat_rules,
        'total_filter_rules': total_filter_rules,
        'total_rules': total_rules,
        'suggestions': suggestions,
        'total_suggestions': total_suggestions,
    }
    return render(request, 'superAdmin/Dashboard.html', context)


def Table_Nat(request):
    rules_nat_list = Regles_NAT.objects.all().order_by('id')  # Tri par ID
    total_rules_nat = Regles_NAT.objects.count()

    dnat_rules = Regles_NAT.objects.filter(type="DNAT").count()
    snat_rules = Regles_NAT.objects.filter(type="SNAT").count()
    masquerade_rules = Regles_NAT.objects.filter(type="MASQUERADE").count()

    context = {
        'rules_nat_list': rules_nat_list,
        'total_rules_nat': total_rules_nat,
        'dnat_rules': dnat_rules,
        'snat_rules': snat_rules,
        'masquerade_rules': masquerade_rules,

    }
    return render(request, 'superAdmin/Table_Nat.html', context)




def Table_Filter(request):

    # Récupérer toutes les règles
    rules_list = Regles_Filter.objects.all().order_by('id')  # Tri par ID
        # Compter toutes les règles
    total_rules = Regles_Filter.objects.count()
    # Compter les règles par chaîne
    # Compter par chaîne
    input_rules = Regles_Filter.objects.filter(chaine="INPUT").count()
    output_rules = Regles_Filter.objects.filter(chaine="OUTPUT").count()
    forward_rules = Regles_Filter.objects.filter(chaine="FORWARD").count()


    context = {
       
        'rules_list': rules_list,
        'total_rules': total_rules,
        'input_rules': input_rules,
        'output_rules': output_rules,
        'forward_rules': forward_rules,
    }

    return render(request, 'superAdmin/Table_Filter.html', context)            
     
    



def Gestion_Users(request):
    return render(request, 'superAdmin/Gestion_Users.html')



def request_admin(request):

    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        mot_de_passe = request.POST.get('mot_de_passe')
        role = request.POST.get('role')

        # Assuming you have a model named Administrateur
        from .models import Administrateur
        administrateur = Administrateur(nom=nom, prenom=prenom, email=email, mot_de_passe=mot_de_passe, role=role)
        administrateur.save()
    return  http.HttpResponse('Administrateur ajouté avec succes')







#la vue qui va permettre d'ajouter une règle de filtrage
def ajout_filter(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        chain = request.POST.get('chain')
        protocol = request.POST.get('protocol')
        ip_source = request.POST.get('ip_source')
        ip_destination = request.POST.get('ip_destination')
        port_source = request.POST.get('port_source') or None
        port_destination = request.POST.get('port_destination') or None
        action = request.POST.get('action')
        description = request.POST.get('description') or None

        priority = int(request.POST.get("priority", 0))  # 1 = priorité, 0 = normal

        # Créer une nouvelle règle
        new_rule = Regles_Filter(
            chaine=chain,
            protocol=protocol,
            ip_source=ip_source,
            ip_destination=ip_destination,
            port_source=port_source,
            port_destination=port_destination,
            action=action,
            description=description
        )
        new_rule.ajouter_en_priorite = bool(priority)
        success, error = executer_ajout_filter(new_rule)

        if not success:
            messages.error(request, f"Erreur lors de l'application de la règle iptables pour filter : {error}")
            return redirect("table_filter")

        new_rule.save()
        messages.success(request, "Règle ajoutée avec succès.")
      
        return redirect('table_filter')
    return render(request, 'superAdmin/Table_Filter.html')



#la vue qui va permettre de supprimer une règle de filtrage
def supprimer_filter(request, pk):
    rule = get_object_or_404(Regles_Filter, pk=pk)

    if request.method == 'POST':
         # Exécution sur iptables
        success, error = executer_supprimer_filter(rule)

        if not success:
            messages.error(request, f"Erreur lors de la suppression iptables pour filter : {error}")
            return redirect("table_filter")

        # Suppression en BD uniquement si iptables OK
        rule.delete()
        messages.success(request, "Règle supprimée avec succès.")

        return redirect('table_filter')
    return render(request, 'superAdmin/Table_Filter.html')





def modifier_filter(request):
    if request.method == "POST":
        rule_id = request.POST.get("rule_id")
      
       
        rule = get_object_or_404(Regles_Filter, id=rule_id)

        # Cloner l'ancienne règle (copie des valeurs actuelles AVANT modif)
        oldrule = Regles_Filter(
            ip_source=rule.ip_source,
            ip_destination=rule.ip_destination,
            port_source=rule.port_source,
            port_destination=rule.port_destination,
            protocol=rule.protocol,
            action=rule.action,
            description=rule.description,
            chaine=rule.chaine,
        )

        # Mettre à jour les champs avec les nouvelles valeurs
        rule.ip_source = request.POST.get("edit-ip-source")
        rule.ip_destination = request.POST.get("edit-ip-destination")
        rule.port_source = request.POST.get("edit-port-source")
        rule.port_destination = request.POST.get("edit-port-destination")
        rule.protocol = request.POST.get("protocol")
        rule.action = request.POST.get("edit-action")
        rule.description = request.POST.get("edit-form-desc")
        rule.chaine = request.POST.get("chain")


     
        success, error = executer_modifier_filter(oldrule, rule)

        if not success:
            # Gérer l'erreur, par exemple avec un message
            messages.error(request, f"Erreur lors de la modification pour filter : {error}")
            return redirect("table_filter")

        # Sauvegarder la nouvelle règle en base après réussite
        rule.save()

        
        return redirect('table_filter')
    return redirect(request, 'superAdmin/Table_Filter.html')






def ajouter_nat(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nat_type = request.POST.get('nat-type')
        protocol = request.POST.get('protocol')
        ip_source = request.POST.get('ip_source')
        ip_destination = request.POST.get('ip_destination')
        new_ip_source = request.POST.get('to_ip') or None
        new_ip_destination = request.POST.get('to_ip') or None
        new_port = request.POST.get('to_port') or None
        port_source = request.POST.get('port_source') or None
        port_destination = request.POST.get('port_destination') or None
        description = request.POST.get('comment') or None
        interface_dentree = request.POST.get('interface_dentree') or None
        interface_sortie = request.POST.get('interface_sortie') or None
      
        # Créer une nouvelle règle NAT
        new_nat_rule = Regles_NAT(
            type=nat_type,
            protocol=protocol,
            ip_source=ip_source,
            ip_destination=ip_destination,
            new_ip_source=new_ip_source,
            new_ip_destination=new_ip_destination,
            new_port=new_port,
            port_source=port_source,
            port_destination=port_destination,
            description=description,
            interface_dentree=interface_dentree,
            interface_sortie=interface_sortie
        )

            # Exécuter la commande iptables
        success, error = executer_ajouter_nat(new_nat_rule) 

        if not success:
            messages.error(request, f"Erreur lors de l'ajout de la règle NAT dans iptables : {error}")
            return redirect("table_nat")
        
        messages.success(request, "Règle NAT ajoutée avec succès.")
         # Sauvegarder seulement si iptables a été mis à jour
        new_nat_rule.save()

        return redirect('table_nat')
    return render(request, 'superAdmin/Table_Nat.html')





# la vue qui va permettre de supprimer une règle NAT
def supprimer_nat(request, pk):
    rule = get_object_or_404(Regles_NAT, pk=pk)
    if request.method == 'POST':
        # Exécuter la suppression sur iptables
        success, error = executer_supprimer_nat(rule)

        if not success:
            messages.error(request, f"Erreur lors de la suppression de la règle NAT dans iptables : {error}")
            return redirect("table_nat")
        
        rule.delete()
        messages.success(request, "Règle NAT supprimée avec succès.")

        return redirect('table_nat')
    return render(request, 'superAdmin/Table_Nat.html')




# la vue qui va permettre de modifier une règle NAT
def modifier_nat(request):
    if request.method == "POST":
        rule_id = request.POST.get("rule_id")
        rule = get_object_or_404(Regles_NAT, id=rule_id)

         # Cloner l'ancienne règle (avant modification)
        oldrule = Regles_NAT(
            type=rule.type,
            protocol=rule.protocol,
            ip_source=rule.ip_source,
            ip_destination=rule.ip_destination,
            new_ip_source=rule.new_ip_source,
            new_ip_destination=rule.new_ip_destination,
            new_port=rule.new_port,
            port_source=rule.port_source,
            port_destination=rule.port_destination,
            description=rule.description,
            interface_dentree=rule.interface_dentree,
            interface_sortie=rule.interface_sortie,
        )

       

        # Mettre à jour les champs
        rule.ip_source = request.POST.get("source")
        rule.ip_destination = request.POST.get("destination")
        rule.port_source = request.POST.get("source_port")
        rule.port_destination = request.POST.get("destination_port")
        rule.protocol = request.POST.get("protocol")
        rule.type = request.POST.get("nat_type")
        rule.new_ip_source = request.POST.get("to-ip") or None
        rule.new_ip_destination = request.POST.get("to-ip") or None
        rule.new_port = request.POST.get("to_port") or None
        rule.description = request.POST.get("comment") or None
        rule.interface_dentree = request.POST.get("interface_dentree") or None
        rule.interface_sortie = request.POST.get("interface_sortie") or None
       
        # Appliquer la modification sur iptables
        success, error = executer_modifier_nat(oldrule, rule)

        if not success:
            messages.error(request, f"Erreur lors de la modification : {error}")
            return redirect("table_nat")

        # Sauvegarder seulement si iptables a été mis à jour
        rule.save()
        messages.success(request, "Règle NAT modifiée avec succès.")

        
        return redirect('table_nat')
    return redirect(request, 'superAdmin/Table_Nat.html')



# la vue qui va permettre de modifier une suggestion
def modifier_suggestion(request):
    if request.method == "POST":
        rule_id = request.POST.get("rule_id")
        rule = get_object_or_404(Suggestions, id=rule_id)
       

        # Mettre à jour les champs
        rule.ip_source = request.POST.get("ip_source")
        rule.ip_destination = request.POST.get("ip_destination")
        rule.port_source = request.POST.get("port_source")
        rule.port_destination = request.POST.get("port_destination")
        rule.protocol = request.POST.get("protocol")
        rule.action = request.POST.get("action")
        rule.description_suggestion = request.POST.get("desc") or None
        rule.chaine = request.POST.get("chaine")
         # Sauvegarder les modifications

        rule.save()
        
        return redirect('dashboard')
    return redirect(request, 'superAdmin/Dashboard.html')



# la vue qui va permettre de supprimer une suggestion
def supprimer_suggestion(request):
    if request.method == 'POST':
        rule_id = request.POST.get('rule_id')
        suggestion = get_object_or_404(Suggestions, id=rule_id)
        suggestion.delete()
        return redirect('dashboard') 
    return redirect(request, 'superAdmin/Dashboard.html') 




# la vue qui va permettre d'appliquer une suggestion
def appliquer_suggestion(request, suggestion_id):

    suggestion = get_object_or_404(Suggestions, id=suggestion_id)

    if request.method == "POST":
        # Création de la règle Filter à partir des infos de la suggestion
        regle = Regles_Filter.objects.create(
            chaine=suggestion.chaine,
            protocol=suggestion.protocol,
            action=suggestion.action,
            ip_source=suggestion.ip_source,
            ip_destination=suggestion.ip_destination,
            port_source=suggestion.port_source,
            port_destination=suggestion.port_destination,
            description=suggestion.description_suggestion
        )

        # Appliquer la règle
        success, error = executer_ajout_filter(regle)

        if not success:
            messages.error(request, f"Erreur lors de l'ajout de la règle Filter dans iptables : {error}")
            return redirect("dashboard")
        
        messages.success(request, "Suggestion appliquée avec succès.")
        suggestion.delete()

        # Redirection vers la page des suggestions
        return redirect("dashboard")
    return redirect(request, 'superAdmin/Dashboard.html')



@csrf_exempt
@require_POST
def chatbot_message(request):
    """Vue API pour le chatbot IA."""
    try:
        data = json.loads(request.body)
        message = data.get("message", "").strip()
        historique = data.get("historique", [])

        if not message:
            return JsonResponse({"error": "Message vide"}, status=400)

        regles_filter = list(Regles_Filter.objects.all())
        regles_nat = list(Regles_NAT.objects.all())
        suggestions = list(Suggestions.objects.filter(statut="proposee"))

        reponse = envoyer_message_claude(
            message, historique, regles_filter, regles_nat, suggestions
        )

        return JsonResponse({"reponse": reponse})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)