---
title: Microsoft Fabric & VNet : Le Guide Sécurité Data Gateway
url: https://blog.antoinewang-tech.com/p/vnet-data-gateway-microsoft-fabric
date: 2026-06-30
author: Antoine Wang
source: substack
---

# Microsoft Fabric & VNet : Le Guide Sécurité Data Gateway

Bonjour à tous, je suis **Antoine Wang**.

J’aide les profils techniques à maîtriser l’architecture de Microsoft Fabric, et j’aide les décideurs à comprendre l’impact réel de cette technologie.

Mon objectif ? Vulgariser le complexe et vous donner les clés pour maîtriser Microsoft Fabric, une plateforme de données SaaS unifiée et alimentée par l’IA pour simplifier la gestion des données et l’analyse.

🆕 **Nouveauté pour les lecteurs** : j’ai créé **Ask Fabric Mastery**, un assistant IA qui répond à vos questions sur Microsoft Fabric & Power BI en s’appuyant uniquement sur les 25 éditions de cette newsletter. Réponses sourcées, sans hallucination, avec un lien direct vers l’édition d’origine.

👉 **Testez-le maintenant** : [ask-fabric-mastery](http://awang1020.github.io/ask-fabric-mastery)  
🔑 **Code d’accès (ce code est réservé aux abonnés Fabric Mastery) :**

Cette newsletter est 100% gratuite. En vous abonnant maintenant, vous recevrez en exclusivité mon “One-Pager” pour cartographier l’ensemble de la solution Fabric en un coup d’œil.

Merci à celles et ceux qui me suivent depuis le début. Sans plus attendre, entrons dans le vif du sujet !

---

Vos sources de données peuvent être on-premises, dans le cloud, ou derrière un Virtual Network (un réseau privé sécurisé), non accessible publiquement depuis internet.

*Fabric est pertinent pour l’analytique de vos données, mais comment récupérer ce qui se trouve derrière cette couche de sécurité VNet, sans friction ?*

La réalité du terrain, c’est que la majorité des bases de données que je rencontre en production, PostgreSQL, SQL Server, Oracle, SAP, ne sont pas exposées sur internet. Et c’est une bonne chose. Mais ça implique de mettre en place la bonne brique de connectivité côté Fabric avant de créer quoi que ce soit.

Je vais décortiquer la méthode issue de la documentation Microsoft pour gérer cette intégration étape par étape, avec des astuces et des points de vigilance.

---

## La solution

Fabric est un service cloud. Par défaut, il ne peut pas atteindre une ressource isolée dans un réseau privé Azure. Pour traverser ce périmètre, vous avez besoin d’une passerelle de données (data gateway), c’est un composant intermédiaire qui reçoit les requêtes Fabric, qui les exécute à l’intérieur du réseau privé, et puis en renvoie les résultats.

Il existe trois types de gateway dans Fabric :

* **Cloud data gateway** : géré nativement par Fabric, pour les sources cloud accessibles publiquement.
* **On-premises data gateway** : à installer sur un serveur ou une VM, pour les environnements locaux et datacenter privé.
* **VNet data gateway** : déployé et géré directement par Microsoft à l’intérieur de votre VNet Azure, sans aucune installation manuelle.

Pour une source hébergée dans un VNet Azure : c’est la troisième brique qui va nous intéresser. Et depuis une mise à jour récente, le Copy Job, l’artefact d’ingestion le plus direct dans Fabric Data Factory, la supporte nativement. Vous pouvez très bien utilisé une pipeline avec Copy Activity (voir à l’étape 2).

La méthode tient en trois étapes. Voici comment les exécuter sans se piéger.

---

## Étape 1 : Configurer la passerelle de données de réseau virtuel

#### Ce qu’il faut comprendre avant de démarrer

Le VNet data gateway ne s’installe pas. Microsoft utilise le service Power Platform VNet pour injecter un conteneur managé directement à l’intérieur de votre réseau virtuel. Il n’y a pas de VM à provisionner, ni d’agent à maintenir. En revanche, il y a trois actions préalables côté Azure que votre équipe réseau doit valider.

**A. Inscrire le fournisseur de ressources**

Sur le portail Azure, en tant que propriétaire de l’abonnement :

* Accédez à votre Abonnement, puis “Fournisseurs de ressources”.
* Recherchez `Microsoft.PowerPlatform` et cliquez sur “S’inscrire”.

**B. Créer et déléguer un subnet dédié**

Dans votre VNet Azure, créez un nouveau subnet dédié exclusivement au VNet data gateway :

* Nommez-le explicitement, évitez `gatewaysubnet` et `AzureBastionSubnet`, ces noms sont réservés à d’autres services Azure et bloqueront la création.
* Dans la délégation de sous-réseau, sélectionnez `Microsoft.PowerPlatform/vnetaccesslinks`.
* Ce subnet ne doit pas contenir d’espace d’adressage IPv6 et ne doit pas chevaucher la plage `10.0.1.x`.

> **💡Astuce** : Si vous manipulez de grands volumes de données, ajoutez le service endpoint `Microsoft.Storage` sur ce subnet dès maintenant.
>
> ⚠️ **Point de vigilance** : Cette délégation nécessite le rôle Contributeur Réseau (ou l’autorisation `Microsoft.Network/virtualNetworks/subnets/join/action`) sur le VNet.

**C. Créer la passerelle dans Fabric**

Dans Fabric : Accédez aux “Settings”, puis “Manage connections and gateways” :

1. Cliquez sur “+ New” puis sélectionnez “Virtual Network data gateway”.
2. Sélectionnez votre Capacity Fabric (toute SKU Fabric est compatible — F2 et au-dessus).
3. Renseignez : Abonnement Azure, Resource Group, VNet, Subnet (seuls les subnets délégués à Power Platform apparaissent dans la liste).
4. Nommez le gateway de façon explicite : `vnet-gw-prod-westeurope` plutôt que `gateway1`. Vous en aurez plusieurs, distinguez-les dès le départ.
5. Cliquez sur “Save”. Le provisionnement prend 2 à 5 minutes.

---

## Étape 2 : Créer un Copy Job dans Microsoft Fabric

Le Copy Job est l’artefact d’ingestion que nous allons mettre en place. Conçu pour les transferts fiables et optimisés en volume, il supporte désormais nativement les connexions via VNet data gateway.

Dans votre Workspace Fabric :

1. Cliquez sur “+ New item” et sélectionnez “Copy job”.
2. Donnez-lui un nom explicite, lié à la source et à l’environnement : `copyjob-erp-prod` par exemple.
3. Choisissez la base de données à partir de laquelle copier des données :

4. Fabric vous guide ensuite vers la configuration de la **connexion source**, c’est là qu’intervient la dernière étape.

---

## Étape 3 : Sélectionner le VNet data gateway lors de la configuration de la connexion source

Dans la configuration du Copy Job, à l’écran de sélection de la **source** :

1. Renseignez les éléments de configuration de la connexion.
2. Dans le champ **Data gateway**, sélectionnez le VNet data gateway créé à l’étape 1.
3. **Testez la connexion** avant de valider.

Une fois la connexion validée, configurez votre **destination** normalement — Lakehouse, Warehouse, ou autre artefact Fabric. La destination est dans Fabric : aucun gateway n’est nécessaire côté destination.

#### Ce qui se passe réellement à l’exécution

Quand le Copy Job tourne :

* Les données transitent depuis votre source, via le conteneur injecté dans votre VNet, vers Fabric.
* Elles ne passent **à aucun moment par l’internet public**.

---

## **⚠️** Pièges à Éviter

**Ne choisissez pas l’on-premises gateway par réflexe pour une source Azure.**

* Je vois des équipes installer un on-premises gateway sur une VM Azure pour atteindre une source dans un VNet. C’est une erreur ! Si votre source est dans Azure, le VNet data gateway est fait exactement pour ça — sans la charge opérationnelle.

**Ne sous-estimez pas l’impact sur votre Capacity.**

* Le VNet data gateway consomme des Capacity Units (CU) à chaque requête. Sur une Capacity mutualisée avec d’autres workloads, un Copy Job massif via gateway peut créer de la contention. Monitorez votre consommation dans le Fabric Capacity Metrics app dès la mise en production.

**Un seul gateway pour tous les environnements : attention à la dette technique.**

* Il est tentant de centraliser dev, recette et prod sur un seul VNet gateway. À court terme, ça simplifie. À moyen terme, un problème sur ce gateway coupe tous vos environnements simultanément. Séparez au minimum la production des environnements de développement sur des gateways distincts.

---

## Matrice de Décision

**Q1 : Votre source est-elle accessible depuis l’internet public ?**

* **OUI** : Cloud data gateway. Aucune configuration requise, passez directement à la création de connexion.
* **NON** : Passez à Q2.

**Q2 : Votre source est-elle hébergée dans un VNet Azure ?**

* **OUI** : VNet data gateway. Pourquoi ? Pas de VM à gérer, déploiement managé par Microsoft, intégration native avec la Capacity Fabric.
* **NON** (datacenter on-premises, réseau privé non-Azure) : On-premises data gateway.

---

## Conclusion

Si tu dois retenir une chose : connecter une source dans un VNet à Fabric, c’est trois étapes dans le bon ordre, configurer le VNet data gateway, créer le Copy Job, sélectionner le gateway sur la connexion source.

L’impact terrain est immédiat : vos données ne transitent plus par l’internet public et vous restez dans le modèle de gouvernance Fabric sans sortie de l’écosystème.

> Et vous, quelle est votre configuration actuelle pour atteindre vos sources privées dans Fabric ?

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [Sécuriser les connexions Microsoft Fabric : bonnes pratiques et service principal](https://blog.antoinewang-tech.com/p/secure-connexion-source-microsoft-fabric)
* [RLS, CLS, OLS Microsoft Fabric : le guide sécurité des données 2026](https://blog.antoinewang-tech.com/p/securite-microsoft-fabric)

---

## 📚 Ressources pour aller plus loin

* 🛠️ [Créer et configurer un VNet data gateway — Documentation officielle Microsoft](https://learn.microsoft.com/fr-fr/data-integration/vnet/create-data-gateways)
* 📘 [Copy Job avec VNet data gateway](https://learn.microsoft.com/fr-fr/fabric/data-factory/copy-job-with-virtual-network-data-gateway)
* 🛠️ [Créer un Copy Job dans Microsoft Fabric](https://learn.microsoft.com/fr-fr/fabric/data-factory/create-copy-job)
* 🔗 [Gérer les connexions et gateways dans Fabric](https://learn.microsoft.com/fr-fr/data-integration/vnet/manage-data-gateways)
