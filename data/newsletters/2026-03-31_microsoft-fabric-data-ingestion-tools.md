---
title: Ingestion Microsoft Fabric : Dataflow, Pipeline ou Notebook ? Guide complet 2026
url: https://blog.antoinewang-tech.com/p/microsoft-fabric-data-ingestion-tools
date: 2026-03-31
author: Antoine Wang
source: substack
---

# Ingestion Microsoft Fabric : Dataflow, Pipeline ou Notebook ? Guide complet 2026

Bonjour à tous, je suis **Antoine Wang**.

J’aide les profils techniques à maîtriser l’architecture de Microsoft Fabric, et j’aide les décideurs à comprendre l’impact réel de cette technologie, sans le jargon inutile.

Mon objectif ? Vulgariser le complexe et vous donner les clés pour maîtriser Microsoft Fabric, une plateforme de données SaaS unifiée et alimentée par l’IA pour simplifier la gestion des données et l’analyse.

Cette newsletter est 100% gratuite. En vous abonnant maintenant, vous recevrez en exclusivité mon “One-Pager” pour cartographier l’ensemble de la solution Fabric en un coup d’œil.

Merci à celles et ceux qui me suivent depuis le début. Sans plus attendre, entrons dans le vif du sujet !

---

Bienvenue dans cette nouvelle édition. Aujourd’hui, on s’attaque au problème de l’ingestion de données dans la plateforme moderne Microsoft Fabric.

Trop de choix tue le choix.

Si vous avez ouvert votre workspace récemment, vous l’avez sûrement remarqué : le menu des outils pour ingérer les données s’allonge à chaque mise à jour.

*Vous voulez déplacer de la donnée ?*

Fabric vous propose désormais : Data Pipeline, Dataflow Gen2, Notebook, mais aussi Copy Job, Eventstream ou même Apache Airflow...

Résultat ? On passe plus de temps à se demander *quel* outil utiliser qu’à réellement construire le flux.

> C’est la question qui revient le plus : *“Antoine, je dois juste charger un CSV, est-ce que je dois vraiment monter un Pipeline ?”*

Aujourd’hui, on tranche. Je vous donne tous les éléments pour faciliter votre prise de décisions sur les possibilités ainsi que la Matrice de Décision définitive.

---

### 1. Les “Classiques” (Le trio de base)

C’est ici que se joue 90% de votre architecture. Il ne faut pas les voir comme des concurrents, mais comme des outils avec des “personnalisations” différentes.

#### a. Data Pipelines : Le Chef d’Orchestre

La Data Pipeline est le moteur d’orchestration et de flux de travail (workflow) de Microsoft Fabric. Sa mission n’est pas de transformer la donnée en profondeur, mais de piloter l’ensemble du cycle de vie de l’information. Elle agit comme un chef d’orchestre qui définit l’ordre, la fréquence et les conditions d’exécution de toutes les autres tâches (Copy Jobs, Notebooks, Dataflows).

* **Orchestration Logique :** Elle permet de créer des séquences intelligentes. Par exemple : *“Lance la copie des données ; si elle réussit, exécute le Notebook de nettoyage ; si elle échoue, envoie une notification Teams.”*
* **Déplacement de Données (Copy Activity) :** Elle intègre un moteur de copie ultra-performant capable de se connecter à différentes sources (On-premises, Cloud, SaaS) pour ramener les données brutes dans le OneLake.
* **Gestion des Dépendances et Planification :** C’est ici que l’on gère le calendrier (Scheduling) ou les déclenchements basés sur des événements. Elle permet de surveiller et de reprendre les flux en cas d’erreur.
* **Contrôle de Flux Avancé :** Elle offre des outils de logique programmatique visuelle : boucles (ForEach), conditions (If/Else), variables et paramètres, rendant les flux dynamiques et réutilisables.

**La Réalité du Terrain :**

* Performance : L’activité Copy Data est un moteur optimisé pour le déplacement de blocs binaires. C’est souvent 2 à 3 fois plus rapide qu’un Dataflow pour la même tâche.
* Coût (CU) : C’est l’option la plus économe en Capacity Units.
* Destinations : Les Pipelines brillent par leur polyvalence en sortie. Ils proposent plus de 40 destinations possibles (Azure SQL, Lakehouse, Warehouse, KQL, etc.), là où les destinations des Dataflows Gen2 restent encore assez restreintes.
* Connectivité : Avec un catalogue d’environ 60+ connecteurs natifs, les Pipelines sont plus limités que les Dataflows Gen2 en entrée. Si votre source est un outil SaaS très spécifique, vous pourriez ne pas l’y trouver.

