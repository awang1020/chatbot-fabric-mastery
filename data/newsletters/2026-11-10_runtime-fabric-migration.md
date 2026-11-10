---
title: Runtime Fabric 1.2 : migrer vers 1.3 ou 2.0 ? (+code)
url: https://blog.antoinewang-tech.com/p/runtime-fabric-migration
date: 2026-11-10
author: Antoine Wang
source: substack
---

# Runtime Fabric 1.2 : migrer vers 1.3 ou 2.0 ? (+code)

Hello les masters Fabric 👋

Quand vous exécutez un Notebook ou un Spark Job dans Microsoft Fabric, vous utilisez un **Runtime Spark**. Derrière ce terme se cache toute la pile qui fait tourner vos traitements : Apache Spark, Python, Java, Scala, Delta Lake et leurs différentes dépendances.

Et tant que tout fonctionne, on y prête rarement attention. Jusqu’au jour où une version arrive en fin de support, où une bibliothèque n’est plus compatible, ou qu’une montée de version change le comportement de votre code.

C’est exactement le sujet du jour : **comment sortir de Runtime 1.2 et choisir intelligemment entre Runtime 1.3 et Runtime 2.0 ?**

---

## ⚡ En 30 secondes

> **Ce qu’il faut retenir :**
>
> * **Runtime 2.0 par défaut** si vos dépendances sont compatibles.
> * **Runtime 1.3 uniquement comme pont temporaire** lorsqu’un blocage technique documenté empêche 2.0.
> * **Inventoriez Workspaces ET Environments**, car changer le Runtime par défaut du Workspace ne suffit pas lorsqu’un Environment impose sa propre version.
>
>   J’ai automatisé une partie de ce travail dans un Notebook Fabric que je partage plus bas.

---

## Un Fabric Runtime

Un Fabric Runtime est la brique d’exécution de vos workloads Spark. Il regroupe Spark, Delta Lake, Java, Scala, Python, R et le système d’exploitation : changer sa version modifie le moteur de calcul et ses dépendances. Retrouvez vos paramètres spark dans les paramètres de vos workspaces.

---

### 1) Runtime 1.2 : rester n’est plus une option

Runtime 1.2 repose sur Spark 3.4.1, Python 3.10, Java 11, Scala 2.12.17 et Delta Lake 2.4. Ces versions expliquent pourquoi vos traitements peuvent encore fonctionner, mais elles ne changent pas le statut du produit : End of Support.

Microsoft ne fournit plus de bug fixes, de mises à jour de sécurité ni de remédiations de vulnérabilités. La désactivation progressive signifie aussi qu’aucune continuité des jobs n’est garantie.

L’erreur classique sur le terrain : attendre le premier job en échec pour lancer l’inventaire. À ce moment-là, vous ne faites plus une migration, vous gérez un incident avec une dépendance déjà hors support.

**Mon conseil :** Traitez chaque artefact encore en 1.2 comme une dette technique datée. L’inventaire doit commencer maintenant, même si la migration de production attend encore sa fenêtre de changement.

---

### 2) Runtime 1.3 ou 2.0 : le vrai arbitrage

Voici les composants actuels publiés :

**Runtime 1.3 est le palier de compatibilité.** Vous restez dans la famille Spark 3, Java 11 et Scala 2.12. Le risque porte surtout sur Python 3.11, Spark 3.5, Delta 3.2 et les bibliothèques préinstallées. Son LTS annoncé prolonge le support jusqu’en mars 2027.

**Runtime 2.0 est la cible durable.** Son support est annoncé jusqu’au 31 août 2028. Spark 4.1, Java 21, Scala 2.13 et Python 3.13 peuvent toutefois casser JARs, wheels, imports ou comportements Spark SQL. Il reste opt-in avant son déploiement par défaut prévu fin septembre 2026.

**Mon conseil :** Pour un nouveau workload, partez sur 2.0. Pour un workload 1.2 critique avec des JARs ou wheels non encore certifiés, utilisez 1.3 comme pont contrôlé, avec une date de sortie explicite.

---

### 3) Inventorier les deux niveaux : Workspace et Environment

Le Runtime du Workspace sert de défaut aux artefacts qui n’ont pas d’Environment attaché.

Un Environment peut toutefois imposer son propre Runtime à un Notebook ou à une Spark Job Definition. Les deux inventaires sont donc obligatoires.

J’ai publié un Notebook dans mon GitHub qui automatise cette étape et la migration :

