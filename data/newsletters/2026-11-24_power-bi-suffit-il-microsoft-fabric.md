---
title: Power BI suffit-il ? Ce que j'ai réellement compris de Microsoft Fabric
url: https://blog.antoinewang-tech.com/p/power-bi-suffit-il-microsoft-fabric
date: 2026-11-24
author: Antoine Wang
source: substack
---

# Power BI suffit-il ? Ce que j'ai réellement compris de Microsoft Fabric

Hello les masters Fabric 👋

Un client m’a dit : « Power BI me suffit pour analyser mes données. »

Power BI peut effectivement suffire pour suivre nos indicateurs et partager des analyses. Aujourd’hui, avec les outils d’IA générative, les agents et leurs skills peuvent nous aider à écrire du code, à explorer les données et même à construire nos rapports.

Le résultat dépend toutefois des données mises à leur disposition, du contexte métier qui les accompagne et des règles de sécurité appliquées.

Ce que je veux souligner ici, c’est ce qui se fait en amont du rapport : la préparation et la gouvernance des données, leur réutilisation et la collaboration entre les équipes. Comment organisez-vous ces travaux aujourd’hui ?

C’est là que je situe la valeur de Microsoft Fabric : un socle commun pour préparer, gouverner et réutiliser les données entre équipes. La BI, la Data Science, le temps réel et les agents deviennent alors différents usages de ce même socle.

## ⚡ En 30 secondes

> **Ce qu’il faut retenir :**
>
> * **Fabric complète vos usages BI.** Vous pouvez conserver vos rapports et élargir le travail en amont : préparation, gouvernance et partage des données entre équipes, au-delà de leur seule restitution dans Power BI.
> * **Un même socle peut alimenter plusieurs usages.** Les données préparées dans Fabric peuvent servir à la BI, aux prévisions, aux alertes et aux agents, en limitant les extractions et les copies propres à chaque projet.
> * **Vous capitalisez sur l’existant des modèles sémantiques Power BI.** Leurs mesures, descriptions et relations apportent du contexte métier aux usages agentiques.

---

## Pourquoi Power BI n’est plus la finalité ?

Quand on utilise déjà Power BI, la question vient naturellement : « Qu’est-ce que Fabric m’apporte de plus ? » Il ne s’agit pas de choisir entre les deux : Power BI fait partie de Fabric.

La réflexion porte plutôt sur ce qui se passe en amont de vos rapports : comment centraliser l’accès aux données, savoir qui en est responsable, organiser les droits et permettre aux équipes de réutiliser les mêmes jeux de données pour différents besoins.

Depuis septembre 2026, l’équipe Power BI présente les **Power BI Agentic Experiences** comme **généralement disponibles (GA)**. Aujourd’hui, créer un rapport ne signifie plus forcément partir de zéro. nous pouvons déléguer le travail à un agent, avec un document qui décrit le besoin ou une capture de la mise en page souhaitée : il peut nous aider à préparer une première version.

Un expert BI reste nécessaire pour relire, ajuster, tester et valider le résultat. La différence, c’est qu’il dispose déjà d’une base de travail, ce qui peut accélérer la création du rapport.

Ce n’est pas une fonctionnalité à activer dans Power BI, mais un ensemble de skills et d’outils que l’on installe dans son agent, par exemple GitHub Copilot, avec le plugin `powerbi-authoring`.

Microsoft annonce aussi, pour les prochains mois, une expérience de création d’applications en langage naturel dans Power BI Desktop, à partir d’un modèle sémantique. Ces applications sont décrites comme capables d’accepter des prompts, de réécrire des données et de soutenir des workflows opérationnels.

Ce que je retiens, ce sont deux compétences à avoir :

* **Formuler le besoin** : être clair et précis sur quelle décision, pour qui, avec quelles données.
* **Relire avec esprit critique** : L’agent produit vite, il ne décide pas à votre place si le rapport répond au bon problème.

**Mon conseil :** formulez d’abord le besoin de données : quelles sources rapprocher, qui en est responsable, qui peut y accéder et pour quels usages ?

## Un socle commun pour gouverner et développer les usages

