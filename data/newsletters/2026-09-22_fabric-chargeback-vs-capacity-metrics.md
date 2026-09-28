---
title: Fabric Chargeback vs Capacity Metrics : refacturer les CU
url: https://blog.antoinewang-tech.com/p/fabric-chargeback-vs-capacity-metrics
date: 2026-09-22
author: Antoine Wang
source: substack
---

# Fabric Chargeback vs Capacity Metrics : refacturer les CU

Hello les masters Fabric !

Plusieurs équipes partagent votre capacité Fabric, mais leurs usages sont différents. **Comment répartir la facture entre elles, et qui prend en charge la capacité inutilisée ?**

Aujourd’hui, on décortique un problème courant sur la refacturation des Capacity Units (CU).

## ⚡ En 30 secondes

**Ce qu’il faut retenir :**

> * Fabric Chargeback App montre qui consomme la capacité Fabric. Ce rapport Power BI ventile les Capacity Units (CU) par workspace, item, domaine et utilisateur, avec des données actualisées chaque jour.
> * Elle fournit la consommation, pas une facture en euros.
> * Utiliser les domaines pour faciliter la refacturation avec le Chargeback.

---

Je vois ce scénario où les équipes IT essayent de refacturer grâce à l’application Capacity Metrics où on peut suivre la consommation au niveau de chaque capacité Elles pensent que “l’outil de monitoring FinOps est en place”, jusqu’au jour où la DAF pose la vraie question de la refacturation par équipe, elles se retrouvent à monter un Notebook custom pour agréger l’export CSV. Plutôt que reconstruire une solution personnalisée, je vais vous montrer qu’il existe une application pour facilement refacturer les CU Fabric.

---

## Deux apps : deux angles de FinOps différents

Microsoft expose deux applications Power BI officielles pour piloter la consommation d’une capacité Fabric, installées par l’administrateur de la capacité depuis AppSource :

1. **Microsoft Fabric Capacity Metrics App** : elle expose la santé, l’usage et la performance de chaque capacité avec des données rafraîchies toutes les 10 à 15 minutes, une granularité de 30 secondes, et des visuels de throttling, d’autoscale, de storage et de plan capacité.
2. **Microsoft Fabric Chargeback App** ! Est-ce la solution miracle ? Elle permet l’allocation des coûts (ventilation par équipe) ! Elle expose la consommation CU par workspace, item, domain / subdomain et user, avec un refresh quotidien, un drill-through et un export pour intégration à vos outils Finance.

Le mécanisme recommandé : d’abord on vérifie ce qui s’est passé avec la Capacity Metrics App, ensuite on attribue les coûts en fonction des CU consommés avec la Chargeback App, enfin la refacturation formelle grâce à Azure Cost Management pour la partie externe entre Fabric capacité et l’abonnement.

