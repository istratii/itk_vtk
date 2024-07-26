# Objectif

L'objectif est de réaliser le suivi des changements d'une tumeur à partir de deux scans effectués sur un même patient à des dates différentes, ce qu’on appelle également une “étude longitudinale”.

# Step 1: Données

Les données utilisées pour ce projet sont des images IRM 3D du cerveau. Les images sont stockées dans le format NRRD et sont disponibles dans le répertoire ./Data. Les fichiers d'image sont:

- case6_gre1.nrrd : Image de référence (fixe)
- case6_gre2.nrrd : Image à aligner (mobile)

Ces images sont lues à l'aide de la bibliothèque ITK et sont utilisées pour les étapes suivantes du projet.

# Step 2: Recalage d'images

Ce projet se concentre sur le recalage d'images IRM 3D du cerveau afin de faciliter l'analyse et la détection de tumeurs. Plusieurs méthodes de recalage ont été testées pour identifier la plus efficace. Voici un résumé des méthodes testées et des raisons pour lesquelles nous avons retenu la méthode finale.

## Méthodes Testées

1. **Transformation de Translation**

   - **Description** : Aligne les images en ajustant uniquement la translation.
   - **Résultats** : Offre un alignement rapide et efficace, avec des résultats satisfaisants pour les images IRM du cerveau dans ce projet spécifique. Cette méthode a produit les meilleurs résultats en termes de rapidité et de qualité d'alignement.

2. **Transformation Affine**

   - **Description** : Prend en compte la translation, la rotation, l'échelle et le cisaillement.
   - **Résultats** : Meilleure que la transformation de translation, mais introduit parfois des distorsions et n'est pas toujours stable pour les structures anatomiques complexes.

3. **Transformation Rigide (Euler 3D Transform)**
   - **Description** : Prend en compte la translation et la rotation pour une transformation de corps rigide. Implémentée avec une stratégie multi-résolution pour améliorer la convergence et la précision.
   - **Résultats** : Offre un alignement précis mais est plus lente et nécessite des ajustements fins des paramètres pour une bonne convergence. Dans ce projet, elle n'a pas surpassé la méthode de translation en termes de résultats pratiques.

## Méthode Retenue

**Transformation de Translation**

- **Précision** : Offre un alignement suffisant pour les images IRM du cerveau sans nécessiter de rotations ou de changements d'échelle.
- **Rapidité** : Plus rapide à exécuter, ce qui est crucial pour des traitements en temps réel ou des analyses nécessitant un traitement rapide.
- **Simplicité** : Moins de paramètres à ajuster, réduisant ainsi la complexité et le risque de divergence.

## Paramètres Optimisés

Pour optimiser le recalage, les paramètres suivants ont été utilisés :

- **Taux d'apprentissage** : 4.0
- **Nombre d'itérations** : 200
- **Stratégie multi-résolution** : Un niveau de résolution

# Step 3: Segmentation des tumeurs

Pour détecter les tumeurs dans les images IRM, la segmentation a été effectuée en utilisant une approche de seuil connecté basée sur des points de départ spécifiques dans l'image. Les étapes incluent:

1. **Segmentation Initiale**:

   - **Méthode**: Nous avons utilisé la méthode de seuil connecté en partant de points de départ (seed points) spécifiques dans l'image. Cette méthode permet de segmenter des régions d'intérêt basées sur l'intensité des voxels autour des points de départ.
   - **Justification**: Cette méthode a été choisie pour sa simplicité et son efficacité à segmenter les régions homogènes des tumeurs à partir de points de départ connus. Les seuils d'intensité ont été ajustés (empiriquement) pour capturer précisément les régions tumorales.

2. **Fermeture Morphologique Binaire**:

   - **Méthode**: Après la segmentation initiale, une opération de fermeture morphologique est appliquée pour éliminer les petits trous et améliorer la qualité des contours segmentés.
   - **Justification**: La fermeture morphologique aide à affiner les bords des tumeurs segmentées en comblant les petits trous et en supprimant les artefacts, ce qui améliore la précision globale de la segmentation.

3. **Exploration et Optimisation**:

   - **Travail Exploratoire**: Nous avons testé plusieurs points de départ et plages de seuils pour optimiser la segmentation. Des itérations ont été effectuées pour ajuster les paramètres afin d'obtenir les meilleurs résultats possibles.
   - **Résultats**: La segmentation résultante a montré une détection précise des tumeurs dans les images fixes et alignées, avec une amélioration notable après l'application de la fermeture morphologique.

Cette approche a permis de produire des cartes binaires représentant les régions des tumeurs dans les images de référence et les images alignées.

# Step 4: Analyse et visualisation des changements

Pour analyser les changements entre les deux images segmentées et visualiser les différences, la méthode suivante a été utilisée :

1. **Calcul de la Différence**:

   - **Méthode**: La différence entre les deux images segmentées est calculée voxel par voxel. Cette opération génère une carte de différence qui met en évidence les variations entre les images au niveau des tumeurs.
   - **Justification**: Calculer la différence voxel par voxel permet de quantifier les changements dans la taille et l'intensité des tumeurs entre les deux images, fournissant une base solide pour l'analyse visuelle.

2. **Visualisation en 3D**:

   - **Méthode**: La carte de différence est convertie en une image VTK, qui est ensuite visualisée en 3D à l'aide de la bibliothèque VTK. Les volumes sont rendus avec des fonctions de transfert de couleur et d'opacité pour mettre en évidence les différences entre les images.
   - **Représentation des Couleurs**:
     - **Rouge**: Représente les zones où la tumeur a augmenté en taille ou en intensité entre les deux images. Cela indique une croissance ou un développement dans ces régions.
     - **Vert**: Représente les zones où la tumeur a diminué en taille ou en intensité entre les deux images. Cela indique une réduction ou une régression dans ces régions.
     - **Noir (ou Transparent)**: Pas de changement.

3. **Interactions et Analyse Quantitative**:

   - **Utilisation des Transfer Functions**: Des fonctions de transfert de couleur et d'opacité ont été utilisées pour mieux visualiser les changements. Les différentes couleurs et niveaux d'opacité aident à distinguer clairement les zones de croissance et de régression des tumeurs.
   - **Interactivité**: La visualisation 3D permet une interaction en temps réel, permettant à l'utilisateur de tourner, zoomer et explorer les différences de manière intuitive.
   - **Analyse Quantitative**: La carte de différence fournit également une base pour une analyse quantitative des changements, permettant de mesurer précisément l'évolution des tumeurs.

Cela permet de voir clairement l'évolution des tumeurs au fil du temps et d'effectuer une analyse visuelle des changements.

# Répartition de tâches

| Tâche | Auteur(s)        |
| ----- | ---------------- |
| Step1 | Étienne, Nicolae |
| Step2 | Étienne          |
| Step3 | Nicolae          |
| Step4 | Nicolae          |