**Mon conseil** : Considérez le Data Pipeline comme la colonne vertébrale de votre orchestration. Son rôle est d’assurer l’ingestion massive et économique de vos données brutes (SQL, Cloud, On-premises) vers le Lakehouse (zone Bronze). C’est le chef d’orchestre indispensable pour séquencer vos flux, déclencher vos transformations (Notebooks, Dataflows Gen2) et piloter vos alertes opérationnelles.

#### b. Dataflow Gen2 : ETL Low-code

C’est Power Query dans le cloud. C’est l’outil de prédilection pour le Low-Code ETL : il permet d’ingérer, de nettoyer et de charger des données une interface visuelle intuitive. Grâce à son moteur de calcul scale-out, il traite des volumes importants sans nécessiter de compétences en Python ou Spark, tout en offrant une intégration transparente avec le reste de l'écosystème Fabric.

**La Réalité du Terrain :**

* Connectivité : Il se connecte à tout (c’est lui qui a le plus de connecteurs natifs).
* Coût & Performance : les Dataflows Gen2 viennent de recevoir une mise à jour majeure.

  + Le Modern Evaluator : Microsoft a intégré un nouveau moteur (.NET 8) qui permet des gains de temps de 20 à 30%.
  + Nouveau modèle de facturation : Le coût en CUs baisse désormais drastiquement après les 10 premières minutes d’exécution (passant de 12 à 1.5 CUs/sec). Plus le flux est long, plus il devient “rentable”.
* L’Upsert : L’Incremental Refresh est basé sur des fenêtres de temps. Ce n'est pas un vrai "Merge". Pour des dédoublonnages complexes, passez sur un Notebook.
* Le bémol de la consommation : Ne vous détrompez pas, cela reste l’item le plus “cher” en CUs. La consommation peut varier de manière imprévisible pour un même flux.
* La limite du Volume : Pour des petits jobs, le Dataflow est imbattable en rapidité de mise en place. Mais dès que le volume grimpe, l’écart de coût avec la Pipeline (2 à 3 fois moins chère) devient impossible à ignorer.

**Mon conseil :** utilisez la Pipeline pour l'orchestration globale et le déplacement de masse au moindre coût, et le Dataflow Gen2 pour vos transformations complexes en mode Low-Code.

#### c. Notebooks (Spark)

Le Notebook est bien plus qu'un simple éditeur de code ; c'est le moteur de calcul à haute performance de Fabric. Propulsé par Apache Spark, il est indispensable pour le traitement de volumes massifs (Big Data) et les transformations complexes que le Low-code ne peut pas gérer efficacement. S'il offre une flexibilité totale en Python (PySpark), Scala ou SQL, son véritable atout réside dans sa capacité à industrialiser le Machine Learning et à optimiser les performances de votre Lakehouse via le format Delta.

**La Réalité du Terrain :**

* Le Roi du “Merge” : Là où le Dataflow galère, le Notebook brille. Faire un MERGE (Upsert) pour gérer les doublons ou l’historisation est trivial et ultra-rapide en PySpark ou SQL (format Delta).
* Économie de CUs imbattable : De toutes les analyses, le Notebook est l’item le moins “coûteux” en CUs pour les gros traitements. C’est l’option la plus efficiente énergétiquement.
* Flexibilité totale : Vous n’êtes jamais limité par un connecteur ou une interface. Si l’API existe, le Notebook peut l’atteindre.
* Ne tombez pas dans le piège de la technologie “tendance” juste pour le plaisir de coder. Posez-vous ces questions :

  + La cohérence de l’équipe : Est-ce que tout le monde comprend le code ? Pouvez-vous diagnostiquer une erreur rapidement à plusieurs, ou dépendez-vous d’un seul expert ?
  + Le coût d’entrée : Est-ce que passer 10 heures à coder un Notebook Python apporte réellement plus de valeur au business que 10 minutes de configuration dans un Dataflow ?

