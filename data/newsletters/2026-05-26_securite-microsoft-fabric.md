---
title: RLS, CLS, OLS Microsoft Fabric : le guide sécurité des données 2026
url: https://blog.antoinewang-tech.com/p/securite-microsoft-fabric
date: 2026-05-26
author: Antoine Wang
source: substack
---

# RLS, CLS, OLS Microsoft Fabric : le guide sécurité des données 2026

Bonjour à tous, je suis **Antoine Wang**.

J’aide les profils techniques à maîtriser l’architecture de Microsoft Fabric, et j’aide les décideurs à comprendre l’impact réel de cette technologie.

Mon objectif ? Vulgariser le complexe et vous donner les clés pour maîtriser Microsoft Fabric, une plateforme de données SaaS unifiée et alimentée par l’IA pour simplifier la gestion des données et l’analyse.

Cette newsletter est 100% gratuite. En vous abonnant maintenant, vous recevrez en exclusivité mon “One-Pager” pour cartographier l’ensemble de la solution Fabric en un coup d’œil.

Merci à celles et ceux qui me suivent depuis le début. Sans plus attendre, entrons dans le vif du sujet !

---

La **sécurité des données** dans le cloud ne date pas d’hier, mais voyons comment Microsoft Fabric relève ce défi.

Imaginons un scénario classique : une équipe BI déploie ses rapports Power BI sur la plateforme. Tout fonctionne à merveille, les visuels sont impeccables. Puis vient la question fatidique du DSI :

* *“Est-ce que le directeur régional de Bordeaux peut voir les chiffres de Lyon ?”*
* *“Est-ce que les RH peuvent voir les salaires des cadres dirigeants ?”*
* *“Comment la sécurité se concrêtise dans la plateforme ?”*

La sécurité de la donnée a souvent été pensée en dernier.

Le problème ? On bricole des dizaines de rôles statiques impossibles à maintenir, on accorde des accès temporaires que l’on finit par oublier, ou on duplique les rapports par profil utilisateur. Cette approche devient rapidement ingérable.

La conséquence ? Une dette technique qui explose à chaque évolution du modèle et un risque sécuritaire qui s’accroît.

Dans Fabric, la sécurité fine de la donnée se joue sur plusieurs couches distinctes.

Comprendre laquelle utiliser selon le contexte, c’est ce qui sépare une gouvernance solide d’un château de cartes.

---

## C’est quoi RLS, CLS et OLS dans Fabric ?

Fabric propose trois niveaux de sécurité granulaire sur la donnée, complémentaires et non interchangeables :

**Row-Level Security (RLS) - Filtrage par ligne.**

* Restreint l’accès aux lignes d’une table selon l’identité de l’utilisateur.
* Le directeur régional de Bordeaux ne voit que les données de sa région.
* Le commercial ne voit que son propre portefeuille clients.
* La donnée existe dans le modèle, l’utilisateur ne voit simplement pas les lignes auxquelles il n’a pas accès.

**Column-Level Security (CLS), Masquage par colonne.**

* Restreint l’accès à certaines colonnes entières.
* Les colonnes salaire, numéro de sécurité sociale, ou marge nette ne sont tout simplement pas accessibles aux profils non autorisés.
* Disponible sur le SQL Endpoint du Lakehouse, dans le Warehouse, et dans les semantic models via OLS.

**Object-Level Security (OLS), Visibilité des objets du modèle.**

* Contrôle la visibilité des tables, colonnes et mesures dans un semantic model Power BI.
* Une table ou une mesure “cachée” via OLS n’apparaît tout simplement pas dans le modèle pour les utilisateurs concernés, même les noms ne sont pas visibles.

Ces trois mécanismes ne sont pas redondants. Ils opèrent à des niveaux différents et se complètent selon la couche d’accès concernée.

---

## La réalité du terrain

✅ **La sécurité dans Fabric opère en couches, et chaque couche a son périmètre.**

* Au niveau OneLake : les rôles RBAC (Object-Level, Row-Level, Column-Level) s’appliquent directement aux données stockées et voyagent avec elles, y compris via les Shortcuts.
* Au niveau SQL Endpoint et Warehouse : RLS, CLS et Dynamic Data Masking configurables via T-SQL.
* Au niveau semantic model Power BI : RLS statique, RLS dynamique, OLS.

Comprendre quelle couche couvre quel moteur d’accès est la première chose à cartographier avant d’implémenter quoi que ce soit.

✅ **La sécurité dynamique est votre meilleure alliée contre l’explosion du nombre de rôles.**

* L’erreur classique sur le terrain : créer un rôle statique par région, par département, par équipe.
* **Résultat** : 30 rôles à maintenir, et à chaque réorganisation interne, tout est à refaire. La sécurité dynamique dans les semantic models repose sur les fonctions DAX `USERPRINCIPALNAME()` ou `USERNAME()` : elles retournent l’identité de l’utilisateur connecté et filtrent automatiquement les données selon une table de mapping chargée dans le modèle.

Un seul rôle dynamique remplace potentiellement des dizaines de rôles statiques.

✅ **OneLake Security sécurise la donnée à la source, quel que soit le moteur qui la consomme.**

* C’est le point architectural clé : les rôles définis dans OneLake s’appliquent en pass-through aux moteurs Spark, et via identité déléguée aux SQL Endpoints et semantic models.
* La sécurité définie une fois dans OneLake reste effective que l’utilisateur accède via Power BI, via SSMS, via les REST APIs ou via un outil tiers compatible ADLS Gen2.

✅ **Le OneLake Catalog centralise la vue de vos configurations de sécurité.**

