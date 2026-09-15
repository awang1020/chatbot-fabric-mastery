---
title: Microsoft Fabric : Explorer tout le potentiel de Copilot dans Dataflow Gen2
url: https://blog.antoinewang-tech.com/p/copilot-dataflow-gen2-microsoft-fabric
date: 2026-06-02
author: Antoine Wang
source: substack
---

# Microsoft Fabric : Explorer tout le potentiel de Copilot dans Dataflow Gen2

Bonjour à tous, je suis **Antoine Wang**.

J’aide les profils techniques à maîtriser l’architecture de Microsoft Fabric, et j’aide les décideurs à comprendre l’impact réel de cette technologie.

Mon objectif ? Vulgariser le complexe et vous donner les clés pour maîtriser Microsoft Fabric, une plateforme de données SaaS unifiée et alimentée par l’IA pour simplifier la gestion des données et l’analyse.

Cette newsletter est 100% gratuite. En vous abonnant maintenant, vous recevrez en exclusivité mon “One-Pager” pour cartographier l’ensemble de la solution Fabric en un coup d’œil.

Merci à celles et ceux qui me suivent depuis le début. Sans plus attendre, entrons dans le vif du sujet !

---

Après avoir décortiqué Copilot pour Power BI dans ma précédente édition *(voir le post ci-dessous),* attaquons-nous à Copilot dans Dataflow Gen2 *:*

