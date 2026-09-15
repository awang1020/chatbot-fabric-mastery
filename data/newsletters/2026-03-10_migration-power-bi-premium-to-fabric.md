---
title: Adieu Power BI Premium : Pourquoi vous devez migrer vers Fabric dès aujourd’hui
url: https://blog.antoinewang-tech.com/p/migration-power-bi-premium-to-fabric
date: 2026-03-10
author: Antoine Wang
source: substack
---

# Adieu Power BI Premium : Pourquoi vous devez migrer vers Fabric dès aujourd’hui

Bonjour à tous, je suis **Antoine Wang**.

J’aide les profils techniques à maîtriser l’architecture de Microsoft Fabric, et j’aide les décideurs à comprendre l’impact réel de cette technologie, sans le jargon inutile.

Mon objectif ? Vulgariser le complexe et vous donner les clés pour maîtriser Microsoft Fabric, une plateforme de données SaaS unifiée et alimentée par l’IA pour simplifier la gestion des données et l’analyse.

Cette newsletter est 100% gratuite. En vous abonnant maintenant, vous recevrez en exclusivité mon “One-Pager” pour cartographier l’ensemble de la solution Fabric en un coup d’œil.

Merci à celles et ceux qui me suivent depuis le début. Sans plus attendre, entrons dans le vif du sujet !

---

De nombreux clients me posent ces questions :

* Qu’est-ce que le modèle de licensing de Microsoft pour Power BI et Microsoft Fabric ?
* Que va devenir ma capacité Power BI Premium ?
* Comment les utilisateurs vont pouvoir accéder à Power BI sans licence individuelle ?
* Qu’est-ce que Microsoft Fabric ?

Si vous gérez actuellement des capacités **Power BI Premium (P-SKU)**, vous savez que Microsoft fait évoluer son modèle de licence. Les capacités Premium classiques ne sont plus commercialisées au profit de **Microsoft Fabric (F-SKU)**.

**Ce qu’il faut retenir :**

* Depuis début 2025, les capacités Power BI Premium existantes ont été progressivement retirées.
* Il existe une équivalence directe entre vos anciens P-SKU et les nouveaux F-SKU.
* La bonne nouvelle ? Fabric vous ouvre les portes du Lakehouse, de Data Factory, de Data Science et du Real-Time Intelligence sans surcoût de licence de base.

---

## 🚀 Pourquoi faire le saut vers Fabric ? (Au-delà de la fin du P-SKU)

Le passage au modèle F-SKU n’est pas qu’une simple mise à jour de licence, c’est un changement de paradigme. Voici pourquoi vous avez tout intérêt à migrer :

* **Unification de la donnée** : Vous passez d’un outil de visualisation (Power BI) à une plateforme data complète pour centraliser toutes vos données au même endroit (OneLake) et casser définitivement les silos entre les métiers.
* **Flexibilité du “Pay-as-you-go”** : Contrairement aux capacités Premium (P-SKU) qui étaient des engagements mensuels ou annuels rigides à des coûts élevés, les capacités Fabric peuvent être approvisionnées à faible coût et mises en pause ou scalées à la volée pour optimiser les coûts.
* **Accès aux services “Advanced”** : Sans surcoût de licence de base, vous débloquez des outils comme **Data Factory** (ETL, pipelines), **Real-Time Intelligence** (Big Data) et des **capacités d’Intelligence Artificielle** (Machine Learning, Gen AI) directement sur vos données OneLake et vos rapports BI.
* **Mutualisation des performances** : La capacité Fabric (F-SKU) n’est pas réservée à Power BI. Elle sert de moteur de calcul (Spark, SQL…) pour tous les autres services de la plateforme, comme pour la centralisation des sources de données ou encore pour le traitement de données, évitant ainsi de payer plusieurs ressources Azure séparées.
* **Le shift stratégique de la “BI augmentée” par l’IA :** Aujourd’hui, les entreprises les plus compétitives ne se contentent plus de l’analyse traditionnelle ; elles intègrent massivement l’IA en complément direct de leur BI. Avec **Copilot** et les **capacités d’IA générative** intégrées nativement à Fabric, vous accélérez drastiquement le développement de vos produits data. Vos équipes data pourront collaborer sur une seule et même plateforme au lieu d’avoir un service data différent pour chaque besoin (ETL, ML, …). Ce n’est plus seulement de la restitution visuelle : c’est un véritable levier de valeur ajoutée pour automatiser les insights, interroger vos données en langage naturel et transformer chaque utilisateur en un décideur “augmenté”.

