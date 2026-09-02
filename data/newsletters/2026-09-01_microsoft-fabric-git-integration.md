---
title: Git Integration Fabric : Versionner ses artefacts, stratégie de branches
url: https://blog.antoinewang-tech.com/p/microsoft-fabric-git-integration
date: 2026-09-01
author: Antoine Wang
source: substack
---

# Git Integration Fabric : Versionner ses artefacts, stratégie de branches

Bonjour à tous, je suis **Antoine Wang**.

J’aide les profils techniques à maîtriser l’architecture de Microsoft Fabric, et j’aide les décideurs à comprendre l’impact réel de cette technologie.

Mon objectif ? Vulgariser le complexe et vous donner les clés pour maîtriser Microsoft Fabric, une plateforme de données SaaS unifiée et alimentée par l’IA pour simplifier la gestion des données et l’analyse.

🆕 **Nouveauté pour les lecteurs** : j’ai créé **Ask Fabric Mastery**, un assistant IA qui répond à vos questions sur Microsoft Fabric & Power BI en s’appuyant uniquement sur les 35 éditions de cette newsletter. Réponses sourcées, sans hallucination, avec un lien direct vers l’édition d’origine.

👉 **Testez-le maintenant** : [ask-fabric-mastery](http://awang1020.github.io/ask-fabric-mastery)  
🔑 **Code d’accès (ce code est réservé aux abonnés Fabric Mastery) :**

Cette newsletter est 100% gratuite. En vous abonnant maintenant, vous recevrez en exclusivité mon “One-Pager” pour cartographier l’ensemble de la solution Fabric en un coup d’œil.

Merci à celles et ceux qui me suivent depuis le début. Sans plus attendre, entrons dans le vif du sujet !

---

## ⚡ En 30 secondes

Ce qu’il faut retenir :

* **Git Integration** relie un workspace Fabric à une branche Git (GitHub ou Azure DevOps). Trois opérations fondamentales :

  + Connect and sync.
  + Commit to Git (workspace → branche)·
  + Update from Git (branche → workspace).

  Chaque artefact devient un dossier de fichiers structurés `[Nom].[Type]/` versionnés.
* **La règle non négociable** : un workspace = une branche à un instant T. Pas de commit direct sur `main`. Chaque développeur travaille sur une feature branch dans son feature workspace, puis passe par une Pull Request (PR) pour merger.
* **L’action à lancer** : activer Git Integration sur votre workspace `dev`, protéger `main` via la branch policy de GitHub, et adopter le workflow branch out > modifier > change review > commit > PR > update from Git. Sans ces cinq étapes câblées, vous n’avez pas de CI, vous avez un espoir.

---

### Pourquoi perdre du temps dans la collaboration ?

Posez-vous la question franchement. Un collègue ouvre votre semantic model “pour tester une mesure vite fait”, écrase votre schéma, sauve, et rentre chez lui. Le lendemain, vous rouvrez le workspace, votre modèle est en morceaux. Personne ne se souvient de ce qui a été touché. Aucune trace, aucun rollback, aucun coupable.

Je vois ce scénario partout. Il est le vestige direct de l’ère “Power BI Desktop”, quand deux analystes se passaient un `.pbix` sur un file share partagé. La réalité du terrain, c’est que Fabric a hérité de cette culture et l’a démultipliée. Vous n’êtes plus deux analystes à vous marcher sur les pieds : vous êtes six Data Engineers, quatre Analytics Engineers et deux Data Scientists à travailler sur le même workspace, sans branche, sans review, sans historique.

**Git Integration** est la brique qui résout ça.

La **Continuous Integration (CI)** est le socle qui garantit que le code (au sens large : semantic model, notebook, pipeline, lakehouse, rapport, dataflow…) est versionné, revu, mergé proprement. Aujourd’hui, on trace le sillon avec GitHub et je vous montre la démo end-to-end.

---

## C’est quoi ?

**Git Integration**, c’est une liaison bidirectionnelle entre un workspace Fabric et une branche Git (GitHub ou Azure DevOps).

Trois piliers à graver :

* Une définition = un dossier : chaque item Fabric (Lakehouse, semantic model, notebook, pipeline…) est représenté dans Git par un dossier `[Item Display Name].[Item Type]/` contenant les fichiers de définition (JSON, TMDL, py, sql selon l’artefact). Vous pouvez lire l’historique, faire des `git diff`, revenir en arrière, comme n’importe quel code source.
* Trois opérations fondamentales :

  + Connect and sync (relier),
  + Commit to Git (pousser du workspace vers la branche),
  + Update from Git (tirer de la branche vers le workspace).
* Selective branching : depuis 2026, un workspace peut switcher de branche à la volée. Ça change tout : plus besoin de créer un workspace jetable pour chaque feature, vous branchez, vous switchez, vous mergez.
* Fournisseurs supportés : Azure DevOps (Repos), GitHub (github.com et GitHub Enterprise Cloud avec data residency `.ghe.com`). Ne cherchez pas plus loin : ni GitLab, ni Bitbucket, ni Git self-hosted à ce jour.

---

## Mini-glossaire : les mots Git indispensables (et leur équivalent Fabric)

Avant d’ouvrir la démo, on aligne le vocabulaire. Si vous venez du monde Power BI et que Git est un mot flou, gardez cette liste sous la main.

* **Repo (repository)** : Le dépôt qui héberge le code versionné (dans notre cas, un dépôt GitHub). C’est là qu’atterrissent les définitions de vos items Fabric sous forme de dossiers `[Nom].[Type]/`.
* **Branch (branche)** : Une ligne de développement parallèle dans le repo. Vous pouvez modifier une branche sans impacter les autres. `main` est la branche de référence, `feature/xxx` sont vos branches de travail.
* **Commit**: Un instantané des changements que vous validez et intégrez à l’historique de la branche. Chaque commit porte un message qui explique “le pourquoi” du changement.
* **Push** : Envoyer vos commits vers le repo distant (côté GitHub). Dans Fabric, c’est exactement ce que fait le bouton **Commit to Git** du Source control pane.
* **Pull / Update** : Récupérer les commits distants vers votre environnement local. Dans Fabric, c’est le bouton **Update from Git**, quand un collègue a poussé, vous récupérez (pullez) ses changements dans votre workspace.
* **Merge (fusion)** : Intégrer les commits d’une branche dans une autre (ex. `feature/xxx` → `main`). Dans notre workflow : toujours via une PR, jamais à la main.
* **PR (Pull Request)** : Une demande de merge dans GitHub, soumise à la revue d’au moins un pair (team lead). C’est obligatoire avant d’intégrer votre feature dans `main`. La PR expose le diff et les commentaires, c’est là que la revue se fait.
* **Checkout** : Basculer votre environnement sur une autre branche. Dans Fabric, c’est la comande **Switch branch** (selective branching) ou **Check out new branch** (en cas de conflit) dans le Source control pane.

---

## La démo GitHub, étape par étape

#### 1. Le setup : connecter votre workspace à GitHub

Prérequis absolu : vous devez être **workspace admin**. Un member ou un contributor ne peut pas activer Git Integration. Si vous êtes coincé, remontez au tenant admin.

**Étapes exactes (démo GitHub) :**

1. Ouvrez votre workspace puis dans **Workspace settings** (icône ⚙️ en haut à droite).

2. Sélectionnez l’onglet **Git integration**.

3. Choisissez **GitHub** comme provider.

4. Si première connexion : autorisez Fabric via un **Personal Access Token (PAT)** GitHub (scope `repo` minimum) ou via OAuth selon votre configuration tenant.

**Recommandé** : Utilisez un fine-grained PAT (avec l’autorisation de read write sur le Content) :

Gardez ce token sous la main pour pouvoir l’utiliser dans l’étape ci-dessous !

5. **Renseignez trois champs :**

* Display Name : doit être unique pour chaque utilisateur de GitHub
* Personal Access Token : collez ici le token généré à l’étape 4.
* Repository URL : l’URL complète de votre repo (ex. `https://github.com/mon-org/fabric-data-platform`)

6. Depuis le menu déroulant, **spécifiez les détails** suivants concernant la branche à laquelle vous souhaitez vous connecter :

* Branche (Sélectionnez une branche existante via le menu déroulant, ou sélectionnez **+ Nouvelle branche** pour en créer une nouvelle. Vous ne pouvez vous connecter qu’à une seule branche à la fois.)
* Dossier (Tapez le nom d’un dossier existant ou un nom pour en créer un nouveau. Si vous laissez le nom du dossier vide, le contenu est créé dans le dossier root. Vous ne pouvez vous connecter qu’à un seul dossier à la fois.)

À partir de là, Fabric fait un premier **Commit to Git** automatique : il génère les dossiers `[Nom].[Type]/` pour chaque item existant du workspace, les pousse dans la branche connectée, et le workspace passe en statut **Synced**.

#### 2. La stratégie de branches : main + feature branches

Le pattern canonique en Fabric CI ressemble à ceci :

* `main` = branche d’intégration. Source de vérité. Aucun push direct, uniquement via Pull Request (PR).
* `feature/xxx` = feature branches, une par chantier (ex. `feature/add-sales-forecast`, `feature/refactor-fact-orders`).
* Chaque feature branch est connectée à son propre workspace, le fameux “feature workspace”.

Pour créer une feature branch + un feature workspace en un clic : depuis le workspace connecté à `main` (le `dev`), utilisez la commande **Branch out to workspace** dans le Source control pane. Fabric crée la nouvelle branche depuis `main`, provisionne un nouveau workspace, et exécute automatiquement un `Update from Git` pour le peupler. Vous héritez de tous les items de `main` dans un espace isolé.

**Alternative :** **Selective branching** est plus légère, vous restez dans le même workspace et vous changez simplement la branche connectée (Source control pane → Switch branch). Fabric fait un `Update from Git` sur la nouvelle branche et remet le workspace en cohérence.

**Une règle terrain qui évitent 90 % des ennuis :**

1 feature = 1 branche = 1 workspace. Résistez à l’envie de mutualiser plusieurs features dans un même workspace pour économiser des ressources. Le coût d’un feature workspace est marginal ; le coût d’un merge conflict cross-features est énorme.

**L’erreur classique sur le terrain** :

Brancher trois workspaces différents sur la même branche pour “économiser”. Résultat : trois développeurs commitent la même feature en écrasant leurs modifications mutuellement, sans que Git ne détecte de conflit puisque le pousseur en dernier gagne. Chaos garanti.

#### 3. Change review : voir les diffs AVANT de commit

Vous êtes dans votre feature workspace, connecté à `*feature/add-sales-forecast*`. Vous modifiez le : ajout d’une mesure DAX, changement d’une relation, refactor d’une hiérarchie. Vous sauvez.

Ouvrez le Source control pane (icône dans la barre supérieure du workspace). Vous voyez maintenant apparaître le nombre **d’Uncommitted changes**.

Nouveauté 2026 majeure : **le granular compare**. Cliquez sur un item modifié, vous obtenez un diff propriété par propriété entre l’état actuel du workspace et l’état de la branche. C’est le `git diff` que Fabric n’a pas eu pendant deux ans.

C’est la brique qui vous évite le commit accidentel. Elle vous permet de :

* Commiter **sélectivement** : cochez seulement les items que vous voulez pousser (pas de “Commit all” aveugle).
* Détecter les modifications parasites : le workspace touche parfois des propriétés techniques (`lastModifiedTime`, cache metadata) qui polluent le diff. Le granular compare les révèle avant qu’elles ne finissent dans l’historique.
* Éduquer votre équipe : le diff propriété par propriété rend visible ce qui, jusqu’ici, était invisible côté Fabric.

#### 4. Updates & sync : quand vos collègues ont poussé du code

Scénario classique de la matinée : vous ouvrez votre feature workspace, et le Source control pane affiche ***”Update available”***. Un ou plusieurs collègues ont poussé sur la branche à laquelle vous êtes connecté.

Le pane détaille les items entrants :

* Nouveaux items côté Git qui n’existent pas encore dans votre workspace.
* Modifiés : items qui existent des deux côtés mais dont la définition Git diverge.
* Supprimés : items présents dans le workspace mais retirés de la branche.

Cliquez **Update all**.

#### 5. Ce que Git Integration ne fait PAS : les vrais garde-fous à connaître

Avant de vendre Git Integration en interne comme “la solution CI/CD complète”, assumez ses limites :

* Pas de gestion multi-environnement : Git Integration versionne, elle ne déploie pas. Dev > Test > Prod, c’est Deployment Pipelines ou `***fabric-cicd***`. Ne confondez pas les deux briques.
* Pas de paramétrisation par environnement : le semantic model commited contient les connexions dev. Si vous faites un `*Update all*` sur un workspace prod, vous récupérez les connexions dev, il faut un une **variable library** pour remplacer les valeurs.
* Pas tous les items sont supportés : La liste évolue à chaque release Fabric — vérifiez la doc Basic concepts in Git integration avant de compter dessus.
* Pas de secrets dans le repo : les credentials de connexion ne sont pas versionnés (par design). Bonne nouvelle pour la sécurité, contrainte pour la reproductibilité. Documentez à côté (`README.md`, wiki, Key Vault).
* PAT GitHub à durée limitée : votre PAT expire (30, 60, 90 jours selon vos policies). Anticipez la rotation, sinon Git Integration se déconnecte en silence et personne ne voit passer les updates.

---

## 🥇 La Règle d’Or

Si tu dois retenir une chose : Git Integration dans Fabric, c’est le mécanisme qui découple ton workspace de tes développeurs. Un workspace = une branche. Aucun commit direct sur main. Chaque feature vit dans sa branche, dans son workspace, et transite par une PR revue.

L’impact terrain est direct : quand Git Integration est bien configurée, un développeur peut casser son feature workspace sans casser la prod, un reviewer peut voir en 30 secondes ce qui change dans un semantic model via le granular compare, et un audit RGPD trouve la matrice de responsabilité dans l’historique Git plutôt que dans les souvenirs de l’équipe. Vous transformez Fabric d’un espace de bricolage collectif en une plateforme d’ingénierie data, sans changer un seul artefact.

> Et vous, aujourd’hui, avez-vous intégré Git Integration dans vos workspaces? Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [Du PoC à la Production : Guide pratique des pipelines de déploiement](https://blog.antoinewang-tech.com/p/deployment-pipelines-microsoft-fabric)
* [Microsoft Fabric en production : la checklist en 10 points avant le Go Live](https://blog.antoinewang-tech.com/p/microsoft-fabric-mise-en-production-checklist)

---

## 📚 Ressources pour aller plus loin

Pour approfondir le sujet et déployer Git Integration proprement, je vous recommande ces lectures essentielles issues de la documentation officielle :

* [What is Microsoft Fabric Git integration?](https://learn.microsoft.com/fabric/cicd/git-integration/intro-to-git-integration) : vue d’ensemble, providers supportés, cas d’usage
* [Basic concepts in Git integration](https://learn.microsoft.com/fabric/cicd/git-integration/git-integration-process) : item types supportés, folder mapping, git status, permissions
* [Get started with Git integration](https://learn.microsoft.com/fabric/cicd/git-integration/git-get-started) : le pas-à-pas de connexion (Azure DevOps + GitHub)
* [Compare changes with granular compare](https://learn.microsoft.com/fabric/cicd/git-integration/granular-compare) : la diff experience propriété par propriété
* [Development process using branched workspace](https://learn.microsoft.com/fabric/cicd/git-integration/branched-workspace) : Branch out to workspace, Switch branch, Check out new branch
* [Fabric CI/CD concepts and best practices](https://learn.microsoft.com/fabric/fundamentals/understand-best-practices-fabric-cicd) : le guide de référence pour aller au-delà de la CI (release process, `fabric-cicd`, deployment pipelines)
* [Automate Git integration by using APIs](https://learn.microsoft.com/fabric/cicd/git-integration/git-automation) : Connect, Commit to Git, Update from Git en PowerShell/REST pour les pipelines automatisés
