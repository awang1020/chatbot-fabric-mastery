---
title: Azure Maps dans Power BI : vos données restent-elles en UE ?
url: https://blog.antoinewang-tech.com/p/azure-maps-conformite-ue
date: 2026-09-29
author: Antoine Wang
source: substack
---

# Azure Maps dans Power BI : vos données restent-elles en UE ?

Hello les masters Fabric !

* Vous avez remplacé vos anciens visuels Map et Filled map basés sur Bing par Azure Maps ?
* Votre tenant Power BI est localisé en Europe ?
* Où est-ce que les données sont traités en utilisant ce visuel ?

Azure Maps possède plusieurs endpoint, notamment un endpoint européen, constituant une garantie technique importante, mais elle dépend de trois niveaux que je vois souvent mélangés : la localisation du tenant, les paramètres d’administration et les fonctionnalités utilisées dans le visuel.

Ici, on tranche : ce qui reste dans la géographie Europe, ce qui peut en sortir, et la checklist à conserver.

## ⚡ En 30 secondes

> **Ce qu’il faut retenir :**
>
> * Pour Azure Maps, Power BI choisit automatiquement l’endpoint selon la **localisation du tenant**. La région de votre Capacité n’entre pas dans cette décision.
> * Avec `eu.atlas.microsoft.com`, les requêtes et données d’entrée restent dans la **géographie Europe**, réplication de haute disponibilité comprise.
> * Il y a deux paramètres sur le portail d’administration qui permet d’autoriser le traitement hors région et de sous-traitance sur des fonctionnalités de la carte.

---

## La résidence des données Azure Maps dans Power BI

Le visuel **Azure Maps** est la brique cartographique native de Power BI. Il appelle un endpoint Azure Maps pour récupérer les tuiles, géocoder le champ `Location` et afficher les données géographiques. La résidence décrit où les requêtes et données d’entrée sont traitées et stockées ; elle ne remplace ni le contrôle d’accès, ni la minimisation, ni l’analyse de conformité de votre organisation.

---

## La réalité du terrain

### ✅ 1. C’est le tenant Power BI qui choisit l’endpoint

Le routage est automatique. Si la localisation du tenant Power BI est en Europe, le visuel appelle `eu.atlas.microsoft.com`. L’auteur du rapport et le lecteur n’ont rien à configurer dans le visuel pour obtenir ce comportement.

Le point qui prête à confusion : **la région de la Capacité n’est pas prise en compte** pour déterminer l’endpoint Azure Maps. Une Capacité en France Central n’est donc pas la preuve à produire.

La donnée de référence se trouve dans le service Power BI : menu **Aide (**`?`**) → About Power BI**, puis la mention indiquant où les données du tenant sont stockées :

Ce découplage est logique : la Capacité porte le moteur de calcul, tandis que le tenant porte la localisation utilisée par le visuel pour son routage géographique.

### ✅ 2. L’endpoint européen garde les entrées dans la géographie Europe

La documentation Microsoft indique qu’avec `eu.atlas.microsoft.com`, les requêtes et les données d’entrée sont traitées et stockées dans la géographie Azure Europe. Pour la reprise après sinistre et la haute disponibilité, Microsoft peut répliquer les données client, mais uniquement dans une autre région de cette même géographie.

Cette garantie porte sur la **résidence du service**. Elle ne limite pas le pays depuis lequel un utilisateur autorisé peut consulter le rapport.

### ✅ 3. Toutes les données du rapport ne partent pas vers Azure Maps

Le visuel transmet ce dont le service cartographique a besoin :

* la zone sur laquelle la carte est centrée, afin de récupérer les tuiles nécessaires au rendu ;
* les données placées dans le compartiment `Location`, lorsqu’un géocodage est nécessaire ;
* une éventuelle télémétrie de santé du visuel, si la télémétrie Power BI est activée.

En dehors de ces scénarios, Microsoft précise que les autres données superposées sur la carte sont rendues localement dans le client et ne sont pas envoyées aux serveurs Azure Maps. Une mesure de chiffre d’affaires utilisée pour dimensionner une bulle n’est donc pas, par ce seul usage, envoyée au service de géocodage.

