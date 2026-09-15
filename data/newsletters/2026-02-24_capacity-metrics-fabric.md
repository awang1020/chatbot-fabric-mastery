---
title: Microsoft Fabric : Comment surveiller votre capacité comme un Pro ?
url: https://blog.antoinewang-tech.com/p/capacity-metrics-fabric
date: 2026-02-24
author: Antoine Wang
source: substack
---

# Microsoft Fabric : Comment surveiller votre capacité comme un Pro ?

Vous avez sauté le pas, votre organisation est sur **Microsoft Fabric**. C’est génial, la puissance est là. Mais soudain, une question vous brûle les lèvres : *« Est-ce que je consomme trop ? Pourquoi mes rapports rament cet après-midi ? »*

Si vous ne voulez pas naviguer à vue (et éviter les mauvaises surprises sur la facture), il existe un outil indispensable : **L’Application** **Microsoft Fabric Capacity Metrics**.

---

## C’est quoi cette application, concrètement ?

Imaginez que votre capacité Fabric est un **moteur de voiture**. Si vous appuyez trop sur le champignon, le moteur chauffe. L’application *Capacity Metrics*, c’est votre **tableau de bord**.

Elle vous permet de voir en temps réel si votre moteur tourne au régime de croisière ou s’il est proche de la surchauffe (ce qu’on appelle le *Throttling*).

### Pourquoi c’est important ?

Dans Microsoft Fabric, tout fonctionne avec des **CU (Capacity Units)**. C’est votre monnaie d’échange pour la puissance de calcul.

* **Si vous consommez trop :** Vos utilisateurs vont subir des lenteurs.
* **Si vous consommez trop peu :** Vous payez peut-être pour une licence (F-SKU) trop grande pour vos besoins réels.

---

## 5 Tips pour maîtriser l’app dès aujourd’hui

Même si vous débutez, voici comment tirer profit de l’outil en 5 minutes :

1. **Surveillez le “Heartbeat” (Battement de cœur) :** Regardez l’onglet *Compute*. Si la courbe dépasse souvent les 100 %, votre capacité est saturée.

> **Le conseil stratégique :** C’est le meilleur moyen de déterminer la taille de capacité (F-SKU) dont vous avez réellement besoin. Si vous saturez, il faut **Scale Up** (augmenter la taille). Si vous êtes toujours à 10 %, vous pouvez **Downscale** pour économiser de l’argent immédiatement !

2. **Identifiez les “Gros Gourmands” :** Utilisez le tableau en bas de l’app pour trier par **CU(s)**. Vous verrez tout de suite quel notebook Python ou quel rapport Power BI dévore vos ressources

> Ne vous contentez pas de regarder ! Une fois le “gourmand” identifié, entreprenez des pistes d’optimisation concrètes.
>
> **L’objectif** : Réduire la consommation des tâches les plus lourdes pour libérer de la “place” pour de nouveaux projets sans avoir à payer une licence supérieure !

3. **Utilisez la page “Explore”** **:** Lorsqu’un pic de consommation apparaît sur votre graphique, ne restez pas en surface.

> **Le Tip :** Cliquez sur le point culminant du pic, puis utilisez la fonction **Explore**.
>
> **Le détail qui change tout :** Cette vue détaillée vous permet de voir exactement **quelle tâche** (quel notebook, quel rapport, …) a provoqué l’explosion et, surtout, **par qui** elle a été lancée. C’est l’outil ultime pour identifier un utilisateur qui aurait lancé une requête “infinie” ou un processus mal optimisé.

4. **Distinguez les opérations en arrière-plan (Background) et interactive**.

***Opération Interactive :*** C’est ce qui se passe **en direct** quand un utilisateur interagit avec la donnée.

* **Exemples :** Ouvrir un rapport Power BI, cliquer sur un filtre (slicer), exécuter une cellule dans un Notebook en live, ou faire une requête SQL manuelle.
* **L’enjeu :** La réactivité. L’utilisateur attend une réponse immédiate. Si la capacité sature, c’est ici que l’on ressent la “latence”.

***Opération Arrière-plan (Background)*** **:** Ce sont les tâches planifiées ou automatiques qui tournent toutes seules.

* **Exemples :** Rafraîchissement programmé d’un jeu de données (dataset), exécution d’un Pipeline Data Factory, ou jobs Spark planifiés.
* **L’enjeu :** Le volume. Ces tâches sont souvent lourdes, mais elles ne nécessitent pas une réponse à la milliseconde.

> **Le saviez-vous ?** Si votre capacité sature (Throttling), ne coupez pas forcément les accès utilisateurs. Regardez d’abord vos tâches de **Background**. En décalant un seul gros rafraîchissement vers une période plus calme, vous lissez votre consommation sur une autre fenêtre de 24h et libérez de l’espace pour les tâches interactives de vos collègues !

5. **Ne négligez pas le stockage (OneLake)**

On parle souvent de la puissance (Compute), mais le stockage a aussi son importance dans votre facture globale.

* **Le Tip :** Surveillez l’onglet dédié au **Stockage** pour suivre la volumétrie de vos données.
* **Pourquoi ?** Savoir combien de To vous stockez sur le OneLake est crucial pour anticiper les coûts de persistance. Un stockage qui dérive, c’est une marge qui réduit. Gardez un œil sur la croissance de vos données pour rester maître de votre budget.

---

## Les pièges à éviter ⚠️

* **Ignorer les alertes de Throttling:** Vous surveillez vos graphiques, vous voyez des ralentissements et des pics de consommation, mais aucune action concrète n’est entreprise pour optimiser les processus.
* **Ne pas installer l’app :** Elle n’est pas installée par défaut ! Allez dans le menu “Apps” de votre workspace, cliquez sur **“Obtenir des applications”** et cherchez **“Microsoft Fabric Capacity Metrics”**.

---

## Conclusion : Prenez les commandes !

La gestion de la capacité, ce n’est pas que pour les administrateurs IT. C’est la clé pour créer des solutions **performantes** et **rentables**. En surveillant régulièrement vos métriques, vous devenez un véritable architecte de la donnée.

**Vous avez aimé cet article ?** Abonnez-vous pour ne rien rater des prochaines astuces Fabric et partagez cette newsletter à un collègue qui lutte avec ses temps de chargement !

---

## 📚 Ressources pour aller plus loin

* 🛠️ **[Installer l’application de métriques](https://learn.microsoft.com/fr-fr/fabric/enterprise/metrics-app-install?tabs=1st)** : Le guide pas à pas pour configurer votre tableau de bord.
* 📈 **[Comprendre l’App Metrics (Vue d’ensemble)](https://learn.microsoft.com/fr-fr/fabric/enterprise/metrics-app)** : Tout savoir sur le fonctionnement global de l’outil de surveillance.
* 🖥️ **[Maîtriser la page Compute](https://learn.microsoft.com/fr-fr/fabric/enterprise/metrics-app-compute-page)** : Apprendre à lire chaque graphique pour traquer le *Smoothing*, le *Bursting* et le *Throttling*.
* 💾 **[Analyser la page Stockage](https://learn.microsoft.com/fr-fr/fabric/enterprise/metrics-app-storage-page)** : Le guide pour surveiller la volumétrie de votre OneLake et anticiper les factures de persistance.