**Mon conseil :** Ne voyez pas le Notebook comme un outil réservé aux "geeks", mais comme le moteur de performance de votre plateforme. C’est l’environnement de code par excellence (PySpark, SQL, Scala) qui prend le relais là où le Low-code atteint ses limites. Utilisez-le pour transformer des volumes massifs de données à une vitesse que seul un cluster Spark peut offrir, ou pour injecter de l'intelligence artificielle (Azure OpenAI) directement dans vos flux.

---

### 2. Les “Spécialistes” (Les outils que vous oubliez peut-être)

Maintenant, voyons voir les plus spécialisés en fonction des besoins. Microsoft a ajouté des outils pour des cas précis où le trio de base n’est pas optimal.

#### a. Eventstream : Le “Maître du Temps Réel”

L’**Eventstream** est la tour de contrôle de Microsoft Fabric dédiée à l’ingestion et au traitement des données en temps réel. Contrairement aux outils classiques qui déplacent des fichiers ou des tables par intervalles (Batch), Eventstream capture des flux d’événements à la milliseconde près, les transforme “au vol” et les distribue instantanément vers plusieurs destinations.

Utilisez-le pour capter des événements instantanés, que ce soit des logs de serveurs, des données IoT (capteurs) ou des transactions e-commerce.

* Il est conçu pour encaisser des volumes massifs de données provenant de sources variées : capteurs IoT, logs d’applications, flux de clics (clickstream) ou encore le CDC (Change Data Capture) qui transforme les modifications de vos bases SQL en flux d’événements.
* C’est un véritable moteur d’ETL temps réel. Sans écrire de code, vous pouvez filtrer les données inutiles, agréger des valeurs (ex: moyenne de température par minute) ou transformer les formats de données avant même qu’elles ne touchent le disque.
* Un seul flux entrant peut être envoyé simultanément vers le OneLake (pour l’historique), une base KQL (pour l’analyse de logs) ou l’Activator (pour déclencher une alerte immédiate sur Teams ou par mail).

**Mon conseil:** Ne simulez pas du temps réel en lançant un Pipeline toutes les minutes, c’est coûteux. Si vous avez besoin de voir la donnée bouger en moins d’une seconde, c’est Eventstream.

#### b. Copy Job : L’Ingestion Haute Performance

C’est l’outil qui permet une expérience simplifiée et optimisée qui se concentre sur une seule mission : déplacer des données d’un point A (SQL, S3, ADLS, …) vers un point B (Lakehouse, …) le plus vite possible.

* Expérience Simplifiée : Il propose une interface guidée qui permet de configurer une copie en quelques secondes. C’est l’outil idéal pour les tâches d’ingestion ponctuelles ou récurrentes qui ne nécessitent pas de logique d’orchestration particulière.
* Performance Brute : Sous le capot, il utilise le même moteur de mouvement de données haute performance que les Pipelines, mais avec moins de “couches” logicielles. Il est taillé pour maximiser le débit (throughput) et réduire le temps de transfert des gros volumes.
* Ingestion “As-Is” : Sa philosophie est de ramener la donnée telle quelle vers la zone Bronze. Il ne fait pas de transformation complexe, garantissant ainsi une fidélité totale entre la source et le OneLake.
* Maintenance Allégée : Une fois configuré, il s’exécute de manière autonome avec son propre monitoring, sans polluer vos orchestrateurs de workflows plus globaux.
* Le + : Support des chargements incrémentaux de manière native et ultra-légère.

**Mon conseil** : Ne sortez pas l'artillerie lourde d'une Pipeline complexe si votre seul besoin est de déplacer des volumes massifs de données sans logique métier. Le Copy Job est votre "voie rapide".

#### c. Apache Airflow Job : L’Orchestrateur Programmatique

L’Apache Airflow Job dans Microsoft Fabric est une instance entièrement managée du célèbre orchestrateur open-source. Contrairement aux Data Pipelines qui reposent sur une interface visuelle (Drag & Drop), Airflow permet de définir vos flux de données sous forme de code Python, appelés DAGs (Directed Acyclic Graphs).