* L’onglet Secure (en preview) du OneLake Catalog offre une vue centralisée des rôles et permissions à travers vos workspaces et items.
* Vue par utilisateurs, vue par rôles de sécurité, c’est votre tableau de bord d’audit pour vérifier que personne n’a des droits excessifs, et pour appliquer le principe du moindre privilège à l’échelle du tenant.

---

## Points de vigilance

⚠️ **Les utilisateurs avec des rôles élevés dans le workspace contournent le RLS et l’OLS.**

C’est une limite fondamentale à connaître : seuls les utilisateurs avec le rôle Viewer (lecture seule) sur le semantic model ou le workspace voient la sécurité RLS et OLS appliquée. Les Admin, Member et Contributor voient tout, sans restriction.

Conséquence directe sur le terrain : si vous donnez des droits Contributor à un utilisateur pour qu’il puisse “juste modifier un rapport”, vous lui donnez aussi accès à toutes les données non filtrées.

Attribuez les rôles workspace avec précision, en gardant en tête cette interaction avec la sécurité modèle.

⚠️ **La sécurité OneLake ne s’applique pas aux SQL Endpoints et semantic models en mode délégué.**

Les SQL Endpoints, semantic models et Warehouses accèdent à OneLake via une identité déléguée, ils ont leur propre couche de sécurité et ignorent les rôles RBAC OneLake.

Si vous sécurisez uniquement au niveau OneLake en pensant couvrir tous les accès, les utilisateurs passant par le SQL Endpoint ou un rapport Power BI contournent cette sécurité.

Les deux couches doivent être configurées de manière cohérente et complémentaire.

⚠️ **Dynamic Data Masking n’est pas une vraie sécurité, c’est de l’obscurcissement.**

Le masquage des données (email, numéro de téléphone, valeur numérique sensible) peut être contourné par des requêtes ad hoc successives permettant de deviner la valeur masquée par itération.

C’est un outil utile pour limiter la visibilité accidentelle, pas pour protéger des données réellement sensibles.

Ne comptez pas dessus comme unique mécanisme de protection.

⚠️ **Les permissions sur les Shortcuts ont leurs propres règles.**

Dans OneLake, les permissions doivent être définies sur la table de destination d’un Shortcut, pas sur le Shortcut lui-même.

Définir des droits sur un Shortcut n’est pas supporté.

C’est une subtilité qui passe souvent inaperçue lors de la mise en place d’architectures multi-sources, et qui crée des failles de sécurité involontaires.

---

## Matrice de décision

**Q1 : Vos utilisateurs accèdent-ils à la donnée via Power BI uniquement, ou aussi via SQL / Spark / API ?**

* **Power BI uniquement** : RLS et OLS dans le semantic model suffisent pour la couche de consommation.
* **Accès multi-moteurs (SQL, Spark, API)** : Configurez également la sécurité au niveau OneLake RBAC et SQL Endpoint pour couvrir tous les chemins d’accès.

**Q2 : Avez-vous de nombreuses combinaisons de profils d’accès (>5 rôles distincts) ?**

* **Oui** : Sécurité dynamique avec `USERPRINCIPALNAME()` et table de mapping dans le semantic model. Un rôle dynamique remplace N rôles statiques.
* **Non (<5 rôles stables)** : Rôles statiques acceptables, plus simples à configurer et à auditer.

**Q3 : Avez-vous des colonnes structurellement sensibles (salaires, données personnelles, marges) ?**

* **Oui** : CLS au niveau SQL Endpoint / Warehouse + OLS dans le semantic model pour masquer ces colonnes selon le profil.
* **Non** : RLS seul couvre votre besoin de filtrage.

---

## Conclusion

Si tu dois retenir une chose : Dans Fabric, la sécurité de la donnée n’est pas une fonctionnalité à activer après coup, c’est une architecture à concevoir en même temps que votre modèle de données.

RLS, CLS, OLS et OneLake RBAC ne se substituent pas : ils se complètent selon le moteur d’accès.

Un seul rôle dynamique bien conçu vaut mieux que vingt rôles statiques impossibles à maintenir.

L’Impact Terrain : Une stratégie de sécurité granulaire bien conçue dans Fabric, c’est la fin des “je vais dupliquer le rapport pour chaque région” et des “on ne peut pas partager ce dashboard parce qu’il contient des données confidentielles”.

Chaque utilisateur voit exactement ce qu’il doit voir à travers un modèle unique, maintenu une seule fois, c’est l’idée du One Security qui va s’annoncer au fur et à mesure dans la plateforme.

C’est aussi ce qui rend possible le self-service BI à grande échelle : quand la sécurité est structurelle et non contournable, vous pouvez ouvrir l’accès aux données sans craindre les fuites.

La confiance des métiers dans la plateforme se construit sur cette garantie.

> Question : comment avez-vous structuré la sécurité dans Fabric ? Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 📚 Ressources pour aller plus loin

Pour approfondir le sujet et affiner vos choix d’architecture, je vous recommande ces lectures essentielles :

* [Sécurité dans Microsoft Fabric](https://learn.microsoft.com/fr-fr/fabric/security/security-overview)
* [Sécuriser les données dans OneLake](https://learn.microsoft.com/fr-fr/fabric/onelake/security/get-started-security)
* [Sécurité au niveau des lignes (RLS) avec Power BI](https://learn.microsoft.com/fr-fr/fabric/security/service-admin-row-level-security)
* [Sécurité au niveau des objets (OLS)](https://learn.microsoft.com/fr-fr/fabric/security/service-admin-object-level-security?tabs=table)
* [Masquage dynamique des données dans Fabric](https://learn.microsoft.com/fr-fr/fabric/data-warehouse/dynamic-data-masking)
