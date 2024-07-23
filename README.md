# SOLUTION

# Recalage d'Images IRM du Cerveau

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


### Segmentation des tumeurs

### Analyse et visualisation des changements