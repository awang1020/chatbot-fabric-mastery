---
title: Microsoft Fabric en production : la checklist en 10 points avant le Go Live
url: https://blog.antoinewang-tech.com/p/microsoft-fabric-mise-en-production-checklist
date: 2026-06-09
author: Antoine Wang
source: substack
---

# Microsoft Fabric en production : la checklist en 10 points avant le Go Live

Un PoC qui “fonctionne bien” et une plateforme production-ready, ce sont deux états radicalement différents.

Le PoC tourne sur un workspace unique, avec des connexions hardcodées, sans gouvernance, sans sécurité granulaire, et sans filet de secours si quelque chose casse.

* Ça suffit pour valider un cas d’usage.
* Ça ne suffit pas pour livrer une plateforme que des équipes métier vont utiliser tous les jours.

Depuis le début de cette série, on a posé les briques une par une: architecture médaillon, gouvernance des workspaces, les pipelines de déploiement, variable library, sécurité RLS/CLS/OLS…

Aujourd’hui, on assemble.

Voici les 10 points à cocher avant de considérer qu’une plateforme Fabric est réellement prête pour la production, et les erreurs classiques associées à chacun.

Gardez cette liste. Elle vous évitera des nuits d’astreinte.

---

## Les 10 points de la checklist Fabric Production-Ready

### ✅ Point 1 : Architecture ! Votre architecture médaillon est-elle un contrat organisationnel, pas juste un nommage ?

