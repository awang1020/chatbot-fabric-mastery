---
title: Architecture Médaillon Microsoft Fabric : Bronze, Silver, Gold expliqués
url: https://blog.antoinewang-tech.com/p/architecture-medaillon-microsoft-fabric
date: 2026-04-21
author: Antoine Wang
source: substack
---

# Architecture Médaillon Microsoft Fabric : Bronze, Silver, Gold expliqués

Bonjour à tous, je suis **Antoine Wang**.

J’aide les profils techniques à maîtriser l’architecture de Microsoft Fabric, et j’aide les décideurs à comprendre l’impact réel de cette technologie.

Mon objectif ? Vulgariser le complexe et vous donner les clés pour maîtriser Microsoft Fabric, une plateforme de données SaaS unifiée et alimentée par l’IA pour simplifier la gestion des données et l’analyse.

Cette newsletter est 100% gratuite. En vous abonnant maintenant, vous recevrez en exclusivité mon “One-Pager” pour cartographier l’ensemble de la solution Fabric en un coup d’œil.

Merci à celles et ceux qui me suivent depuis le début. Sans plus attendre, entrons dans le vif du sujet !

---

Le OneLake de Microsoft Fabric a une promesse séduisante : il peut avaler n’importe quel type de données, quels que soient le format ou la volumétrie.

Delta parquet, compressé et optimisé !

Mais attention au revers de la médaille. Sans une gouvernance claire, votre lac de données va très vite se transformer en un marécage.

Aujourd’hui, nous allons explorer une bonne pratique pour bâtir une plateforme de données robuste et évolutive : l’architecture Medallion (Bronze, Silver, Gold).

Et mettons les choses au clair : ce n’est pas qu’une simple convention de nommage pour faire beau dans vos espaces de travail. C’est une stratégie de découplage, autant technique qu’organisationnelle.

Le but ? Qu’à chaque nouvelle source de données à ingérer, vous sachiez parfaitement comment la gérer, la transformer et la mettre à disposition, sans tout mélanger.

---

## C’est quoi l’architecture Medaillon ?

Conceptualisée par Databricks et adoptée nativement par Microsoft Fabric, l’architecture Medaillon organise les données en trois couches de raffinement progressif :

🥉 **Bronze — La zone brute.** La donnée arrive telle quelle, dans son format d’origine. Pas de transformation. Pas de nettoyage. C’est la zone où l’historique des données est préservé. Si les règles métiers changent ou si quelque chose plante en aval, vous pouvez toujours re-traiter depuis ici sans avoir à interroger à nouveau les systèmes sources.

🥈 **Silver — La zone de confiance.** C’est la zone où on commence à traiter les données : la donnée est validée, dédupliquée, enrichie et harmonisée. Voici quelques exemples :

* Alignement des référentiels : On réconcilie les données venant de systèmes différents (ex: un ID produit de l’ERP avec celui du CRM) et on uniformise les formats (comme les timestamps dans un seul fuseau horaire).
* Qualité des données : On nettoie les doublons, on gère les valeurs nulles et on écarte ou corrige les erreurs de saisie.
* Gouvernance et stockage : Les données sont structurées et stockées sous forme de tables relationnelles dans un Lakehouse. À ce stade, la donnée est propre, fiable et interrogeable, mais elle reste à sa maille la plus fine (non agrégée).

🥇 **Gold — La zone métier.** La donnée est agrégée, pré-calculée et modélisée spécifiquement pour la consommation analytique. On quitte la logique “système” pour adopter le vocabulaire des utilisateurs, voici quelques exemples :

* **Modélisation métier :** C’est ici que l’on construit les modèles en étoile (tables de faits et tables de dimensions) pour faciliter l’analyse.
* **Calcul des indicateurs :** Les KPI vont être calculés à ce niveau pour des besoins métiers spécifiques (chiffre d’affaires mensuel, taux de churn, panier moyen), cela permet garantir des temps de réponse ultra-rapides pour la visualisation de ces données.
* **Consommation sécurisée :** C’est cette couche (et uniquement celle-ci) que voient vos data analysts, qui alimente vos dashboards Power BI ou vos modèles sémantiques. Les règles de sécurité (qui a le droit de voir quoi) y sont strictement appliquées.

---

## La réalité du terrain

✅ **Chaque zone a son équipe propriétaire.**

* Bronze → équipe ingestion IT.
* Silver → Data Engineers.
* Gold → équipe BI ou métier.

Ce découplage organisationnel est le vrai bénéfice de l’architecture Medaillon : chacun travaille dans son périmètre sans bloquer l’autre.

En règle générale, on ne va pas exposer directement les données de la couche Bronze aux équipes métiers. La gestion des accès, de la sécurité fine et du partage se fait au niveau de la couche Gold, là où la donnée est propre, qualifiée et prête à être consommée.

**✅ La couche Gold n’est pas forcément un Lakehouse.**

La force du Lakehouse réside principalement dans son moteur Spark et la flexibilité de préparer les données via des Notebooks (en Python, Scala, etc.). Mais si votre équipe d’analystes est avant tout experte en T-SQL, un Warehouse est tout à fait adapté. Les profils SQL y retrouveront leurs marques immédiatement et pourront y implémenter nativement la sécurité fine (RLS, CLS et Data Masking).

✅ **Un item physique par couche.**

Vous stockez peut-être toutes vos données dans un seul et même Lakehouse, en vous contentant de préfixer vos tables par « Bronze », « Silver » et « Gold ».

