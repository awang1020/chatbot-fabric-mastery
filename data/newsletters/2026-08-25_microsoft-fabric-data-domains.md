---
title: Microsoft Fabric : Bonnes pratiques pour créer et gérer les domaines
url: https://blog.antoinewang-tech.com/p/microsoft-fabric-data-domains
date: 2026-08-25
author: Antoine Wang
source: substack
---

# Microsoft Fabric : Bonnes pratiques pour créer et gérer les domaines

Bonjour à tous, je suis Antoine Wang.

J’aide les profils techniques à maîtriser l’architecture de Microsoft Fabric, et j’aide les décideurs à comprendre l’impact réel de cette technologie.

Mon objectif ? Vulgariser le complexe et vous donner les clés pour maîtriser Microsoft Fabric, une plateforme de données SaaS unifiée et alimentée par l’IA pour simplifier la gestion des données et l’analyse.

🆕 **Nouveauté pour les lecteurs** : j’ai créé **Ask Fabric Mastery**, un assistant IA qui répond à vos questions sur Microsoft Fabric & Power BI en s’appuyant uniquement sur les 34 éditions de cette newsletter. Réponses sourcées, sans hallucination, avec un lien direct vers l’édition d’origine.

👉 **Testez-le maintenant** : [ask-fabric-mastery](http://awang1020.github.io/ask-fabric-mastery)  
🔑 **Code d’accès (ce code est réservé aux abonnés Fabric Mastery) :**

Cette newsletter est 100% gratuite. En vous abonnant maintenant, vous recevrez en exclusivité mon “One-Pager” pour cartographier l’ensemble de la solution Fabric en un coup d’œil.

Merci à celles et ceux qui me suivent depuis le début. Sans plus attendre, entrons dans le vif du sujet !

---

## ⚡ En 30 secondes

Ce qu’il faut retenir :

* Un **domaine Fabric** regroupe logiquement des workspaces autour d’un périmètre métier (Finance, Sales, Supply Chain…). Il porte la gouvernance déléguée (settings, sensitivity labels, certification) et alimente le filtre du OneLake Catalog.
* Un workspace = un seul domaine (+ éventuellement un sous-domaine). Ce n’est pas un tag transverse. Le rattachement multi-domaines n’existe pas by-design.
* L’action à lancer : verrouiller le scope Contributors de vos domaines (\*\*AdminsOnly\*\*), poser une alerte d’audit sur DeleteDataDomainFolderRelationsAsFolderOwner, et gérer les rattachements as-code via les REST APIs Admin ou le provider Terraform Fabric.

---

## Combien de vos workspaces sont rattachés à un domaine, aujourd’hui ?

Posez-vous la question franchement. Ouvrez votre tenant Fabric, comptez vos workspaces, et regardez combien ont réellement un domaine assigné. La réalité du terrain, je vous la donne : entre les workspaces “test-demo-lab” créés par les métiers, les workspaces techniques oubliés par la BI centrale et les workspaces migrés depuis Power BI Premium sans nettoyage, c’est souvent la majorité qui vit **sans propriétaire clair**.

Résultat visible dans le OneLake Catalog : un utilisateur cherche **les données Finance**, et il tombe sur des artefacts dispersés dans dix workspaces, dont trois qu’un consultant a créés en 2020 et dont plus personne ne connaît le contenu. C’est exactement le marécage que la data mesh est censée éviter.

Les **Domaines dans Fabric** sont la brique qui résout ce problème.

---

## C’est quoi ?

Un domaine, dans Fabric, c’est un **regroupement logique de workspaces** autour d’un périmètre métier (Finance, Sales, Manufacturing…). Quand un workspace est rattaché à un domaine, tous les artefacts qu’il contient héritent d’un attribut de domaine dans leurs métadonnées.

**Trois piliers à graver :**

* Rattachement 1:1 : un workspace est rattaché à **un seul domaine** (et optionnellement à un seul sous-domaine sous ce domaine).
* Gouvernance fédérée : certains tenant settings peuvent être délégués au niveau du domaine (sensitivity labels par défaut, certification, endorsement). Chaque business unit fixe ses règles.
* Consommation ciblée : le OneLake Catalog filtre les items par domaine. Un utilisateur ne voit que ce qui est pertinent pour lui.

Ne vous détrompez pas : le domaine n’est pas un mécanisme de sécurité. Il ne restreint pas l’accès aux artefacts. La visibilité et l’accès dépendent des rôles de workspace et des permissions d’item, pas du domaine.

---

## Concepts Clés

### 1. Les trois rôles avant tout

Avant de créer votre premier domaine, il faut comprendre qui fait quoi. Fabric introduit trois rôles distincts autour des domaines :

#### a. Fabric admin : le tenant admin

Il crée, édite, supprime les domaines. Il nomme les “domain admins” et les “domain contributors”. Il rattache les workspaces via l’onglet **Domains** de l’admin portal. C’est le seul rôle à voir tous les domaines de tous les tenants.

#### b. Domain admin : l’expert métier

Idéalement, un data owner métier, pas un profil IT central. Il gère son domaine : description, image, contributors, default domain, override des tenant settings délégués. Il ne peut pas supprimer le domaine, changer son nom, ou ajouter d’autres domain admins. C’est une frontière volontaire pour éviter la dérive.

#### c. Domain contributor : le workspace admin habilité

Un domain contributor est un workspace admin (au sens du rôle workspace) qu’un domain admin ou un Fabric admin a autorisé à rattacher ses workspaces à un domaine, via l’onglet **Domain** des settings du workspace. Il n’a pas accès à l’onglet Domains de l’admin portal.

### 2. Les trois façons d’assigner des workspaces

Fabric propose trois méthodes pour rattacher des workspaces à un domaine, plus un mécanisme automatique.

#### a. Par nom de workspace

Vous cherchez les workspaces par leur nom, et vous cochez ceux à rattacher. Utile si votre convention de nommage est propre (ex. `FIN-Reporting-Prod`, `FIN-Modeling-Dev` → tous rattachés à Finance).

#### b. Par admin de workspace

Vous sélectionnez un user ou un security group. Tous les workspaces dont ce user (ou ce groupe) est admin sont rattachés. Attention : l’action ne concerne que les workspaces existants, pas les futurs workspaces créés.

#### c. Par capacité

Vous sélectionnez une ou plusieurs Fabric capacités. Tous les workspaces attachés à ces capacités sont rattachés au domaine. C’est le pattern data mesh par excellence : une capacité par département, un domaine par département.

#### d. Le Default domain : le mécanisme automatique

Vous désignez un domaine comme default pour des users ou security groups. Le système scanne alors les workspaces :

* Si le workspace a déjà un domaine : il est préservé (pas d’override).
* Si le workspace est non rattaché : il est rattaché automatiquement rattaché au domaine par défaut.

**Et bonus** : les futurs workspaces créés par ces users (ou security groups) seront automatiquement rattachés. Les users concernés deviennent en général domain contributors des workspaces ainsi rattachés.

⚠️ **Point de vigilance sur l’override** : un Fabric admin ou domain admin peut écraser un rattachement existant, mais uniquement si le tenant setting **[Allow tenant and domain admins to override workspace assignments (preview)](https://learn.microsoft.com/en-us/fabric/admin/service-admin-portal-domain-management-settings)** est activé. Cette option est activée par défaut, mais elle peut avoir été coupée par prudence dans votre tenant. Les REST APIs respectent aussi ce toggle.

Mon conseil : Commencez par la méthode par capacité si vous avez adopté le modèle une capacité par département. C’est le rattachement le plus stable, le plus lisible, et celui qui aligne le mieux la gouvernance financière (SKU, CU) avec la gouvernance data (domaine).

### 3. Les deux angles morts qui font mal en production

Ici, on rentre dans le dur. Ces deux pièges reviennent systématiquement dans les projets et méritent chacun une section dédiée.

#### 3.a L’admin de workspace peut retirer le domaine

Le contexte : vous avez posé un default domain pour votre équipe Finance. Tous les workspaces créés par ces users sont rattachés automatiquement au domaine Finance. Excellent. Sauf que…

Le problème : le workspace admin peut aller dans les settings de son workspace, ouvrir l’onglet Domain, et retirer le rattachement au domaine. Silencieusement. Sans que personne ne soit notifié. Et si votre stratégie de gouvernance, refacturation repose sur ce rattachement (sensitivity label par défaut, certification, filtrage OneLake Catalog), vous venez de perdre le contrôle.

L’audit Fabric enregistre l’événement sous `DeleteDataDomainFolderRelationsAsFolderOwner`. Encore faut-il le surveiller.

Voici comment le blinder, par couche :

**Préventif : Restreindre les Contributors du domaine.**

Dans les settings du domaine, l’onglet **Contributors**, trois choix :

* **Tout le monde dans l’organisation (default)** : n’importe quel workspace admin peut rattacher/détacher son workspace au domaine.
* **Users et groupes spécifiques** : seuls ces users, s’ils sont aussi workspace admins, peuvent le faire.
* **Tenant et domain admins uniquement** : seuls les tenant admins et domain admins peuvent rattacher/détacher.

Passez ce paramètre à “Tenant et domain admins uniquement**”** pour les domaines critiques (Finance, RH, conformité). Communiquez aux workspace admins que le rattachement au domaine relève de la gouvernance centrale, pas de leur périmètre.

**Détectif : poser une alerte sur l’audit log.**

Le schéma d’audit dédié aux domaines expose les opérations suivantes (extrait des plus importantes) :

* DeleteDataDomainFolderRelationsAsFolderOwner : Un workspace owner a retiré le domaine depuis les settings du workspace
* UpdateDataDomainFoldersRelationsAsAdmin Un tenant/domain admin a (dés)assigné des workspaces |

Je vous laisse regarder plus en détails dans la [documentation](https://learn.microsoft.com/en-us/fabric/governance/domains-audit-schema).

---

## Points de vigilance

⚠️ Le domaine n’est pas de la sécurité

Un rattachement à un domaine ne restreint pas l’accès. Un user peut ne pas être domain contributor, ni domain admin, et voir quand même les items du domaine dans le OneLake catalog si les permissions d’item l’autorisent. À l’inverse, tous les users du tenant voient tous les domaines dans le filtre du catalog, peu importe leurs droits. Le domaine sert à organiser et gouverner, pas à cloisonner.

⚠️ Les sous-domaines ont des settings limités

À date, les sous-domaines n’exposent que les general settings (nom, description). Pas d’image, pas de contributors dédiés, pas de default domain, pas d’override de tenant settings. Toute la mécanique de délégation vit au niveau du domaine parent. Ne comptez pas sur les sous-domaines pour une gouvernance différenciée fine.

⚠️ Le default domain ne rétro-applique pas

Quand vous définissez un default domain, il ne remplace pas les rattachements existants, il ne fait qu’assigner les workspaces non rattachés. Si vous voulez homogénéiser un tenant existant, le default domain seul ne suffira pas. Il vous faudra un premier passage manuel (ou en API) pour aligner l’existant, puis le default domain gère les nouveaux workspaces.

---

## 🥇 La Règle d’Or

Si tu dois retenir une chose : un workspace = un domaine, celui qui en est responsable. Le domaine porte l’ownership et la gouvernance déléguée, pas les tags, pas la classification transverse, pas la sécurité.

L’impact terrain est direct : quand vos domaines sont bien câblés, un consommateur qui cherche une donnée sait immédiatement à qui la demander, un DPO qui audite votre tenant retrouve la matrice de responsabilité en trois clics, et vos data owners métier reprennent la main sur leurs settings (sensitivity, certification) sans passer par un ticket IT. Vous transformez le tenant Fabric de marécage en plateforme structurée, sans avoir à refondre l’organisation, juste en posant la brique de gouvernance au bon endroit.

> Et vous, quel est votre avis sur les domaines dans Fabric ?

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [Microsoft Fabric : Comprendre OneLake, le "OneDrive" de la Data](https://blog.antoinewang-tech.com/p/onelake-microsoft-fabric-guide)
* [Microsoft Fabric : Bonnes pratiques pour la Gouvernance des workspaces](https://blog.antoinewang-tech.com/p/gouvernance-workspaces-microsoft-fabric)

---

## 📚 Ressources pour aller plus loin

Pour approfondir le sujet et affiner votre design de domaines, je vous recommande ces lectures essentielles issues de la documentation officielle :

* [Fabric domains — concepts et setup](https://learn.microsoft.com/en-us/fabric/governance/domains) : rôles, création, rattachement, default domain, delegated settings
* [Best practices for planning and creating domains](https://learn.microsoft.com/en-us/fabric/governance/domains-best-practices) : structures organisationnelles (functional, product, process, region, mixed) et méthodes d’assignation
* [Audit schema for domains in Fabric](https://learn.microsoft.com/en-us/fabric/governance/domains-audit-schema) : la liste complète des OperationNames à surveiller dans le Fabric activity log
* [Domains — Fabric REST Admin API reference](https://learn.microsoft.com/en-us/rest/api/fabric/admin/domains) : endpoints pour les rattachements as-code
* [Domain management tenant settings](https://learn.microsoft.com/en-us/fabric/admin/service-admin-portal-domain-management-settings) : override des rattachements existants et paramètres tenant liés