* Le “Code-First” par excellence : Il s’adresse aux Data Engineers qui souhaitent versionner leurs workflows (Git), créer des pipelines dynamiques (boucles, conditions complexes) et manipuler des dépendances fines que l’interface visuelle ne permet pas.
* Une Interopérabilité Totale : Grâce à sa vaste bibliothèque de “Providers”, Airflow peut piloter des tâches au sein de Fabric (Notebooks, Pipelines) mais aussi interagir avec des services externes (AWS S3, Google BigQuery, Snowflake, APIs tierces, etc.).
* Zéro Gestion d’Infrastructure : Fabric s’occupe de toute la complexité opérationnelle. Vous n’avez pas à gérer de serveurs, de bases de données de métadonnées ou de mises à jour de version ; vous vous concentrez uniquement sur l’écriture de vos scripts d’orchestration.

**Mon conseil :** Si vos besoins dépassent le cadre visuel des Pipelines Fabric, tournez-vous vers l’Apache Airflow Job. C’est l’outil indispensable pour les architectures “Code-First”.

#### d. Shortcuts : Le “Zéro Copie” Intelligent

Le Shortcut est une fonctionnalité unique de Microsoft Fabric qui permet de virtualiser l’accès aux données. Au lieu de copier physiquement des fichiers d’un point A vers un point B, vous créez un lien direct (un pointeur) qui rend les données stockées ailleurs visibles et utilisables dans votre OneLake comme si elles y étaient réellement hébergées.

* Élimination de la Redondance (Single Source of Truth) : Les données ne sont pas dupliquées. Vous accédez à la version originale, ce qui garantit la cohérence des données et réduit drastiquement vos coûts de stockage.
* Interopérabilité Multi-Cloud : Les Shortcuts permettent de connecter instantanément des sources externes comme Amazon S3, Google Cloud Storage, Azure Data Lake Gen2, Sharepoint... Vos données AWS apparaissent dans votre Lakehouse Fabric sans aucun flux ETL.
* Performance Transparente : Les moteurs de calcul de Fabric (Spark, SQL, Power BI) lisent les données via le Shortcut avec une latence minimale, en utilisant les protocoles optimisés de OneLake.
* Unification du OneLake : Vous pouvez créer des Shortcuts entre différents Lakehouses ou Workspaces au sein de Fabric. Cela permet de briser les silos internes et de partager des données entre équipes sans mouvement de fichier.

#### e. Mirroring : La réplication en temps réel, sans code

Le **Mirroring** est une technologie de réplication de données “Cloud-native” qui permet de créer une copie conforme et synchronisée de vos **bases de données externes** directement dans Microsoft Fabric.

Contrairement à un ETL classique qui extrait les données par intervalles, le Mirroring utilise le Change Data Capture (CDC) pour répercuter chaque modification de la source vers le OneLake en quasi temps réel.

* Configuration “Zéro-ETL” : Vous ne créez pas de pipelines, pas de schémas, et vous n’avez pas à gérer les types de données. Vous connectez votre base (Azure SQL, Cosmos DB, Snowflake, MongoDB, etc.), et Fabric s’occupe de tout.
* Synchronisation Continue : Une fois activé, le miroir reste à jour automatiquement. Dès qu’une ligne est insérée ou modifiée dans votre base de production, elle est disponible dans Fabric en quelques secondes.
* Format Open Delta : Les données sont stockées au format Delta Parquet dans le OneLake. Cela signifie qu’elles sont immédiatement prêtes pour être l’objet de requêtes SQL, de scripts Spark ou de rapports Power BI en mode Direct Lake (vitesse maximale).
* Impact Minimal sur la Source : Le Mirroring est conçu pour lire les journaux de transactions des bases de données, ce qui évite de ralentir vos applications de production pendant la réplication.

> **En résumé :** Le Mirroring est le pont invisible entre le monde transactionnel (vos applications) et le monde analytique (Fabric). C’est la fin des projets d’ingestion complexes pour les bases de données supportées.

---

### 3. La Matrice de Décision : 3 Questions pour Trancher

Avant de cliquer sur le bouton “New Item”, passez votre besoin au crible de ces 4 questions. C’est votre filet de sécurité pour éviter la dette technique.

**Q1 : Quel est votre objectif prioritaire ? 🎯**

* Virtualiser sans bouger la donnée ? 👉 **Shortcut**.
* Ingérer massivement ? 👉 **Pipeline (Copy Activity)** ou **Copy Job**.
* Transformer visuellement ? 👉 **Dataflow Gen2**.
* Répliquer une BDD de prod sans ETL ? 👉 **Mirroring**.
* Agir en moins d’une seconde ? 👉 **Eventstream**.

**Q2 : Qui va maintenir le flux de données dans 6 mois ? 🛠️**

