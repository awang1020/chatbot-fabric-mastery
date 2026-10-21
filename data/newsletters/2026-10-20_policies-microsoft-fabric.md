---
title: Policies dans Microsoft Fabric : cibler sans tout bloquer
url: https://blog.antoinewang-tech.com/p/policies-microsoft-fabric
date: 2026-10-20
author: Antoine Wang
source: substack
---

# Policies dans Microsoft Fabric : cibler sans tout bloquer

Hello les masters Fabric 👋

Plusieurs équipes partagent une même capacité Fabric, mais vous ne voulez pas forcément leur donner les mêmes possibilités partout.

**Comment limiter la création de certains items Fabric pour un groupe, tout en laissant les autres équipes travailler normalement ?**

C’est typiquement le genre de scénario où les **Microsoft Fabric Policies** deviennent intéressantes, notamment pour appliquer des règles plus granulaires et mieux protéger vos environnements de production.

## **⚡ En 30 secondes**

> **Ce qu’il faut retenir sur les Policies:**
>
> * **Contrôle granulaire** : appliquer des règles ciblées plutôt que de restreindre toute la capacité ou toutes les équipes.
> * **Gouvernance par groupe** : différencier ce que certains groupes d’utilisateurs peuvent créer, tout en laissant les autres travailler normalement.
> * **Protection des environnements** : éviter certaines créations sur des workspaces sensibles, notamment en production, sans bloquer les autres usages Fabric.

---

## Ce que les Policies gouvernent aujourd’hui

Trois niveaux sont à distinguer :

* le **Policy set**, item Fabric qui contient les configurations et que vous activez sur une portée ;
* la **Policy**, qui contrôle une opération précise ;
* les **règles**, qui décrivent les cas autorisés en mode Advanced.

La portée de cette Policy est à deux niveau : **Capacité ou Tenant**. La documentation consultée décrit trois Policies disponibles :

La création relève donc de la **Capacity**, pas d’une Policy tenant qui couvrirait indistinctement toutes les opérations. Les Workspaces peuvent être des conditions ; ce ne sont pas des portées administratives autonomes dans cette preview.

Cette liste ne contient pas de Policy générale « interdire la lecture ou l’utilisation des Data agents ». Nous reviendrons sur les permissions des agents existants dans le premier exemple.

## 1. Trois mode : Allowed, Blocked et Advanced

Pour la Policy **Allow item creation**, voici ce que change chaque mode :

Pour résumer en d’autres termes :

* **“Allowed” ne donne pas de droits supplémentaires.** Un Viewer ne devient pas créateur.
* **“Blocked” interdit toute création mais ne révoque pas les accès aux items existants.** Le contrôle porte sur l’opération de création.
* **“Advanced” permet d’autoriser les cas voulus (c’est la partie la plus intéressante),** en fonction du type d’éléments, du groupe de personnes et du workspace.

✅ **Ce qu’il faut savoir sur “Advanced” :**

* Plusieurs conditions dans une règle : **ET**.
* Plusieurs règles : **OU**.
* **Is any of** (`AnyOf`) : au moins une valeur correspond.
* **Is none of** (`NoneOf`) : aucune des valeurs configurées ne correspond.
* Une condition omise ne restreint pas la règle sur cette dimension.

Dès que vous configurez Advanced avec des règles Allow, la Policy fonctionne comme une **liste d’autorisation**. Tout ce qu’aucune règle n’autorise est implicitement bloqué. Il n’y a pas de règle `Deny` prioritaire sur les autres.

**Conséquence : une règle trop étroite bloque des usages attendus ; une règle trop large peut réautoriser le cas que vous vouliez interdire.**

## 2. Organiser les Policy sets : noms, nombre et lisibilité

### Une convention de nommage explicite

✅ **Recommandations**

* Des noms de Policy sets et de règles qui indiquent la **portée et l’objectif**.
* Un nom de Policy set **unique, descriptif et sans espaces**.
* Pour chaque règle, un nom et une description précisant **à qui elle s’applique, ce qu’elle autorise et où**.

🛠️ **Convention proposée, pas norme Microsoft**

