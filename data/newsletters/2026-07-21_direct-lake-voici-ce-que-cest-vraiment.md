---
title: Direct Lake en production : Configuration, fallback Import/DQ, performance réelle, limites
url: https://blog.antoinewang-tech.com/p/direct-lake-voici-ce-que-cest-vraiment
date: 2026-07-21
author: Antoine Wang
source: substack
---

# Direct Lake en production : Configuration, fallback Import/DQ, performance réelle, limites

Bonjour à tous, je suis Antoine Wang.

J’aide les profils techniques à maîtriser l’architecture de Microsoft Fabric, et j’aide les décideurs à comprendre l’impact réel de cette technologie.

Mon objectif ? Vulgariser le complexe et vous donner les clés pour maîtriser Microsoft Fabric, une plateforme de données SaaS unifiée et alimentée par l’IA pour simplifier la gestion des données et l’analyse.

🆕 **Nouveauté pour les lecteurs** : j’ai créé **Ask Fabric Mastery**, un assistant IA qui répond à vos questions sur Microsoft Fabric & Power BI en s’appuyant uniquement sur les 29 éditions de cette newsletter. Réponses sourcées, sans hallucination, avec un lien direct vers l’édition d’origine.

👉 **Testez-le maintenant** : [ask-fabric-mastery](http://awang1020.github.io/ask-fabric-mastery)  
🔑 **Code d’accès (ce code est réservé aux abonnés Fabric Mastery) :**

Cette newsletter est 100% gratuite. En vous abonnant maintenant, vous recevrez en exclusivité mon “One-Pager” pour cartographier l’ensemble de la solution Fabric en un coup d’œil.

Merci à celles et ceux qui me suivent depuis le début. Sans plus attendre, entrons dans le vif du sujet !

---

## ⚡ En 30 secondes

**Ce qu’il faut retenir :**

* Direct Lake combine la performance de l’Import et la fraîcheur du DirectQuery, mais il a des guardrails liés à votre SKU
* Le fallback DirectQuery est un filet de sécurité, pas une stratégie,si vous tombez en fallback régulièrement, c’est un signal d’alarme !
* Optimisez vos tables Delta (V-Order, taille des segments, cardinalité) avant de dimensionner votre capacité

---

Votre rapport Power BI est en mode Direct Lake. La promesse ? La performance de l’Import sans la contrainte du rafraîchissement. La réalité ? Votre dashboard exécutif rame depuis ce matin, et personne ne comprend pourquoi.

La réalité du terrain, c’est que Direct Lake est le mode de stockage par défaut sur Fabric, mais la majorité des équipes le déploient en production sans comprendre ses mécanismes internes. Le framing, le fallback, les guardrails par SKU… Ce sont ces détails qui font la différence entre un rapport qui charge en 2 secondes et un rapport qui tombe en DirectQuery sans prévenir.

Aujourd’hui, on tranche. On va décortiquer Direct Lake pour que vous sachiez exactement ce qui se passe sous le capot, et comment l’optimiser pour la production.

---

## C’est quoi Direct Lake ?

Direct Lake est un mode de stockage pour les modèles sémantiques Power BI qui lit directement les fichiers Delta Parquet depuis OneLake, sans import préalable et sans passer par une requête SQL. Il combine :

1. **La performance de l’Import** : les données sont chargées en mémoire dans le moteur VertiPaq
2. **La fraîcheur du DirectQuery** : les changements dans OneLake sont reflétés automatiquement (framing)
3. **Zéro duplication**, pas de copie des données dans le modèle sémantique

C’est le mode par défaut pour tout nouveau modèle sémantique créé sur un Lakehouse ou un Warehouse dans Fabric.

---

## Direct Lake mode VS Import / DirectQuery mode

Avant de plonger dans les variantes et les guardrails, il faut bien comprendre pourquoi Direct Lake n’est ni de l’Import, ni du DirectQuery, même si on entend souvent “c’est le meilleur des deux mondes”. Le vrai marqueur de différence, c’est ce qui se passe au moment du rafraîchissement.

✅ **Import** : Le moteur copie l’intégralité des données dans le modèle sémantique. Chaque refresh produit une nouvelle copie complète : lecture de la source, transfert réseau, compression VertiPaq, écriture en mémoire. C’est long, ça consomme du CPU et de la mémoire côté capacité, et ça met la source sous pression à chaque itération.

✅ **DirectQuery** : Aucune donnée n’est stockée dans le modèle. Chaque interaction utilisateur génère une requête SQL envoyée à la source. Pas de refresh à proprement parler, mais chaque clic dans le rapport est un aller-retour vers le moteur SQL. Performance dépendante de la source, et coût récurrent à chaque requête.

✅ **Direct Lake** : Le refresh ne copie pas les données. Il met à jour uniquement les métadonnées qui pointent vers les derniers fichiers Delta dans OneLake. C’est l’opération de \*\***framing**\*\* : quelques secondes, quasi gratuite en CU. Les données restent dans OneLake, et le moteur VertiPaq les charge en mémoire à la demande, colonne par colonne, au fil des requêtes.

**La conséquence directe** : avec Direct Lake, la préparation des données sort du modèle sémantique et redescend dans OneLake. Vous utilisez les outils natifs de Fabric (Spark, T-SQL, Dataflows Gen2, pipelines…) pour produire des tables Delta propres en couche Silver/Gold. Le modèle sémantique se contente de pointer dessus. Plus de logique de transformation enfouie dans Power Query qui s’exécute à chaque refresh nocturne.

---

## Pourquoi Direct Lake change la donne ?

Maintenant qu’on a posé la différence avec Import et DirectQuery, voyons ce que Direct Lake apporte vraiment en production. Ce n’est pas juste “un nouveau mode de stockage”, c’est un changement de modèle économique et opérationnel pour vos rapports Power BI.

✅ **Performance VertiPaq sans la corvée du refresh** ! Les requêtes Direct Lake sont traitées par le même moteur VertiPaq que l’Import. Vous obtenez des temps de réponse équivalents, sans avoir à orchestrer, surveiller et débugger des cycles de rafraîchissement qui rechargent l’intégralité des données chaque nuit. C’est autant de pipelines en moins à maintenir.

✅ **Réutilisation de vos investissements Fabric** :Direct Lake s’intègre nativement avec les Lakehouses, les Warehouses et toute source produisant des tables Delta dans OneLake. Pas de duplication, pas de second système à synchroniser. C’est le mode idéal pour la couche \*\***Gold**\*\* d’une architecture Medallion : votre Lakehouse devient directement la source de vos rapports, sans intermédiaire.

✅ **ROI maximisé sur la mémoire de capacité** : Direct Lake charge en mémoire uniquement les colonnes et les segments nécessaires à la requête en cours. Conséquence directe : le volume total de données analysées peut largement dépasser la mémoire maximale de votre capacité. Là où un modèle Import vous oblige à tenir l’intégralité du dataset en RAM, Direct Lake vous permet d’exposer des téraoctets sur une capacité raisonnable.

✅ **Latence réduite, fraîcheur automatique** : Plus besoin de planifier des refreshes toutes les heures pour “rapprocher” le rapport de la source. Le framing synchronise le modèle quasi instantanément à chaque écriture dans la table Delta. Les utilisateurs métier voient les nouvelles données dès qu’elles sont écrites en OneLake, sans intervention.

---

## Direct Lake on OneLake vs Direct Lake on SQL ?

La première chose à comprendre, c’est que Direct Lake existe désormais en **deux variantes**, et qu’elles ne se comportent pas du tout pareil quand ça coince.

✅ **Direct Lake on OneLake** ***(la plus récente)*** : le modèle lit directement les fichiers Delta Parquet depuis OneLake, sans aucun couplage au SQL analytics endpoint. Conséquence : pas de fallback DirectQuery possible. Si un guardrail est dépassé, il n’y a pas de filet, le modèle part en erreur (voir section suivante). En contrepartie, cette variante offre une intégration plus fine avec OneLake security, des plans de requête DAX plus efficaces (pas de contrôle de sécurité SQL à chaque requête), et elle supporte les modèles composites (mix avec des tables Import) ainsi que les colonnes calculées.

✅ **Direct Lake on SQL endpoint** ***(la variante historique)*** : le modèle s’appuie sur le SQL analytics endpoint pour la découverte des tables et la vérification des permissions. Quand Direct Lake ne peut pas charger les données nativement, vue SQL, RLS/OLS appliquée au niveau SQL, ou guardrail dépassé, il bascule automatiquement en DirectQuery via ce même endpoint. C’est le fameux filet de sécurité : les requêtes continuent de répondre, mais en mode DirectQuery, avec la perte de performance qui va avec.

> 🔑 Le vrai marqueur de différence : DL/OneLake échoue quand il sort des clous, DL/SQL dégrade (il tombe en DirectQuery). L’un est franc, l’autre est silencieux pour l’utilisateur, et c’est précisément ce silence qui rend DL/SQL piégeux en prod.

💡 **Mon conseil**

**Direct Lake sur OneLake** est le format à privilégier pour charger rapidement vos données en mémoire sémantique lorsque vos tables (ou vues matérialisées) sont déjà propres dans un Warehouse ou un Lakehouse. Et la bascule entre les deux variantes reste simple : il suffit de modifier la requête M de l’Expression partagée référencée par les partitions Direct Lake.

---

## Les guardrails par SKU Fabric : combien de lignes, de fichiers, de mémoire ?

✅Les guardrails sont des limites qui varient selon votre SKU Fabric et portent sur quatre choses : le nombre de fichiers Parquet par table Delta, le nombre de row groups par table, le nombre de lignes par table, et la taille totale sur disque des données du modèle. (La limite de mémoire par modèle existe aussi, mais ce n’est techniquement pas un guardrail.)

Le point crucial, c’est que le comportement en cas de dépassement dépend de la variante :

✅ **Direct Lake on OneLake** : pas de fallback, donc pas de demi-mesure. Le build/refresh part en erreur (un *framing fail* du type « *the source Delta table has too many parquet files, which exceeds the maximum guardrails* »), et le modèle n’est plus interrogeable du tout tant que vous n’avez pas réoptimisé les tables Delta (`OPTIMIZE`). C’est brutal, mais au moins c’est visible immédiatement.

✅ **Direct Lake on SQL endpoint** : contre toute attente, le refresh RÉUSSIT, mais avec un avertissement dans le Refresh History (« *…source Delta tables exceed the resource limits… requiring queries to fallback to DirectQuery* »). À partir de là, l’intégralité du modèle bascule en DirectQuery, pour toutes les requêtes, ce n’est pas un fallback ponctuel, c’est un état permanent du modèle. Vos utilisateurs ne voient rien… sauf un dashboard qui rame. *(Cas limite : sur le plus gros SKU, un F2048, le refresh échoue mais le modèle reste interrogeable, toujours en fallback DQ.)*

---

## Optimiser Direct Lake !

✅ **V-Order compression** : Appliquez la compression V-Order sur vos tables Delta. C’est le format natif de Fabric qui optimise à la fois le chargement (streaming compressé) et les requêtes (VertiScan calcule directement sur les données compressées). Les Notebooks Spark de Fabric l’appliquent par défaut.

✅ **Taille des segments** : VertiPaq stocke les données par segments de colonnes. Visez entre 1 million et 16 millions de lignes par segment pour les grandes tables. Trop de petits segments = performance dégradée.

✅ **Cardinalité des colonnes** : Les colonnes à forte cardinalité (beaucoup de valeurs uniques) ralentissent les requêtes. Réduisez la cardinalité là où c’est possible : arrondissez les timestamps, regroupez les valeurs rares.

✅ **Types de données** : Utilisez des types entiers plutôt que des chaînes de caractères pour les IDs. Évitez de stocker des nombres sous forme de texte.

Voir doc pour plus d’informations : [Cross-Workload Table Maintenance and Optimization - Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/fundamentals/table-maintenance-optimization)

---

## 🥇 La Règle d’Or

Si tu dois retenir une chose : Direct Lake n’est ni de l’Import, ni du DirectQuery. C’est un moteur qui déplace ton travail d’ingénierie data en amont, dans tes tables Delta, pour que ton modèle sémantique ne fasse plus que pointer dessus.

Concrètement : connais tes guardrails de SKU avant de partir en prod, mesure tes tables (lignes, fichiers Parquet, row groups) avant de monter en capacité, et applique OPTIMIZE + V-Order avant de toucher au portefeuille.

> Et vous, avez-vous déjà rencontré des fallbacks DirectQuery inattendus sur vos rapports Direct Lake ? Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [Architecture Médaillon Microsoft Fabric : Bronze, Silver, Gold expliqués](https://blog.antoinewang-tech.com/p/architecture-medaillon-microsoft-fabric)
* [Data Stores Microsoft Fabric : Lakehouse vs Warehouse vs KQL](https://blog.antoinewang-tech.com/p/data-stores-microsoft-fabric-comparatif)
* [Microsoft Fabric : Tout savoir sur le OneLake](https://blog.antoinewang-tech.com/p/onelake-microsoft-fabric-guide)
* [Ingestion Microsoft Fabric : Dataflow, Pipeline ou Notebook ?](https://blog.antoinewang-tech.com/p/microsoft-fabric-data-ingestion-tools)

---

## 📚 Ressources pour aller plus loin

* [Vue d’ensemble de Direct Lake](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview)
* [Comment Direct Lake fonctionne](https://learn.microsoft.com/fabric/fundamentals/direct-lake-how-it-works)
* [Optimiser le stockage Direct Lake](https://learn.microsoft.com/fabric/fundamentals/direct-lake-understand-storage)
* [Intégrer la sécurité avec Direct Lake](https://learn.microsoft.com/fabric/fundamentals/direct-lake-security-integration)
* [Gérer les modèles sémantiques Direct Lake](https://learn.microsoft.com/fabric/fundamentals/direct-lake-manage)