* Profil Analyste (No-Code) : 👉 **Dataflow Gen2**.
* Profil Engineer (Code-First) : 👉 **Notebook** (Python/Spark) ou **Airflow**.
* Besoin de simplicité absolue : 👉 **Copy Job** ou **Pipeline**.

---

### 4. Le Récapitulatif “Cheat Sheet”

Pour celles et ceux qui sont visuels, Microsoft a publié ce guide de décision officiel très complet sur le sujet et voici le tableau à garder sous le coude pour vos arbitrages :

📚 **Pour aller plus loin :** Je vous recommande vivement de le mettre en favori : 👉 **[Consulter le Guide de décision officiel Microsoft Fabric](https://learn.microsoft.com/fr-fr/fabric/data-factory/decision-guide-data-integration?toc=%2Ffabric%2Ffundamentals%2Ftoc.json&bc=%2Ffabric%2Ffundamentals%2Fbreadcrumb%2Ftoc.json)**

---

### 5. L'Astuce Navigation

On s’est penché sur la théorie, mais en pratique, l’interface de Fabric peut vite ressembler à un inventaire sans fin.

**Bonne nouvelle** **:** **Microsoft a uniformisé l’interface**.

Plus besoin de chercher dans quelle “expérience” se cache votre outil. Tout est désormais centralisé pour vous permettre de choisir en fonction de votre tâche :

1. Allez dans votre Workspace.
2. Cliquez sur le bouton “New Item” (Nouvel élément).
3. Dans la fenêtre qui s’ouvre, cliquez sur le filtre “Get Data” (ou “Obtenir des données”) dans la colonne de gauche.

**Boom !** Fabric filtre instantanément l’arsenal dédié à l’ingestion : Pipelines, Dataflows, Eventstreams, Copy Jobs... Tout est réuni au même endroit. C’est votre point de départ unique pour comparer les options et lancer votre flux en un clic.

---

### Conclusion

Pour résumer ma philosophie, retenez ceci : **La complexité est l’ennemi de la maintenance.**

Lors de la conception de votre architecture, analysez toujours le volume de données, la fréquence d’accès et le niveau d’automatisation requis.

* Virtualisez dès que possible avec les Shortcuts. Si la donnée est déjà dans le cloud, ne la déplacez pas.
* Répliquez sans effort avec le Mirroring pour vos bases de production. Évitez l’ETL manuel quand l’outil peut le faire pour vous.
* Industrialisez avec les Pipelines (Copy Activity) pour la performance brute et le contrôle des coûts.
* Valorisez avec les Dataflows Gen2 pour donner de l’autonomie au métier sur des transformations agiles.
* Optimisez avec les Notebooks dès que la complexité technique (comme l’Upsert) ou le volume l’exigent.

Ne choisissez pas l’outil qui vous flatte l’œil le premier jour, choisissez celui que votre équipe pourra maintenir sans douleur — et sans ruiner votre capacité Fabric — dans un an.

> Et vous, quel outil privilégiez-vous ? Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

### 📚 Ressources pour aller plus loin

Pour approfondir le sujet et affiner vos choix d’architecture, je vous recommande ces lectures essentielles :

* [Notebook in Microsoft Fabric](https://learn.microsoft.com/fr-fr/fabric/data-engineering/how-to-use-notebook)
* [Dataflow Gen2 in Microsoft Fabric](https://learn.microsoft.com/fr-fr/fabric/data-factory/dataflows-gen2-overview)
* [Data Pipelines in Microsoft Fabric](https://learn.microsoft.com/fr-fr/fabric/data-factory/pipeline-overview)
* [Copy Job in Microsoft Fabric](https://learn.microsoft.com/fr-fr/fabric/data-factory/what-is-copy-job)
* [Eventstream in Microsoft Fabric](https://learn.microsoft.com/fr-fr/fabric/real-time-intelligence/event-streams/overview)
* [Apache Airflow jobs in Microsoft Fabric](https://learn.microsoft.com/fr-fr/fabric/data-factory/apache-airflow-jobs-concepts)
* [Shortcut in Microsoft Fabric](https://learn.microsoft.com/fr-fr/fabric/onelake/onelake-shortcuts)
* [Mirroring in Microsoft Fabric](https://learn.microsoft.com/fr-fr/fabric/mirroring/overview)