*En savoir plus sur la [Capacité Metric App](http://Microsoft Fabric Capacity Metrics App) :*

[#### Microsoft Fabric : Comment surveiller votre capacité comme un Pro ?

[Antoine Wang](https://substack.com/profile/410602111-antoine-wang)

·

Feb 24

[Lisez l’intégralité de l’article](https://blog.antoinewang-tech.com/p/capacity-metrics-fabric)](https://blog.antoinewang-tech.com/p/capacity-metrics-fabric)

---

### Fabric Chargeback App : la ventilation par équipe

#### a. Ce que ça fait

Est-ce encore une application pour faire beau ? Là où Metrics App expose la santé technique d’une capacité, la Chargeback App répond à une seule question : **qui consomme quoi ?**

Ses visuels sont pensés pour la refacturation, voici l’interface de la Chargeback app :

1. **Workspace, Item, Domain / Subdomain** : trois onglets pour voir quel pourcentage de la capacité a été consommé par chaque axe.
2. **Utilization (CU) by date** montre l’utilisation quotidienne agrégée et permet de cerner les tendances.
3. **Utilization (CU) details**, c’est une matrice ligne à ligne avec les détails de consommation.
4. **Drill-through** permet d’avoir une vue dédiée et détaillée sur un périmètre précis (workspace, item ou domain).

5. **Export data**, matrice complète exportable avec des slicers pour filtrer, colonnes de hiérarchie sélectionnables, format compatible Excel / Power BI Desktop.

La configuration de l’application est très simple, il y a deux paramètres qui définissent son cadre d’analyse :

* **UTC Offset**, le timezone à adapter avec l’heure de votre pays (typiquement `10` pour Sydney, `2` pour Paris été).
* **Days Ago to Start**, c’est la fenêtre historique à choisir entre 14 jours ou à 30 jours.

#### b. La Réalité du Terrain

* **Actualisation quotidien uniquement** : “The Fabric Chargeback Report data isn’t real-time; it’s refreshed daily.”
* **Les domaines Fabric sont un prérequis**, sans domaine assigné aux workspaces, l’app catégorise tout sous “No domain” et “No subdomain”. Vous refacturez au workspace sans axe métier. C’est le piège n°1 que je vois sur le terrain, et il est traité en amont dans [le guide Fabric Domains : structurer vos workspaces sans transformer Fabric en marécage](https://blog.antoinewang-tech.com/p/fabric-domains-gouvernance). (exemple ci-dessous)

* **Setting tenant “Show user data” :** Lorsque ce paramètre est activé, les données utilisateur actives, y compris les noms et adresses e-mail, sont affichées. Si votre tenant admin a désactivé ce setting côté audit, tous vos utilisateurs remontent comme “Masked user” et le count agrège tous les masked users en un seul.
* **Non supporté sur Government clouds** : Si vous êtes secteur public / défense sur un tenant `gov.` ou souverain, l’app n’est pas disponible.
* **Non supporté avec Private Link** : Si votre tenant utilise Private Links, cette app ne fonctionnera pas du tout.
* **Installer dans un workspace Pro** : Microsoft recommande explicitement un workspace avec licence Pro pour l’installation, afin d’éviter que l’app elle-même consomme des CU de votre capacity de production.

* Le modèle sémantique n’est pas réutilisable : Vous ne pouvez pas construire vos propres rapports Power BI par-dessus le modèle sémantique de l’app. Il est supporté uniquement pour les rapports fournis. Pour du reporting custom, vous exportez et vous rechargez ailleurs.

---

### De la facture Azure à la refacturation à la bonne équipe

**La facture Microsoft reste inchangée.** Chargeback mesure la consommation et Cost Management présente les coûts.

1. **Croiser trois données.** Coût Azure de la capacité, consommation Chargeback sur la même période et correspondance **workspace / domaine > équipe > centre de coûts**.
2. **Valider la clé de répartition.** Par exemple, le prorata des CU consommées par équipe.
3. **Vérifier les droits et les cibles.** Les règles nécessitent un contrat pris en charge et les droits **Enterprise Administrator (EA)** ou **Billing account owner (MCA)**.
4. **Appliquer la ventilation.** Dans **Cost Management > Configuration > Cost allocation**, répartissez les coûts entre **subscriptions, resource groups ou tags**. Les pourcentages ne se synchronisent pas avec Chargeback.
5. **Contrôler et clôturer.** Vérifiez que le total réparti correspond au coût de départ, archivez les sources et la clé retenue, puis transmettez les montants par centre de coûts à Finance pour les écritures internes.

**Exemple fictif :** sur **10 000 €** à répartir, une clé validée de **30 / 50 / 20 %** donne **3 000 € pour Finance**, **5 000 € pour Marketing** et **2 000 € pour la plateforme**.

---

## 🥇 La Règle d’Or

**Si tu dois retenir une chose :** Metrics App est ton radar technique, Chargeback App est ta ventilation par équipe. Installe les deux, la première pour diagnostiquer, la seconde pour refacturer. Et avant de télécharger Chargeback, verrouille tes domaines dans Fabric, sinon 80 % de la valeur de l’app tombe dans “No domain”.

Et vous, avez-vous déjà installé la Chargeback App, ou vous êtes encore sur un export Notebook custom ? Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [Fabric Copilot Capacity (FCC) : le guide 2026 sans throttling](https://blog.antoinewang-tech.com/p/fabric-copilot-capacity-dedicated) : la FCC est une capacity Fabric à part entière : elle apparaîtra dans votre Chargeback et dans votre Metrics App, avec sa propre ventilation.
* [Fabric Domains : structurer vos workspaces sans transformer Fabric en marécage](https://blog.antoinewang-tech.com/p/fabric-domains-gouvernance) : la prérequis absolu pour que Chargeback ne remonte pas 80 % de “No domain”.

---

## 📚 Ressources pour aller plus loin

Pour approfondir le sujet et passer à la pratique, je vous recommande ces lectures essentielles issues de la documentation officielle :

* 📘 [Microsoft Fabric Chargeback app](https://learn.microsoft.com/fabric/enterprise/chargeback-app) : visuels, drill-through, considérations, limitations.
* 🛠️ [Install the Microsoft Fabric Chargeback app](https://learn.microsoft.com/fabric/enterprise/chargeback-app-install) : installation AppSource, paramètres UTC Offset / Days Ago, troubleshooting.
* 📘 [What is the Microsoft Fabric Capacity Metrics app?](https://learn.microsoft.com/fabric/enterprise/metrics-app) : les 10 pages de l’app, latence, partage, support SKUs.
* 🔗 [The Fabric throttling policy](https://learn.microsoft.com/fabric/enterprise/throttling) : smoothing, overages, carryforward, burndown : les mécaniques que Metrics App expose.
* 🛠️ [Compute page in the Fabric Capacity Metrics app](https://learn.microsoft.com/fabric/enterprise/metrics-app-compute-page) : throttling par fenêtre, ribbon charts, matrix par item et opération.
* 📘 [FinOps framework Invoicing and chargeback](https://learn.microsoft.com/cloud-computing/finops/framework/manage/invoicing-chargeback) : le cadre méthodologique Showback → Cost allocation → Chargeback appliqué au cloud Microsoft.