**Ne vous y trompez pas** : une coordonnée, une adresse ou un nom de lieu peut rester sensible selon son contexte. La bonne pratique consiste à préparer dans votre couche Gold le niveau géographique strictement nécessaire à la valorisation de la donnée : ville plutôt qu’adresse complète, zone plutôt que point précis, lorsque le besoin métier le permet. C’est la même logique de minimisation que dans une [architecture Médaillon Bronze, Silver, Gold sur Microsoft Fabric](https://blog.antoinewang-tech.com/p/architecture-medaillon-microsoft-fabric).

### ✅ 4. La migration Bing vers Azure Maps doit être recettée

Les anciens visuels **Map** et **Filled map** utilisent Bing Maps.

Power BI Desktop propose une conversion de tous les anciens visuels cartographiques du rapport ou d’un seul visuel. Les réglages sont repris, mais Microsoft avertit que la taille de certains marqueurs peut différer, car les plages de taille ne sont pas identiques entre les plateformes.

La migration est donc un projet de recette, pas une formalité : comparez le cadrage, les couches, les marqueurs, les tooltips, les interactions, les bookmarks et le rendu mobile. Puis refaites l’audit de résidence sur le visuel converti. Remplacer une brique ne valide pas les paramètres du tenant à votre place.

**Mon conseil :** Inventoriez d’abord les rapports contenant Map ou Filled map, versionnez une copie, convertissez par lot contrôlé et faites signer la recette fonctionnelle ainsi que la revue de résidence avant publication.

---

## Points de vigilance

### ⚠️ 1. « Process data outside your region or boundary » change la conclusion

Le **portail d’administration Power BI** permet d’autoriser le **traitement des données Azure Maps hors de la région géographique**, de la limite de conformité ou de l’instance de cloud national du tenant. Ce réglage sert notamment aux tenants situés dans une zone où les services Azure Maps requis ne sont pas disponibles.

Pour un tenant européen qui utilise l’endpoint européen, activer cette option élargit volontairement le périmètre possible. Vous ne pouvez plus reprendre la conclusion « les données ne quittent pas la géographie Europe » sans documenter les opérations concernées.

**Mon conseil :** Laissez ce réglage désactivé pour les groupes qui n’en ont pas besoin. Si une exception est nécessaire, limitez son périmètre, nommez un propriétaire et consignez la justification ainsi que la date de revue.

### ⚠️ 2. L’outil de sélection peut faire intervenir un sous-traitant

Un second réglage autorise les sous-traitants Microsoft Online Services à traiter les données. Il nécessite l’activation préalable du traitement hors région. Certaines fonctions, dont **l’outil de sélection Azure Maps**, peuvent alors utiliser des capacités cartographiques tierces ; la documentation de prise en main cite les données TomTom et prévient que les données utilisateur peuvent ne pas rester dans la frontière géographique.

Microsoft indique que seules les informations essentielles liées à la **localisation** sont partagées, par exemple des **coordonnées ou noms de lieux**, et que les identités des utilisateurs ainsi que les informations de consommation des rapports ne sont pas incluses.

---

## Architecture / Fonctionnement

Voici l’architecture de traitement et les flux de données du visuel Azure Maps dans Power BI (pour les abonnés free/paid) :

**Couleurs** :

* orange = données susceptibles d’être envoyées ;
* vert = données métier restant dans le client ;
* bleu = traitements ;
* jaune = stockage cloud ;
* rouge = sous-traitance conditionnelle ;
* turquoise = sortie ;
* gris = contrôles.

### Exécution étape par étape

1. **Préparer les données** : Power BI applique les permissions, RLS, filtres, segments et interactions. Les filtres ne sont pas directement envoyés à Azure Maps, mais ils déterminent les lieux et coordonnées restant à afficher.
2. **Séparer les données** :

   * **2A, susceptibles d’être envoyées** : zone visible et niveau de zoom, valeurs textuelles de `Location` si elles doivent être géocodées, latitude et longitude, puis télémétrie de santé si elle est activée ;
   * **2B, non envoyées selon le comportement documenté** : `Legend`, `Size`, `Tooltips`, mesures métier, titre du modèle sémantique, nom du rapport, de la page ou du visuel, identité utilisateur et informations de consommation du rapport.
3. **Construire l’appel** : le visuel choisit automatiquement le point de terminaison Azure Maps selon l’emplacement du locataire Power BI, puis transmet uniquement les éléments nécessaires de l’étape 2A.
4. **Traiter dans Azure Maps** : Azure Maps récupère les tuiles correspondant à la zone visible et, si nécessaire, transforme les valeurs de `Location` en coordonnées. Une télémétrie de santé, par exemple un rapport de plantage, peut être collectée si l’option Power BI est activée.
5. **Retourner le résultat** : Azure Maps renvoie les tuiles du fond de carte et les coordonnées produites par le géocodage. Les requêtes nécessaires peuvent être stockées temporairement ; la durée propre au visuel n’est pas publiée. Un sous-traitant peut intervenir uniquement pour les fonctions autorisées.
6. **Assembler localement** : le client Power BI combine les réponses Azure Maps avec les coordonnées disponibles et les données 2B restées dans Power BI pour dessiner les points, couleurs, tailles et infobulles.
7. **Afficher la carte** : le lecteur voit la carte finale. Les contrôles Power BI continuent de régir l’accès aux données métier affichées.

---

## 🥇 La Règle d’Or

**Si tu dois retenir une chose : l’endpoint européen protège la résidence seulement tant que les paramètres et les fonctionnalités respectent cette frontière. Vérifiez la chaîne tenant, réglages, outil de sélection avant d’écrire « conforme UE ».**

L’impact terrain est concret : vous savez quelle preuve demander, quel réglage challenger et quelle exception faire valider. Vous pouvez migrer les anciens visuels Bing sans déplacer aveuglément la dette de conformité vers Azure Maps, et répondre à un audit avec une chaîne de décision documentée.

Votre organisation a-t-elle déjà audité les deux tenant settings Azure Maps et l’usage de l’outil de sélection dans ses rapports ?

Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [RLS, CLS, OLS Microsoft Fabric : guide sécurité des données](https://blog.antoinewang-tech.com/p/securite-microsoft-fabric) : pour compléter la résidence par les contrôles d’accès dans Power BI, OneLake et Fabric.
* [Fabric Domains : structurer la gouvernance des Workspaces](https://blog.antoinewang-tech.com/p/fabric-domains-gouvernance) : pour attribuer un propriétaire clair aux Workspaces et aux décisions de conformité associées.

---

## 📚 Ressources pour aller plus loin

Pour approfondir le sujet et affiner vos choix d’architecture, je vous recommande ces lectures essentielles issues de la documentation officielle :

* 📘 [Résidence des données du visuel Azure Maps Power BI](https://learn.microsoft.com/fr-fr/azure/azure-maps/power-bi-visual-data-residency) : routage automatique selon la localisation du tenant.
* 📘 [Étendue géographique du service Azure Maps](https://learn.microsoft.com/fr-fr/azure/azure-maps/geographic-scope) : endpoints, stockage et réplication dans une même géographie.
* 🛠️ [Gérer le visuel Power BI Azure Maps dans votre organisation](https://learn.microsoft.com/fr-fr/azure/azure-maps/power-bi-visual-manage-access) : tenant settings pour le traitement hors région et les sous-traitants.
* 🔗 [Bien démarrer avec le visuel Azure Maps Power BI](https://learn.microsoft.com/en-us/azure/azure-maps/power-bi-visual-get-started) : données envoyées, rendu local et avertissement sur l’outil de sélection.
* 🛠️ [Convertir Map et Filled map vers Azure Maps](https://learn.microsoft.com/en-us/azure/azure-maps/power-bi-visual-conversion) : procédure de migration et point de vigilance sur le rendu.