*→ **Post de référence** : [Architecture Medallion dans Fabric](https://antoinewang.substack.com/p/architecture-medaillon-microsoft-fabric)*

Bronze, Silver, Gold : trois lakehouses bien nommées ne font pas une Medallion.

La vraie question est : **chaque couche a-t-elle une équipe propriétaire clairement désignée ?**

* Bronze → équipe ingestion IT.
* Silver → Data Engineers.
* Gold → équipe BI ou métier.

Sans ce contrat organisationnel, la Médaillon est une convention de nommage. Avec lui, c’est un découplage structurel qui permet à chaque équipe de livrer sans bloquer les autres.

**À vérifier :**

* Avez-vous documenté qui est responsable de quoi dans chaque couche ?
* La couche Gold est-elle un Lakehouse ou un Warehouse selon les compétences de l’équipe consommatrice ?
* Est-ce que vous avez réellement besoin de trois couches ?

---

### ✅ Point 2 : Organiser les données ! Votre OneLake est-il organisé ou subi ?

*→ **Post de référence** : [Architecture OneLake, Choix du Data Store](https://open.substack.com/pub/antoinewang/p/data-store-microsoft-fabric?r=6sgmm7&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true)*

OneLake est le socle de données de toute la plateforme.

Avant de créer votre dixième Lakehouse, avez-vous défini une convention de nommage des dossiers, une stratégie de partitionnement, et une règle claire sur ce qui va dans la zone Tables (managed) vs la zone Files (unmanaged) ?

Lakehouse ? Warehouse ? Eventhouse ? SQL DB ? Comment choisir le bon moteur de stockage sans créer une “dette technique” future ?

**À vérifier :**

* Vos données sont-elles déjà dans une application Azure ?
* Quelle est la vitesse et le volume de la donnée ?
* Quelle est la compétence technique de votre équipe ?

---

### ✅ Point 3 : Gouvernance ! Votre gouvernance des workspaces tient-elle à l’échelle ?

*→ **Post de référence** : [Gouvernance des Workspaces dans Fabric](https://open.substack.com/pub/antoinewang/p/gouvernance-workspaces-microsoft-fabric?r=6sgmm7&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true)*

Trois questions simples à vous poser maintenant, avant que le chaos s’installe :

* Qui peut créer des workspaces ?
* Qui associe les workspaces aux capacités ?
* Qui est propriétaire de quoi ?

Si vous n’avez pas de réponse documentée à ces trois questions et que vous avez des workspaces, c’est que vous avez un problème de gouvernance.

Référez-vous au post pour avoir une convention de nommage claire et propre (`[Domaine]-[Couche]-[Environnement]`) et des Domaines dans Fabric pour déléguer la gestion par entité métier.

**À vérifier :**

* Avez-vous restreint la création de workspaces dans les paramètres tenant ?
* Vos workspaces sont-ils rattachés à des domaines Fabric avec des Domain Admins désignés ?

---

### ✅ Point 4 : La sécurité ! Vos rôles workspace sont-ils gérés par groupes de sécurité, pas par individus ?

*→ **Post de référence** : [Gouvernance des Workspaces dans Fabric](https://open.substack.com/pub/antoinewang/p/gouvernance-workspaces-microsoft-fabric?r=6sgmm7&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true)*

C’est le détail d’implémentation qui coûte le plus cher en maintenance sur la durée.

Si vous attribuez les rôles, utilisateur par utilisateur, au niveau des workspaces, à chaque départ, arrivée ou changement de poste, cela nécessite une intervention manuelle sur chaque workspace concerné.

Ouf, gérer les rôles via des groupes de sécurité, c’est retirer/ajouter une personne d’un groupe, et toutes ses permissions suivent automatiquement.

**À vérifier :**

* Avez-vous zéro rôle workspace attribué directement à un utilisateur individuel ?
* Tous vos rôles passent-ils par des groupes de sécurité ?

---

### ✅ Point 5 : En prod, on pense au CI/CD ! Votre chaîne DEV → TEST → PROD est-elle configurée avant le premier déploiement ?

*→ **Post de référence** : [Deployment Pipelines dans Fabric](https://open.substack.com/pub/antoinewang/p/deployment-pipelines-microsoft-fabric?r=6sgmm7&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true)*

Le nombre de stages d’un Deployment Pipeline Fabric est figé à la création, vous ne pouvez pas en ajouter après coup sans tout recréer.

Et un workspace ne peut appartenir qu’à un seul pipeline, quel que soit le stage.

Ces deux contraintes structurelles exigent de planifier votre architecture d’environnements sur papier avant de créer votre premier pipeline.

**La bonne séquence** : Git integration en premier, Deployment Pipelines ensuite. Pas l’inverse.

**À vérifier :**

* Vos workspaces DEV, TEST et PROD sont-ils créés et nommés avant la configuration du pipeline ?
* Votre workspace DEV est-il synchronisé avec un repository Git ?

---

### ✅ Point 6 : Paramétrage ! Avez-vous zéro connexion hardcodée dans vos items Fabric ?

*→ **Post de référence** : [Variable Library et paramétrage dans Fabric](https://open.substack.com/pub/antoinewang/p/variable-library-microsoft-fabric?r=6sgmm7&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true)*

Une chaîne de connexion hardcodée dans un pipeline, c’est une bombe à retardement. Elle voyage silencieusement lors du déploiement DEV → PROD et envoie vos données de production au mauvais endroit.

La Variable Library est la réponse native de Fabric : elle centralise vos paramètres de configuration par workspace, avec des jeux de valeurs distincts par environnement.

Point d’attention critique : l’activation du bon jeu de valeurs post-déploiement n’est pas automatique.

Elle doit être automatisée via les APIs Fabric ou documentée comme étape obligatoire dans votre runbook.

**À vérifier :**

* Avez-vous une Variable Library configurée sur chaque workspace avec des jeux de valeurs DEV, TEST et PROD ?
* L’activation du jeu de valeurs cible est-elle automatisée ou documentée dans votre processus de déploiement ?

---

### ✅ Point 7 : Sécurité, encore et encore ! Votre stratégie de sécurité granulaire est-elle architecturée, pas rajoutée en dernier ?

*→ **Post de référence** : [RLS / CLS / OLS dans Fabric](https://open.substack.com/pub/antoinewang/p/securite-microsoft-fabric?r=6sgmm7&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true)*

La sécurité fine de la donnée dans Fabric opère sur trois couches distinctes et complémentaires : OneLake RBAC (Object-Level, Row-Level, Column-Level) pour la couche stockage, SQL Endpoint et Warehouse pour la couche requêtage, semantic model Power BI pour la couche consommation.

Ces trois couches ne se substituent pas, elles se complètent selon le moteur d’accès.

L’erreur classique : sécuriser uniquement le semantic model Power BI en oubliant que certains utilisateurs accèdent aussi via le SQL Endpoint ou directement via Spark.

**À vérifier :**

* Avez-vous cartographié tous les chemins d’accès à vos données sensibles ?
* Votre sécurité dynamique (USERPRINCIPALNAME) remplace-t-elle vos rôles statiques par profil là où c’est possible ?
* Les utilisateurs Contributor dans vos workspaces de consommation sont-ils au strict minimum nécessaire ?

---

### ✅ Point 8 : Ingestion ! Votre stratégie d’ingestion est-elle choisie, pas subie ?

*→ Post de référence :*

* [Maîtriser l’Écosystème d’Ingestion et d’Orchestration](https://open.substack.com/pub/antoinewang/p/microsoft-fabric-data-ingestion-tools?r=6sgmm7&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true)
* *[Flux de tâches dans Fabric](https://open.substack.com/pub/antoinewang/p/flux-de-taches-microsoft-fabric?r=6sgmm7&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true)*

C’est la question que personne ne pose assez tôt : **“Quel outil d’ingestion pour quel cas d’usage ?”** Et pourtant, c’est souvent le premier choix structurant de votre plateforme, celui qui conditionne vos coûts de CUs, la maintenabilité de vos flux, et l’autonomie de vos équipes sur la durée.

Shortcut, Pipeline, Dataflow Gen2, Notebooks, Eventstream, choisissez l’outil le plus adapté à vos besoins.

**À vérifier :**

* Avez-vous cartographié chaque flux d’ingestion avec l’outil approprié selon le volume, la fréquence et le profil de l’équipe qui le maintient ?

---

### ✅ Point 9 : Administrer la plateforme ! Avez-vous un responsable désigné pour gérer la charge de la capacité ?

*→ **Post de référence** : [Gestion de capacité Fabric](https://open.substack.com/pub/antoinewang/p/capacity-metrics-fabric?r=6sgmm7&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true)*

La capacité Fabric est une ressource partagée entre tous vos workspaces.

Plus vous y rattachez de workspaces et de workloads simultanés, plus vous mutualisez, et plus vous exposez l’ensemble aux variations de performance.

Sur le terrain, la question “qui gère la capacité ?” n’a souvent pas de réponse claire au moment où un job batch mal dimensionné pénalise les dashboards de la direction en production.

Désignez explicitement une équipe DataOps ou un responsable pour gérer les capacités par domaines/workspaces, pour surveiller de manière proactive les CUs, et de prendre des décisions d’optimisation et de scaling.

**À vérifier :**

* Avez-vous un propriétaire de capacité Fabric désigné ?
* Avez-vous des capacités séparées pour production, développement et expérimentation ?

---

### ✅ Point 10 : Comprendre vos données ! Votre OneLake est-il gouverné, découvrable et documenté ?

*→ Post de référence : [Comprendre OneLake, le “OneDrive” de la Data](https://open.substack.com/pub/antoinewang/p/microsoft-fabric-onelake?r=6sgmm7&utm_campaign=post&utm_medium=web&showWelcomeOnShare=true)*

Voici la question qui fait mal : combien de fois la même donnée est-elle copiée dans votre organisation ?

Une fois dans le Data Lake, une fois dans le Warehouse, une fois dans le Datamart Finance, et encore une copie sur le poste d’un analyste qui n’était pas sûr que la version partagée était la bonne.

**C’est le chaos des données.**

Et **OneLake** est la réponse structurelle de Fabric à ce problème, à condition de l’exploiter correctement.

La philosophie OneLake est simple : amener le calcul à la donnée, pas l’inverse.

* Shortcuts pour virtualiser sans copier.
* Mirroring pour répliquer sans ETL.
* Delta Parquet comme format universel lisible par tous les moteurs.

Mais cette promesse ne tient que si votre organisation de la donnée dans OneLake est structurée, pas subie.

**À vérifier :**

* Avez-vous activé l’endorsement sur vos datasets critiques dans le OneLake Catalog ?
* Votre équipe utilise-t-elle les Shortcuts avant de créer des pipelines de copie — ou duplique-t-elle encore de la donnée par réflexe ?

---

## 🥇 La Règle d’Or

**Si tu dois retenir une chose :** Une plateforme Fabric production-ready n’est pas le résultat d’une configuration technique parfaite, c’est le résultat de décisions organisationnelles prises avant d’ouvrir la plateforme.

Architecture, gouvernance, déploiement, paramétrage, sécurité : chacun de ces sujets exige des choix humains avant des choix techniques.

Les outils Fabric sont là pour exécuter ces choix, pas pour les remplacer.

---

## 💬 À vous de jouer

Sur ces 10 points, lequel est le **grand oublié** dans vos projets Fabric, celui que vous avez découvert trop tard ? Et si vous deviez en ajouter un onzième à cette checklist, lequel serait-il ?

**On construit la liste ensemble en commentaire.** 👇
