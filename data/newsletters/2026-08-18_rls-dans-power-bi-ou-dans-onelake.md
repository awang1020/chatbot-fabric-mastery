---
title: Microsoft Fabric RLS : Settings in Power BI or OneLake Security ?
url: https://blog.antoinewang-tech.com/p/rls-dans-power-bi-ou-dans-onelake
date: 2026-08-18
author: Antoine Wang
source: substack
---

# Microsoft Fabric RLS : Settings in Power BI or OneLake Security ?

Bonjour à tous, je suis **Antoine Wang**.

J’aide les profils techniques à maîtriser l’architecture de Microsoft Fabric, et j’aide les décideurs à comprendre l’impact réel de cette technologie.

Mon objectif ? Vulgariser le complexe et vous donner les clés pour maîtriser Microsoft Fabric, une plateforme de données SaaS unifiée et alimentée par l’IA pour simplifier la gestion des données et l’analyse.

🆕 **Nouveauté pour les lecteurs** : j’ai créé **Ask Fabric Mastery**, un assistant IA qui répond à vos questions sur Microsoft Fabric & Power BI en s’appuyant uniquement sur les 33 éditions de cette newsletter. Réponses sourcées, sans hallucination, avec un lien direct vers l’édition d’origine.

👉 **Testez-le maintenant** : [ask-fabric-mastery](http://awang1020.github.io/ask-fabric-mastery)  
🔑 **Code d’accès (ce code est réservé aux abonnés Fabric Mastery) :**

Cette newsletter est 100% gratuite. En vous abonnant maintenant, vous recevrez en exclusivité mon “One-Pager” pour cartographier l’ensemble de la solution Fabric en un coup d’œil.

Merci à celles et ceux qui me suivent depuis le début. Sans plus attendre, entrons dans le vif du sujet !

---

## ⚡ En 30 secondes

Ce qu’il faut retenir :

* Le RLS filtre les **lignes** **d’une table** pas les objets (tables, colonnes, mesures : ça, c’est l’OLS). Et il vit désormais à deux endroits.
* **RLS dans le modèle sémantique Power BI** : mature, dynamique (par utilisateur), mais il ne protège que Power BI.
* **RLS dans OneLake Security** : une seule définition, appliquée partout (Spark, SQL analytics endpoint, Direct Lake, moteurs tiers autorisés). En Direct Lake on OneLake, les deux se combinent, Power BI ne peut que restreindre ce qu’OneLake autorise.

---

## Où définissez-vous votre RLS, au juste ?

Posez-vous la question franchement : aujourd’hui, où vit votre sécurité au niveau des lignes ?

Si la réponse est “dans Power BI, comme depuis toujours”, vous n’avez pas tort, mais le terrain a bougé. Pendant des années, le RLS était une affaire de modèle sémantique : des rôles, des règles DAX, et basta.

Le problème ? Ce filtre ne protège que Power BI. Le jour où un Data Engineer ouvre un Notebook Spark sur le même Lakehouse, ou qu’un analyste interroge le SQL analytics endpoint, votre RLS sémantique ne s’applique plus. La donnée est nue.

La réalité du terrain, c’est que dans une plateforme unifiée comme Fabric, la même table est consommée par plusieurs moteurs de calcul. Définir le filtre au niveau du rapport ne suffit plus. C’est exactement le trou que vient combler **OneLake Security** : un RLS défini une fois, au niveau de la donnée, et appliqué de façon cohérente quel que soit le moteur qui requête.

Pour cet article, j’ai monté un banc d’essai complet avec un star schema (`fact\_sale` + dimensions), quatre personas avec de vrais comptes Entra de test, et la même question rejouée dans Spark, le SQL endpoint et Power BI. Mes quatre cobayes :

* Alice, Sales Manager EMEA, doit voir toutes les ventes EMEA.
* Bob et Carol, Sales Reps (EMEA et AMER), chacun ne voit que ses ventes.
* Dan, Finance, voit toutes les ventes de l’année courante, mais pas la colonne `Profit`.

Aujourd’hui, on tranche. Voici les deux RLS, ce qui les sépare, comment ils se combinent, et lequel choisir sans exposer vos données par accident.

---

## Un même mot, deux implémentations

D’abord, levons une ambiguïté fréquente : le RLS filtre les **lignes** d’une table en fonction de l’identité du lecteur. Il ne masque ni une colonne (ça, c’est le CLS), ni une table ou une mesure entière (ça, c’est l’OLS).

Un commercial voit ses comptes, pas ceux du voisin : voilà du RLS.

Là où ça se corse, c’est qu’il existe désormais deux endroits pour le définir :

* Le RLS du modèle sémantique Power BI : Des rôles et des règles DAX, appliqués à chaque requête du rapport. Il protège le modèle sémantique, et lui seul.
* Le RLS de OneLake Security : récent. Des rôles définis sur la donnée dans OneLake, avec des règles en syntaxe SQL, appliqués de manière cohérente sur tous les moteurs Fabric (Spark, SQL analytics endpoint, Direct Lake) et les moteurs tiers autorisés, via les API OneLake.

La distinction tient en une phrase : le RLS Power BI sécurise un rapport ; le RLS OneLake sécurise la donnée elle-même, pour tous ceux qui la lisent.

---

## Les deux RLS, en détail

### 1. Le RLS du modèle sémantique Power BI : le classique, toujours pertinent

C’est le RLS que vous connaissez. Vous créez des rôles dans Power BI Desktop, vous écrivez une règle DAX par table à filtrer, puis vous mappez vos utilisateurs aux rôles après publication.

Ce qu’il faut maîtriser :

#### a. Les rôles sont additifs

Si un utilisateur appartient à plusieurs rôles, les filtres s’additionnent : il voit l’union des lignes autorisées par chaque rôle. Contrairement aux permissions SQL, le principe “ce qui est refusé une fois est toujours refusé” ne s’applique pas. L’exemple canonique de la doc est parlant : un rôle `Workers` qui filtre tout (`FALSE()`) et un rôle `Managers` qui ouvre tout (`TRUE()`). Un utilisateur membre des deux… voit toutes les lignes.

**Mon conseil** : Visez un seul rôle par audience qui accorde toutes les autorisations nécessaires, plutôt qu’une mosaïque de rôles cumulables. Et mappez des groupes de sécurité Entra ID aux rôles, pas des comptes individuels : vous déléguez la gestion des appartenances et vous réduisez la dette de maintenance.

#### b. Le RLS dynamique : un seul rôle pour tous vos commerciaux

Le vrai pouvoir du RLS Power BI, c’est le dynamique : un seul rôle qui sert tous les utilisateurs grâce à `**USERPRINCIPALNAME()**`.

Le UserPrincipalName (UPN) est l’identifiant de connexion unique d’un utilisateur dans Entra ID / Microsoft 365, au format e‑mail, utilisé pour s’authentifier aux services cloud et permet d’être utilisé pour du RLS.

#### c. La performance : filtrez les dimensions, pas les faits

Le RLS applique un filtre à chaque requête DAX, ce qui peut peser sur les performances. La règle d’or de modélisation s’applique pleinement.

Filtrer une table de faits volumineuse à chaque requête, c’est se condamner à des rapports lents. Le RLS efficace repose sur un schéma en étoile propre.

**Mon conseil** : Appliquez vos filtres RLS sur les tables de dimension, et laissez les \*\*relations actives\*\* propager le filtre vers les faits. Évitez `LOOKUPVALUE` quand une relation fait le même travail.

## 2. Le RLS de OneLake Security : un filtre, tous les moteurs

Ici, on change de niveau. Le RLS OneLake se définit sur la donnée elle-même : depuis votre Lakehouse, Manage OneLake security, un rôle, “...” sur la table, Row security. La règle s’écrit en **syntaxe SQL**, pas en DAX.

Pour le rôle `SalesManagerEMEA` de mon lab, la règle ressemble à ça, une clause `WHERE` sur des valeurs statiques.

Et surtout, cette définition unique est appliquée partout : Spark, SQL analytics endpoint (en mode **user identity**), modèle sémantique en Direct Lake on OneLake, et moteurs tiers autorisés via les API OneLake. OneLake reste la source unique de vérité.

**Ce qu’il faut maîtriser :**

#### a. Deux modes d’accès (Preview)

Au niveau du SQL analytics endpoint, le mode d’accès choisi détermine qui gouverne la sécurité :

* **User identity mode** : l’identité de l’utilisateur connecté est passée à OneLake. L’accès en lecture est gouverné **entièrement par les rôles OneLake** (RLS, CLS, OLS y sont définis). C’est le mode de la gouvernance centralisée, cohérente sur Power BI, Notebooks, Lakehouse et SQL endpoint.

**Delegated identity mode** : le endpoint se connecte avec l’identité du propriétaire de l’artefact, et la sécurité est gouvernée exclusivement par les permissions SQL (GRANT/REVOKE, `CREATE SECURITY POLICY`, Dynamic Data Masking). Dans ce mode, les règles RLS définies dans OneLake ne s’appliquent pas au SQL endpoint.

Docs : [OneLake Security for SQL analytics endpoints - Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/onelake/security/sql-analytics-endpoint-onelake-security#access-modes-in-sql-analytics-endpoint)

#### b. Les contraintes à connaître avant de vous lancer

OneLake Security RLS n’est pas un copier-coller du RLS Power BI. La règle s’écrit en SQL, mais c’est un sous-ensemble volontairement étroit, et c’est là que mon test m’a le plus appris :

* La syntaxe se limite à `SELECT \* FROM schema.table WHERE …`, \*\*1000 caractères\*\* max, avec uniquement `= <>, <, <=, >, >=, IN NOT AND OR IS BLANK IS NULL`. Pas de sous-requête, pas de jointure, pas de fonction utilisateur (`CURRENT\_USER()` n’existe pas ici).
* Le RLS ne s’applique qu’aux tables Delta parquet. Sur un objet non-Delta, le rôle bloque l’accès à toute la table au lieu de filtrer.
* RLS et CLS peuvent se combiner, mais dans un seul et même rôle. Un utilisateur dans un rôle “RLS” \*et\* un rôle “CLS” sur la même table va produire une erreur d’exécution.
* Les rôles Admin, Member et Contributor du workspace ne sont pas filtrés. Si vous testez avec votre propre compte d’admin, vous verrez tout, et vous conclurez à tort que votre RLS ne marche pas.

La Réalité du Terrain : OneLake RLS brille sur les **filtres statiques** (régions, périmètres figés). Le besoin “chaque utilisateur voit sa ligne via son identité”, lui, n’est pas son terrain, c’est du ressort du RLS dynamique Power BI, ou du combo des deux (section suivante).

Docs : [Row-level security in OneLake](https://learn.microsoft.com/fabric/onelake/security/row-level-security)

### c. L’interaction avec Power BI : Direct Lake combine les deux

C’est le moment “wow” de mon lab. Un modèle sémantique en **Direct Lake on OneLake** ne se contente pas d’hériter du RLS OneLake : il combine les deux niveaux.

**Deux conséquences :**

* Plusieurs rôles (OneLake ou Power BI) sur un même utilisateur impliquent que leurs filtres s’additionnent (comme un union, `OR`). Ajouter un rôle ne peut qu’élargir le périmètre.
* Entre les deux mondes, c’est une intersection : Power BI ne peut que restreindre ce qu’OneLake autorise, jamais l’étendre.

---

## 🥇 La Règle d’Or

Si tu dois retenir une chose : le RLS du modèle sémantique protège un rapport ; le RLS de OneLake Security protège la donnée pour tous ceux qui la lisent. Dans une plateforme unifiée, c’est au plus près de la donnée qu’il faut poser le filtre, à condition de surveiller le mode d’accès et les limites preview.

L’impact terrain est direct : en posant le RLS au bon niveau, vous arrêtez de redéfinir le même filtre dans chaque outil, et d’espérer qu’ils restent cohérents. Un seul point de vérité, c’est moins de dette technique, moins de surface d’erreur, et surtout la certitude qu’un Notebook Spark ou un SQL endpoint n’expose pas ce qu’un rapport Power BI cachait soigneusement.

> Et vous, où vit votre RLS aujourd’hui ? Avez-vous déjà testé ce qu’un utilisateur voit en passant par le SQL endpoint plutôt que par votre rapport Power BI ?

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [RLS, CLS, OLS Microsoft Fabric : le guide sécurité des données 2026](https://blog.antoinewang-tech.com/p/securite-microsoft-fabric)
* [Sécuriser les connexions Microsoft Fabric : bonnes pratiques et service principal](https://blog.antoinewang-tech.com/p/secure-connexion-source-microsoft-fabric)
* [Microsoft Fabric & VNet : Le Guide Sécurité Data Gateway](https://blog.antoinewang-tech.com/p/vnet-data-gateway-microsoft-fabric)

---

## 📚 Ressources pour aller plus loin

Pour approfondir le sujet et affiner vos choix d’architecture, je vous recommande ces lectures essentielles issues de la documentation officielle :

* [Aide sur la sécurité au niveau des lignes (RLS) dans Power BI Desktop](https://learn.microsoft.com/fr-fr/power-bi/guidance/rls-guidance) : bonnes pratiques de conception, RLS dynamique, performance
* [Row-level security in OneLake](https://learn.microsoft.com/fabric/onelake/security/row-level-security) : définition, syntaxe SQL, enforcement multi-moteurs
* [OneLake Security for SQL analytics endpoints](https://learn.microsoft.com/fabric/onelake/security/sql-analytics-endpoint-onelake-security) : user identity vs delegated mode, security sync, Shortcuts
* [Restreindre l’accès aux données avec la RLS (Power BI Desktop](https://learn.microsoft.com/fr-fr/fabric/security/service-admin-row-level-security)) : le how-to pas à pas du RLS sémantique
* [Get started with OneLake security](https://learn.microsoft.com/fabric/onelake/security/get-started-onelake-security) : types d’items supportés et activation
