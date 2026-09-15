---
title: Fabric Copilot Capacity (FCC) : le guide 2026 pour activer Copilot sans throttling
url: https://blog.antoinewang-tech.com/p/fabric-copilot-capacity-dedicated
date: 2026-07-14
author: Antoine Wang
source: substack
---

# Fabric Copilot Capacity (FCC) : le guide 2026 pour activer Copilot sans throttling

Bonjour à tous, je suis **Antoine Wang**.

J’aide les profils techniques à maîtriser l’architecture de Microsoft Fabric, et j’aide les décideurs à comprendre l’impact réel de cette technologie.

Mon objectif ? Vulgariser le complexe et vous donner les clés pour maîtriser Microsoft Fabric, une plateforme de données SaaS unifiée et alimentée par l’IA pour simplifier la gestion des données et l’analyse.

🆕 **Nouveauté pour les lecteurs** : j’ai créé **Ask Fabric Mastery**, un assistant IA qui répond à vos questions sur Microsoft Fabric & Power BI en s’appuyant uniquement sur les 28 éditions de cette newsletter. Réponses sourcées, sans hallucination, avec un lien direct vers l’édition d’origine.

👉 **Testez-le maintenant** : [ask-fabric-mastery](http://awang1020.github.io/ask-fabric-mastery)  
🔑 **Code d’accès (ce code est réservé aux abonnés Fabric Mastery) :**

Cette newsletter est 100% gratuite. En vous abonnant maintenant, vous recevrez en exclusivité mon “One-Pager” pour cartographier l’ensemble de la solution Fabric en un coup d’œil.

Merci à celles et ceux qui me suivent depuis le début. Sans plus attendre, entrons dans le vif du sujet !

---

Vous avez sûrement entendu parler de Copilot dans Fabric : meilleure productivité, accès rapide à l’information dans les rapports, génération de mesures DAX en langage naturel... Le pitch est convaincant.

Mais sur le terrain, je vois régulièrement des équipes Data bloquer le déploiement à grande échelle, non pas parce que la fonctionnalité déçoit, mais parce que personne ne sait répondre clairement à cette question : *qui absorbe la consommation en CU de Copilot, et sur quelle capacité ?*

Si vos pipelines de données, vos notebooks Spark et vos rafraîchissements de modèles sémantiques tournent sur la même capacité que vos utilisateurs Power BI, activer Copilot sans garde-fou, c’est ajouter une charge non planifiée sur une infrastructure déjà dimensionnée au plus juste. Le risque de throttling n’est pas théorique : il arrive, très sûrement, et il perturbe exactement les traitements que vous ne voulez pas voir s’arrêter.

La **Fabric Copilot Capacity (FCC)** est la réponse structurelle à ce problème.

---

## De quoi parle-t-on ?

La Fabric Copilot Capacity est une brique de configuration qui vous permet de désigner une capacité Fabric comme capacité dédiée au Copilot. Une fois configurée, la consommation Copilot de vos utilisateurs assignés est **dirigée vers cette capacité dédiée**, et non vers la capacité du workspace où se trouve leur contenu.

En clair : votre capacité de production n’absorbe plus les requêtes IA de vos cinquante analystes qui interrogent leurs rapports en langage naturel.

Depuis avril 2025, cette fonctionnalité est accessible à partir d’une capacité de SKU F2, la plus petite capacité Fabric disponible.

---

## **1️⃣** Le problème que FCC résout concrètement

Historiquement, pour qu’un utilisateur Power BI accède à Copilot, il fallait que son workspace soit hébergé sur une capacité Premium (P1 ou supérieur, ou F64 minimum).

Résultat : les équipes qui avaient des workspaces Pro ou PPU n’avaient tout simplement pas accès à Copilot, même si l’organisation disposait d’une capacité Fabric ailleurs.

FCC résout ce problème en permettant aux administrateurs de capacité d’accorder un accès direct à Copilot, sans avoir à migrer le contenu vers un workspace Premium.

Vos utilisateurs gardent leurs workspaces Pro. Vous leur donnez accès à Copilot via la FCC. Aucun déménagement d’artefacts.

---

## 2️⃣ Les scénarios couverts

Une fois un utilisateur assigné à une Fabric Copilot Capacity, sa consommation Copilot est facturée sur cette capacité dédiée dans ces cas précis :

* Copilot dans Power BI Desktop
* Copilot dans Power BI Service (workspaces Pro, PPU, ou Fabric capacity)
* Copilot sur les workloads Fabric (Data Factory, Data Engineering, Data Warehouse, Data Science, Real-Time Analytics, Activator) pour les capacités inférieures à F64
* Data Agents sur les capacités inférieures à F64

💡 **Astuce** : Si vous êtes déjà sur une capacité F64 ou supérieure, la FCC est moins critique pour les workloads Fabric (la capacité gère déjà Copilot nativement). Son intérêt est maximal pour isoler les usages Power BI Pro/PPU et pour les petites capacités de production.

---

## 3️⃣ Le modèle de coût qui change tout

Cela signifie que si vous êtes sur une licence Pro ou PPU, vous pouvez activer Copilot pour votre organisation pour moins de 300 dollars par mois en démarrant une F2 et en la désignant comme Fabric Copilot Capacity dédiée.

La logique économique est simple :

* Vous achetez une petite capacité (F2 à F64 selon le volume d’usage Copilot attendu)
* Vous la désignez comme FCC
* Toute la consommation IA de vos utilisateurs assignés remonte sur cette capacité
* Votre capacité de production reste préservée pour ses vraies charges : ingestion, transformation, rafraîchissements

La consommation Copilot dans Power BI impacte votre capacité Fabric disponible, si elle n’est pas isolée, une surconsommation peut conduire au throttling et perturber vos autres opérations Fabric.

C’est exactement le risque que FCC supprime.

---

## 4. La configuration : 3 étapes, pas plus

Le déploiement d’une FCC implique deux rôles distincts : l’administrateur Fabric et l’administrateur de capacité. Ne les confondez pas : chacun intervient à une étape spécifique, et l’ordre est important.

#### Étape 1 : L’administrateur Fabric active Copilot pour l’organisation

Dans le portail d’administration Fabric, sous Copilot and Azure OpenAI Service, activez le paramètre **“Users can use Copilot and other features powered by Azure OpenAI”**. Ce paramètre est activé par défaut sur les nouveaux tenants, mais vérifiez qu’il ne soit pas désactivé manuellement dans votre environnement.

#### Étape 2 : L’administrateur Fabric autorise la désignation d’une FCC

Dans ce même groupe de paramètres, activez **“Capacities can be designated as Fabric Copilot capacities”**. Ce paramètre est **désactivé par défaut** — c’est souvent là que le déploiement bloque sans que l’on comprende pourquoi. Sans cette étape, l’administrateur de capacité ne verra pas l’option de désignation FCC dans ses paramètres. Vous pouvez restreindre cette autorisation à des groupes de sécurité spécifiques plutôt qu’à toute l’organisation.

#### Étape 3 : L’administrateur de capacité assigne les utilisateurs à la FCC

Une fois la capacité désignée comme FCC, l’administrateur de capacité accède aux **Capacity settings** et assigne les groupes d’utilisateurs autorisés à utiliser cette capacité pour leur consommation Copilot. À partir de là, aucune action supplémentaire n’est requise côté utilisateur, le routage de facturation est transparent.

**💡 Tips :** Créez un groupe de sécurité dans votre Entra ID et assignez ce groupe directement à la Fabric Copilot Capacity dans le portail d'administration. Ils pourront utiliser l'IA partout, sans que vous n'ayez besoin de migrer le moindre rapport vers une nouvelle capacité physique.

---

## ⚠️ Points de vigilance

* **La région.** La Fabric Copilot Capacity n’est supportée que dans la région d’accueil du tenant Fabric. Si votre tenant est hors US/France, vérifiez le paramètre de traitement des données hors région avant tout déploiement.
* **Un seul FCC par utilisateur.** Si un utilisateur est assigné à plusieurs Copilot capacities, c’est la plus récemment créée qui enregistre son usage. Évitez les configurations ambiguës dans vos groupes de sécurité.
* **Les Fabric AI functions ne sont pas concernées.** FCC ne couvre pas les AI functions (les transformations IA natives dans les notebooks et dataflows). Ce sont deux mécanismes distincts.
* **Les capacités Embedded sont exclues.** Les SKUs de type A1, A2, EM1 dédiés à l’embedding externe ne sont pas compatibles. FCC ne fonctionne qu’avec les capacités F-type et P-type.

---

## **✅** Conclusion

**Si tu dois retenir une chose :** La Fabric Copilot Capacity ne supprime pas la consommation de Copilot, elle l’isole. Sans elle, vous choisissez entre priver vos utilisateurs Pro/PPU d’un accès à Copilot, ou accepter que l’IA grignote votre capacité de production au moment le moins opportun.

Mais isoler la consommation ne dispense pas de la surveiller.

La **Fabric Capacity Metrics App** reste votre meilleur allié une fois la FCC en production. En analysant l’onglet *Item history* de votre FCC, vous pouvez identifier précisément quels rapports et quels workspaces génèrent le plus de consommation Copilot et agir en conséquence : dimensionner la capacité à la hausse, restreindre l’accès à certains groupes, ou simplement comprendre qui utilise vraiment la fonctionnalité avant de la déployer plus largement.

> Et vous, comment avez-vous structuré l’accès Copilot dans votre organisation ? Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [Fabric Data Agent vs Copilot : les 3 différences qui comptent en 2026](https://blog.antoinewang-tech.com/p/microsoft-fabric-data-agent-copilot)
* [Microsoft Fabric : Comment surveiller votre capacité comme un Pro ?](https://blog.antoinewang-tech.com/p/capacity-metrics-fabric)
* [Power BI : Fini la page blanche avec Copilot](https://blog.antoinewang-tech.com/p/microsoft-fabric-copilot-powerbi)

---

## **📚** Ressources pour aller plus loin

📘 [Fabric Copilot Capacity — Documentation officielle Microsoft](https://learn.microsoft.com/en-us/fabric/enterprise/fabric-copilot-capacity)

🛠️ [Activer Copilot dans Fabric — Guide administrateur](https://learn.microsoft.com/en-us/fabric/fundamentals/copilot-enable-fabric)

🛠️ [Activer Copilot pour Power BI — Prérequis et configuration](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-enable-power-bi)

📘 [Vue d’ensemble de Copilot dans Fabric](https://learn.microsoft.com/en-us/fabric/fundamentals/copilot-fabric-overview)

🔗 [Updates to Fabric Copilot Capacity — Blog Microsoft Fabric](https://blog.fabric.microsoft.com/en-US/blog/updates-to-fabric-copilot-capacity/)
