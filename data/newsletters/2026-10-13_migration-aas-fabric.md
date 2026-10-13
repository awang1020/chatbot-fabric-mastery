---
title: Migration Azure Analysis Services vers Fabric : la check-list démo
url: https://blog.antoinewang-tech.com/p/migration-aas-fabric
date: 2026-10-13
author: Antoine Wang
source: substack
---

# Migration Azure Analysis Services vers Fabric : la check-list démo

Hello les masters Fabric !

Beaucoup d’entre vous se posent la question de la migration AAS to Fabric, qu’est-ce que c’est ? pourquoi on en parle et comment le faire ?

J’aimerai vous partager ma démo réalisée sur la migration de modèles AAS vers les modèles sémantiques sur Microsoft Fabric. Pendant 5 mins, je décrypte tout ce tu as besoin de savoir et comment le réaliser.

## **⚡** En 30 secondes

> **Ce qu’il faut retenir :**
>
> * Avant de cliquer sur **Migrate** dans Fabric, j’ai configuré 3 services adjacents :
>
>   + le **Storage Account de backup AAS** (networking public + storage account key access ON),
>   + le **workspace / la Capacité** (F-SKU, Large model ON, XMLA Read/Write),
>   + et le **tenant Fabric** (`Azure Connections` activé + workspace lié à un ADLS Gen 2).
> * **Migrate** : lance la migration du modèle AAS vers le modèle sémantique Fabric / Power BI.
> * Après **Migrate**, j’ai deux boutons à activer :
>
>   + la **redirection XMLA** (pour vos outils Tabular Editor, SSMS, PowerShell)
>   + et le **rebind** (pour vos rapports Power BI live-connect).

---

Migrate dans Fabric, c’est le point de départ concret de la migration : un bouton qui permet de prendre votre modèle AAS et de lancer sa migration vers un modèle sémantique dans Microsoft Fabric. Une fois la migration réalisée, il reste ensuite à rediriger les outils utilisant XMLA et à reconnecter les rapports Power BI au nouveau modèle.

**⚠️ Avant de migrer : vérifiez le sizing de votre capacité Fabric**

La migration d’AAS vers Fabric n’est pas uniquement une question de compatibilité fonctionnelle. Il faut aussi vérifier que la **capacité Fabric cible est correctement dimensionnée** pour accueillir vos modèles et leur consommation.

Pour dimensionner la cible d’une migration AAS, Microsoft recommande notamment de considérer la **taille du plus gros modèle AAS**, **le nombre d’utilisateurs et la consommation CPU**. La consommation CPU entre AAS et Fabric/Power BI peut différer selon les workloads, refresh et patterns de requêtes.

👉 **En clair : ne choisissez pas votre F-SKU uniquement en faisant une équivalence avec votre SKU AAS actuel. Regardez la taille de vos modèles et mesurez la charge réelle.**

