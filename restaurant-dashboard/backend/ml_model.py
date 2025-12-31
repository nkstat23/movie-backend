"""
Module de Machine Learning pour prédire les scores d'inspection des restaurants
et classifier les niveaux de risque sanitaire.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
import joblib 
import os

class RestaurantMLModel:
    """
    Modèle ML pour analyser et prédire les performances sanitaires des restaurants
    """
    
    def __init__(self):
        self.score_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.risk_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.cuisine_encoder = LabelEncoder()
        self.borough_encoder = LabelEncoder()
        self.is_trained = False
        
    def extract_features(self, restaurants_data):
        """
        Extrait les features à partir des données brutes des restaurants
        
        Args:
            restaurants_data: Liste de dictionnaires contenant les données des restaurants
            
        Returns:
            DataFrame avec les features, labels de score, labels de risque
        """
        features_list = []
        scores = []
        risk_levels = []
        
        for restaurant in restaurants_data:
            # Ignorer si pas de grades
            if not restaurant.get('grades') or len(restaurant['grades']) == 0:
                continue
                
            grades = restaurant['grades']
            
            # Calculer les statistiques historiques
            historical_scores = [g['score'] for g in grades]
            historical_grades = [g['grade'] for g in grades]
            
            # Features numériques
            avg_score = np.mean(historical_scores)
            max_score = np.max(historical_scores)
            min_score = np.min(historical_scores)
            std_score = np.std(historical_scores) if len(historical_scores) > 1 else 0
            num_inspections = len(grades)
            
            # Tendance (score le plus récent - moyenne)
            latest_score = historical_scores[0]
            score_trend = latest_score - avg_score
            
            # Compter les mauvaises notes (B, C, Z)
            bad_grades_count = sum(1 for g in historical_grades if g in ['B', 'C', 'Z'])
            bad_grades_ratio = bad_grades_count / num_inspections if num_inspections > 0 else 0
            
            # Features catégorielles
            cuisine = restaurant.get('cuisine', 'Unknown')
            borough = restaurant.get('borough', 'Unknown')
            
            # Calcul du niveau de risque (target pour classification)
            if avg_score <= 13:
                risk_level = 'Low'  # Faible risque
            elif avg_score <= 27:
                risk_level = 'Medium'  # Risque moyen
            else:
                risk_level = 'High'  # Risque élevé
            
            features_list.append({
                'cuisine': cuisine,
                'borough': borough,
                'avg_score': avg_score,
                'max_score': max_score,
                'min_score': min_score,
                'std_score': std_score,
                'num_inspections': num_inspections,
                'score_trend': score_trend,
                'bad_grades_ratio': bad_grades_ratio
            })
            
            scores.append(latest_score)
            risk_levels.append(risk_level)
        
        df = pd.DataFrame(features_list)
        
        return df, np.array(scores), np.array(risk_levels)
    
    def train(self, restaurants_data):
        """
        Entraîne les modèles de prédiction
        
        Args:
            restaurants_data: Liste de dictionnaires avec les données des restaurants
        """
        print("Extraction des features...")
        df_features, scores, risk_levels = self.extract_features(restaurants_data)
        
        if len(df_features) == 0:
            raise ValueError("Pas assez de données pour entraîner le modèle")
        
        print(f"Nombre d'exemples d'entraînement: {len(df_features)}")
        
        # Encoder les variables catégorielles
        df_features['cuisine_encoded'] = self.cuisine_encoder.fit_transform(df_features['cuisine'])
        df_features['borough_encoded'] = self.borough_encoder.fit_transform(df_features['borough'])
        
        # Sélection des features pour le modèle
        feature_columns = [
            'cuisine_encoded', 'borough_encoded', 'avg_score', 'max_score', 
            'min_score', 'std_score', 'num_inspections', 'score_trend', 'bad_grades_ratio'
        ]
        
        X = df_features[feature_columns].values
        
        # Entraîner le prédicteur de score
        print("Entraînement du prédicteur de score...")
        self.score_predictor.fit(X, scores)
        
        # Entraîner le classificateur de risque
        print("Entraînement du classificateur de risque...")
        self.risk_classifier.fit(X, risk_levels)
        
        self.is_trained = True
        print("Entraînement terminé avec succès!")
        
        # Afficher les importances des features
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': self.score_predictor.feature_importances_
        }).sort_values('importance', ascending=False)
        print("\nImportance des features:")
        print(feature_importance)
        
        return {
            'score_r2': self.score_predictor.score(X, scores),
            'risk_accuracy': self.risk_classifier.score(X, risk_levels),
            'num_samples': len(df_features)
        }
    
    def predict(self, restaurant_data):
        """
        Prédit le prochain score et niveau de risque pour un restaurant
        
        Args:
            restaurant_data: Dict avec les données d'un restaurant
            
        Returns:
            Dict avec prédictions
        """
        if not self.is_trained:
            raise ValueError("Le modèle doit être entraîné avant de faire des prédictions")
        
        # Extraire les features
        df_features, _, _ = self.extract_features([restaurant_data])
        
        if len(df_features) == 0:
            return None
        
        # Encoder
        df_features['cuisine_encoded'] = self.cuisine_encoder.transform(df_features['cuisine'])
        df_features['borough_encoded'] = self.borough_encoder.transform(df_features['borough'])
        
        feature_columns = [
            'cuisine_encoded', 'borough_encoded', 'avg_score', 'max_score', 
            'min_score', 'std_score', 'num_inspections', 'score_trend', 'bad_grades_ratio'
        ]
        
        X = df_features[feature_columns].values
        
        # Prédire
        predicted_score = float(self.score_predictor.predict(X)[0])
        predicted_risk = self.risk_classifier.predict(X)[0]
        risk_probabilities = self.risk_classifier.predict_proba(X)[0]
        
        # Mapper les probabilités aux classes
        risk_classes = self.risk_classifier.classes_
        risk_probs_dict = {risk_classes[i]: float(risk_probabilities[i]) for i in range(len(risk_classes))}
        
        return {
            'predicted_score': round(predicted_score, 1),
            'predicted_risk_level': predicted_risk,
            'risk_probabilities': risk_probs_dict,
            'current_avg_score': round(float(df_features['avg_score'].values[0]), 1),
            'num_inspections': int(df_features['num_inspections'].values[0])
        }
    
    def get_risk_statistics(self, restaurants_data):
        """
        Calcule des statistiques sur les niveaux de risque dans l'ensemble de données
        
        Returns:
            Dict avec les statistiques de risque
        """
        df_features, _, risk_levels = self.extract_features(restaurants_data)
        
        risk_counts = pd.Series(risk_levels).value_counts()
        total = len(risk_levels)
        
        return {
            'total_analyzed': total,
            'risk_distribution': {
                'Low': int(risk_counts.get('Low', 0)),
                'Medium': int(risk_counts.get('Medium', 0)),
                'High': int(risk_counts.get('High', 0))
            },
            'risk_percentages': {
                'Low': round(100 * risk_counts.get('Low', 0) / total, 1),
                'Medium': round(100 * risk_counts.get('Medium', 0) / total, 1),
                'High': round(100 * risk_counts.get('High', 0) / total, 1)
            }
        }
    
    def save_model(self, filepath='restaurant_ml_model.pkl'):
        """Sauvegarde le modèle entraîné"""
        if not self.is_trained:
            raise ValueError("Le modèle doit être entraîné avant d'être sauvegardé")
        
        joblib.dump({
            'score_predictor': self.score_predictor,
            'risk_classifier': self.risk_classifier,
            'cuisine_encoder': self.cuisine_encoder,
            'borough_encoder': self.borough_encoder
        }, filepath)
        print(f"Modèle sauvegardé dans {filepath}")
    
    def load_model(self, filepath='restaurant_ml_model.pkl'):
        """Charge un modèle pré-entraîné"""
        if os.path.exists(filepath):
            data = joblib.load(filepath)
            self.score_predictor = data['score_predictor']
            self.risk_classifier = data['risk_classifier']
            self.cuisine_encoder = data['cuisine_encoder']
            self.borough_encoder = data['borough_encoder']
            self.is_trained = True
            print(f"Modèle chargé depuis {filepath}")
            return True
        return False


# Instance globale du modèle
ml_model = RestaurantMLModel()
