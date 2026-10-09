---
title: FUAM : Capacity Compute Page more than 14 day on Metrics App
url: https://blog.antoinewang-tech.com/p/fuam-capacity-compute-historique
date: 2026-10-06
author: Antoine Wang
source: substack
---

# FUAM : Capacity Compute Page more than 14 day on Metrics App

Hello les masters Fabric !

Capacity Metrics App est l’application Microsoft dédiée au suivi et à l’analyse des capacités Fabric. Elle permet de visualiser la consommation, l’état de santé et l’utilisation du stockage, avec un historique de 14 jours disponible sur la page Compute

Aujourd’hui, on décortique un problème d’historique sur la Capacity App Metrics en se penchant sur une solution avec FUAM. De plus, je vais détailler le throttling sur Microsoft Fabric pour vous permettre de tout comprendre sur la capacité.

## ⚡ En 30 secondes

> Ce qu’il faut retenir :
>
> * La page Compute de Capacity Metrics couvre les 14 derniers jours. FUAM persiste les collectes dans son Lakehouse pour construire un historique plus long à partir de son déploiement.
> * Les graphiques `Interactive delay`, `Interactive rejection` et `Background rejection` suivent le même principe de Throttling sur des fenêtres différentes (de 10 minutes, 60 minutes et 24 heures).
> * Sous `100 %`, le palier n’est pas actif. Au-dessus, Fabric retarde l’interactif, rejette l’interactif, puis rejette toutes les nouvelles requêtes.

---

## Capacity Metrics App et FUAM

**Capacity Metrics App** est l’application Microsoft native pour diagnostiquer une Capacity : consommation CU, throttling, overages, timepoints et opérations, avec 14 jours sur la page Compute.

**FUAM (Fabric Unified Admin Monitoring)** est un **Solution Accelerator** permettant de centraliser la supervision d’un environnement Microsoft Fabric à l’échelle du tenant. Il collecte les logs, métriques de capacité, informations d’inventaire et données d’usage dans un Lakehouse unique, puis expose des rapports Power BI pour l’administration et l’optimisation de la plateforme.

⚠️ **Note** : FUAM n’est pas un produit officiel Microsoft Fabric, mais un accélérateur développé par la Fabric Customer Advisory Team.

---

## Que s’est-il passé avant les 14 derniers jours ?

Nous savons que la page **Compute de l’application Capacity Metrics** couvre 14 jours : c’est souvent trop court pour comparer deux clôtures mensuelles ou prouver qu’un pic se produit principalement en été ou en fin d’année.

La solution FUAM conserve les extractions concernant les métriques de capacités successivement dans son Lakehouse. L’historique grandit après le déploiement, puis ses graphiques permettent de suivre l’utilisation des Capacity Units (CU), les délais d’interactives et throttling sur la durée.

⚠️ **FUAM ne récupère pas rétroactivement des mois disparus**. Le chargement initial reste limité à 14 jours, c’est l’exécution régulière de la Pipeline d’ingestion qui construit l’historique long terme.

---

## Une couche d’historisation et de diagnostic

Pour information, FUAM extrait au maximum 14 jours depuis le modèle Capacity Metrics lors du chargement initial, puis peut réduire la fenêtre des exécutions suivantes et ajouter les nouvelles données dans ses tables Delta dans le lakehouse. Le rapport principale de FUAM est **FUAM\_Core\_Report**, où la page **Capacity Compute** fournit ainsi une vue historique au-delà de la fenêtre native, et vous pouvez ainsi filtrer la période que vous voulez pour comparer l’usage de votre consommation CU de vos capacités sur plus de 14 jours.

Vous pouvez utiliser le bandeau de droite “**Filters**” pour filtrer sur une capacité spécifique avec le champ “Capacity” et tous les graphiques présents se mettent dynamiquement à jour :

---

## Que représente les pourcentages des graphiques de Throttling ?

Voici comment la capacité arrive à du Throttling :

Regardons ensemble les mécanismes de Throttling dans Fabric, les trois courbes lisent la même consommation lissée sur des horizons différents :

