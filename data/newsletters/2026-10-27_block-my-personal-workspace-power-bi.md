---
title: Désactiver les workspaces Personnel Power BI : est-ce possible ?
url: https://blog.antoinewang-tech.com/p/block-my-personal-workspace-power-bi
date: 2026-10-27
author: Antoine Wang
source: substack
---

# Désactiver les workspaces Personnel Power BI : est-ce possible ?

Hello les masters Fabric 👋

Aujourd’hui, on va parler d’un Workspace que quasiment tous les utilisateurs Power BI possèdent, mais qui est parfois oublié lorsque l’on construit sa gouvernance : **My Workspace**.​‌

Sur le papier, son rôle est simple : permettre à chacun de créer et tester du contenu dans son espace personnel.​‌

**La question qu’on se pose : Peut-on tout simplement désactiver My Workspace pour l’ensemble du tenant et si oui, comment ?**​‌

## ⚡ En 30 secondes

> 1. **My Workspace ne se désactive pas avec un simple tenant setting.** Chaque utilisateur dispose de son espace personnel et les paramètres d’administration permettent surtout d’en encadrer les usages.
> 2. **Le vrai risque est qu’un espace personnel devienne un canal de diffusion non gouverné.** Un rapport créé « juste pour tester » peut progressivement être partagé et utilisé par plusieurs personnes sans passer par vos Workspaces collaboratifs et votre cycle de gouvernance habituel.
> 3. **Pour aller jusqu’au blocage opérationnel, une approche consiste à isoler les My Workspaces sur une F-SKU dédiée**, empêcher leur réaffectation, puis mettre cette capacité en pause. La capacité pausée ne consommant plus de ressources, le contrôle peut rester en place sans faire tourner inutilement du compute.

---

Chaque utilisateur Fabric possède son propre espace de travail personnel. En revanche, il existe un moyen d’administration qui le rend indisponible : concentrer tous les espaces personnels sur une capacité Fabric dédiée, empêcher leur réaffectation, puis mettre en pause cette capacité.

Ne vous y trompez pas : cette méthode détourne une fonction d’arrêt de capacité pour produire un verrou de gouvernance. Il doit donc être traité comme un contrôle réversible, supervisé et assumé et c’est ce qu’on va voir concrètement par la suite.

---

## La méthode « F-SKU en pause »

Le mécanisme repose sur trois briques :

* une capacité F-SKU Azure dédiée aux My Workspaces,
* le tenant setting qui interdit aux propriétaires de revenir en capacité partagée,
* et la pause de la capacité.

Tant que cette dernière reste en arrêt, les contenus qui lui sont affectés deviennent indisponibles. Les Workspaces collaboratifs gouvernés restent sur leurs Capacités habituelles.

---

## La réalité du terrain

### ✅ 1. Les tenant settings réduisent le risque, mais ne ferment pas My Workspace

Quatre réglages dans le portail d’administration de la plateforme sont souvent cités dans la même discussion :

* **“Allow shareable links to grant access to everyone in your organization”** permet de retirer l’option **People in your organization** pour restreindre le partage de rapports à toute les personnes de l’entreprise.
* **“Restrict content with protected labels from being shared via link with everyone in your organization”** permet de restreindre le partage de contenus portant un étiquette de sensibilité de protection.
* **“Create workspaces”** contrôle la création de Workspaces collaboratifs. Il ne supprime pas le My Workspace automatiquement attribué à chaque utilisateur.
* **“Export to Excel”** et “**Export reports as PowerPoint presentations or PDF documents”** peuvent être désactivés ou limités à des groupes.

