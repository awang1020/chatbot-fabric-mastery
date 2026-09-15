---
title: Microsoft Fabric : Comment utiliser Rayfin et les Apps ? (+démo)
url: https://blog.antoinewang-tech.com/p/rayfin-fabric-apps-demo
date: 2026-06-23
author: Antoine Wang
source: substack
---

# Microsoft Fabric : Comment utiliser Rayfin et les Apps ? (+démo)

Bonjour à tous, je suis Antoine Wang.

J’aide les profils techniques à maîtriser l’architecture de Microsoft Fabric, et j’aide les décideurs à comprendre l’impact réel de cette technologie.

Mon objectif ? Vulgariser le complexe et vous donner les clés pour maîtriser Microsoft Fabric, une plateforme de données SaaS unifiée et alimentée par l’IA pour simplifier la gestion des données et l’analyse.

🆕 **Nouveauté pour les lecteurs** : j’ai créé **Ask Fabric Mastery**, un assistant IA qui répond à vos questions sur Microsoft Fabric & Power BI en s’appuyant uniquement sur les 24 éditions de cette newsletter. Réponses sourcées, sans hallucination, avec un lien direct vers l’édition d’origine.

👉 **Testez-le maintenant** : [ask-fabric-mastery](http://awang1020.github.io/ask-fabric-mastery)  
🔑 **Code d’accès (ce code est réservé aux abonnés Fabric Mastery) :**

Cette newsletter est 100% gratuite. En vous abonnant maintenant, vous recevrez en exclusivité mon “One-Pager” pour cartographier l’ensemble de la solution Fabric en un coup d’oeil.

Merci à celles et ceux qui me suivent depuis le début. Sans plus attendre, entrons dans le vif du sujet !

---

## ⚡ En 30 secondes

**Ce qu’il faut retenir :**

* **Rayfin** vous permet de définir backend, data model, API et policies en code, puis de déployer dans Fabric avec `*rayfin up*`.
* Avec **Fabric Apps (Preview)**, l’app devient un artefact Fabric gouverné, avec SSO Entra ID, backend URL, SQL + API GraphQL et static hosting.
* Ma démo est pensée pour être **testée dans VOTRE environnement** : aucune config tenant commitée, chacun cible son propre workspace capacity-backed.

---

L’IA générative avance à une vitesse fulgurante. Voici ce qui est devenu possible aujourd’hui : un agent IA (GitHub Copilot, Claude, Cursor…) génère une app complète, frontend, backend, base de données, API, en moins de 10 minutes. Et contrairement à ce qu’on croyait il y a 2 ans, ce n’est plus juste un prototype jetable : vous pouvez le **déployer directement en production** sur une plateforme gouvernée comme Fabric.

Mais voilà le piège : la plupart des gens ne le savent pas encore. Et même ceux qui l’essaient se retrouvent bloqués au moment du déploiement.

* Où stocker les données ?
* Comment mettre en place l’authentification sans exposer les secrets ?
* Qui peut accéder à quoi ?
* Comment transformer ce prototype généré en une app qui tient vraiment en production, avec gouvernance et RBAC ?

C’est exactement ce problème que Rayfin (+ Fabric Apps) résout.

---

## C’est quoi ? Rayfin + Fabric Apps (Preview)

**Rayfin** est un SDK + CLI open source annoncé à Build 2026 pour définir un backend complet en code (modèles, API, accès, logique), puis le déployer sur Microsoft Fabric.

**Fabric Apps (Preview)** est la brique d’exécution managée dans Fabric : l’application tourne comme un item de la plateforme, avec gouvernance, sécurité, et intégration native avec l’écosystème Fabric.

En pratique, vous passez d’un bricolage multi-services à un workflow code-first plus direct : **définir, déployer, itérer**.

---

## Réflexion

✅ **Qui va vraiment en tirer de la valeur ? (métier vs dev)**

* **Profils métier (non-code) :** oui, il y a une opportunité de **vibe coding** avec un agent pour prototyper vite une app interne. Mais le cadre idéal reste un binôme avec une personne technique pour vérifier le schéma, les droits et le déploiement.
* **Développeurs applicatifs classiques** : beaucoup ne vont pas “coder une app dans Fabric” au sens plateforme complète, car cela demande de comprendre les prérequis tenant/capacity, les permissions et le modèle de déploiement.
* **La bonne lecture** : Rayfin n’est pas “no-code magique” ni “réservé aux experts Fabric”. C’est surtout un accélérateur pour des équipes mixtes métier + tech qui veulent livrer vite sans perdre la gouvernance.

---

## 🎯 Démo rapide et efficace !

**Zava Deliveries** est une application de preuve de livraison (POD) complète et authentifiée (je n’ai codé aucune ligne de code, tout en “vibe coding” avec Github Copilot).

**GitHub** : [awang1020/rayfin-delivery-app](https://github.com/awang1020/rayfin-delivery-app)

**Le contexte métier :**

* Les chauffeurs **enregistrent chaque livraison** (destinataire, adresse, articles) avec preuves photo et état des articles (bon, endommagé, manquant, partiel).
* Les clients **confirment la réception** avec avis ou signalent un problème.
* En cas de litige, le chauffeur **propose une résolution** (avec preuve mise à jour) ; le client **revalide** ou **relance** une nouvelle contestation.

**Pourquoi c’est un cas d’école** :

* Authentification Fabric SSO (aucun accès anonyme).
* Row-level security : une livraison n’est visible que par son chauffeur ou son client.
* Workflow réaliste multi-étapes avec résolution de litige.

---

## Points de vigilance / Pièges à éviter

1. **Preview n’est pas GA**

   Fabric Apps est en preview. Le bon reflexe est de tester sur un environnement de validation et de verifier votre region/capacity supportee avant de planifier un usage business-critical.
2. **Prérequis tenant souvent oubliés**

   Il faut :

   1. Un workspace sur Fabric capacity (trial ou payant) et vérifiez la [disponibilité sur la région](https://learn.microsoft.com/en-us/fabric/admin/region-availability).
   2. Le workload Fabric Apps (preview) activé par un tenant admin.
   3. Les droits pour créer des items dans le workspace cible.
3. **Ne confondez pas vitesse et gouvernance automatique**

   Rayfin accélère la mise en route, mais vous restez responsable de ce que votre app expose. Concrètement : gestion des secrets, politiques d’accès, et hygiène des permissions item-level.

---

## 🥇 La Règle d’Or

Si tu dois retenir une chose : Rayfin ne remplace pas votre discipline d’architecture, mais il élimine une grosse partie de la plomberie qui vous ralentit entre “idée” et “app testable

Le vrai gain, ce n’est pas seulement de deployer vite. C’est de permettre à plusieurs personnes de tester la même application dans leur propre environnement Fabric, avec des règles de gouvernance explicites, sans copier-coller de secrets ni bricolage infra.

Et oui, les profils métier peuvent s’en servir en mode “vibe coding” pour accélérer le prototype. Mais pour aller au-delà du “démo effect” et tenir en conditions reelles, il faut une couche de discipline technique sur le déploiement et la sécurite.

> Et vous, avez-vous testé Rayfin et Fabric Apps ? Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [Migration Power BI Premium → Microsoft Fabric](https://blog.antoinewang-tech.com/p/migration-power-bi-premium-to-fabric)
* [Microsoft Fabric : Révolution ou simple rebranding ?](https://blog.antoinewang-tech.com/p/microsoft-fabric-revolution-ou-rebranding)

  ---

## 📚 Ressources pour aller plus loin

* [What is Fabric Apps (Preview)?](https://learn.microsoft.com/en-us/fabric/apps/overview)
* [Introducing Rayfin: A new AI-first way to build, deploy, and govern application backends](https://community.fabric.microsoft.com/t5/Fabric-Updates-Blog/Introducing-Rayfin-A-new-AI-first-way-to-build-deploy-and-govern/ba-p/5191676)
* [Demo repo](https://github.com/awang1020/rayfin-delivery-app)
