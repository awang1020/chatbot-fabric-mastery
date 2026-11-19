---
title: Power BI avec Git et Azure DevOps : du rapport à la production
url: https://blog.antoinewang-tech.com/p/power-bi-avec-git-et-azure-devops-backup-versioning
date: 2026-11-17
author: Antoine Wang
source: substack
---

# Power BI avec Git et Azure DevOps : du rapport à la production

Hello les masters Fabric 👋

Un client m’a posé recemment la question : Comment je fais le back-up et le versionnement de mes rapports ? J’ai un fichier pbix que je versionne en dupliquant… Super, on va parler bonnes pratiques !

Quand plusieurs personnes font évoluer un rapport Power BI, comment valider les changements et choisir ce qui part en production ? Aujourd’hui, je pars d’une démonstration concrête en parcourant avec Git, Azure DevOps et les Deployment pipelines pour construire cette chaîne sans confondre version du rapport et données chargées.

## ⚡ En 30 secondes

> **Ce qu’il faut retenir :**
>
> * **Le nouveau format du rapport Power BI, PBIP rend les définitions du rapport et du modèle versionnables.** Une branche feature et une Pull Request permettent de relire les changements avant leur intégration dans `main`.
> * **La synchronisation Git au niveau du workspace facilite les mises à jour du rapport mais ne remplace pas les contrôles CI.** Le Workspace DEV récupère la version intégrée ; une validation Azure Pipelines peut bloquer une Pull Request (PR) incorrecte avant la fusion.
> * **On peut charger un échantillon de données dans le workspace DEV et TEST et le workspace PROD qui récupère toutes les données.** Grâce au Deployment rules dans les Deployments Pipeline, on peut modifier valeur d’un paramètre du modèle dans chaque étape cible.

## Comment faire le back-up ou le versionnement de mon rapport Power BI ?

Conserver une copie de votre fichier PBIX permet de retrouver un état de votre travail. Mais lorsque vous faites évoluer un rapport à plusieurs, vous avez aussi besoin de savoir **qui a changé quoi, pourquoi et quelle version a été validée**.

C’est la différence entre **sauvegarder** et **versionner**. Dans ma démo, je pars d’un projet Power BI au format **PBIP** et j’utilise Git avec Azure DevOps pour conserver l’historique de ses définitions et faire relire les modifications avant leur mise en production.

Voici le parcours, du développement local à la production.

### 1. Développer le rapport dans Power BI Desktop

Je travaille dans Desktop, puis j’enregistre mon projet au format **PBIP**. Le rapport et le modèle sémantique sont représentés dans des dossiers distincts : pages, visuels, tables, relations, mesures DAX… Ces définitions sont enregistrées sous forme de fichiers texte, ce qui permet de comparer leurs versions avec Git.

### 2. Versionner le projet dans Azure DevOps

J’utilise un dépôt **Azure Repos Git (Data-Analytics-Platform)**, que je clone dans **VS Code**. J’y enregistre mon projet Power BI : le dépôt distant devient le point de partage de l’équipe, tandis que chacun dispose de son clone local pour travailler.

### 3. Synchroniser main avec le Workspace DEV

Dans Fabric :

**Workspace DEV → Workspace settings → Git integration → Azure DevOps**.

Sélectionnez l’organisation, le projet, le dépôt, la branche `main` et le dossier `powerbi` correspondant à l’exemple. Un Workspace est connecté à **une branche et un dossier à la fois**.

Pour la première connexion, partez de préférence d’un Workspace DEV vide afin d’éviter de mélanger deux versions existantes sans arbitrage.

### 4. Proposer une modification avec une branche et une PR

Pour ajouter une page ou modifier un visuel, je crée une **branche feature**.

Une fois le changement enregistré, je fais un **commit** avec un message explicite, puis un **push** vers Azure DevOps.

J’ouvre ensuite une **Pull Request (PR)** pour faire valider les modifications de ma branche feature vers la branche principale `main`. Le team lead peut relire les différences et demander des ajustements avant la fusion. Des contrôles CI peuvent compléter cette revue, à condition d’avoir été configurés.

### 5. Intégrer la version validée dans le Workspace DEV

Côté Fabric, mon **Workspace DEV** est connecté à la branche `main` et au dossier du projet. Après la validation **et la fusion** de la PR, je vérifie les changements sur Review changes et récupère les changements avec **Source control → Updates → Update all**.

**Le point à retenir :** approuver une PR ne suffit pas à mettre le Workspace à jour. Dans ce parcours, la fusion puis la synchronisation sont deux actions distinctes. Une fois synchronisé, la colonne Git status devient “Synced”.

### 6. Promouvoir le contenu vers TEST, puis PROD

J’utilise ensuite un **Deployment pipeline Fabric** pour promouvoir le rapport et son modèle de **DEV vers TEST**, puis de **TEST vers PROD**, après les vérifications. Je ne développe donc pas directement dans l’environnement de production.

Les **règles de déploiement** sur le modèle sémantique permettent d’adapter certains paramètres à la cible. Par exemple, si on veut garder qu’un échantillon des données en DEV et TEST et charger toutes les données en PROD.

Par exemple, on veut filtrer les données dans le rapport que sur « année = 2023 » pour limiter l’affichage. Dans Power BI Desktop :

**Transformer les données → Gérer les paramètres → Nouveau paramètre**.

Pour cet exemple pédagogique, on crée:

* **Nom** : `AnneeFiltre`
* **Type** : `Number`
* **Valeurs suggérées** : liste `2023`, `ALL`
* **Valeur actuelle en développement** : `2023`

