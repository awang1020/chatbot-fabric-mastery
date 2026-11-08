---
title: Activer Copilot dans Power BI : où passent vos données ?
url: https://blog.antoinewang-tech.com/p/copilot-power-bi-compliance-security-data-residency
date: 2026-11-03
author: Antoine Wang
source: substack
---

# Activer Copilot dans Power BI : où passent vos données ?

Hello les masters Fabric 👋

Avant d'ouvrir Copilot, votre RSSI pose la question qui fâche : les données utilisées par Copilot restent-elles dans la région ?

Pour répondre, il faut séparer trois sujets : qui peut utiliser Copilot (et depuis quelle application), où l’IA traite les données et quelles traces restent ensuite. C’est parti !

## ⚡ En 30 secondes

> **Ce qu’il faut retenir :**
>
> * **Europe, pas France.** Avec Azure OpenAI opéré par Microsoft, le traitement IA d’une capacité située dans l’EU Data Boundary reste dans cette frontière. Ce n’est pas une garantie « France uniquement ».
> * **Vos valeurs, pas seulement le schéma.** Copilot peut traiter des données réelles. Dans certains scénarios, votre question et son contexte restent 48 h en cache, notamment dans la région d’origine du tenant.
> * **Pas tous les interrupteurs.** Vérifiez qui a accès à Copilot, quel fournisseur d’IA est activé et quelles régions sont autorisées. « Processed outside » et « stored outside » n’ouvrent pas la même chose.

---

## C’est quoi, le traitement des données par Copilot ?

Copilot n’envoie pas votre question seule. Il l’enrichit d’un **contexte**, appelé *grounding* ou données d’ancrage, puis transmet le tout à un modèle de langage (LLM). Il transforme ensuite la réponse en texte, en DAX ou en contenu de rapport.

Ce contexte peut contenir des métadonnées, mais aussi des valeurs métier. Trois questions sont donc à traiter séparément :

1. 🔐 **Qui** peut utiliser Copilot, et depuis quelle application ? → sections 1 et 7
2. 🌍 **Où** partent vos données, et qui les traite ? → sections 2 à 5
3. 🗂️ **Quelles traces** restent après la réponse ? → section 6

---

## La réalité du terrain

### Etape 1. Activer Copilot : qui fait quoi, et dans quel ordre

**Les prérequis**