Le rapport est une façon d’exploiter vos données, mais ce n’est pas la seule. Les mêmes données peuvent aussi servir à produire des prévisions, déclencher des alertes ou alimenter des agents.

C’est là que Fabric peut compléter vos usages BI : en proposant un socle commun pour préparer, gouverner et partager les données entre équipes. Voici cinq raisons de l’envisager en complément de Power BI.

### 1. Rassembler les sources sans multiplier les copies

**Symptôme :** chaque équipe refait ses extractions et sa préparation ; il devient difficile de savoir quelle donnée réutiliser et qui en est responsable.

**Ce que Fabric apporte :**

* **Data Factory** : des pipelines ETL/ELT pour ingérer, préparer et transformer, avec plus de 200 connecteurs natifs vers des sources sur site et dans le cloud.
* **Mirroring** : ajoute une base ou un catalogue externe (par exemple Azure SQL Database, Snowflake ou Azure Databricks) à Fabric, sans pipeline de déplacement à construire ni à exploiter.
* **Shortcuts** : ajoutent à OneLake une référence vers des tables, dossiers ou fichiers en formats ouverts (Azure Data Lake Storage, Amazon S3, Google Cloud Storage, Dataverse…), sans copie.

### 2. Réunir les usages : BI et Data Science

**Symptôme :** vous utilisez un outil pour la BI et un autre pour la Data Science. Les mêmes données sont parfois copiées et préparées plusieurs fois, tandis que chaque environnement demande des compétences spécifiques.

**Ce que Fabric apporte :** une même donnée peut être réutilisée par plusieurs moteurs via OneLake, sans créer une copie pour chaque équipe. Vous pouvez, par exemple, les exploiter dans un notebook avec AutoML pour entraîner et comparer des modèles de machine learning. Les prédictions produites peuvent ensuite être enregistrées dans un Lakehouse et analysées dans Power BI.

### 3. Relier les événements aux actions métier

**Symptôme :** les événements opérationnels restent isolés des données métier, et les équipes découvrent les écarts lors d’une consultation de rapport.

**Ce que Fabric apporte :** **Real-Time Intelligence** analyse les données au fil de leur arrivée (capteurs IoT, journaux applicatifs, clics web). **Eventstream** ingère et transforme, **Eventhouse** stocke et analyse, **Activator** détecte une condition sans code et déclenche une action : message Teams à une personne, un groupe ou un canal, e-mail, flux Power Automate, pipeline ou notebook.

Deux scénarios illustratifs, qui ne sont pas des retours clients :