*Source : [Migrate from Azure Analysis Services to Power BI](https://learn.microsoft.com/en-us/power-bi/guidance/migrate-azure-analysis-services-to-power-bi-migration-scenarios)*

Maintenant, voyons la check-list pour que votre migration dans Microsoft Fabric se passe correctement. Chaque point est un paramétrage à valider **AVANT** ou **APRÈS** avoir cliqué sur le bouton **Migrate** dans le portail Microsoft Fabric.

---

### **✅** 1. Préparer le compte de stockage utilisé pour le backup AAS

Avant de lancer la migration, il faut préparer **un compte de stockage Azure utilisé par Azure Analysis Services pour sauvegarder le modèle AAS**.

Lors de la migration, le modèle AAS est d’abord sauvegardé sous la forme d’un fichier `.abf` (Analysis Services Backup File) dans un **container Blob configuré au niveau du serveur AAS**. Ce backup constitue une étape intermédiaire permettant ensuite au processus de migration de récupérer le modèle pour le transférer vers Fabric.

👉 **Attention : il s’agit ici du Storage Account configuré pour le backup du serveur AAS**, et non du stockage associé au workspace Fabric.

Trois réglages à vérifier en premier sur les comptes de stockage:

**1. Networking du Storage Account**

Le serveur AAS doit pouvoir accéder au compte de stockage dans lequel il écrit son backup.

Dans mon environnement de démo, j’ai donc vérifié la configuration réseau du Storage Account et autorisé l’accès nécessaire.

Pour un PoC, cela peut notamment passer par une configuration réseau suffisamment ouverte. Dans un environnement de production, il faut évidemment adapter cette configuration aux règles réseau et de sécurité de l’organisation.

**2. Accès via la clé du Storage Account**

J’ai également vérifié que `Allow storage account key access` était activé afin que le mécanisme de backup AAS puisse utiliser le Storage Account configuré.

**3. Configurer le Storage Account côté AAS**

Enfin, le compte de stockage doit être déclaré comme destination de backup du serveur AAS :

**Azure Portal > serveur Azure Analysis Services > Settings > Backup**

Il faut y configurer le **container Blob** qui recevra les fichiers `.abf`.

---

### **✅** 2. Créer et déployer un modèle BIM dans AAS

> 💡 **Cette étape est spécifique à ma démo. Si vous avez déjà un modèle AAS à migrer, vous pouvez directement passer à l’étape suivante.**

Personnellement, je ne disposais pas d’un modèle AAS existant. J’ai donc dû en créer un afin de pouvoir reproduire le scénario de migration de bout en bout.

Mais tout d’abord, qu’est-ce qu’un modèle BIM ?

Un fichier `.bim` décrit le **modèle tabulaire Analysis Services** : il contient notamment la définition du modèle, ses tables, colonnes, relations, mesures, partitions, sources de données et rôles.

Dans ma démo, j’ai donc :

**Azure SQL Database > création du modèle BIM dans Tabular Editor > déploiement sur AAS > processing du modèle > connexion d’un rapport Power BI**

#### Étape 2.1 : création du modèle

J’ai créé dans **Tabular Editor** un modèle tabulaire basé sur plusieurs tables provenant d’une **Azure SQL Database**.

Une fois le modèle construit, je l’ai déployé vers mon serveur AAS via :

**Model → Deploy…**

avec :

* **Server** : URI de mon serveur AAS
* **Database** : nom du modèle à créer sur AAS
* **Structure**
* **Data Sources**
* **Partitions**
* **Roles**

À ce stade, le modèle existe dans AAS, mais cela ne signifie pas encore que ses données sont chargées.

#### Étape 2.2 : processing du modèle

Le **déploiement du modèle** et le **chargement des données** sont deux étapes distinctes dans mon scénario.

J’ai donc rouvert le modèle AAS directement depuis Tabular Editor :

**File → Open → From DB → URI du serveur AAS**

Puis j’ai configuré l’accès à mon Azure SQL Database et lancé un **Full Refresh** afin de charger les données dans le modèle AAS.

Dans mon environnement de démonstration, j’ai utilisé un **compte SQL Auth dédié en lecture** pour permettre à AAS d’accéder à la source.

Une fois le refresh terminé, j’ai vérifié dans **DAX Studio** que les tables du modèle contenaient bien des données.

#### Étape 2.3 : création du rapport Power BI de test

Enfin, j’ai créé un rapport Power BI connecté au modèle AAS :

**Power BI → Get Data → Azure Analysis Services → serveur AAS → modèle**

Ce rapport est important pour la suite de la démonstration : **il me sert de test de bout en bout pour vérifier, après la migration, que le rapport peut être rebindé vers le nouveau modèle sémantique Fabric.**

---

### ✅ 3. Préparer le workspace Fabric cible et sa capacité

À ce stade, **le côté AAS est prêt** : le modèle est déployé, les données sont chargées et mon rapport Power BI en Live Connection vers AAS est publié.

On passe maintenant côté cible.

L’objectif est de préparer le workspace qui accueillera le modèle AAS une fois transformé en modèle sémantique Power BI/Fabric.

Ce workspace ne peut pas être configuré comme un simple workspace Power BI Pro. La fonctionnalité de migration nécessite un environnement compatible, notamment :

* Une capacité Fabric F-SKU (recommandé).
* Dans les paramètres du workspace, activer le “Large semantic model storage format”.
* Au niveau de la capacité, le XMLA endpoint doit être configuré en Read/Write.
* Un compte ADLS Gen2 connecté au workspace *(voir le prochain point).*

On a donc deux stockages à ne pas confondre dans cette migration :

* **côté AAS** : le Storage Account avec son container destiné au backup AAS ;
* **côté cible** : l’ADLS Gen2 connecté au workspace vers lequel on migre.

### 🔐 Et côté permissions ?

Pour réaliser la migration, vérifiez également vos droits.

**Côté AAS**, Microsoft demande des permissions **Server Administrator** et d’appartenir aux rôles **Owner et/ou Contributor de la subscription**. **Côté Power BI/Fabric**, vous devez être **Workspace Administrator** du workspace cible.

*Source : [Migrate Azure Analysis Services to Power BI - Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/aas-pbi-migration-overview)*

---

### **✅** 4. Connecter le workspace à ADLS Gen2

Dernier prérequis avant de cliquer sur **Migrate** : le workspace cible doit être connecté à un **Azure Data Lake Storage Gen2 (ADLS Gen2)** situé dans le même tenant. Microsoft recommande également que ce stockage soit dans la même région que la capacité du workspace pour de meilleures performances.

💡 **ADLS Gen2 est un compte Azure Storage utilisant les fonctionnalités Data Lake**, notamment le *hierarchical namespace*.

Dans Fabric, j’ai donc vérifié deux choses :

* **Au niveau du tenant** : le paramètre permettant l’utilisation des connexions Azure est activé.

* **Au niveau du workspace** : le workspace cible est connecté au compte **ADLS Gen2** que j’ai préparé.

---

### **✅** 5. Maintenant, on migre !

À ce stade, **tous les prérequis sont en place** :

* **AAS prêt**
* **Backup configuré**
* **Capacité Fabric dimensionnée**
* **Large Model activé**
* **XMLA Read/Write**
* **ADLS Gen2 connecté**
* **permissions vérifiées.**

On peut maintenant passer à la partie concrète : **lancer la migration du modèle AAS vers Fabric.**

#### Étape 1 : Créer le pairing AAS au Workspace

Dans le workspace Fabric : **Migrate > Data Model (AAS)**.

Puis compléter les informations :

* Subscription Azure,
* Resource group,
* Server AAS,
* Workspace Fabric cible.

Cliquer sur “**Start Migration**”.

#### Étape 2 : Sélectionner les modèles à migrer

Sur la page **Migration Details**, cochez le ou les modèles de databases à migrer sur la colonne “Include in Migration”, puis **Migrate** (en haut à droite).

Fabric gère : backup sur le Blob AAS qui le copie dans ADLS Gen 2 du workspace puis restore en modèle sémantique. On peut avoir jusqu’à 5 modèles en parallèle.

#### Étape 3 : Activer la redirection serveur (XMLA)

Une fois le modèle sémantique présent dans Fabric, la migration **n’a pas encore redirigé vos outils**. Vos Tabular Editor, SSMS, PowerShell continuent à parler à AAS.

Sur la colonne **Server redirection enabled**, passez le slider à “**On”**. Cela crée un alias transparent : les scripts qui se connectaient à `asazure://...` sont automatiquement redirigés vers l’endpoint XMLA du workspace Fabric.

#### Étape 4 : Rebind du rapport Power BI

La redirection XMLA gère les outils. Elle ne gère PAS les rapports déjà publiés dans le service Power BI. Pour ceux-là, un mécanisme distinct : **Rebind**.

Sur la page **Migration Details** du modèle migré, cliquez sur “**Rebind reports”**. Fabric parcourt tous les rapports du tenant qui pointaient vers ce modèle AAS et les réoriente vers le semantic model Fabric.

Le processus prend quelques minutes. Vous pouvez suivre l’avancement via “**Rebind status”**. Si un rapport pose problème, vous pouvez faire “**Undo rebind”**, les rapports repointent alors vers AAS (à condition que le serveur ne soit pas encore pausé).

#### Étape 5 : Vérifier le rebind dans le Lineage Fabric

C’est l’étape que je vois trop souvent sautée. Sans elle, vous croyez la migration terminée alors qu’un rapport peut encore taper AAS en douce.

Ouvrez le workspace Fabric, sur **Lineage view**. Le rapport migré doit afficher un lien direct vers le **nouveau modèle sémantique** (nom du modèle qui vient d’apparaître), et **plus** vers l’ancien connecteur AAS.

**Deuxième vérification côté modèle sémantique, le mode de stockage :** ouvrez le rapport dans Power BI Desktop ou dans le service Fabric et regardez la source. Elle ne doit plus mentionner l’endpoint AAS mais bien le nouveau modèle sémantique, avec un mode de stockageapproprié (Import) :

---

## 🥇 La Règle d’Or

**Si tu dois retenir une chose : la migration AAS vers Fabric n’échoue jamais sur le modèle. Il y a des paramètres à prendre en compte en amont comme la taille des modèles, le backup Blob, les paramètres du tenant,…**

Vous avez déjà migré un modèle AAS vers Fabric ?

Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## **🔗** À lire dans Fabric Mastery

* [Direct Lake en production : les prérequis à valider avant de basculer](https://blog.antoinewang-tech.com/p/direct-lake-production) : après avoir migré votre modèle AAS en Import, la question suivante est le mode de stockage : rester en Import restauré, ou basculer Direct Lake sur OneLake. Voici les critères de décision.
* [RLS, CLS, OLS Microsoft Fabric : guide sécurité des données](https://blog.antoinewang-tech.com/p/rls-onelake-security-power-bi) : vos rôles AAS (Read, Administrator) deviennent des permissions Fabric (Build, Write) : les mappings ne sont pas 1:1, voici comment restructurer la sécurité fine post-migration.
* [Fabric Chargeback vs Capacity Metrics : dimensionner votre F-SKU](https://blog.antoinewang-tech.com/p/fabric-chargeback-vs-capacity-metrics) : dimensionner la Capacity cible qui remplace votre S-SKU AAS n’est pas un simple ratio cœurs pour cœurs, voici la méthode de sizing.

---

## 📚 Ressources pour aller plus loin

Pour approfondir le sujet et passer à la pratique, je vous recommande ces lectures essentielles issues de la documentation officielle :

* 📘 [Migrate from Azure Analysis Services to Power BI (guidance)](https://learn.microsoft.com/power-bi/guidance/migrate-azure-analysis-services-to-power-bi) : la vision stratégique et la matrice de comparaison AAS vs Fabric.
* 🛠️ [Migrate Azure Analysis Services to Power BI (how-to)](https://learn.microsoft.com/fabric/enterprise/powerbi/aas-pbi-migration-overview) : le pas-à-pas exact du portail Fabric, avec captures et prérequis.
* 🛠️ [Analysis Services database backup and restore](https://learn.microsoft.com/analysis-services/azure-analysis-services/analysis-services-backup?view=sql-analysis-services-2025) : la configuration du Storage Account et du container Blob côté AAS.
* 🔗 [Manage Azure connections (Fabric admin)](https://learn.microsoft.com/fabric/admin/service-admin-portal-azure-connections) : la référence pour activer le tenant setting `Azure connections` et le workspace-level ADLS Gen 2.
* 🔗 [Migration scenarios AAS to Power BI](https://learn.microsoft.com/power-bi/guidance/migrate-azure-analysis-services-to-power-bi-migration-scenarios) : six scénarios chiffrés pour choisir le bon SKU cible selon votre profil de consommation.