```
Capacity : ps-cap-<capacite>-<policy>-v<NN>
Tenant   : ps-tnt-<policy>-v<NN>
```

Exemples fictifs : `ps-cap-prod-fr-itemcreation-v01` et `ps-tnt-workspacesettings-v01`.

Le segment `policy` décrit l’intention du set ; il n’impose pas un item distinct pour chaque règle ou chaque Policy.

Le suffixe `vNN` distingue l’actif de son candidat ou de son prédécesseur lors du remplacement décrit en section 4.

Pour les règles, utilisez des noms comme `R00-autres-types` ou `R10-dataagent-horsgroupe`. **La numérotation sert uniquement à la lecture : les règles restent combinées en OU, sans ordre de priorité.**

Une description utile ajoute au **qui / quoi / où** le **propriétaire**, par exemple : « Autorise les créations hors Data agent dans les Workspaces de prod-fr ; tous les utilisateurs éligibles ; propriétaire : équipe plateforme. »

### Combien de Policy sets et de règles ?

✅ **Limites et fonctionnement documentés**

* **Un seul Policy set actif par portée à un instant donné.** Un même set n’est actif que sur une portée à la fois ; pour l’activer sur une autre Capacité, il faut d’abord le désactiver.
* Donc **N Capacities gouvernées simultanément nécessitent N Policy sets actifs** à portée Capacité.
* Jusqu’à **50 règles par Policy à portée Capacité**, **100 à portée Tenant**, et **50 valeurs par condition**.
* Les Workspaces référencés par la Policy de création doivent appartenir à la Capacité sélectionnée.
* Microsoft recommande de regrouper dans un **Workspace d’administration sécurisé** les Policy sets gérés par la même équipe. La Capacité qui héberge ce Workspace n’est pas nécessairement la Capacité ciblée par les règles.

🛠️ **Recommandations terrain**

* **Pas de Policy set « par principe ».** Pour la création, sans restriction active, les permissions Workspace continuent de s’appliquer. Commencez par les capacités de production où un besoin est identifié.
* **Une cible de deux sets conservés par capacité** : l’actif et son candidat, ou l’actif et le précédent pour revenir en arrière. C’est une discipline d’exploitation, pas un maximum produit ; l’historique reste dans Git.
* **Viser 10 à 15 règles par Capacité** comme seuil de lisibilité interne. Approcher 50 doit déclencher une revue de conception, pas une recherche de contournement.
* Utiliser des **groupes Entra** plutôt que des listes d’utilisateurs ; pour la création, l’appartenance transitive aux groupes est résolue.
* Aligner, quand cela répond à l’architecture, les capacités sur les zones de gouvernance. Une capacité entièrement dédiée à la production peut éviter de répéter des filtres Workspaces.

Le **Policies center** présente les sets actifs, pas tous vos candidats inactifs. Complétez l’inventaire via API, avec l’opération API **List Policy Sets** et les items du Workspace d’administration.

Enfin, choisissez consciemment les types d’items : **AnyOf** n’autorise que la liste choisie, donc pas automatiquement les nouveaux types ajoutés par Microsoft ; **NoneOf** autorise tout sauf la liste exclue, y compris de nouveaux types couverts par le contrôle.

## 3. Trois exemples pour mieux comprendre

Les noms, groupes et périmètres que j’ai utilisé ci-dessous sont **fictifs**. Les tableaux utilisent les libellés de l’interface

### Exemple 1 : Bloquer la création de Data agents pour un groupe

**Besoin :** les membres de `sg-fabric` ne créent pas de Data agents ; les autres créations restent disponibles pour eux, et les autres utilisateurs conservent la possibilité de créer des agents.

Question : faut-il créer une règle avec ET ou deux règles avec OU.

Je voulais laisse réfléchir et je vous mets la réponse ci-dessous et les distinctions :

Créez deux règles distinctes :

**Tests attendus** :