Le pourcentage décrit le niveau d’occupation de la fenêtre de throttling à un timepoint. Il ne prédit ni le nombre d’utilisateurs touchés ni la durée d’une requête. Voyons un exemple de pourcentage sur “Interactive Delay” dans ma démo :

À 50 % sur Interactive Delay, c’est 5 des 10 minutes autorisées qui sont déjà engagées. Les 50 % restants peuvent partir en un seul timepoint de 30 secondes, ou ne jamais être consommés si la capacité respire.

Chaque graphique est normalisé sur **SA propre fenêtre**, donc 50 % partout n'est pas la même marge. Un 50 % sur la courbe Interactive Delay c’est 5 minutes, mais un 50% sur la courbe Background Rejection, c'est une demi-journée de capacité hypothéquée.

**La règle terrain** : **100%** est la ligne de seuil commune. Dans les définitions détaillées Microsoft, le palier devient effectif lorsque sa courbe franchit ce seuil. Traitez toute valeur inférieure à 100 % comme un signal de contexte, pas comme la preuve d’une limitation. Comparez toujours les trois fenêtres et leur tendance.

> **Le bon réflexe se joue en deux temps :**
>
> *Diagnostiquer* : le franchissement de 100 %, sa durée et la tendance des courbes, jamais le niveau instantané d’une seule d’entre elles.
>
> *Traiter* : identifier ce qui alimente la charge avant de scaler le SKU, de rééquilibrer entre capacités ou de replanifier les jobs.

---

## 🥇 La Règle d’Or

Si tu dois retenir une chose : FUAM étend l'observation, pas la règle. La pipeline d’ingestion construit, collecte après collecte, un historique au-delà des 14 jours natifs de la Capacity Metrics App.

Sur la page Capacity Compute du rapport, les trois courbes indiquent si la capacité a subi un throttling récurrent, jusqu'à quel palier afin d'anticiper la charge avant le prochain incident.

***La limite native de 14 jours vous a-t-elle déjà empêché d’identifier un motif récurrent sur votre Capacity ?***

Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [Capacity Metrics App Microsoft Fabric : piloter votre capacité](https://blog.antoinewang-tech.com/p/capacity-metrics-fabric) : pour installer l’app native et explorer ses pages Compute, Timepoint et Overages.
* [Ingestion Microsoft Fabric : Dataflow, Pipeline ou Notebook ?](https://blog.antoinewang-tech.com/p/microsoft-fabric-data-ingestion-tools) : pour arbitrer entre les principales charges background selon leur volume, leur orchestration et leur consommation en CU.
* [Fabric Copilot Capacity : isoler les workloads IA](https://blog.antoinewang-tech.com/p/fabric-copilot-capacity-dedicated) : pour comprendre quand le découplage d’une charge Copilot protège la Capacity de production.

---

## 📚 Ressources pour aller plus loin

Pour approfondir le sujet et affiner vos choix d’architecture, je vous recommande ces lectures essentielles issues de la documentation officielle :

* 📘 [Understand capacity throttling and smoothing](https://learn.microsoft.com/en-us/fabric/enterprise/throttling) : bursting, lissage, carryforward, burndown et paliers de throttling.
* 📘 [Metrics app calculations](https://learn.microsoft.com/fabric/enterprise/metrics-app-calculations) : interprétation des pourcentages et formule de récupération.
* 🛠️ [Compute page in the Fabric Capacity Metrics app](https://learn.microsoft.com/fabric/enterprise/metrics-app-compute-page) : lecture des graphiques Utilization, Throttling et Overages.
* 🔗 [Understand the metrics app timepoint page](https://learn.microsoft.com/fabric/enterprise/metrics-app-timepoint-page) : identification des opérations contributrices sur une fenêtre de 30 secondes.
* 🔗 [Explore Fabric capacity overview events](https://learn.microsoft.com/fabric/real-time-hub/explore-fabric-capacity-overview-events) : schéma des événements et définition des trois pourcentages.
* 🧰 [Fabric Unified Admin Monitoring sur microsoft/fabric-toolbox](https://github.com/microsoft/fabric-toolbox/tree/main/monitoring/fabric-unified-admin-monitoring) : code source et avertissement de support de FUAM.
