# VintedManager - Gestion de Comptabilité

## Description
**VintedManager** est une application Python permettant de gérer une base de données SQLite pour la comptabilité des ventes de produits. Elle inclut des fonctionnalités de gestion de stock, d'ajout et de modification de produits, ainsi que le calcul des métriques financières.

## Fonctionnalités
- **Ajout de produits** avec des détails comme le type, la marque, la taille, la couleur, l'état, le prix d'achat, la date d'achat, etc.
- **Modification et suppression de produits** en base de données.
- **Affichage du stock** des produits encore disponibles.
- **Calcul des métriques financières** : chiffre d'affaires, bénéfice brut et net.
- **Prise en charge des taxes** avec modification du taux d'imposition.

## Menu principal :
   - `1` : Ajouter un produit
   - `2` : Modifier/Supprimer un produit
   - `3` : Voir le stock
   - `4` : Voir les métriques financières
   - `5` : Modifier le taux d'imposition
   - `6` : Quitter

## Base de données
- `products` : contient les produits avec leurs détails (prix d'achat, estimation, prix de vente, etc.).
- `settings` : stocke les paramètres globaux (ex: taux d'imposition).

## Calcul des Métriques
- **Chiffre d'affaires (CA)** : Somme des prix de vente.
- **Bénéfice brut** : Somme des (prix de vente - prix d'achat).
- **Bénéfice net** : Bénéfice brut après déduction des taxes.

