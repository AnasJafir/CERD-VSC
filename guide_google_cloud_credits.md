# Guide étape par étape : Obtenir les 300 $ de crédits Google Cloud (GCP)

Ce guide explique comment créer un compte, réclamer les crédits offerts et lier ce compte à l'API Gemini pour contourner les limites de requêtes (Rate Limits).

## 1. Critères d'éligibilité (Pour bénéficier des 300 $)

Pour que Google vous accorde les crédits promotionnels, vous devez respecter ces conditions :
- **Nouveau client Google Cloud** : Vous n'avez jamais été un client payant de Google Cloud par le passé.
- **Essai gratuit inédit** : Vous (et l'adresse email utilisée) n'avez jamais activé d'essai gratuit sur Google Cloud auparavant.
- **Moyen de paiement valide** : Vous devez fournir une carte bancaire ou un compte bancaire valide. **Rassurez-vous :** Google n'effectuera aucun prélèvement à la fin des crédits ou des 90 jours, à moins que vous ne mettiez manuellement à niveau (upgrade) votre compte vers un compte payant complet. C'est uniquement pour vérifier votre identité.

## 2. Étapes pour créer le compte et réclamer les crédits

### Étape 1 : Créer un nouveau compte Google (Optionnel mais recommandé)
Si votre adresse Gmail actuelle a déjà été utilisée sur Google Cloud, créez-en une nouvelle (ex: `votre.nom.cerd@gmail.com`).

### Étape 2 : Activer l'Essai Gratuit
1. Rendez-vous sur la page officielle : [Google Cloud Free Trial](https://cloud.google.com/free).
2. Cliquez sur le bouton **Commencer gratuitement** (Get started for free).
3. Connectez-vous avec votre compte Google.

### Étape 3 : Remplir les informations du profil
1. Sélectionnez votre **Pays**.
2. Acceptez les conditions d'utilisation.
3. Passez à l'étape du **Profil de paiement**.
4. Cochez le type de compte (Individuel ou Entreprise).
5. Saisissez vos coordonnées de carte bancaire. 
*(Une petite empreinte de vérification de 0$ ou 1$ peut apparaître sur votre relevé bankaire, elle sera annulée immédiatement).*
6. Validez. Vous verrez alors une bannière en haut de votre console confirmant que vous disposez de 300 $ valables pendant 90 jours.

## 3. Lier ce compte à Gemini (Google AI Studio)

Pour utiliser ce compte facturé avec notre script d'ingestion et éliminer les erreurs de limite :

1. Un **Projet Cloud** a été créé par défaut lors de votre inscription (ex: `My First Project`).
2. Allez sur **[Google AI Studio](https://aistudio.google.com/)** avec le même compte Google.
3. Cliquez sur **Get API key** à gauche.
4. Cliquez sur **Create API key**.
5. Au lieu de créer une clé sur un projet gratuit, sélectionnez **votre nouveau projet Google Cloud** (qui a la facturation active avec les crédits) dans le menu déroulant.
6. Copiez la clé générée.

## 4. Mettre à jour l'application CERD

1. Ouvrez votre fichier `.env` dans VS Code.
2. Remplacez l'ancienne clé par la nouvelle :
   ```env
   GEMINI_API_KEY=AIzaSyVotreNouvelleCleIci...
   ```
3. Sauvegardez le fichier.
4. Relancez le script Python d'ingestion. Vous êtes désormais en mode "Pay-as-you-go" couvert par les 300 $ !