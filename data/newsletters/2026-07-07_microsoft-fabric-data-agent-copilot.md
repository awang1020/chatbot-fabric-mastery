---
title: Fabric Data Agent vs Copilot : les 3 différences qui comptent en 2026
url: https://blog.antoinewang-tech.com/p/microsoft-fabric-data-agent-copilot
date: 2026-07-07
author: Antoine Wang
source: substack
---

# Fabric Data Agent vs Copilot : les 3 différences qui comptent en 2026

Bonjour à tous, je suis Antoine Wang.

J’aide les profils techniques à maîtriser l’architecture de Microsoft Fabric, et j’aide les décideurs à comprendre l’impact réel de cette technologie.

Mon objectif ? Vulgariser le complexe et vous donner les clés pour maîtriser Microsoft Fabric, une plateforme de données SaaS unifiée et alimentée par l’IA pour simplifier la gestion des données et l’analyse.

🆕 **Nouveauté pour les lecteurs** : j’ai créé **Ask Fabric Mastery**, un assistant IA qui répond à vos questions sur Microsoft Fabric & Power BI en s’appuyant uniquement sur les 27 éditions de cette newsletter. Réponses sourcées, sans hallucination, avec un lien direct vers l’édition d’origine.

👉 **Testez-le maintenant** : [ask-fabric-mastery](http://awang1020.github.io/ask-fabric-mastery)  
🔑 **Code d’accès (ce code est réservé aux abonnés Fabric Mastery) :**

Cette newsletter est 100% gratuite. En vous abonnant maintenant, vous recevrez en exclusivité mon “One-Pager” pour cartographier l’ensemble de la solution Fabric en un coup d’œil.

Merci à celles et ceux qui me suivent depuis le début. Sans plus attendre, entrons dans le vif du sujet !

---

## ⚡ En 30 secondes

* **Copilot** est un assistant préconfiguré et généraliste, intégré aux workloads Fabric et à Power BI. Il fait deux choses : il aide à produire (code, DAX, requêtes) et il répond en langage naturel aux utilisateurs métier (Copilot dans Power BI, expérience standalone). Vous ne le paramétrez pas.
* **Data Agent** est un artefact que vous configurez : un expert curé sur un domaine précis (instructions, exemples, sources choisies). Gouverné, en lecture seule, il s’expose dans tout l’écosystème Microsoft : Teams, M365 Copilot, Foundry… et jusque dans Copilot lui-même.
* L’action à lancer : arrêtez de demander “Copilot ou Data Agent ?”. Demandez plutôt “Ai-je besoin d’un assistant généraliste prêt à l’emploi, ou d’un expert gouverné que je configure sur mon domaine ?”. Vous avez la réponse.

---

Ce matin, j’ai un client qui me dit : “Antoine, on a activé Copilot dans Fabric. Du coup, on n’a plus besoin des Data Agents, c’est bien ça ?”

Je vois souvent cette confusion, et elle est parfaitement logique. Les deux utilisent des grands modèles de langage. Les deux répondent en langage naturel. Sur le papier, on dirait deux noms pour la même chose.

La réalité du terrain, c’est que ce sont deux briques bien distinctes, et je vais vous expliquer la différence au niveau des configurations et des rôles.

Let’s go !

---

## Deux IA, Deux Niveaux de Configuration

Posons le cadre simplement. Copilot et Data Agent reposent sur des LLM (Azure OpenAI) et savent tous les deux répondre en langage naturel. Ce qui les sépare, c’est le niveau de configuration et le rôle :

* **Copilot dans Fabric & Power BI** est un assistant IA intégré nativement dans toute l’expérience : partout où apparaît l’icône Copilot ([Dataflow gen2](https://antoinewang.substack.com/p/copilot-data-flow-gen2-microsoft-fabric), [Power BI](https://antoinewang.substack.com/p/microsoft-fabric-copilot-powerbi), notebooks, …), vous dialoguez en langage naturel. Préconfiguré et prêt à l’emploi, il aide à créer des visuels et des pages de rapport, écrire et expliquer du DAX ou du SQL, résumer des insights et générer des narratifs, et accélérer les transformations de données. Il travaille dans le contexte Fabric actif, avec mémoire conversationnelle et portée à l’échelle du workspace.
* Un **Data Agent** est un artefact Fabric que vous créez dans un workspace et publiez, exactement comme un rapport Power BI. C’est un agent conversationnel d’analyse (text-to-query) : agentique dans son fonctionnement interne (il choisit la source, invoque l’outil, génère, valide et exécute la requête) mais strictement cantonné à la lecture (aucune écriture ni action sur les systèmes). On spécifie des instructions, des exemples et jusqu'à cinq sources choisies en sélectionnant les tables pertinentes.

La distinction tient en une phrase : Copilot est l’assistant généraliste prêt à l’emploi ; le Data Agent est l’expert gouverné que vous façonnez et diffusez.

---

## Les Deux Briques (en détail)

### 1. Copilot in Fabric & Power BI : l’assistant généraliste préconfiguré

Copilot vit à l’intérieur de vos artefacts. Vous ne le créez pas, vous ne le configurez pas : il est là, contextuel, prêt dès que vous ouvrez un Notebook, l’éditeur SQL d’un Warehouse ou un rapport Power BI.

Et surtout, il joue sur deux tableaux, c’est le point que tout le monde oublie :

#### Côté production (pour ceux qui construisent)

* Dans un Notebook : il connaît votre workspace, le Lakehouse attaché, les schémas et tables. Vous lui demandez “crée un dataframe à partir de sales.csv” ou “explique-moi cette erreur”, et il génère le code, le refactore, le commente.
* Dans le \*\*Warehouse\*\* : il vous assiste pour écrire et expliquer du T-SQL, directement dans l’éditeur.
* Dans \*\*Data Factory\*\* : il génère et explique les transformations.

#### Côté consommation (pour les utilisateurs métier)

* Dans Power BI, Copilot répond à des questions en langage naturel sur vos données : il interroge le modèle sémantique et renvoie une réponse sous forme de visuel, résume un rapport, crée même des calculs DAX à la volée.
* L’expérience standalone de Copilot dans Power BI va plus loin : un chat plein écran qui trouve tout seul le bon rapport, le bon modèle sémantique, ou le bon Data Agent, pour répondre sans que l’utilisateur ouvre quoi que ce soit.

**La Réalité du Terrain** : Copilot n’est pas “juste pour écrire du code”. C’est un assistant qui sert aussi bien le créateur que le consommateur. Sa limite n’est pas le langage naturel, c’est la configuration : vous ne lui donnez pas d’instructions métier, vous ne choisissez pas ses sources. Il prend ce qu’il trouve et fait au mieux.

### 2. Fabric Data Agent : l’expert conversationnel que vous configurez

Le Data Agent, lui, est un artefact que vous créez délibérément dans un workspace, puis publiez. C’est un expert que vous façonnez sur un domaine précis, pour qu’un utilisateur, souvent non technique, obtienne une réponse fiable et gouvernée, sans écrire une ligne de code.

Ce qui le caractérise :

* **Vous le configurez.** Vous sélectionnez jusqu’à 5 sources de données (Lakehouse, Warehouse, modèle sémantique Power BI, base KQL, ontologie, Microsoft Graph), vous choisissez les tables pertinentes, et vous l’affinez avec des instructions en langage naturel, au niveau de l’agent et de chaque source, ainsi que des exemples de requêtes (jusqu’à 100 par source). C’est vous qui définissez son rôle, son périmètre et sa logique.
* **Il est gouverné et en lecture seule**. Il s’exécute avec l’identité et les permissions de l’utilisateur qui pose la question. Il ne génère que des requêtes de lecture (jamais de création, mise à jour ou suppression) et respecte les politiques Microsoft Purview, le Data Loss Prevention (DLP), la sécurité niveau ligne/colonne (RLS/CLS) et le moindre privilège. Personne ne voit une donnée à laquelle il n’a pas droit.
* **Il s’expose hors de Fabric**. Un Data Agent se consomme depuis Microsoft 365 Copilot, Copilot Studio, Microsoft Foundry, Teams (ou via un endpoint MCP). Vous amenez la réponse là où vos utilisateurs travaillent déjà.

**La réalité du terrain** : Là où Copilot prend les sources qu’il trouve, le Data Agent ne répond que sur ce que vous lui avez confié, avec les instructions que vous avez écrites. C’est un produit data que vous livrez à une audience : sa qualité dépend directement du soin mis dans sa configuration. Un agent bien cadré devient un expert de confiance ; un agent mal cadré répond vite et faux.

À noter pour vos utilisateurs francophones : le Fabric Data Agent ne prend actuellement pas en charge les langues autres que l’anglais.

*Source : [Limitations Data Agent](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent#limitations)*

---

## Les 3 différences qui comptent vraiment

Si vous ne deviez retenir que trois lignes de démarcation, ce sont celles-ci.

#### a. La configuration : préconfiguré vs paramétrable

Copilot arrive prêt à l’emploi, sans réglage métier. Le Data Agent, à l’inverse, est hautement configurable : instructions, définitions de termes métier, exemples de requêtes. C’est vous qui lui apprenez votre langage.

Mon conseil : Si votre besoin exige que l’IA comprenne votre jargon (vos acronymes, vos définitions de “client actif” ou de “marge nette”), seul le Data Agent vous le permet. Copilot ne se paramètre pas à ce niveau.

#### b. La spécialisation : généraliste vs expert de domaine

Copilot est généraliste : dans son expérience standalone, il route tout seul votre question vers le rapport ou le modèle sémantique le plus pertinent. Pratique, mais sans garantie qu’il tape dans la bonne source ni qu’il connaisse vos définitions métier. Le Data Agent, lui, est un expert curé : il ne couvre qu’un périmètre choisi, avec un vocabulaire que vous lui avez appris. Sur son domaine, il est plus fiable ; hors de son domaine, il ne répond pas.

#### c. La portabilité : capacité intégrée vs brique réutilisable

Copilot est une capacité des produits Microsoft (Fabric, Power BI) : il vit là où Microsoft l’a mis. Le Data Agent, lui, est une brique réutilisable que vous branchez où vous voulez, M365 Copilot, Copilot Studio, Foundry, Teams, architectures multi-agents… et jusque dans l’expérience standalone de Copilot dans Power BI, qui peut l’appeler comme l’une de ses sources.

---

## Matrice de Décision : Copilot ou Data Agent ?

**Q1 : Avez-vous besoin de configurer un expert gouverné sur un domaine précis ?**

* **NON**, je veux un assistant prêt à l’emploi (générer du code, ou laisser un métier explorer librement ses rapports) = Copilot !
* **OUI**, il me faut une réponse fiable sur un périmètre métier cadré = Data Agent.

**Q2 : Avez-vous besoin que l’IA comprenne votre vocabulaire métier spécifique ?**

* **OUI** = Data Agent. Lui seul accepte des instructions et des définitions de termes (jusqu’à 15 000 caractères) pour s’aligner sur votre langage.
* **NON** = Copilot. Le paramétrage métier serait inutile ; vous voulez de la productivité inline.

**Q3 : La réponse doit-elle être réutilisable en dehors des surfaces Microsoft prêtes à l’emploi (Teams, Copilot Studio, Foundry, app custom, multi-agents) ?**

* **OUI** = Data Agent. C’est une brique portable qui s’intègre partout, et que Copilot lui-même peut appeler.
* **NON** = Copilot. La capacité est déjà là, intégrée, sans développement.

---

## 🥇 La Règle d’Or

Si tu dois retenir une chose : Copilot est l’assistant généraliste préconfiguré, il code ET répond en langage naturel ; le Data Agent est l’expert que tu configures sur un domaine et que tu diffuses partout, jusque dans Copilot. Le premier est une capacité, le second est une brique que tu façonnes.

L’impact terrain : en posant la bonne question “ai-je besoin d’un assistant prêt à l’emploi, ou d’un expert gouverné sur mon domaine ?” vous arrêtez de choisir au hasard et vous arrêtez d’opposer deux briques qui, en réalité, s’emboîtent. Vos métiers gagnent en autonomie immédiate avec Copilot (j’ai écris d’autres blogs sur ces capacités); vos sujets sensibles gagnent en fiabilité avec des Data Agents. La complexité est l’ennemie de la maintenance, et clarifier ces deux briques, c’est déjà réduire votre dette technique future.

> Et vous, où en êtes-vous ? Vos métiers se contentent-ils du Copilot généraliste dans Power BI, ou avez-vous déjà construit des Data Agents spécialisés pour vos besoins ? Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [Fabric Copilot Capacity (FCC) : le guide 2026 sans throttling](https://blog.antoinewang-tech.com/p/fabric-copilot-capacity-dedicated)
* [Power BI : Fini la page blanche avec Copilot](https://blog.antoinewang-tech.com/p/microsoft-fabric-copilot-powerbi)
* [Copilot Dataflow Gen2 Fabric : guide pratique et cas d’usage](https://blog.antoinewang-tech.com/p/copilot-dataflow-gen2-microsoft-fabric)

---

## 📚 Ressources pour aller plus loin

Pour approfondir le sujet et passer à la pratique, je vous recommande ces lectures essentielles issues de la documentation officielle :

* [Concepts du Fabric Data Agent](https://learn.microsoft.com/fabric/data-science/concept-data-agent) : la différence officielle entre Data Agent et Copilot, en détail
* [Vue d’ensemble de Copilot dans Fabric et Power BI](https://learn.microsoft.com/fabric/fundamentals/copilot-fabric-overview) ; architecture, workloads couverts, sécurité
* [Poser des questions à Copilot sur vos données (Power BI)](https://learn.microsoft.com/power-bi/create-reports/copilot-ask-data-question) : le Q&A en langage naturel, côté consommateur
* [Expérience standalone de Copilot dans Power BI](https://learn.microsoft.com/power-bi/explore-reports/copilot-chat-with-data-standalone) :comment Copilot route vers un rapport, un modèle… ou un Data Agent