* ✅ Une Capacité payante **Fabric F2 ou supérieure**, ou **Power BI Premium P1 ou supérieure**, dans une région prise en charge.
* ✅ Ou une [Fabric Copilot Capacity](https://blog.antoinewang-tech.com/p/fabric-copilot-capacity-dedicated) **(FCC)**. Elle permet aux utilisateurs affectés d’utiliser Copilot avec des Workspaces Pro ou PPU. Elle centralise la consommation IA ; les requêtes sur le modèle sémantique restent à la charge de la Capacité de ce modèle.
* ❌ Une licence Pro ou PPU seule, ou une Capacité d’essai (Trial).
* ❌ Private Link ou un réseau fermé : selon la procédure Power BI, Copilot n’y est pas pris en charge à ce jour. Si cette contrainte est obligatoire, ne contournez pas votre architecture pour faire apparaître le bouton.

**L’activation, rôle par rôle**

1. **Administrateur Fabric** (portail d’administration > **Tenant settings** > **Copilot and AI**) :

   * vérifiez **Users can use Copilot and other features powered by Azure OpenAI**, activé par défaut ;
   * limitez le pilote à un groupe de sécurité Entra, puis sélectionnez **Apply**.

   Attention : ce réglage ouvre Copilot dans toutes les charges de travail Fabric, pas seulement dans Power BI.
2. **Administrateur de Capacité** : contrôlez les **Delegated tenant settings** et les groupes effectifs de chaque Capacité (Capacity settings > Fabric capacity > nom de la Capacité > Delegated tenant settings).
3. **Utilisateur du service Power BI** : vérifiez la Capacité du Workspace et vos droits.
4. **Créateur dans Power BI Desktop** : sans FCC, il vous faut un Workspace compatible où vous êtes Admin, Member ou Contributor. Desktop vous demande de le choisir au premier usage, et vous pouvez le changer ensuite dans ses paramètres. Le modèle de langage ne tourne pas sur votre poste.

Conséquence :

⚠️ **Couper Copilot au niveau du tenant ne suffit pas.** Le réglage est délégué automatiquement aux administrateurs de capacité, et l’administrateur du tenant ne peut pas désactiver cette délégation. Une capacité peut donc activer Copilot même si le tenant l’a désactivé. Le réglage hors zone, lui, reste désactivé et n’est pas délégué automatiquement.

Le **Copilot autonome**, qui cherche parmi plusieurs éléments, a son propre réglage : **Users can access a standalone, cross-item Copilot in Power BI experience (preview)**. Il exige que le réglage Azure OpenAI soit activé au niveau du tenant : l’activer au niveau d’une capacité ne suffit pas.

Conséquence:

### Etape 2. Quelles données partent réellement vers l’IA

Copilot ne récupère que les données auxquelles l’utilisateur a accès. Mais ce contexte va bien au-delà du schéma. Selon le *[fonctionnement documenté de Copilot dans Fabric](https://learn.microsoft.com/en-us/fabric/fundamentals/how-copilot-works)*, il peut contenir :

* l’historique de la session en cours ;
* des métadonnées, comme le schéma du modèle sémantique ou celles d’un visuel de rapport ;
* des points de données précis, comme ceux affichés dans un visuel ;
* des méta-prompts, c’est-à-dire des instructions ajoutées pour chaque expérience.

Pour une question de données, c’est encore plus net : le modèle produit d’abord une requête, évaluée sur le modèle sémantique, puis Copilot renvoie le résultat de cette requête à Azure OpenAI pour en obtenir un résumé. Et vous ne pouvez ni intercepter ni modifier ces données avant leur envoi.

Les [bonnes pratiques Prep Data for AI dans Power BI](https://blog.antoinewang-tech.com/p/microsoft-fabric-copilot-in-powerbi-desktop-prep-data-for-ai) améliorent ce contexte et la qualité des réponses. Elles ne remplacent pas le contrôle d’accès.

**Mon conseil :** qualifiez les données des réponses attendues, pas seulement les noms des tables. Un résultat agrégé reste une donnée métier à gouverner.

### Etape 3. Où sont-elles traitées : France, Europe ou ailleurs ?

**Réponse courte : en Europe, pas forcément en France.** Le service Azure OpenAI qui alimente Copilot dans Fabric est déployé dans des centres de données américains (East US, East US2, South Central US et West US) et dans l’EU Data Boundary.

Voici les correspondances documentées, selon la zone de votre Capacité :

* **Capacité aux États-Unis** = traitement aux États-Unis, sans sortie de zone. Action : activer Copilot.
* **Capacité dans l’EU Data Boundary**, comme France Central = traitement dans l’EU Data Boundary, sans sortie de zone. Action : activer Copilot.
* **Capacité au Royaume-Uni** = traitement dans l’EU Data Boundary, donc hors zone. Actions : activer Copilot et autoriser le traitement hors zone.
* **Australie, Brésil, Canada, Inde, Asie, Japon, Corée, Afrique du Sud, Émirats arabes unis** = traitement aux États-Unis, donc hors zone. Actions : activer Copilot et autoriser le traitement hors zone.

Hors des États-Unis et de l’EU Data Boundary, Copilot est d’ailleurs désactivé par défaut, tant que l’administrateur n’autorise pas ce traitement hors zone.

*Source : [disponibilité et flux géographiques de Copilot Fabric](https://learn.microsoft.com/en-us/fabric/fundamentals/copilot-fabric-overview#available-regions).*

**Une frontière n’est pas un datacenter.** L’EU Data Boundary ne promet ni un traitement dans la seule région France Central, ni un traitement exclusivement en France.

### Etape 4. Azure OpenAI ≠ OpenAI sous-traitant

Les noms se ressemblent, pas les flux. Fabric peut s’appuyer sur deux fournisseurs, chacun avec son propre réglage :

* **Azure OpenAI, opéré par Microsoft** : activé par défaut. Ce service n’utilise ni les services publics ni les API d’OpenAI, et OpenAI n’a pas accès à vos données.
* **OpenAI comme sous-traitant de Microsoft** : désactivé par défaut. L’activer peut faire sortir vos données de la frontière de conformité de Fabric, vers un système tiers dont les contrôles de conformité peuvent être moins stricts. Ces modèles restent inclus dans l’EU Data Boundary, sauf exceptions précisées dans sa documentation.

⚠️ Une exception compte : avec les modèles opérés par OpenAI dans les Microsoft Generative AI Services, un **identifiant utilisateur pseudonymisé** est traité et stocké aux États-Unis, pour des finalités opérationnelles et de sécurité. Selon la *[documentation EU Data Boundary](https://learn.microsoft.com/en-us/privacy/eudb/eu-data-boundary-ongoing-partial-transfers#openai-operated-models-with-microsoft-generative-ai-services)*, les autres données concernées sont traitées dans l’EU Data Boundary et ne sont pas stockées par OpenAI.

Le réglage s'appelle **Users can use Copilot, AI Agents and other AI experiences powered by OpenAI as a Microsoft Subprocessor :**

**Mon conseil :** gardez le sous-traitant désactivé si le périmètre validé est Azure OpenAI. Certaines fonctionnalités ou certains modèles peuvent n’être disponibles qu’avec lui : son ouverture doit donc être une décision contractuelle explicite, pas une case cochée pour débloquer un écran.

### Etape 5. « Processed outside » ≠ « stored outside »

Les libellés sont presque identiques. Le verbe change le périmètre :

* **Data sent to Azure OpenAI can be processed outside your capacity’s geographic region, compliance boundary, or national cloud instance** : l’IA peut **traiter** vos données hors de la zone de votre Capacité. C’est le réglage hors zone (cross-geo) de la section 3.
* **Data sent to Azure OpenAI can be stored outside your capacity’s geographic region, compliance boundary, or national cloud instance** : l’historique de conversation peut être **stocké** hors de votre zone. Ce réglage concerne Copilot dans les notebooks et les agents de données Fabric, qui conservent cet historique d’une session à l’autre. Si l’utilisateur ne l’efface pas, il est gardé 28 jours.

Un troisième réglage, **Data sent to OpenAI as a Microsoft Subprocessor can be processed outside…**, fait la même chose pour les modèles opérés par OpenAI, pas pour Azure OpenAI.

Les trois sont désactivés par défaut. Surtout, ils ne s’appliquent qu’aux capacités situées hors de l’EU Data Boundary et des États-Unis.

💡 **Mon conseil :** si toutes vos Capacités sont dans l’EU Data Boundary, ces réglages ne vous concernent pas : laissez-les désactivés. Si vous en activez un, par exemple pour une Capacité au Royaume-Uni, documentez pourquoi.

### Etape 6. Fin de session ≠ Aucune trace

En règle générale, Copilot ne se souvient pas de l’historique des sessions précédentes et ne l’utilise pas. Mais il reste des traces, à plusieurs endroits :

* **Un cache de 48 heures** : dans certains scénarios, Copilot met en cache votre prompt et les données d’ancrage pendant 48 heures. Ce cache se trouve à deux endroits : dans le **navigateur de l’utilisateur**, et dans un premier cache côté serveur, situé dans la **région d’origine** (**home region**) **du tenant** et conservé à des fins d’audit. Rien n’est mis en cache dans le service Azure OpenAI ni là où se trouvent les GPU.
* **L’historique des expériences conversationnelles** (Copilot dans les notebooks, agents de données) : 28 jours par défaut, voir la section 5.
* **Les journaux Purview**, si vous les configurez (voir plus bas).

⚠️ **Le cache serveur suit le tenant, pas forcément votre Capacité.** Pour connaître la région d’origine de votre tenant : **Help > About > Your home region is**.

Côté Purview, l’option **Allow Microsoft Purview to secure AI interactions** du portail d’administration Fabric est activée par défaut. Cela ne prouve pas que la collecte et la rétention sont configurées.

Vérifiez trois points :

* une stratégie de collecte, comme **DSPM for AI – Capture interactions for Copilot experiences**, pour capturer prompts et réponses ;
* une stratégie de rétention sur l’emplacement **Microsoft Copilot Experiences** ;
* la facturation à l’usage (pay-as-you-go), requise pour gérer ces interactions avec Purview.

Prompts et réponses sont aussi capturés dans le journal d’audit unifié. Ils sont stockés dans la boîte aux lettres de l’utilisateur, ce qui permet de les retrouver avec eDiscovery.

### Etape 7. Droit de lecture ≠ destination

Copilot utilise les droits de l’utilisateur, sans permission supplémentaire : il respecte les rôles de workspace, les permissions sur les éléments et la sécurité des données. Mais **la RLS et l’OLS ne s’appliquent pas aux rôles Admin, Member ou Contributor** d’un Workspace, qui ont des droits d’édition. Testez donc les parcours lecteurs avec un compte Viewer.

Deux réflexes à oublier :

* **Masquer une colonne** : Copilot ignore bien les objets masqués, mais ce n’est pas une règle de sécurité.
* **Compter sur un filtre de page** : ce n’est pas une RLS. Microsoft précise que les filtres du rapport ne s’appliquent pas aux questions de données posées à Copilot.

C’est **la sécurité du modèle** qui doit porter la restriction.

Reste la destination : la RLS limite ce qu’un utilisateur lit, pas l’endroit où partent ensuite les résultats. Or vos données peuvent être interrogées depuis plusieurs applications.

**Depuis quelle application ?**

* **Service Power BI ou Fabric** (navigateur) : Capacité du Workspace ou FCC.
* **Power BI Desktop** : un Workspace compatible, ou une FCC.
* **Application mobile Power BI** : le rapport doit se trouver dans un workspace pris en charge, avec Copilot activé.
* **Copilot autonome** : son réglage active aussi l’agent Power BI dans Microsoft 365.
* **Agents de données Fabric** : une fois publiés, ils peuvent être utilisés depuis Microsoft 365 Copilot, Copilot Studio, Microsoft Foundry ou n’importe quel client MCP. Ce sont des utilisateurs qui les y connectent, pas forcément un administrateur. Leurs réponses peuvent alors sortir de la frontière de conformité ou de la zone géographique de Fabric, et suivent les règles du service qui les reçoit.
* **Copilot Chat et Copilot Cowork, via Fabric IQ** : Copilot peut chercher les rapports Power BI pertinents et utiliser leurs modèles sémantiques pour répondre. Dans Cowork, le plugin Fabric IQ est installé par défaut. Les droits de l’utilisateur s’appliquent, RLS et OLS comprises. Une licence Microsoft 365 Copilot Premium est requise.

⚠️ Point d’attention sur le dernier point, sur **Copilot Chat et Cowork :**

* **Le réglage principal est dans Microsoft 365.** Le réglage **Fabric data available in M365 Copilot**, dans le centre d’administration Microsoft 365, est activé par défaut. L’utilisateur n’a pas besoin d’accès à Copilot dans Fabric. Et contrairement à Copilot dans Fabric, les workspaces Pro et PPU sont pris en charge.
* **L’EU Data Boundary tient, sauf avec Anthropic.** Pour un client européen, Microsoft Copilot est un service EU Data Boundary. Mais les modèles Anthropic en sont actuellement exclus. Ils sont désactivés par défaut dans l’EU Data Boundary et au Royaume-Uni. Un administrateur peut toutefois les activer, et Cowork peut alors les utiliser.
* **Les données sortent ensuite de Power BI.** Cowork peut réutiliser une réponse dans un e-mail, un document ou une réunion. Or la DLP n’y est pas encore prise en charge.

💡 **Mon conseil :** avant de publier un agent de données, décidez où il a le droit d'être utilisé. Soyez particulièrement vigilant avec le serveur MCP : il accepte n'importe quel client. Associez l’administrateur Microsoft 365 à votre revue. Les réglages **Fabric data available in M365 Copilot** et **AI providers operating as Microsoft subprocessors** font partie de votre périmètre Power BI.

---

### **✅** Checklist avant d’ouvrir Copilot

* ☐ Capacité F2+/P1+ (ou FCC) dans une région prise en charge, sans Trial ni Private Link
* ☐ Réglage Azure OpenAI limité à un groupe pilote
* ☐ Délégations vérifiées sur chaque Capacité
* ☐ Copilot autonome : décision explicite
* ☐ Sous-traitant OpenAI désactivé, sauf décision contractuelle
* ☐ « Processed outside » et « stored outside » désactivés, sauf pour une Capacité hors EU Data Boundary et hors États-Unis
* ☐ Région d’origine du tenant notée (Help > About)
* ☐ Purview : collecte, rétention et facturation à l’usage configurées
* ☐ Canaux ouverts listés et testés avec un compte Viewer
* ☐ Agents de données : services autorisés validés avant publication (Microsoft 365, Copilot Studio, Foundry, MCP)
* ☐ Microsoft 365 : réglage Fabric data available in M365 Copilot et sous-traitant Anthropic vérifiés

---

## 🥇 La Règle d’Or

**Si vous ne devez retenir qu’une chose : activer Copilot ouvre l’accès, mais la résidence des données se vérifie ailleurs (fournisseur, régions autorisées, cache et rétention).**

Pour revenir à la question de départ : avec Azure OpenAI opéré par Microsoft et sans autorisation hors zone, le traitement IA de votre Capacité « France Central » reste dans l’EU Data Boundary, sans garantie « France uniquement ». Et dans certains scénarios, le cache suit la région d’origine du tenant.

Séparer ces sujets donne au métier un périmètre clair, et à vos admins des contrôles vérifiables.

Et chez vous, qu’est-ce qui bloque encore ?

Répondez simplement à cet email ou ce post, je lis tous vos messages.

Bon mardi et à la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [Fabric Copilot Capacity : isoler la consommation IA](https://blog.antoinewang-tech.com/p/fabric-copilot-capacity-dedicated) — la centralisation des coûts, distincte du lieu de traitement.
* [RLS Power BI ou OneLake Security : choisir la frontière](https://blog.antoinewang-tech.com/p/rls-dans-power-bi-ou-dans-onelake) — les contrôles de lecture avant d’ajouter un consommateur IA.
* [Tenant, Workspace, Capacity : les fondamentaux Fabric](https://blog.antoinewang-tech.com/p/tenant-workspace-capacity-licence) — les périmètres administratifs de votre déploiement.

---

## 📚 Ressources pour aller plus loin

Pour approfondir le sujet et affiner vos choix d’architecture, je vous recommande ces lectures essentielles issues de la documentation officielle :

* 🛠️ [Activer Copilot pour Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-enable-power-bi) — service, Desktop et délégation.
* 🛠️ [Paramètres Copilot et agents du tenant](https://learn.microsoft.com/en-us/fabric/admin/service-admin-portal-copilot) — portée des autorisations et historique intersessions.
* 📘 [Comment Copilot dans Fabric fonctionne](https://learn.microsoft.com/en-us/fabric/fundamentals/how-copilot-works) — grounding, cache, appels IA et restitution.
* 📘 [Disponibilité régionale et flux géographiques de Copilot](https://learn.microsoft.com/en-us/fabric/fundamentals/copilot-fabric-overview#available-regions) — zones de traitement.
* 📘 [OpenAI comme sous-traitant dans Fabric](https://learn.microsoft.com/en-us/fabric/fundamentals/copilot-openai-subprocessor) — opérateur, engagements et exclusions.
* 🔗 [Gouverner Copilot Fabric avec Microsoft Purview](https://learn.microsoft.com/en-us/purview/ai-copilot-fabric) — audit, collecte et rétention.