[#### Power BI : Fini la page blanche avec Copilot

[Antoine Wang](https://substack.com/profile/410602111-antoine-wang)

·

Feb 17

[Read full story](https://antoinewang.substack.com/p/microsoft-fabric-copilot-powerbi)](https://antoinewang.substack.com/p/microsoft-fabric-copilot-powerbi)

Pour rappel, Dataflow Gen2 est la brique de prédilection pour le low-code ETL, permettant d’ingérer, de nettoyer et de charger des données via une interface visuelle familière dans Microsoft Fabric.

Je vois souvent la même limite émerger : quand les règles métier se complexifient et que vous enchaînez des dizaines d’étapes de transformation, personne n’a en tête toutes les fonctions du code M et cela peut se transformer en une dette technique.

Alors, comment accélérer nos traitements ? Peut-on déléguer l’écriture d’une colonne calculée complexe ou générer instantanément l’explication d’une requête héritée et non documentée ?

C’est là que Copilot dans Dataflow Gen2 révèle tout son intérêt. Il agit comme un accélérateur de productivité, avec des cas d’usage pour livrer plus vite et sécuriser vos développements.

---

## Copilot & Dataflow Gen2

Copilot pour Dataflow Gen2 est l’assistant IA intégré directement dans l’interface Dataflow Gen2 de Microsoft Fabric.

Son rôle : générer, expliquer et ajuster des transformations de données en code M (le langage natif de Power Query) à partir de vos instructions en langage naturel.

Voici comment l’exploiter sur le terrain à travers ses trois caractéristiques clés.

---

### 1. Générer des étapes de transformation à la volée

Au lieu de fouiller dans les menus ou d'écrire manuellement des fonctions M complexes (comme des pivots, des extractions conditionnelles ou des regroupements), vous décrivez le résultat attendu dans le panneau Copilot. Le moteur traduit votre prompt en une nouvelle étape de transformation appliquée directement à votre flux.

Par exemple, si votre tableau comprend des champs tels que OrderID, Quantity, Category et Total, vous pouvez saisir une description comme celle-ci :

*If the Total order is more than 2000 and the Category is B, then provide a discount of 10%. If the total is more than 200 and the Category is A, then provide a discount of 25% but only if the Quantity is more than 10 otherwise just provide a 10% discount*

**💡 Tips :** Soyez précis dans vos prompts. Utilisez les noms exacts des colonnes.

**⚠️ Point de vigilance :** Attention au *Query Folding* (la capacité à déléguer le calcul au système source comme une base SQL). Si Copilot génère une fonction M non supportée par la source, la transformation s'exécutera dans le moteur de calcul de Fabric (Mashup engine). Vérifiez toujours vos plans de requêtes pour éviter d'effondrer les performances de votre ingestion.

---

### 2. Faire de la rétro-ingénierie et documenter l’existant

Pour faire de la rétro-ingénierie, Copilot propose deux niveaux de lecture interactifs qui agissent comme une véritable *Living Documentation* générée à la volée :

* **Expliquer la requête globale (”Explain this query”) :** Accessible via le volet Copilot ou par un simple clic droit sur votre requête dans le panneau latéral. Le moteur lit l’intégralité du code M et génère un résumé global en langage clair de toutes les transformations appliquées de bout en bout.

* **Expliquer une étape spécifique (”Explain this step”) :** Parfois, le blocage vient d’une seule ligne de code M obscure. Allez directement dans la section des “Étapes appliquées” (*Applied steps*), faites un clic droit sur l’étape ciblée, et sélectionnez l’option pour que Copilot décrive uniquement cette opération isolée.

**💡 Tips :** Utilisez ce résumé généré pour créer une véritable *Living Documentation*. Copiez l’explication fournie par Copilot et collez-la dans les “Propriétés” de la requête. Le prochain ingénieur (ou vous-même dans 6 mois) comprendra instantanément la logique sans avoir à décrypter le code M ligne par ligne.

**⚠️ Point de vigilance :** Copilot vous explique le *Comment* (ce que fait le code), mais il n’a aucune idée du *Pourquoi* (la règle métier sous-jacente). S’il vous dit “Cette étape supprime les lignes avec des valeurs nulles”, il ne vous dira pas que c’est une exigence réglementaire de la comptabilité. Ne laissez pas l’IA remplacer l’encadrement métier de vos artefacts.

---

### 3. Générer de nouvelles requêtes et jeux d’essais

**Description :** Copilot peut créer une requête entièrement nouvelle (from scratch) basée sur un prompt, générer des données factices pour tester une logique, ou créer une requête qui référence une table existante pour l’enrichir sans casser la source.

**💡 Tips :** C’est le moyen le plus rapide de générer des tables de dimensions standard. Demandez-lui : *“Génère une table de calendrier complète allant du 1er Janvier 2020 au 31 Décembre 2025 avec les colonnes Année, Trimestre, Mois et Jour de la semaine”*. Vous économiserez 15 minutes de recherche de script M sur internet.

**⚠️ Point de vigilance :** Le typage des données. Quand Copilot génère une requête from scratch, il laisse parfois les colonnes en type “Any” (Texte/Général). Ne chargez jamais ce résultat tel quel dans votre Lakehouse ou Warehouse : repassez toujours derrière pour forcer le typage strict (Int64, Date, Decimal) afin de ne pas introduire de la dette technique dès la couche d’ingestion.

---

## Les limites de Copilot dans Dataflow Gen2

Je vois souvent des équipes qui découvrent ces points de friction en production. Mieux vaut les anticiper :

* **Copilot génère du code mais ne valide pas le résultat.**

  Le M code produit peut être syntaxiquement correct et logiquement faux. Si votre règle métier est complexe, Copilot peut interpréter à sa façon et cela peut engendrer des données incorrectes dans l’aperçu.
* **Copilot n’est pas activé par défaut.**

  L’administrateur Fabric de votre organisation doit avoir activé Copilot au niveau du portail d’administration.
* **Copilot consomme des Capacity Units (CU).**

  Chaque interaction mobilise du moteur de calcul. Ce n’est pas négligeable dans un environnement où plusieurs utilisateurs exploitent Copilot en parallèle. Surveillez votre Capacity Metrics App si vous déployez Copilot à grande échelle.
* **Copilot ne peut pas effectuer de transformations ou d’explications sur plusieurs requêtes dans une seule entrée.**

  Par exemple, vous ne pouvez pas demander à Copilot de « Mettre en majuscule tous les en-têtes de colonne pour chaque requête dans mon dataflow ».

---

## 4. Au-delà de Copilot : AI Prompt

Copilot accélère la création de votre logique de transformation. Mais pour enrichir le *contenu* de vos données, Dataflow Gen2 embarque une nouvelle fonctionnalité : les AI Prompt (actuellement en Preview).

Concrètement, vous utilisez des modèles pré-entraînés (basés sur Azure AI) d’IA générative appelables directement via l’interface, sans avoir à créer des modèles ou de gérer l’infrastructure sous-jacente. La réalité du terrain, c'est que l'on a souvent besoin de valoriser de la donnée non structurée.

L’objectif est direct : vous passez une instruction spécifique à votre contexte métier, qui s’exécutera individuellement sur chaque ligne de vos données !

Par exemple, vous pouvez demander à l'IA de :

* **Analyse de sentiment :** Détecter le ton (positif, négatif, neutre) d’un commentaire client ou d’un retour utilisateur.
* **Extraction de mots-clés :** Isoler les termes principaux d’un champ texte long.
* **Détection de langue :** Identifier automatiquement l’idiome d’une colonne (très utile pour router des données internationales).
* **Générer du contenu :** Résumer l’avis d’un client et formuler automatiquement une proposition de réponse dans sa langue d’origine.

**💡 Tips :** Si votre prompt fait référence à un ou plusieurs champs spécifiques, assurez-vous d'avoir explicitement sélectionné la ou les colonnes correspondantes dans le menu de configuration de votre AI Prompt.

---

## Matrice de Décision

**Q1 : Héritez-vous d’un flux Dataflow Gen2 avec des dizaines d’étapes de transformation non documentées ?**

* **OUI :** Utilisez immédiatement la fonction “Explain this query” de Copilot.

**Q2 : Devez-vous implémenter des règles de gestion de calcul très spécifiques ?**

* **OUI :** Utilisez Copilot pour accélérer la création de ces règles de gestion métiers, et valider les résultats.

**Q3 : Avez-vous besoin d’extraire des informations de champs textes libres (commentaires, logs) sur votre couche Bronze ?**

* **OUI :** Utilisez les *AI Prompts* de Dataflow Gen2 pour valoriser cette donnée.

---

## Conclusion

**Si tu dois retenir une chose :** Copilot dans Dataflow Gen2 est une brique puissante qui ne remplace pas ton expertise d’ingénieur, mais qui te libère de la dette technique pour accélérer la valorisation de la donnée dès l’ingestion.

Ne vous y trompez pas : c’est toujours votre responsabilité de valider le code, de comprendre les règles métier, et de maîtriser ce qui part en production.

Pour une équipe qui embarque des profils métier dans ses projets Fabric, cet assistant supprime la barrière d’entrée technique.

Le résultat concret : moins de tickets IT pour des transformations de premier niveau, plus d’autonomie côté analyste, et des Data Engineers qui peuvent concentrer leur énergie sur les briques d’architecture à haute valeur ajoutée.

> Et vous, quel usage faites-vous de Copilot dans vos Dataflows Gen2 ? Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

### 📚 Ressources pour aller plus loin

* 📘 [Vue d’ensemble de Copilot pour Data Factory](https://learn.microsoft.com/fr-fr/fabric/data-factory/copilot-fabric-data-factory-get-started)
* 🛠️ [Utiliser les AI Functions et AI Prompts dans Dataflow Gen2](https://learn.microsoft.com/en-us/fabric/data-factory/dataflow-gen2-ai-functions)
* 🔗 [Générer une Living Documentation avec l’explication de requêtes Copilot](https://learn.microsoft.com/fr-fr/fabric/data-factory/dataflow-gen2-copilot-explain)