* **Usine** : un capteur de ligne sort de sa plage, la maintenance reçoit un message Teams. L’[architecture de référence « connected factory »](https://learn.microsoft.com/fabric/real-time-intelligence/architectures/connected-factory) décrit une logique voisine : événements IIoT, prévision de pannes et notification des techniciens sur site avec Activator.
* **Supply chain** : un transport prend du retard ou un stock passe sous un seuil, une notification part. L’[architecture de référence « supply chain »](https://learn.microsoft.com/fabric/real-time-intelligence/architectures/supply-chain) combine flux ERP et logistiques, prévision des retards de livraison et escalade avec Activator.

### 4. Gouverner les accès au-delà d’un rapport

**Symptôme :** les mêmes données servent plusieurs équipes, mais chacune ne doit pas tout voir.

La gouvernance ne se limite pas aux permissions : elle suppose un responsable identifié, une description des données et des usages autorisés. Le catalogue OneLake aide à découvrir et gouverner les données ; les contrôles d’accès déterminent ensuite ce que chaque personne peut utiliser.

**Ce que Fabric apporte :** **OneLake securité** définit des rôles d’accès sur les dossiers et les tables, jusqu’aux lignes (RLS) et aux colonnes (CLS), et les applique dans tous les moteurs de Fabric. Un utilisateur qui n’a droit qu’à une partie des données n’en voit que cette partie, qu’il interroge en SQL, exécute un notebook Spark ou ouvre un rapport Power BI.

### 5. Et l’IA générative ?

Une fois les données préparées et les accès organisés, une autre question se pose : comment donner aux agents le contexte métier nécessaire pour les exploiter ?

Vous ne partez pas de zéro : vos **modèles sémantiques Power BI** contiennent déjà une partie de ces repères. Les descriptions des champs, les mesures et les relations que vous avez définies pour vos rapports peuvent aussi aider les agents à interpréter vos données.

À mon avis, c’est un différenciateur important de Fabric : **réutiliser le travail déjà réalisé dans Power BI pour partager un même contexte métier entre les rapports, les applications et les agents**, plutôt que le redéfinir pour chaque nouvel usage.

Le schéma résume cette progression :

1. **OneLake rassemble l’accès aux données**, pour les rendre réutilisables entre les différents usages.
2. **Les modèles sémantiques Power BI apportent le sens métier** : mesures, relations et définitions déjà utilisées dans vos analyses.
3. **Les ontologies (preview) peuvent élargir ce contexte** en reliant les concepts métier, leurs relations et leurs règles à plusieurs sources de données.

Ces usages peuvent aussi rejoindre les outils du quotidien. Côté Microsoft 365, deux parcours sont documentés :

* **Copilot Chat** : poser des questions sur vos rapports et modèles sémantiques Power BI depuis Microsoft Copilot Chat. Les réponses s’appuient sur la logique métier du modèle, dans les limites des droits de l’utilisateur et des politiques Purview DLP applicables.
* **Teams via un data agent** : publier un data agent Fabric dans l’Agent Store de Microsoft Copilot, puis l’interroger depuis Teams.

> Pour commencer sur Fabric, choisissez un jeu de données déjà utilisé et un usage complémentaire à tester. Identifiez son responsable, les droits d’accès et les coûts, puis évaluez le résultat avant d’élargir.

---

## Et pourquoi choisir Microsoft Fabric plutôt qu’une autre plateforme ?

Snowflake, Databricks et d’autres plateformes de données font aussi partie des choix possibles. Mon propos n’est pas d’en nier les atouts : le besoin de centralisation et de gouvernance ne désigne pas, à lui seul, un fournisseur.

Pour moi, Fabric présente des avantages concrets lorsque ces critères correspondent à l’organisation :

* **Continuité Microsoft** : Power BI et les modèles sémantiques existants, avec des usages dans Excel et Microsoft Teams.
* **Prise en main pour les équipes métier** : Data Factory et des parcours low-code ou no-code, aux côtés de SQL et Spark pour les équipes techniques.
* **Réutilisation des données** : OneLake et les Shortcuts pour partager des données compatibles entre moteurs, sans copie systématique.
* **Services réunis en SaaS** : ETL, SQL, Spark, Data Science et temps réel dans une même plateforme, avec moins d’intégrations entre services à construire.

Voici Microsoft Fabric.

---

## 🥇 La Règle d’Or

**Si tu dois retenir une chose : la valeur de Fabric, c’est de permettre aux équipes de réutiliser les mêmes données et les mêmes définitions métier, avec des accès maîtrisés, du rapport Power BI aux agents.**

*Dans votre organisation, qu’est-ce qui freine le plus la réutilisation des données : leur dispersion, les droits d’accès ou le manque de définitions partagées ?*

Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [Microsoft Fabric : Tout savoir sur le OneLake](https://blog.antoinewang-tech.com/p/onelake-microsoft-fabric-guide) — pour approfondir le socle commun dont parle cet article.
* [Microsoft Fabric : Bonnes pratiques pour optimiser Copilot dans Power BI (Prep Data for AI)](https://blog.antoinewang-tech.com/p/microsoft-fabric-copilot-in-powerbi-desktop-prep-data-for-ai) — pour préparer un modèle sémantique avant de l’exposer à Copilot.
* [Microsoft Fabric : Data Agent vs Copilot](https://blog.antoinewang-tech.com/p/microsoft-fabric-data-agent-copilot) — pour distinguer les deux expériences avant de choisir.
* [Microsoft Fabric RLS : Settings in Power BI or OneLake Security ?](https://blog.antoinewang-tech.com/p/rls-dans-power-bi-ou-dans-onelake) — pour décider où appliquer vos droits de lecture.
* [Piloter votre capacité Fabric comme un Pro](https://blog.antoinewang-tech.com/p/capacity-metrics-fabric) — pour mesurer la consommation d’une Capacity partagée.

## 📚 Ressources pour aller plus loin

Pour approfondir le sujet et passer à la pratique :

* [Power BI September 2026 Feature Summary](https://community.fabric.microsoft.com/blog/fbc_pbiupdatesblog/power-bi-september-2026-feature-summary/5325831) — Power BI Agentic Experiences (GA), réponses Power BI dans Copilot Chat (GA), partage de visuels dans Outlook on the web (preview), contrôle d’accès de Copilot aux modèles.
* [Power BI’s next chapter: The evolution of business intelligence](https://community.fabric.microsoft.com/blog/fbc_pbiupdatesblog/power-bi%E2%80%99s-next-chapter-the-evolution-of-business-intelligence/5369131) — création d’applications en langage naturel depuis Power BI Desktop, annoncée pour les prochains mois.
* [Power BI Agentic overview](https://learn.microsoft.com/power-bi/developer/agentic/power-bi-agentic-overview) — skills, outils MCP et installation du plugin `powerbi-authoring`.
* [What is Microsoft Fabric?](https://learn.microsoft.com/fabric/fundamentals/microsoft-fabric-overview) et [What is OneLake?](https://learn.microsoft.com/fabric/onelake/onelake-overview) — plateforme SaaS, workloads, analogie avec OneDrive, copie unique, Shortcuts, Mirroring.
* [Unify data with OneLake shortcuts and mirroring](https://learn.microsoft.com/fabric/onelake/unify-data) — choisir entre référence et réplication.
* [OneLake integration for semantic models](https://learn.microsoft.com/fabric/enterprise/powerbi/onelake-integration-overview) et [Direct Lake overview](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview) — prérequis de l’export Delta et place d’Import dans Fabric.
* [Use the low-code AutoML interface in Fabric](https://learn.microsoft.com/fabric/data-science/low-code-automl) — tâches, notebook généré et suivi MLflow.
* [What is Fabric Activator?](https://learn.microsoft.com/fabric/real-time-intelligence/data-activator/activator-introduction) — règles, actions Teams ou e-mail, aperçu d’impact et coût.
* Architectures de référence [Connected factory](https://learn.microsoft.com/fabric/real-time-intelligence/architectures/connected-factory) et [Supply chain](https://learn.microsoft.com/fabric/real-time-intelligence/architectures/supply-chain) — scénarios temps réel documentés.
* [Get started securing your data in OneLake](https://learn.microsoft.com/fabric/onelake/security/get-started-security) et [Table, column, and row-level security in OneLake](https://learn.microsoft.com/fabric/onelake/security/table-column-row-security) — rôles Viewer et Read, RLS, CLS, rôles exemptés.
* [What is Fabric IQ?](https://learn.microsoft.com/fabric/iq/overview) et [What is ontology (preview)?](https://learn.microsoft.com/fabric/iq/ontology/overview) — couches IQ, génération depuis des modèles sémantiques, statut preview.
* [Consume Fabric data agent in Microsoft Copilot](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-365-copilot) et [Fabric data agent concepts](https://learn.microsoft.com/fabric/data-science/concept-data-agent) — publication dans l’Agent Store, prérequis, frontière de conformité, lecture seule.
* [Copilot for Power BI overview](https://learn.microsoft.com/power-bi/create-reports/copilot-introduction) et [End-to-end: From raw data to a shared Power BI app](https://learn.microsoft.com/power-bi/create-reports/tutorial-end-to-end-power-bi) — exigences de capacité, statuts des expériences Copilot, impact du modèle sémantique sur les réponses.
* [Understand Microsoft Fabric licenses and capacity](https://learn.microsoft.com/fabric/enterprise/licenses), [Power BI Premium to Fabric migration FAQ](https://learn.microsoft.com/power-bi/support/premium-migration-faq) et [guide de décision P SKU vers F SKU](https://learn.microsoft.com/power-bi/support/premium-migration-decision-guide) — lecteurs Free, Pro et PPU, retrait des P SKU, protections d’usage.
* [Fabric capacity planning guide: Scale for decentralized analytics](https://learn.microsoft.com/fabric/enterprise/capacity-planning-scale-self-service-analytics) — Capacity partagée ou dédiée, contention.