* Alice, hors du groupe, crée un Data Agent: **autorisé par R10**.
* Alice crée un Notebook : **Autorisée** **par R00 et R10**.
* Bob, membre de `sg-fabric`, crée un Data Agent : **refusée car aucune règle l’autorise.**
* Bob, membre de `sg-fabric`, crée un notebook : **autorisée par R00**.

#### Une règle avec deux conditions ou deux règles distinctes ?

En “Advanced”, une règle décrit **ce qui est autorisé**, pas ce qui est interdit. À type et groupe ciblés identiques, les deux configurations ne sont donc pas équivalentes :

* **Une seule règle** avec `Item type Is none of [Fabric data agent]` **ET** `Security groups Is none of [groupe interdit]` autorise uniquement les autres types pour les utilisateurs hors du groupe. Si c’est la seule règle, les membres du groupe ne peuvent créer **aucun type d’item**, et les non-membres ne peuvent **pas non plus créer de Data agent**.
* **Deux règles distinctes**, comme ci-dessus, autorisent une création si le type n’est pas un Data agent **OU** si l’utilisateur est hors du groupe. Une seule des règles doit correspondre : les autres types restent disponibles pour le groupe, et les autres utilisateurs peuvent toujours créer des agents.

Voici les résultats attendus, sans autre règle susceptible d’autoriser l’opération :

C’est la loi de De Morgan.

### Exemple 2 : Réserver Dataflow Gen2 à un groupe sur toute la Capacité

**Besoin :** seuls les membres de `sg-fabric` créent des Dataflow Gen2 ; le reste demeure disponible.

Sans filtre Workspace, ces règles couvrent tous les Workspaces de la Capacité.

**Tests attendus :**

* Alice, hors du groupe, crée un Notebook : **autorisé par R00**.
* Alice crée un Dataflow Gen2 : **refusé**, aucune règle ne correspond.
* Bob, membre de `sg-fabric`, crée un Dataflow Gen2 : **autorisé par R10**.

### Exemple 3 : Bloquer la création de dbt jobs dans toute la Capacité

**Besoin :** personne ne doit créer de nouvel item **dbt job** dans les Workspaces de la Capacité cible, mais les créations d’autres items doivent rester disponibles.

## 4. Créer, remplacer et maintenir sans surprise

### Préparer la fonctionnalité et la population concernée

Avant de commencer :

1. Vérifiez la région. La documentation liste actuellement **West Europe, North Europe et West US** parmi les régions de Capacity non prises en charge. Ne déplacez pas des données pour une preview sans revue de résidence.
2. Préparez le Workspace d’administration sur une Capacity Fabric. Un rôle **Contributor**, **Member** ou **Admin** permet d’y créer l’item ; seul l’administrateur de la portée peut l’activer : **Capacity administrator** pour la Capacité, **Fabric administrator** pour le Tenant.
3. Un administrateur Fabric ouvre **OneLake catalog > Govern > Policies** pour gouverner les Policies par capacité ou au niveau du tenant.

### Activer ou remplacer

Ouvrez le candidat depuis son Workspace, sélectionnez le statut **Active**, choisissez la Capacité cible et confirmez le remplacement éventuel.

L’ancien set devient inactif. Le nouveau prend effet sous **15 minutes** ; les modifications d’un set déjà actif peuvent aussi prendre jusqu’à 15 minutes.

Le **Policies center**, dans **OneLake catalog > Govern > Policies**, sert à voir et gérer les configurations actives par portée. Ses changements sont synchronisés avec l’item actif. Il ne permet pas actuellement de créer, activer ou désactiver un Policy set : utilisez l’item Workspace ou l’API appropriée pour ces opérations.

Une personne ayant les droits nécessaires sur l’item peut modifier les règles ; l’activation reste réservée à l’administrateur de portée. **Un set actif n’est pas figé** : limitez aussi les droits de modification pour éviter qu’une édition ne change le contrôle hors du processus prévu.

### Vérifier, puis conserver la preuve

Après propagation, utilisez des comptes avec des permissions et prérequis comparables, dont le fonctionnement initial a été contrôlé :

* membre et non-membre des groupes ciblés ;
* compte appartenant à plusieurs groupes, y compris par imbrication ;
* types autorisés et type restreint ;
* Workspace de production, hors production et, si possible, hors de la Capacity cible ;
* compte hors de la population soumise aux Policies si vous avez limité le pilote.