La véritable bonne pratique sur Fabric est de dédier un item physique par couche.

*Par exemple :* *un Lakehouse* `LH_Bronze`*, un Lakehouse* `LH_Silver`*, et un Warehouse* `WH_Gold`*.*

Sur Fabric, la gestion des droits d’accès (RBAC) est beaucoup plus simple et robuste lorsqu’elle est appliquée au niveau de l’item. En séparant physiquement vos couches, vous garantissez que vos analystes n’ont accès qu’au conteneur Gold, sans jamais risquer d’exposer accidentellement les données brutes et sensibles du Bronze.

✅ **Multi-workspaces ? Aucun problème grâce aux Shortcuts.**

Vos données réparties sur plusieurs espaces de travail (workspaces) ne sont pas un problème, elles restent accessibles via le OneLake sans aucune duplication physique !

Le secret ? Les Shortcuts (raccourcis). Ils vous permettent de référencer les données dans la couche Gold et de donner accès à des tables pour un domaine métier spécifique par exemple. Ainsi, l’équipe métier peut explorer ces tables et créer son propre reporting BI, tandis que vous conservez une gestion centralisée des droits et des permissions.

---

## Pièges à Eviter

⚠️ **Le Bronze n’est pas une poubelle.**

Ingérer tout type de données et tout déverser dans le Bronze sans structure de répertoires, sans partitionnement ni nommage clair, c’est la garantie de créer un marécage où l’on ne retrouve plus rien. De plus, si vous n’intégrez aucun élément d’historisation, vous finirez vite par oublier les différentes versions et l’objectif initial de ces données.

Imposez une convention de nommage et de partitionnement stricte dès l’ingestion. Par exemple : `/{source}/{année}/{mois}/{jour}/`.

⚠️ **Ne sautez pas le Silver sous prétexte de “gagner du temps”.**

Vous vous dites sûrement : *« Mes données sources sont déjà propres et bien formatées, je vais passer directement du Bronze au Gold pour gagner du temps ! »*

Ça marche… jusqu’au jour où une deuxième source vient s’ajouter et remonte des doublons sur un même client, mais avec un format différent qui n’a pas été géré.

La couche Silver n’est pas optionnelle. C’est la couche qui gère la complexité et les incohérences des systèmes sources (dédoublonnage, standardisation des formats, typage) pour garantir que votre couche Gold reste un espace de consommation propre pour la visualisation.

⚠️ **Vouloir nettoyer trop tôt.**

À l’inverse, face à des données mal formatées (mauvais typage, mapping erroné, fichiers mal structurés), on est souvent tenté de nettoyer les données dès l’ingestion pour « aller plus vite ».

C’est une erreur stratégique. La couche Bronze doit rester la plus passive possible. Si vous commencez à appliquer des transformations lourdes dès l’ingestion, vous perdez la traçabilité de la donnée brute : en cas de bug ou de besoin de recalcul, vous n’avez plus de point de référence. Gardez vos notebooks de transformation pour le passage vers le Silver.

---

## Matrice de décision : comment structurer votre Medallion ?

Avant de créer votre premier Lakehouse, répondez à ces questions :

---

## 🥇 La Règle d’Or

**Si tu dois retenir une chose :** L’architecture Medallion dans Fabric n’est pas une convention de nommage de lakehouses.

C’est un découplage organisationnel — un workspace, une équipe, une responsabilité. Sans ça, vous aurez trois lakehouses bien nommées et zéro gouvernance.

Une Architecture Medaillon bien construite dans Microsoft Fabric, c’est la fin du goulot d’étranglement IT sur la donnée.

L’équipe ingestion livre en Bronze, l’équipe Data Engineering transforme en Silver, l’équipe BI construit en Gold — sans se marcher dessus, sans blocages inter-équipes.

C’est ce socle qui permet aux analystes de se concentrer sur la valorisation de la donnée plutôt que de passer leur temps à nettoyer des fichiers mal structurés ou à chercher quelle version de la table est “la bonne”.

> Et vous, quelle est votre expérience avec l’architecture Medallion ? Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [Data Stores Microsoft Fabric : Lakehouse vs Warehouse vs KQL](https://blog.antoinewang-tech.com/p/data-stores-microsoft-fabric-comparatif)
* [Ingestion Microsoft Fabric : Dataflow, Pipeline ou Notebook ?](https://blog.antoinewang-tech.com/p/microsoft-fabric-data-ingestion-tools)
* [Microsoft Fabric : Tout savoir sur le OneLake](https://blog.antoinewang-tech.com/p/onelake-microsoft-fabric-guide)
* [Microsoft Fabric : Gouvernance des workspaces](https://blog.antoinewang-tech.com/p/gouvernance-workspaces-microsoft-fabric)

---

## 📚 Ressources pour aller plus loin

Pour approfondir le sujet et passer à la pratique, voici les documentations officielles indispensables :

* [Qu’est-ce que l’architecture de médaillon dans un lakehouse ?](https://learn.microsoft.com/fr-fr/azure/databricks/lakehouse/medallion)
* [Comprendre l’architecture de lakehouse en médaillon pour Microsoft Fabric avec OneLake](https://learn.microsoft.com/fr-fr/fabric/onelake/onelake-medallion-lakehouse-architecture)
* [Mettre en œuvre l’architecture de médaillon avec des vues sur le lac matérialisées](https://learn.microsoft.com/fr-fr/fabric/data-engineering/materialized-lake-views/tutorial)