Pour **PROD**, après création initiale des items, configurez également sa propre règle `AnneeFiltre = ALL`, puis redéployez de TEST vers PROD avant l’actualisation et les contrôles.

* **DEV** **et TEST**: Valeur du projet : `AnneeFiltre = 2023` ; Ventes de 2023 uniquement
* **PROD** : Règle cible : `AnneeFiltre = ALL` ; Tout l’historique disponible dans la source PROD

> **Deux limites à garder en tête :** Git conserve les fichiers suivis du projet, pas les données des sources, les credentials ni l’ensemble des réglages du service. Et un déploiement de modèle Import ne copie pas ses données : l’actualisation et les contrôles restent à réaliser dans la cible, il faudra se reconnecter dans les différents workspaces pour actualiser les données.

## Les bonnes pratiques pour passer de la démo à la production

**Gardez une seule voie de promotion.** Dans cette architecture, `main` alimente DEV, puis le Deployment pipeline alimente TEST et PROD. Évitez d’alimenter les mêmes items cibles en parallèle par Git et par déploiement sans stratégie explicite.

**Séparez configuration et secrets.** Les valeurs attendues et le mapping des environnements doivent être documentés. Les secrets restent dans les mécanismes de connexion ou un coffre adapté à l’automatisation, jamais dans Git. Ne supposez pas que les règles créées dans l’interface sont sauvegardées avec le PBIP.

**Protégez l’environnement d’intégration.** Une modification faite directement dans DEV crée une divergence avec Git tant qu’elle n’a pas suivi le circuit prévu. Corrigez-la via une branche et une PR plutôt que de contourner `main`.

**Ne traitez pas le paramètre comme une sécurité.** `AnneeFiltre = 2023` réduit le jeu de développement ; ce n’est ni une RLS ni une interdiction d’accès aux autres années. Si les développeurs ne doivent jamais accéder à certaines données, appliquez la restriction dans les droits et les sources.

**Recettez aussi le volume complet.** TEST avec toutes les données permet de contrôler ce que le sous-ensemble DEV ne révèle pas : durée d’actualisation, taille du modèle et comportement des mesures sur tout l’historique. Cela suppose aussi que les données TEST soient autorisées pour les personnes qui y accèdent.

**Préparez le retour arrière.** Revenir à un commit restaure une définition, pas les anciennes données ni tous les réglages du service. Réintégrez la version voulue via le circuit contrôlé, redéployez et actualisez si nécessaire.

Enfin, une chaîne pilotée à la main reste une **livraison contrôlée**, pas un déploiement continu sans intervention. Pour automatiser, reliez explicitement validation, mise à jour Git, déploiement, actualisation, contrôles et approbation de production. Microsoft documente l’[automatisation des Deployment pipelines via API et Azure DevOps](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/pipeline-automation).

**Limite de périmètre :** l’exemple de réduction du chargement concerne Import. En DirectQuery, il faut examiner les requêtes réellement envoyées à la source. Direct Lake suit un autre mécanisme de liaison et de chargement ; ne lui transposez pas ce filtre Power Query ni une promesse générale « aucun refresh nécessaire ».

---

## 🥇 La Règle d’Or

**Si tu dois retenir une chose : Git versionne la définition, le pipeline promeut les items et l’actualisation charge les données. Les trois doivent être contrôlés pour valider une mise en production.**

Votre DEV peut rester limité à 2023 sans imposer cette restriction à TEST et PROD, à condition de paramétrer le modèle, de définir les règles cibles et de vérifier le résultat après chargement.

*Dans votre chaîne Power BI actuelle, qu’est-ce qui empêche une version non relue ou un périmètre de données incorrect d’arriver en production ?*

Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [Git Integration Fabric : versionner ses artefacts et choisir sa stratégie de branches](https://blog.antoinewang-tech.com/p/microsoft-fabric-git-integration) — pour élargir le workflow aux autres items Fabric.
* [Du PoC à la production : guide pratique des pipelines de déploiement](https://blog.antoinewang-tech.com/p/deployment-pipelines-microsoft-fabric) — pour comprendre la promotion entre Workspaces.
* [Sécuriser les connexions dans Microsoft Fabric](https://blog.antoinewang-tech.com/p/secure-connexion-source-microsoft-fabric) — pour traiter les accès aux sources séparément du versionnement.

## 📚 Ressources pour aller plus loin

* [Power BI Desktop projects](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview) — structure PBIP, exclusions Git et limites des dossiers synchronisés.
* [Power BI Desktop projects Azure DevOps integration](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-azdo) — création du dépôt, clone VS Code et enregistrement du projet.
* [Power BI Desktop project report folder](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report) — structure PBIR et schémas JSON.
* [PBIP and Azure DevOps build pipelines for validation](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-build-pipelines) — exemple de contrôles CI et de validation avant fusion.
* [Set and manage branch policies](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops) — protection de `main`, revue et Build validation.
* [Get started with Git integration](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started) — prérequis, connexion du Workspace et opération Update from Git.
* [Using parameters](https://learn.microsoft.com/en-us/power-query/power-query-query-parameters) et [Query evaluation and query folding](https://learn.microsoft.com/en-us/power-query/power-query-folding) — paramétrage M et exécution des filtres à la source.
* [Get started with deployment pipelines](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/get-started-with-deployment-pipelines) — création des étapes et affectation des Workspaces.
* [Create deployment rules](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/create-rules) — règles de paramètres et de sources, permissions et limites.
* [The deployment pipelines process](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/understand-the-deployment-process) — définitions copiées, données non copiées et liaisons entre items.
* [Automate deployment pipelines using APIs and DevOps](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/pipeline-automation) — prolongement pour automatiser les promotions.