Rapprochez les résultats des **Fabric audit logs** et conservez les opérations horodatées, la version et la configuration testée. Un refus dû aux permissions Workspace ne prouve pas que votre Policy fonctionne.

Pour revenir en arrière, réactivez la version précédente en remplaçant l’actuelle, puis refaites les contrôles. **Désactiver sans remplacement rétablit le comportement système applicable**, pas votre ancienne configuration : pour la création, cela peut rouvrir les créations selon les permissions. L’item désactivé reste dans le Workspace.

### **Versionner les définitions, contrôler l’activation**

Git et le CI/CD permettent de versionner, relire et promouvoir les définitions. **Git n’active pas le Policy set** : l’activation passe par une opération API ou par l’item dans son Workspace.

Les API Policies prennent en charge les jetons utilisateur, les **principaux de service** et les **identités managées**. Cela permet l’automatisation, sans supprimer les exigences de droits sur l’item et sur la portée d’activation.

**Mon conseil :** une mise à jour est validée seulement lorsque le refus attendu **et** le maintien des usages autorisés sont prouvés. Le statut Active n’est pas une recette.

---

## 🥇 La Règle d’Or

**Si tu dois retenir une chose : en “Advanced”, chaque opération qui ne correspond à aucune règle est refusée ; décrivez donc aussi tout ce qui doit continuer à fonctionner.**

Nommez l’intention, gardez des règles lisibles et préparez le remplacement avant de toucher à l’actif. Et ne confondez jamais création d’item et accès aux données existantes.

Quel serait votre premier contrôle utile : réserver les notebooks à une équipe, limiter la création de Data agents ou différencier production et exploration ?

Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [Microsoft Fabric : Data Agent vs Copilot](https://blog.antoinewang-tech.com/p/microsoft-fabric-data-agent-copilot) — pour distinguer les usages avant de choisir un contrôle qui affecte l’un ou les deux.
* [Microsoft Fabric : Git Integration](https://blog.antoinewang-tech.com/p/microsoft-fabric-git-integration) — pour replacer les définitions de gouvernance dans un cycle de versionnement.
* [Sécurité des données : Pourquoi vous ne pouvez plus la traiter en fin de projet](https://blog.antoinewang-tech.com/p/securite-microsoft-fabric) — pour replacer les permissions et la sécurité des données dans la conception de votre plateforme.

  ---

## 📚 Ressources pour aller plus loin

* [Vue d’ensemble des Fabric policies (preview)](https://learn.microsoft.com/en-us/fabric/governance/fabric-policies-overview) — Policies disponibles, périmètres, logique d’autorisation et restrictions régionales.
* [Créer et activer une Fabric policy](https://learn.microsoft.com/en-us/fabric/governance/fabric-policies-get-started) — paramètre tenant, création du Policy set, activation, recette et désactivation.
* [Gérer le Policies center du OneLake catalog](https://learn.microsoft.com/en-us/fabric/governance/fabric-policies-manage-onelake-catalog) — rôles, éligibilité des utilisateurs, gestion des règles et synchronisation avec l’item actif.
* [Allow item creation](https://learn.microsoft.com/en-us/fabric/governance/fabric-policies-item-creation) — conditions, opérateurs `AnyOf` et `NoneOf`, identifiants de groupes et blocage implicite.
* [Fabric policies REST APIs](https://learn.microsoft.com/en-us/fabric/governance/fabric-policies-rest-api) — création, inventaire List Policy Sets, activation, Git, CI/CD et identités d’automatisation.
* [Référence API : types d’items Fabric](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/create-item#itemtype) — identifiant `DataAgent`, distinct du nom affiché dans l’interface.
* [Partage et permissions des Fabric data agents](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-sharing) — version publiée, droits de consommation et accès nécessaires aux sources.
* [Modèle de permissions Fabric](https://learn.microsoft.com/en-us/fabric/security/permission-model) — articulation entre permissions d’items et rôles Workspace.