Pour structurer ce qui doit remplacer l’usage personnel, rattachez les contenus durables à des Workspaces avec un propriétaire, un domaine et des règles documentées. J’ai détaillé cette logique dans [le guide Fabric Domains pour gouverner les Workspaces](https://blog.antoinewang-tech.com/p/fabric-domains-gouvernance).

### ✅ 2. Les prérequis à valider

Préparez le changement comme une migration de service, pas comme un réglage isolé :

* droits **Administrateur de Fabric** pour administrer le tenant et les affectations;
* droits Azure **Contributeur** sur l’abonnement pour permettre de créer, modifier, suspendre la capacité Fabric.

### **✅** 3. Passons à la pratique : rendre My Workspace indisponible

Maintenant que le principe est clair, passons à la mise en œuvre. L’objectif est de mettre en place le mécanisme progressivement, depuis la création de la capacité dédiée jusqu’à la validation finale avec un utilisateur non-admin.

#### Étape 1 : Créer la Capacité Fabric dédiée

Dans le portail Azure, créez une ressource **Microsoft Fabric** :

1. Sélectionnez la souscription et le Resource Group de gouvernance.
2. Choisissez une région conforme à vos exigences de résidence.
3. Sélectionnez une capacité F2.
4. Nommez clairement la ressource.
5. Affectez uniquement les administrateurs responsables du contrôle.
6. Ajoutez des tags de coût, de propriétaire et de finalité.

#### Étape 2 : Configurer la capacité côté Fabric

Dans le portail Microsoft Fabric :

1. Ouvrez **Admin portal** > **Capacity settings** > **Fabric capacity**.
2. Sélectionnez la capacité créée.
3. Dans **Details**, développez “**Preferred capacity for My workspace”**.
4. Activez l’option, puis sélectionnez **Apply**.

⚠️ Ce réglage place la capacité comme **destination préférée des My Workspaces** concernés par le mécanisme de capacité par défaut. Dans le pattern retenu, il couvre notamment les nouveaux utilisateurs et ceux qui n’avaient pas encore initialisé leur espace personnel.

#### Étape 3 : Activer le tenant setting anti-rollback

Dans le portail Microsoft Fabric :

1. Ouvrez **Admin portal** > **Tenant settings** > **Workspace settings**.
2. Développez “**Block users from reassigning personal workspaces (My Workspace)”**.
3. Activez l’option, puis sélectionnez **Apply**.

Sans ce verrou, un propriétaire peut réaffecter son My Workspace vers un type Power BI Pro. Vous auriez alors déplacé les espaces personnels sans fermer la porte de sortie.

Ce tenant setting ne bloque pas “My Workspace” à lui seul. Il fige son affectation. C’est le couplage avec la Capacité pausée qui produit l’indisponibilité.

#### Étape 4 : Affecter tous les My Workspaces existants

Retournez dans **Capacity settings**, puis :

1. Sélectionnez la capacité créée.
2. Ouvrez **Workspaces assigned to this capacity**.
3. Sélectionnez **Assign workspaces**.
4. Choisissez **The entire organization’s My workspaces**.
5. Confirmez l’affectation.

Cette option observée dans l’interface F SKU permet de rattraper en masse les espaces personnels déjà créés.

Après l’opération, contrôlez un échantillon de My Workspaces dans “**Admin portal** > **Workspaces”** et vérifiez le nom de capacité.

#### Étape 5 : Mettre en pause la capacité

Dans le portail Azure :

1. Ouvrez la ressource **Microsoft Fabric**.
2. Sélectionnez **Pause**.
3. Confirmez l’opération.
4. Attendez que l’état de la ressource indique **Paused**.

La pause est une opération de plateforme. Microsoft indique qu’elle peut rendre indisponible le contenu affecté à la capacité.

#### Étape 6 : Vérifier depuis un compte non-admin

Depuis un compte de test représentatif :

1. Connectez-vous à `app.powerbi.com`.
2. Ouvrez **My Workspace**.
3. Tentez d’ouvrir un rapport.
4. Tentez de créer un rapport.

Le résultat attendu est une erreur indiquant que l’action ne peut pas être exécutée parce que la capacité est pausée.

---

## 🥇 La Règle d’Or

**Si tu dois retenir une chose :** My Workspace ne se désactive pas avec un tenant setting. Pour le rendre indisponible, concentrez tous les espaces personnels sur une capacité F SKU dédiée, empêchez leur retour en capacité partagée, puis pausez cette capacité.

L’impact terrain est immédiat : les rapports personnels ne peuvent plus servir de canal parallèle de diffusion, tandis que les Workspaces gouvernés restent disponibles. Vous obtenez aussi une règle vérifiable : inventaire des affectations, état Azure, test non-admin et alerte de reprise.

***Votre organisation veut-elle réduire le partage depuis My Workspace, ou assumer son blocage opérationnel complet avec un chemin gouverné de remplacement ?***

Répondez simplement à cet email ou ce post, je lis tous vos messages.

Bon mardi et à la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [Fabric Copilot Capacity : isoler les workloads IA](https://blog.antoinewang-tech.com/p/fabric-copilot-capacity-dedicated) : pour appliquer la même discipline d’isolation, de périmètre et de gouvernance à une Capacity spécialisée.
* [Capacity Metrics App : surveiller une Capacity Fabric](https://blog.antoinewang-tech.com/p/capacity-metrics-fabric) : pour construire le volet détection et conserver une lecture opérationnelle des événements de Capacity.

---

## 📚 Ressources pour aller plus loin

Pour approfondir le sujet et passer à la pratique, je vous recommande ces lectures essentielles issues de la documentation officielle :

* 📘 [Gouverner les My Workspaces dans Microsoft Fabric](https://learn.microsoft.com/fabric/admin/portal-workspaces#govern-my-workspaces) : accès administrateur, Capacity par défaut et anti-réaffectation.
* 🛠️ [Configurer et gérer une Fabric Capacity](https://learn.microsoft.com/fabric/admin/capacity-settings) : réglages **Preferred capacity for My workspace** et affectation des Workspaces.
* 🔐 [Paramètres d’export et de partage Power BI](https://learn.microsoft.com/fabric/admin/service-admin-portal-export-sharing) : liens organisationnels, invités, Publish to web et exports.
* 🏷️ [Paramètres de protection de l’information](https://learn.microsoft.com/fabric/admin/service-admin-portal-information-protection) : sensitivity labels et restriction des liens vers toute l’organisation.
* ⏸️ [Pauser et reprendre une Fabric Capacity](https://learn.microsoft.com/fabric/enterprise/pause-resume) : prérequis RBAC, effets et procédure Azure.
* 📘 [Licences et capacités des utilisateurs Power BI](https://learn.microsoft.com/power-bi/fundamentals/end-user-license#licenses) : capacités de création, publication et partage associées à Power BI Pro.
