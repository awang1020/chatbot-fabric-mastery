---
title: Microsoft Fabric : Tout savoir sur les fondamentaux (Tenant, Workspace, Capacity)
url: https://blog.antoinewang-tech.com/p/tenant-workspace-capacity-licence
date: 2026-08-11
author: Antoine Wang
source: substack
---

# Microsoft Fabric : Tout savoir sur les fondamentaux (Tenant, Workspace, Capacity)

Bonjour à tous, je suis **Antoine Wang**.

J’aide les profils techniques à maîtriser l’architecture de Microsoft Fabric, et j’aide les décideurs à comprendre l’impact réel de cette technologie.

Mon objectif ? Vulgariser le complexe et vous donner les clés pour maîtriser Microsoft Fabric, une plateforme de données SaaS unifiée et alimentée par l’IA pour simplifier la gestion des données et l’analyse.

🆕 **Nouveauté pour les lecteurs** : j’ai créé **Ask Fabric Mastery**, un assistant IA qui répond à vos questions sur Microsoft Fabric & Power BI en s’appuyant uniquement sur les 32 éditions de cette newsletter. Réponses sourcées, sans hallucination, avec un lien direct vers l’édition d’origine.

👉 **Testez-le maintenant** : [ask-fabric-mastery](http://chat.antoinewang-tech.com)  
🔑 **Code d’accès (ce code est réservé aux abonnés Fabric Mastery) :**

Cette newsletter est 100% gratuite. En vous abonnant maintenant, vous recevrez en exclusivité mon “One-Pager” pour cartographier l’ensemble de la solution Fabric en un coup d’œil.

Merci à celles et ceux qui me suivent depuis le début. Sans plus attendre, entrons dans le vif du sujet !

---

Vous démarrez un projet Microsoft Fabric.

* *Quelles sont les notions à maîtriser pour bien comprendre l’architecture ?*
* *De quoi parle-t-on exactement lorsqu’on fait référence au Tenant, au Workspace, à la Capacity ou aux licences ?*

La réalité du terrain, c’est que ces concepts sont les fondations sur lesquelles repose toute votre plateforme. Mal maîtrisés, ils génèrent des surprises coûteuses et un manque de maturité : des données stockées dans une région non prévue, des utilisateurs bloqués par leurs licences, ou des choix d’architecture à corriger en pleine production.

Ce post est un rappel des notions fondamentales de Microsoft Fabric, pour accélérer votre progression sur la plateforme et poser les bons mots sur les bons concepts dès le départ.

---

### 1. Le Tenant

Le Tenant est votre organisation dans Microsoft Entra ID (anciennement Azure Active Directory). C’est le conteneur de plus haut niveau dans la hiérarchie Microsoft Fabric. Un tenant = une entité sécuritaire et organisationnelle unique.

**Ce que cela implique concrètement :**

* Tous vos utilisateurs, groupes, et applications sont gérés dans ce tenant.
* Tous vos Workspaces, artefacts, et données Fabric y sont rattachés.
* La frontière du tenant est quasi-imperméable nativement : partager des données *entre* tenants nécessite des mécanismes dédiés (External Data Sharing, cross-tenant shortcuts).

💡 **Tips** : Dans un contexte de groupe avec plusieurs entités juridiques, la question “un tenant ou plusieurs ?” doit être tranchée avant tout déploiement Fabric. C’est une décision organisationnelle et réglementaire, pas technique.

---

### 2. La Home Region

La **Home Region** est la région Azure datacenter liée à votre tenant Fabric, choisie au moment de la création de votre tenant. C’est là que résident par défaut vos données et les métadonnées de votre tenant.

**Comment la trouver ?** Depuis le portail Fabric, allez sur *About Microsoft Fabric et trouvez la valeur à côté de “Your data is stored in”* :

**Ce que cela implique concrètement :**

* Cette région n’est pas celle que vous choisissez librement. Elle est héritée de la création du tenant.
* Si votre Home Region ne figure pas parmi les régions où Fabric est disponible, vous ne pourrez pas accéder à toutes les fonctionnalités Fabric. Dans ce cas, vous pouvez créer une Capacity dans une région où Fabric est disponible.

⚠️ **Point de vigilance** : La Home Region d’un tenant est très difficile à changer. Ce n’est pas une opération en libre-service, cela nécessite l’intervention des équipes Microsoft. Si votre organisation a des exigences de souveraineté des données (RGPD, NIS2, secteurs régulés), vérifiez votre Home Region *avant* tout déploiement.

---

### 3. La Capacity (F SKU)

La **Capacity** est le moteur de calcul que vous provisionnez dans Azure pour faire fonctionner Microsoft Fabric. Elle est définie par un SKU (F2, F8, F32, F64, F128...) qui exprime sa puissance en **Capacity Units (CU)**.

Les trois rôles d’une Capacity :

1. Fournir la puissance de calcul pour tous les Workspaces qui lui sont rattachés (Spark, SQL, Power BI, Pipelines...).
2. Débloquer les fonctionnalités Fabric : c’est le SKU de la Capacity qui détermine ce que vos utilisateurs peuvent faire (Lakehouse, Warehouse, Eventstream, etc.).
3. Flexibilité : une seule Capacity suffit pour l’ensemble de vos usages, inutile de multiplier les capacités par workload. Data engineering, data science, ETL, reporting… tous vos workloads partagent la même puissance de calcul.

#### Home Region vs région de la Capacity !

Par défaut, sans configuration particulière, vos données résident dans la **Home Region** de votre tenant.

Lorsque vous utilisez le Multi-Geo, le compute et le stockage (incluant OneLake et le stockage spécifique aux expériences) sont localisés dans la région Multi-Geo, mais certaines métadonnées du tenant restent dans la Home Region.

En clair : si vous provisionnez votre Capacity F64 en *West Europe* alors que votre Home Region est *France Central*, vous entrez en configuration **Multi-Geo**. Les données des Workspaces rattachés à cette Capacity seront stockées en *West Europe*, mais les métadonnées du tenant resteront en *France Central*. Ce n’est pas automatique ni anodin, c’est un choix d’architecture explicite avec des implications réglementaires.

Multi-Geo est une fonctionnalité de Microsoft Fabric qui aide les clients multinationales à répondre aux exigences de résidence des données spécifiques à une région, à un secteur ou à une organisation.

💡 **Tips** : Pour la majorité des organisations françaises, provisionnez votre Capacity dans la même région que votre Home Region. Cela simplifie la gouvernance, la conformité, et évite des coûts de transfert de données inter-région.

---

### 4. Le Workspace

Le Workspace est le conteneur de travail et de gouvernance dans Microsoft Fabric. C’est là que vivent vos artefacts : Lakehouses, Warehouses, Pipelines, Semantic Models, Reports...

**Les règles structurantes à connaître :**

* Un Workspace est obligatoirement rattaché à une Capacity pour utiliser les fonctionnalités Fabric.
* Un Workspace ne peut être rattaché qu’à une seule Capacity à la fois.
* Les rôles dans un Workspace (Admin, Member, Contributor, Viewer) déterminent ce que chaque utilisateur peut faire sur l’ensemble des artefacts qu’il contient.
* Les Workspaces peuvent être organisés en Domaines pour structurer la gouvernance à l’échelle de l’organisation.

#### La question stratégique : combien de Workspaces ?

Il n’existe pas de réponse universelle. Les critères de segmentation les plus courants sont :

* **Par environnement** : un Workspace DEV, un TEST, un PROD par domaine fonctionnel.
* **Par couche Medallion** : un Workspace Bronze (ingestion), un Silver (transformation), un Gold (consommation), avec une Capacity distincte par environnement.
* **Par équipe responsable** : qui possède les artefacts ? Qui a les droits d’écriture ?

💡 **Tips** : En phase de démarrage, résistez à la tentation d’avoir un Workspace par projet. Commencez par un découplage environnement (DEV/PROD) et domaine fonctionnel. Vous affinerez la granularité au fur et à mesure que les équipes montent en maturité.

---

### 5. Les Licences utilisateur

Les licences utilisateur déterminent ce qu’une personne peut *faire* dans Fabric, indépendamment de la Capacity à laquelle son Workspace est rattaché.

---

### 6. Un point d’attention sur les migrations

Ce post n’est pas un guide de migration, mais deux situations méritent d’être anticipées dès la phase de conception de votre plateforme.

#### Migration cross-tenant

Les artefacts Fabric (Lakehouse, Warehouse, pipelines Fabric, bases KQL, etc.) ne se migrent pas nativement d’un tenant à un autre.  
En cas de fusion, acquisition ou carve-out impliquant un changement de tenant, il est important d’anticiper une reconstruction.

#### Migration cross-région (Multi-Geo)

Les workspaces contenant des artefacts Fabric autres que Power BI ne peuvent pas être déplacés entre régions.  
Avant tout déplacement, il est nécessaire de supprimer ces artefacts. Par ailleurs, les grands modèles sémantiques (Large Semantic Model Storage Format) ne peuvent pas être migrés d’une région à l’autre et doivent être redéployés comme de nouveaux modèles.

Si l’une de ces situations est à l’horizon pour votre organisation, il est essentiel de les analyser en amont, avant de démarrer le déploiement.  
Ce ne sont pas des blocages, mais des contraintes structurantes qui doivent être anticipées.

---

### Conclusion

Si tu dois retenir une chose : avant de choisir un SKU ou de dessiner votre architecture Medallion, posez-vous deux questions fondamentales :

* “Quelle est notre Home Region ?”
* “Qui est propriétaire de quoi dans nos Workspaces ?”

Tout le reste en découle.

**L’impact terrain** : Maîtriser ces concepts, c’est éviter les conversations difficiles en phase de déploiement, quand l’équipe métier attend le Go Live et que l’IT réalise que la Home Region ne correspond pas aux exigences de souveraineté, ou que les licences PPU ne débloquent pas les fonctionnalités attendues.

> **Et vous, comment avez-vous structuré la relation Capacity / Workspace dans vos projets Fabric actuels ?**

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

### 🔗 À lire dans Fabric Mastery

* [Microsoft Fabric : Révolution ou simple rebranding ?](https://blog.antoinewang-tech.com/p/microsoft-fabric-revolution-ou-rebranding)
* [Microsoft Fabric : Comprendre OneLake, le "OneDrive" de la Data](https://blog.antoinewang-tech.com/p/onelake-microsoft-fabric-guide)

---

### 📚 Ressources pour aller plus loin

* 📘 [Comprendre les licences Microsoft Fabric — Microsoft Learn](https://learn.microsoft.com/en-us/fabric/enterprise/licenses)
* 🔗 [Trouver votre Home Region Fabric — Microsoft Learn](https://learn.microsoft.com/en-us/fabric/admin/find-fabric-home-region)
* 🛠️ [Disponibilité régionale de Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/admin/region-availability)
* 📘 [Support Multi-Geo pour Microsoft Fabric — limitations et configuration](https://learn.microsoft.com/en-us/fabric/admin/service-admin-premium-multi-geo)
* 🔗 [Git Integration dans Microsoft Fabric — guide de démarrage](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration)
* 🛠️ [Rôles dans les Workspaces Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/fundamentals/roles-workspaces)