**[Notebook Fabric Runtime Upgrade sur GitHub](https://github.com/awang1020/ms-fabric-upgrade-runtime/blob/main/Notebook_runtime_upgrade.ipynb)**

Le Notebook :

* inventorie les Workspaces et tous leurs Environment items paginés ;
* fonctionne en **dry run** et exige allowlist + confirmation avant écriture ;
* bloque les Environments avec des changements compute non publiés ;
* suit la publication asynchrone, relit le Runtime effectif et conserve les erreurs.

Configuration de départ :

```
TARGET_RUNTIME = "2.0"  # Ou "1.3"
TARGET_WORKSPACES = []
EXECUTE_MIGRATION = False
CONFIRMATION = ""
```

En dry run, une liste vide inventorie tous les Workspaces accessibles. En écriture, elle devient obligatoire et la confirmation doit être **UPGRADE TO 1.3 ou 2.0**.

---

### 4) Permissions : quels droits pour changer le Runtime ?

Les permissions nécessaires dépendent du niveau auquel vous souhaitez effectuer la modification.

* **Au niveau du Workspace**, la modification des paramètres Spark, dont le Runtime par défaut, nécessite le rôle **Workspace Admin**.
* **Au niveau d’un Environment**, les rôles **Member et Contributor** peuvent modifier sa configuration lorsque la personnalisation du compute au niveau des items est autorisée par le Workspace Admin. Le changement de Runtime doit ensuite être **sauvegardé et publié** pour devenir effectif.
* Le rôle **Viewer** ne permet pas de modifier les items ou leur configuration.
* Les paramètres Spark configurés **au niveau de la Capacité** nécessitent quant à eux les droits **Capacity Admin**.

⚠️ **Attention : les permissions Workspace et Environment sont deux sujets distincts.** Modifier le Runtime par défaut du Workspace ne modifie pas automatiquement le Runtime explicitement configuré dans un Environment.

#### 🔑 Et dans mon Notebook ?

Pour automatiser la migration, mon Notebook intègre également une logique d’**élévation temporaire des privilèges en Workspace Admin** lorsque celle-ci est nécessaire pour modifier le Runtime du Workspace.

L’objectif est de respecter le principe du **moindre privilège** :

**Élévation temporaire → Migration → Vérification → Retrait du rôle**

Le rôle Workspace Admin n’a donc pas vocation à être conservé après l’opération : le Notebook réalise la migration puis **retire l’élévation afin de revenir aux permissions initiales**.

---

### 5) Migrer par vagues, pas par tenant

Migrez selon les frontières de votre plateforme :

1. **DEV** : un Workspace, ses Environments, puis les workloads représentatifs.
2. **UAT** : mêmes artefacts, données et déclenchements proches de la production.
3. **PROD** : fenêtre contrôlée, nouvelles sessions Spark, validation fonctionnelle et surveillance des premiers runs.

**Mon conseil :** Commencez par un Workspace de développement peu critique mais représentatif. Un pilote sans bibliothèques custom, sans Spark Job Definition et sans table partagée ne valide rien pour votre production.

---

## 🥇 La Règle d’Or

**Si tu dois retenir une chose : sortir de Runtime 1.2 est urgent, mais choisir Runtime 2.0 sans test n’est pas une stratégie. Inventorie les Workspaces et Environments, valide les dépendances sur un pilote, puis migre par vagues.**

L’impact terrain est concret : Chaque équipe sait quel moteur de calcul exécute ses artefacts, quelles dépendances ont été validées et pourquoi un workload reste temporairement en 1.3 ou passe en 2.0.

***Votre inventaire Fabric sait-il aujourd’hui distinguer le Runtime du Workspace de celui de chaque Environment ?***

Répondez simplement à cet email ou ce post, je lis tous vos messages.

Bon mardi et à la semaine prochaine pour continuer à explorer ensemble les entrailles de Fabric !

---

## **🔗** À lire dans Fabric Mastery

* [OneLake Microsoft Fabric : comprendre le socle partagé](https://blog.antoinewang-tech.com/p/onelake-microsoft-fabric-guide) : replacer Spark et Delta Lake dans le stockage commun.
* [Data Stores Fabric : Lakehouse, Warehouse ou Eventhouse](https://blog.antoinewang-tech.com/p/data-stores-microsoft-fabric-comparatif) : identifier les artefacts qui dépendent réellement de Spark.
* [Gouvernance des Workspaces Microsoft Fabric](https://blog.antoinewang-tech.com/p/gouvernance-workspaces-microsoft-fabric) : structurer les vagues DEV, UAT et PROD.

---

## 📚 Ressources pour aller plus loin

Pour approfondir le sujet et passer à la pratique, je vous recommande ces lectures essentielles issues de la documentation officielle :

* 📘 [Fabric Runtime 1.2 (EOS)](https://learn.microsoft.com/fabric/data-engineering/runtime-1-2) : statut et risques.
* 📘 [Apache Spark runtimes in Fabric](https://learn.microsoft.com/fabric/data-engineering/runtime) : comparaison 1.3 / 2.0.
* 🔗 [Fabric Runtime 1.3](https://learn.microsoft.com/fabric/data-engineering/runtime-1-3) : composants et compatibilité.
* 🔗 [Fabric Runtime 2.0](https://learn.microsoft.com/fabric/data-engineering/runtime-2-0) : composants et limites.
* 📘 [Lifecycle of Apache Spark runtimes](https://learn.microsoft.com/fabric/data-engineering/lifecycle) : GA, LTS et fin de support.
* 🛠️ [Manage Fabric Environments through public APIs](https://learn.microsoft.com/fabric/data-engineering/environment-public-api) : APIs stables.