Pour aller plus loin sur Microsoft Fabric, j’ai décortiqué pour vous tous ses bénéfices dans ce post exclusif :

[#### Microsoft Fabric : Révolution ou simple rebranding ?

[Antoine Wang](https://substack.com/profile/410602111-antoine-wang)

·

Feb 10

[Read full story](https://antoinewang.substack.com/p/microsoft-fabric)](https://antoinewang.substack.com/p/microsoft-fabric)

---

## 📊 Equivalence des SKUs : De Power BI Premium à Microsoft Fabric

Microsoft a conçu une correspondance directe entre les anciens **P-SKU** (Power BI Premium) et les nouveaux **F-SKU** (Fabric). Cette équivalence repose sur la puissance de calcul brute, passant des vCores Power BI aux **Capacity Units (CU)** de Fabric.

#### 💡 Tableau de correspondance

Comme vous pouvez le voir sur ce comparatif, la transition suit une logique simple de multiplication par 8 pour obtenir le nombre de CU nécessaires :

* **P1 (8 vCores)** devient un **F64 (64 CU)**.
* **P2 (16 vCores)** devient un **F128 (128 CU)**
* …

**Ce qu’il faut retenir :** Bien que l’équivalence soit directe en termes de puissance, Fabric offre une granularité bien plus fine.

---

## La granularité des SKU : La fin du 'Tout ou Rien'

**Concrètement, qu’est-ce que ce tableau nous apprend ?**

* Regardez la première ligne : **la F2**.
* C’est la porte d’entrée de l’écosystème. Pour environ **262 $ par mois** (en Pay-as-you-go), vous avez accès à **toute** la plateforme Fabric. Data Engineering, Data Science, Real-Time Analytics... tout est inclus, sans bridage de fonctionnalités.
* C’est une révolution par rapport au ticket d’entrée à 5 000 € de l’époque Power BI Premium Capacity.

Mais la véritable puissance de ce modèle réside dans deux leviers financiers pour votre DSI :

**1. Le choix du mode de consommation (CAPEX vs OPEX)**

* **Pay-as-you-go (Flexible) :** Idéal pour démarrer, tester un projet ou gérer des pics de charge. Vous payez ce que vous consommez.
* **Réservation (Économique) :** Une fois votre charge de travail stabilisée, vous pouvez réserver votre capacité sur 1 an. Le tableau est formel : l’économie est **d’environ 40 %** (une F2 passe de ~262 $à ~156$ mensuels).

**2. La capacité à “Pauser” (Pause & Resume)**

* Contrairement aux anciennes capacités Power BI Premium qui tournaient 24/7 (même le dimanche quand personne ne travaillait), les capacités Fabric (F) peuvent être **mises en pause**.
* Si vous n’utilisez votre F64 que pendant les heures de bureau, vous ne payez que ces heures-là. C’est une optimisation impossible auparavant.

⚠️ **Le point de vigilance pour les décideurs :**

* Si la F2 permet de tout *faire* techniquement, elle ne permet pas de tout *partager* gratuitement.
* La “ligne magique” reste à partir de la capacité **F64**. C’est à partir de ce SKU (environ 5 000 $ en réservé) que vous débloquez les “Free Viewers”, permettant à vos utilisateurs de consulter les rapports Power BI sans licence Pro individuelle.

> **En résumé :** Commencez petit avec une F2 ou F4, validez la valeur, puis montez en puissance (Scale-up) vers une F64 uniquement si votre volume d’utilisateurs le justifie.

Maintenant, voyons concrètement quels sont les prérequis pour préparer une transition fluide des P-SKU vers les F-SKU.

---

## Check-list technique : Évitez les "bloquants" Azure avant de lancer Fabric

Passer de Power BI Premium Capacity à Fabric Capacity ne se fait pas d’un simple clic dans le portail Office. Cela commence dans Azure. Je vois souvent des déploiements bloqués par de simples oublis. Voici votre check-list pour préparer votre environnement Azure sereinement.

### 1. La cohérence des Régions

Avant de déployer, vérifiez la région de votre tenant Power BI actuel.

* **L’impératif :** Votre nouvelle capacité Fabric doit être créée dans la **même région** que vos ressources existantes.

Dans [Power BI](https://app.fabric.microsoft.com/home?experience=power-bi),

* Cliquer sur l’icône point d’interrogation et sélectionner « À propos de Power BI ».
* Identifier votre région de stockage de données

### 2. Un abonnement Azure actif et budgété

Cela semble évident, mais c’est la base de tout. Votre abonnement doit être **Active** dans le [portail Azure](https://portal.azure.com/#home).

* **Le conseil d’expert :** Assurez-vous que cet abonnement est déjà rattaché à un centre de coûts ou à un budget défini pour éviter toute coupure de service imprévue.

### 3. Le bon niveau de droits (RBAC)

La création d’une capacité Microsoft Fabric n’est pas ouverte à tous. L’utilisateur responsable du déploiement doit posséder l’un des deux rôles suivants sur l’abonnement ou du Groupe de Ressources :

* **Owner** (Propriétaire) : Accès total à toutes les ressources et gestion des accès.
* **Contributor** (Contributeur) : Accès total pour créer et gérer les ressources, sans pouvoir donner d'accès à d'autres utilisateurs.

**Comment vérifier (ou demander) vos droits ?**

Pour s’assurer que vous disposez des droits nécessaires avant de vous lancer, rendez-vous dans la section **Access control (IAM)** de votre abonnement/groupe de ressources Azure.

1. Dans l’onglet “**Check access**”, vérifiez que vous apparaissez bien avec le rôle **Owner** ou **Contributor**.

2. **Ajout de rôle** : Si vous êtes administrateur de l’abonnement et que vous devez déléguer ce droit à un collègue, cliquez sur le bouton **+ Add** puis sélectionnez **Add role assignment**.

3. **Sélection du rôle** : Dans l’écran suivant, naviguez dans l’onglet “**Privileged administrator roles”** pour trouver et sélectionner le rôle **Contributor** (ou Owner).

💡 **Note importante** : Sans l'un de ces deux rôles, l'option de création de la capacité Fabric sera grisée ou renverra une erreur d'autorisation lors de la validation finale. Si vous n'avez pas ces droits, contactez votre administrateur Azure pour qu'il vous assigne le rôle de **Contributeur** sur le groupe de ressources concerné.

### 4. L’enregistrement du “Resource Provider”

C’est l’étape technique la plus souvent oubliée. Pour que le service Fabric soit reconnu par votre abonnement, vous devez enregistrer le fournisseur de ressources dédié. Par défaut, un abonnement Azure n'active que les services de base.

#### La manipulation en 3 clics :

1. **Localisation** : Dans le menu latéral de votre abonnement, descendez jusqu’à la section **Settings** (Paramètres) et cliquez sur **Resource providers**.
2. **Recherche** : Tapez `Microsoft.Fabric` dans la barre de recherche.
3. **Action** : Si le statut est “NotRegistered”, sélectionnez la ligne et cliquez sur le bouton **Register** en haut de la page.

⏳ **Patience** : Le statut passera de "Registering" à **Registered** en quelques minutes. Une fois le voyant au vert, la voie est libre pour déployer votre capacité !

### 5. La validation des Quotas (F-SKUs)

Chaque souscription Azure possède des limites par défaut. Avant de vous lancer, vous devez impérativement valider que le **SKU** souhaité (F2, F4, F64, etc.) est disponible et autorisé dans votre zone géographique.

#### 🔍 Étape 1 : Vérifier votre quota de capacité actuelle

Dans le menu de votre abonnement, rendez-vous dans la section **Quotas** (souvent située sous l’onglet *Settings*). Filtrez ensuite la liste par le fournisseur **Microsoft.Fabric** pour isoler les ressources concernées.

Vous pourrez alors voir, par région, le nombre d’unités de capacité déjà utilisées par rapport au maximum autorisé (ex: “2 of 64”).

#### 🛠️ Étape 2 : Ajuster si nécessaire

Si le quota affiché est insuffisant pour votre projet (par exemple, si vous voyez **“0 of 0”**), vous ne pourrez pas finaliser la création de votre capacité Fabric.

* **Action** : Cliquez sur l’icône de crayon dans la colonne **Request adjustment** à droite de la ligne correspondante.
* **Alternative** : Si le bouton n’est pas disponible, ouvrez un ticket au support Microsoft pour demander l’augmentation vers le SKU nécessaire (ex: passer à un quota permettant un F64).

### 6. Anticiper la Réservation d’Instance (RI) pour le 24/7

Si votre capacité Fabric nécessite une disponibilité constante (**24h/24, 7j/7**) sans interruption de service, la question du coût devient centrale. C'est ici qu'intervient la **Réservation d'Instance.**

#### Le principe : Engagement = Économies

Contrairement au modèle **“Pay-as-you-go”** (paiement à l’usage) où vous payez chaque heure de fonctionnement au prix fort, la réservation vous permet de vous engager sur une durée fixe (1 an ou 3 ans).

* **Avantage** : Une réduction drastique sur votre facture, souvent autour de **40% d’économie** par rapport au prix public.
* **Prérequis** : Assurez-vous d’avoir le budget validé pour un paiement initial ou un engagement mensuel fixe.

#### Comment procéder ?

Dans le portail Azure, recherchez le service **Reservations**, cliquez sur “Acheter” et sélectionnez **Microsoft Fabric** dans la liste des services éligibles.

#### 💡 Le conseil d’expert : Ne vous précipitez pas !

N’activez la réservation qu’une fois votre **SKU cible (F-SKU)** stabilisé après quelques semaines d’utilisation réelle.

> **Attention** : La réservation est liée à une capacité spécifique. Si vous vous engagez sur un F64 et que vous vous rendez compte plus tard qu’un F32 suffit, ou qu’un F128 est nécessaire, vous devrez gérer un échange ou un ajustement de réservation pour ne pas perdre l’avantage financier. **Testez en Pay-as-you-go, optimisez, puis réservez !**

---

## Conclusion : La migration n’est pas une fin, c’est un début.

Passer du modèle P-SKU aux capacités Fabric (F-SKU) peut sembler intimidant au premier abord, surtout avec ces nouvelles mécaniques Azure. Mais ne vous y trompez pas : c’est l’occasion de repenser votre architecture pour plus de flexibilité.

Vous ne faites pas que changer de licence ; vous passez d’une simple plateforme de BI à un écosystème Data complet, prêt pour l’IA et unifié par le OneLake.

> Une question sur votre migration ? Répondez simplement à cet email ou ce post, je lis tous vos messages.

À la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

### 📚 Ressources pour aller plus loin

Pour approfondir le sujet, je vous recommande ces lectures essentielles :

* **Documentation Microsoft :** [Aperçu de la capacité Microsoft Fabric](https://learn.microsoft.com/fr-fr/fabric/enterprise/licenses)
* **Guide de tarification :** [Calculateur Azure](https://www.microsoft.com/en-us/microsoft-fabric/capacity-estimator)
* **Guide d’automatisation :** [Automate your migration to Microsoft Fabric capacities](https://www.microsoft.com/en-us/microsoft-fabric/blog/2024/12/02/automate-your-migration-to-microsoft-fabric-capacities)
* **Blog Microsoft Fabric :** [Annonces et mises à jour](https://blog.fabric.microsoft.com/fr-fr/blog/)
