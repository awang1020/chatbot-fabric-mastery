---
title: Microsoft Fabric : Bonnes pratiques pour optimiser Copilot dans Power BI (Prep Data for AI)
url: https://blog.antoinewang-tech.com/p/microsoft-fabric-copilot-in-powerbi-desktop-prep-data-for-ai
date: 2026-09-08
author: Antoine Wang
source: substack
---

# Microsoft Fabric : Bonnes pratiques pour optimiser Copilot dans Power BI (Prep Data for AI)

Bonjour à tous, je suis **Antoine Wang**.

J’aide les profils techniques à maîtriser l’architecture de Microsoft Fabric, et j’aide les décideurs à comprendre l’impact réel de cette technologie.

Mon objectif ? Vulgariser le complexe et vous donner les clés pour maîtriser Microsoft Fabric, une plateforme de données SaaS unifiée et alimentée par l’IA pour simplifier la gestion des données et l’analyse.

🆕 **Nouveauté pour les lecteurs** : j’ai créé **Ask Fabric Mastery**, un assistant IA qui répond à vos questions sur Microsoft Fabric & Power BI en s’appuyant uniquement sur les 36 éditions de cette newsletter. Réponses sourcées, sans hallucination, avec un lien direct vers l’édition d’origine.

👉 **Testez-le maintenant** : [Chatbot Fabric Mastery](https://chat.antoinewang-tech.com)  
🔑 **Code lecture pour accès illimité (réservé aux abonnés) :**

Cette newsletter est 100% gratuite. En vous abonnant maintenant, vous recevrez en exclusivité mon “One-Pager” pour cartographier l’ensemble de la solution Fabric en un coup d’œil.

Merci à celles et ceux qui me suivent depuis le début. Sans plus attendre, entrons dans le vif du sujet !

---

### ⚡ En 30 secondes

Ce qu’il faut retenir :

* Copilot dans Power BI Desktop, ce sont 4 fonctionnalités disponibles depuis le Copilot pane :

  + Data questions (interroger en langage naturel),
  + Verified Answers (phrases déclencheuses vers des visuels validés),
  + AI Instructions (spécifier votre vocabulaire métier),
  + Report page creation (générer pages et visuels).
* Les 3 premières briques (Data questions, Verified Answers, AI Instructions) vivent sur le semantic model donc partagées entre tous les rapports qui l’utilisent.
* L’action à lancer : ouvrir le Copilot pane, taper ”Summarize the model semantic” pour voir ce que Copilot comprend de votre modèle. Cette seule query révèle 80 % des problèmes de nommage, de descriptions et de couverture, avant même d’écrire une AI Instruction.

---

Avez-vous cliqué sur le bouton Copilot dans Power BI Desktop ? Vous avez tapé une question vague et vous avez obtenu un graphique bâton générique, sans contexte métier, sans les bonnes mesures = vous avez conclu que Copilot n’était pas prêt.

Je vois cette scène sur tous les clients où j’interviens. La réalité du terrain, c’est que Copilot Desktop n’est pas un chat magique, c’est un outil qui exécute très bien à condition qu’on l’utilise dans le bon ordre, avec les bons prompts, sur un modèle sémantique préparé. Le problème n’est presque jamais Copilot.

Aujourd’hui, je vous joue la démo end-to-end. Les mêmes 4 fonctionnalités que je passe systématiquement chez mes clients, avec les queries concrètes que j’utilise, les cas d’usage où ça marche, et pourquoi le semantic model reste toujours le plus important dans l’équation.

---

## Copilot Power BI Desktop en 4 briques

Copilot dans Power BI Desktop, c’est un panneau latéral (le Copilot pane) qui expose 4 fonctionnalités distinctes, chacune adressant un usage précis :

1. Data questions : Poser des questions en langage naturel sur les données. Copilot génère un visuel + une explication texte à partir du semantic model.
2. Verified Answers : Lier des phrases déclencheuses à un visuel de rapport validé. Copilot renvoie ce visuel tel quel quand la question matche (exact ou sémantique).
3. AI Instructions : Fournir en langage naturel le contexte métier, la terminologie interne que Copilot ne peut pas deviner du modèle seul.
4. Report page creation : Générer une nouvelle page de rapport (ou modifier des visuels existants) depuis un prompt textuel.

---

## La démo en 4 gestes, dans l’ordre chronologique

#### Geste 1 : Data questions, commencer par comprendre ce que Copilot comprend

Ouvrez votre rapport, cliquez sur l’icône Copilot dans le ruban Home. Le Copilot pane s’ouvre à droite.

Vous pouvez poser ces questions pour examiner le rapport que vous êtes en train d’analyser :

* “*Summarize the model semantic*”
* *What does the report page tell me?”*

On peut facilement vérifier la réponse en cliquant sur les chiffres dans la réponse pour voir le visuel associé :

***Question : Comment réagit Copilot pour les questions dont la réponse n’est PAS sur les visuels du rapport mais présent dans le modèle sémantique ?***

Si aucun visuel de votre rapport ne montre cette information, Copilot va quand même interroger le modèle sémantique, générer un visuel ad hoc dans le pane, et vous proposer de l’ajouter au rapport.

**Par exemple : list the top 5 products sold in a column chart** (avec le bouton +Add to page).

En cliquant sur “**How Copilot arrived at this**”, cela vous permet de vérifier les données utilisés et les filtres qui ont permis d’arriver à ce résultat.

#### Geste 2 : Verified Answers, vérifier les questions récurrentes

Vous connaissez bien votre rapport, la raison de pourquoi on a chaque visuel dans ce rapport et les questions associés. Au lieu de laisser Copilot sortir une réponse en naviguant dans tout le modèle sémantique, vous pouvez créer des **Verified Answers**. Ces questions doivent renvoyer toujours la même réponse, lorsque Copilot reconnaît la question.

Exemple : la query ”*Give me a Bob/Antoine Analysis*”, une analyse que seule les métiers peuvent comprendre mais que Copilot ne reconnaît pas. Pour cela, on veut qu’elle renvoie toujours le visuel “bar chart” que l’analyste a construit.

**Setup en 4 étapes** :

1. Sélectionner le visuel qui doit servir de réponse.

2. Menu 3 points sur le header du visuel > Set up a verified answer.

3. Ajouter les phrases connectés à la réponse vérifiée : les formulations que les utilisateurs peuvent poser (”Give me a Bob/Antoine Analysis”. Copilot suggère automatiquement des trigger phrases basées sur le visuel, accueillez ces suggestions puis affinez.

4. Optionnel : ajouter des filtres persistants (jusqu’à 10 permutations), l’utilisateur pourra alors slicer via son prompt (”\*for the Northeast region\*”).

Comment ça fonctionne ?

* Match exact : la phrase de l’utilisateur = la trigger phrase caractère par caractère.
* Match sémantique : Copilot reconnaît les reformulations proches.
* Stocké sur le semantic model donc se propage automatiquement à tous les rapports utilisant ce modèle.

**Mon conseil** : Ajoutez 5-7 Questions aux Verified Answers pour améliorer la pertinence et le trigger des réponses aux questions les plus posées pour améliorer la fiabilité de Copilot.

#### Geste 3 : AI Instructions, spécifier votre vocabulaire métier

Le problème qu’elle résout : votre entreprise utilise des termes internes que le modèle ne connaît pas.

Exemple : la query ”Show blabla by Employee”.

Résultat : Copilot ne comprend pas. “blabla” n’existe nulle part dans le modèle. Il vous renvoie soit un message d’incapacité.

Fix en 30 secondes :

1. Ouvrir Prep data for AI > onglet AI Instructions.
2. Écrire une phrase claire et surgicale : ”blabla means the Order Count measure”.
3. Appliquer.

Relancer la même query. Cette fois, Copilot utilise la mesure `Order Count`, groupée par `Employee`.

**Bonnes pratiques :**

* Spécifier du contexte temporel lorsqu’il s’agit d’une analyse de Ventes : “Any sales analysis question must include a time period. If not specified by the user, use the current fiscal year.”
* Règles de repli : “If data is missing or the question can’t be answered from the model, say so explicitly and suggest the user contacts the Data team.”

#### Geste 4 : Report page creation, générer des pages complètes

Envie d’aller plus vite dans la création de visuels ? Copilot peut générer des pages entières depuis un prompt textuel.

Exemple : la query : ”*Create a new report page showing Product & Category Performance with a slicer for products”*

Copilot génère :

* Une nouvelle page nommée automatiquement (”Product & Category Performance” ou similaire)
* Une sélection de visuels adaptés : bar chart de ventes par catégorie, KPI de revenu total, table par produit
* Un slicer produits, comme demandé
* Un layout raisonnable (pas parfait, mais un vrai point de départ)

Vous pouvez ensuite modifier les visuels en langage naturel :

* ”Change the column chart to a pie chart, total revenue by category”

Copilot remplace le visuel. Undo/redo dispos. Vous ajoutez, vous retirez, vous ajustez, le tout par prompts.

J’ai laissé ce [démo de rapport BI sur mon répo github](https://github.com/awang1020/sales-retail-powerbi-demo), vous pouvez dès maintenant tester Copilot avec le même report.

---

## 🥇 La Règle d’Or

Si tu dois retenir une chose : Copilot dans Power BI Desktop, ce n’est pas un chat magique, c’est un outil qui exécute bien à condition qu’on lui prépare 4 briques d’ancrage. Le semantic model AI-ready d’abord (Phase 0), les AI Instructions pour traduire votre vocabulaire métier, les Verified Answers pour spécifier les questions récurrentes, et des prompts précis pour la génération de pages. Avec ces 4 gestes, tu as un accélérateur que tes utilisateurs adoptent parce qu’il marche.

L’impact terrain est direct : vous passez d’un Power BI “outil analyste” à un Power BI conversationnel, sans changer un seul rapport existant, juste en préparant le modèle correctement.

> Et vous, aujourd’hui, quel geste Copilot Desktop utilisez-vous le plus ? Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## 🔗 À lire dans Fabric Mastery

* [Power BI : Fini la page blanche avec Copilot (Guide Complet)](https://blog.antoinewang-tech.com/p/microsoft-fabric-copilot-powerbi)
* [Microsoft Fabric : Explorer tout le potentiel de Copilot dans Dataflow Gen2](https://blog.antoinewang-tech.com/p/copilot-dataflow-gen2-microsoft-fabric)
* [Fabric Copilot Capacity (FCC) : le guide 2026 pour activer Copilot sans throttling](https://blog.antoinewang-tech.com/p/fabric-copilot-capacity-dedicated)
* [Fabric Data Agent vs Copilot : les 3 différences qui comptent en 2026](https://blog.antoinewang-tech.com/p/microsoft-fabric-data-agent-copilot)

---

## 📚 Ressources pour aller plus loin

Pour approfondir le sujet et jouer la démo chez vous, je vous recommande ces lectures essentielles issues de la documentation officielle :

* [Copilot for Power BI overview](https://learn.microsoft.com/power-bi/create-reports/copilot-introduction) : vue d’ensemble des capacités, du Copilot pane, des skills disponibles
* [Ask Copilot questions about your data](https://learn.microsoft.com/power-bi/create-reports/copilot-ask-data-question) : data questions, ad hoc DAX, limitations
* [Prepare your data for AI : Verified Answers](https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai-verified-answers) : trigger phrases, filtres
* [Prepare your data for AI to improve Copilot results](https://learn.microsoft.com/power-bi/create-reports/copilot-prepare-data-ai) : AI Data Schema + AI Instructions + Verified Answers + Approved for Copilot
* [Create and edit Power BI reports with Copilot](https://learn.microsoft.com/power-bi/create-reports/copilot-create-reports) : le how-to complet de la génération de pages
* [Semantic model best practices for data agent](https://learn.microsoft.com/fabric/data-science/semantic-model-best-practices) : comment votre Prep for AI sert aussi les Data Agents Fabric
