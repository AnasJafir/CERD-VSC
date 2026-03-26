# Guide d'Utilisation : Application d'Ingestion CERD

Ce document est un guide complet pour utiliser l'application web d'ingestion intelligente du Centre d'Études et de Recherche Documentaire (CERD).

## 📌 Présentation
L'application permet d'importer facilement des articles (formats PDF ou Microsoft Word), d'en extraire automatiquement les métadonnées grâce à l'Intelligence Artificielle (Titre, Auteur, Thème, Mots-clés, etc.), d'extraire les images contenues dans le document, et d'enregistrer le tout structuré dans une base de données **Airtable**.

---

## 🚀 Comment utiliser l'Assistant IA (Recommandé)

Ce mode permet de traiter un ou plusieurs documents simultanément (Batch) en déléguant la lecture à l'IA.

### Étape 1 : Choisir le niveau d'Analyse
Dans la barre latérale gauche, sous la section **"Périmètre d'import"**, vous avez deux choix :
- **Métadonnées Uniquement** : L'IA ne lit le document que pour extraire les informations clés (Titre, Mots-clés, Résumé). Idéal pour un traitement ultra-rapide.
- **Complet (Images + Document)** : L'IA extrait les métadonnées, mais le système fouille également le document pour **isoler les images (graphiques, photos)** et télécharge le fichier source complet.

### Étape 2 : Importer les documents
1. Au centre de l'écran, utilisez la zone **"Déposez vos articles ici"**.
2. Vous pouvez glisser-déposer vos fichiers (PDF ou DOCX) directement depuis votre ordinateur.
3. Vous pouvez déposer **plusieurs fichiers en même temps** (exemple : 5 à 10 fichiers pour une session).

### Étape 3 : Lancer l'Analyse
1. Cliquez sur le bouton bleu **"Lancer l'analyse de X fichiers 🧠"**.
2. Une barre de progression s'affiche. L'IA lit les documents un par un. (Comptez environ 10 à 15 secondes par article).
3. Ne quittez pas la page pendant le traitement.

### Étape 4 : Vérification et Sélection des Images
Une fois l'analyse terminée, la liste de vos documents apparaît.
Pour chaque document :
1. **Passez en revue les métadonnées** (Titre, Série, Thème, Extrait) générées par l'IA.
2. Si vous êtes en mode "Complet", **les images extraites du document s'affichent**. Vous pouvez décocher les images inutiles (comme les logos de bas de page) pour ne garder que les graphiques pertinents.

### Étape 5 : Sauvegarder dans Airtable
1. En bas du document vérifié, cliquez sur **"Valider et Importer"**.
2. L'application envoie alors les données vers la base Airtable.
3. Si vous avez plusieurs documents, une fois le dernier validé, **le formulaire se réinitialise automatiquement** pour un nouveau lot !

---

## ✍️ Comment utiliser la Saisie Manuelle

Si vous avez un document physique (papier) ou des informations non présentes dans un fichier, vous pouvez utiliser ce mode.
1. Dans la barre latérale gauche, passez le "Mode d'import" sur **"Saisie Manuelle ✍️"**.
2. Un formulaire classique apparaît.
3. Remplissez simplement les champs (Titre, Thème, Contenu, etc.).
4. Vous pouvez importer des images manuellement.
5. Cliquez sur "Créer l'Article" à la fin du formulaire.

---

## 🛠️ Résolution des problèmes courants

- **Problème : Les champs restent vides après l'analyse.**
  *Cause :* L'IA n'a pas pu lire le document (PDF scanné sans texte, ou document protégé).
  *Erreur signalée :* Message rouge "Impossible d'extraire le texte" ou "Erreur IA".
  
- **Problème : "Manque de configuration Airtable".**
  *Cause :* L'application a perdu sa connexion.
  *Solution :* Rechargez la page web (F5) ou prévenez l'administrateur technique.

- **Problème : L'application semble figée pendant l'analyse.**
  *Cause :* Vous avez importé trop de documents d'un coup (ex: 50 documents).
  *Solution :* Limitez-vous à des lots plus petits (10 maximum) pour des performances optimales sur le navigateur Web.
