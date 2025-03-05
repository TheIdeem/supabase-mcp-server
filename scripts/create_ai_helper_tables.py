import os
import sys
import json
from dotenv import load_dotenv
from supabase import create_client, Client

# Charger les variables d'environnement
load_dotenv()

# Récupérer les informations de connexion à Supabase
supabase_url = f"https://{os.getenv('SUPABASE_PROJECT_REF')}.supabase.co"
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_key:
    print("Erreur: Les variables d'environnement SUPABASE_PROJECT_REF et SUPABASE_SERVICE_ROLE_KEY doivent être définies.")
    sys.exit(1)

print(f"Connexion à Supabase à {supabase_url}")

# Créer le client Supabase
supabase: Client = create_client(supabase_url, supabase_key)

def create_ai_suggestions_table():
    """Crée la table ai_suggestions si elle n'existe pas déjà."""
    try:
        # Vérifier si la table existe déjà
        response = supabase.table('ai_suggestions').select('id').limit(1).execute()
        print("La table ai_suggestions existe déjà.")
        return True
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            print("La table ai_suggestions n'existe pas. Création en cours...")
            
            # Définir la structure de la table ai_suggestions
            ai_suggestions_definition = {
                "name": "ai_suggestions",
                "schema": "public",
                "comment": "Suggestions générées par l'IA pour aider les utilisateurs à configurer leurs recherches",
                "columns": [
                    {
                        "name": "id",
                        "type": "uuid",
                        "primaryKey": True,
                        "default": "uuid_generate_v4()"
                    },
                    {
                        "name": "user_id",
                        "type": "uuid",
                        "references": "users.id",
                        "onDelete": "CASCADE",
                        "notNull": True
                    },
                    {
                        "name": "created_at",
                        "type": "timestamp with time zone",
                        "default": "now()",
                        "notNull": True
                    },
                    {
                        "name": "updated_at",
                        "type": "timestamp with time zone",
                        "default": "now()",
                        "notNull": True
                    },
                    {
                        "name": "user_info",
                        "type": "jsonb",
                        "notNull": True,
                        "comment": "Informations fournies par l'utilisateur via le questionnaire"
                    },
                    {
                        "name": "suggestions",
                        "type": "jsonb",
                        "notNull": True,
                        "comment": "Suggestions générées par l'IA"
                    },
                    {
                        "name": "is_applied",
                        "type": "boolean",
                        "default": "false",
                        "notNull": True,
                        "comment": "Indique si l'utilisateur a appliqué une suggestion"
                    },
                    {
                        "name": "applied_suggestion_index",
                        "type": "integer",
                        "comment": "Index de la suggestion appliquée (si applicable)"
                    },
                    {
                        "name": "applied_at",
                        "type": "timestamp with time zone",
                        "comment": "Date à laquelle la suggestion a été appliquée"
                    }
                ],
                "indexes": [
                    {
                        "name": "ai_suggestions_user_id_idx",
                        "columns": ["user_id"]
                    },
                    {
                        "name": "ai_suggestions_created_at_idx",
                        "columns": ["created_at"]
                    }
                ],
                "enableRLS": True,
                "policies": [
                    {
                        "name": "ai_suggestions_user_policy",
                        "definition": "auth.uid()::text = user_id::text",
                        "check": None,
                        "operation": "ALL"
                    }
                ]
            }
            
            # Créer la table via l'API REST
            # Note: Cette partie est conceptuelle car l'API Supabase ne permet pas directement de créer des tables
            # En pratique, il faudrait utiliser l'interface SQL de Supabase ou une connexion directe à la base de données
            print("⚠️ La création de tables via l'API Supabase n'est pas directement supportée.")
            print("⚠️ Veuillez utiliser l'interface SQL de Supabase pour exécuter le script SQL suivant:")
            
            # Générer le SQL pour créer la table
            sql = """
-- Table pour stocker les suggestions générées par l'IA
CREATE TABLE IF NOT EXISTS public.ai_suggestions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
  user_info JSONB NOT NULL, -- Informations fournies par l'utilisateur via le questionnaire
  suggestions JSONB NOT NULL, -- Suggestions générées par l'IA
  is_applied BOOLEAN DEFAULT false NOT NULL, -- Indique si l'utilisateur a appliqué une suggestion
  applied_suggestion_index INTEGER, -- Index de la suggestion appliquée (si applicable)
  applied_at TIMESTAMP WITH TIME ZONE -- Date à laquelle la suggestion a été appliquée
);

-- Index pour améliorer les performances des requêtes
CREATE INDEX IF NOT EXISTS ai_suggestions_user_id_idx ON public.ai_suggestions(user_id);
CREATE INDEX IF NOT EXISTS ai_suggestions_created_at_idx ON public.ai_suggestions(created_at);

-- Commentaires sur la table
COMMENT ON TABLE public.ai_suggestions IS 'Suggestions générées par l''IA pour aider les utilisateurs à configurer leurs recherches';

-- Accorder les privilèges nécessaires
ALTER TABLE public.ai_suggestions ENABLE ROW LEVEL SECURITY;

-- Politique RLS pour ai_suggestions: les utilisateurs ne peuvent voir que leurs propres suggestions
CREATE POLICY ai_suggestions_user_policy ON public.ai_suggestions
  FOR ALL
  USING (auth.uid()::text = user_id::text);
"""
            print(sql)
            return False
        else:
            print(f"Erreur lors de la vérification de la table ai_suggestions: {e}")
            return False

def create_user_searches_table():
    """Crée la table user_searches si elle n'existe pas déjà."""
    try:
        # Vérifier si la table existe déjà
        response = supabase.table('user_searches').select('id').limit(1).execute()
        print("La table user_searches existe déjà.")
        return True
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            print("La table user_searches n'existe pas. Création en cours...")
            
            # Générer le SQL pour créer la table
            sql = """
-- Table pour stocker l'historique des recherches des utilisateurs
CREATE TABLE IF NOT EXISTS public.user_searches (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
  query JSONB NOT NULL, -- Configuration de la recherche (mots-clés, filtres, etc.)
  extraction_id UUID REFERENCES public.extractions(id), -- ID de l'extraction associée (si applicable)
  ai_suggestion_id UUID REFERENCES public.ai_suggestions(id), -- ID de la suggestion IA associée (si applicable)
  results_count INTEGER, -- Nombre de résultats obtenus
  is_successful BOOLEAN DEFAULT true NOT NULL -- Indique si la recherche a été réussie
);

-- Index pour améliorer les performances des requêtes
CREATE INDEX IF NOT EXISTS user_searches_user_id_idx ON public.user_searches(user_id);
CREATE INDEX IF NOT EXISTS user_searches_created_at_idx ON public.user_searches(created_at);
CREATE INDEX IF NOT EXISTS user_searches_extraction_id_idx ON public.user_searches(extraction_id);
CREATE INDEX IF NOT EXISTS user_searches_ai_suggestion_id_idx ON public.user_searches(ai_suggestion_id);

-- Commentaires sur la table
COMMENT ON TABLE public.user_searches IS 'Historique des recherches effectuées par les utilisateurs';

-- Accorder les privilèges nécessaires
ALTER TABLE public.user_searches ENABLE ROW LEVEL SECURITY;

-- Politique RLS pour user_searches: les utilisateurs ne peuvent voir que leurs propres recherches
CREATE POLICY user_searches_user_policy ON public.user_searches
  FOR ALL
  USING (auth.uid()::text = user_id::text);
"""
            print(sql)
            return False
        else:
            print(f"Erreur lors de la vérification de la table user_searches: {e}")
            return False

def create_updated_at_trigger():
    """Crée la fonction et le trigger pour mettre à jour automatiquement le champ updated_at."""
    sql = """
-- Fonction pour mettre à jour automatiquement le champ updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour mettre à jour automatiquement le champ updated_at de la table ai_suggestions
DROP TRIGGER IF EXISTS update_ai_suggestions_updated_at ON public.ai_suggestions;
CREATE TRIGGER update_ai_suggestions_updated_at
BEFORE UPDATE ON public.ai_suggestions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
"""
    print("Pour créer la fonction et le trigger de mise à jour automatique du champ updated_at, exécutez le SQL suivant:")
    print(sql)

def main():
    """Fonction principale pour créer les tables nécessaires."""
    print("Création des tables pour la fonctionnalité AI Search Helper...")
    
    # Créer les tables
    ai_suggestions_created = create_ai_suggestions_table()
    user_searches_created = create_user_searches_table()
    
    # Créer la fonction et le trigger pour updated_at
    create_updated_at_trigger()
    
    # Générer le fichier SQL complet
    with open('create_ai_helper_tables.sql', 'w') as f:
        f.write("""-- Table pour stocker les suggestions générées par l'IA
CREATE TABLE IF NOT EXISTS public.ai_suggestions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
  user_info JSONB NOT NULL, -- Informations fournies par l'utilisateur via le questionnaire
  suggestions JSONB NOT NULL, -- Suggestions générées par l'IA
  is_applied BOOLEAN DEFAULT false NOT NULL, -- Indique si l'utilisateur a appliqué une suggestion
  applied_suggestion_index INTEGER, -- Index de la suggestion appliquée (si applicable)
  applied_at TIMESTAMP WITH TIME ZONE -- Date à laquelle la suggestion a été appliquée
);

-- Index pour améliorer les performances des requêtes
CREATE INDEX IF NOT EXISTS ai_suggestions_user_id_idx ON public.ai_suggestions(user_id);
CREATE INDEX IF NOT EXISTS ai_suggestions_created_at_idx ON public.ai_suggestions(created_at);

-- Table pour stocker l'historique des recherches des utilisateurs
CREATE TABLE IF NOT EXISTS public.user_searches (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
  query JSONB NOT NULL, -- Configuration de la recherche (mots-clés, filtres, etc.)
  extraction_id UUID REFERENCES public.extractions(id), -- ID de l'extraction associée (si applicable)
  ai_suggestion_id UUID REFERENCES public.ai_suggestions(id), -- ID de la suggestion IA associée (si applicable)
  results_count INTEGER, -- Nombre de résultats obtenus
  is_successful BOOLEAN DEFAULT true NOT NULL -- Indique si la recherche a été réussie
);

-- Index pour améliorer les performances des requêtes
CREATE INDEX IF NOT EXISTS user_searches_user_id_idx ON public.user_searches(user_id);
CREATE INDEX IF NOT EXISTS user_searches_created_at_idx ON public.user_searches(created_at);
CREATE INDEX IF NOT EXISTS user_searches_extraction_id_idx ON public.user_searches(extraction_id);
CREATE INDEX IF NOT EXISTS user_searches_ai_suggestion_id_idx ON public.user_searches(ai_suggestion_id);

-- Fonction pour mettre à jour automatiquement le champ updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour mettre à jour automatiquement le champ updated_at de la table ai_suggestions
DROP TRIGGER IF EXISTS update_ai_suggestions_updated_at ON public.ai_suggestions;
CREATE TRIGGER update_ai_suggestions_updated_at
BEFORE UPDATE ON public.ai_suggestions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Commentaires sur les tables et les colonnes pour la documentation
COMMENT ON TABLE public.ai_suggestions IS 'Suggestions générées par l''IA pour aider les utilisateurs à configurer leurs recherches';
COMMENT ON TABLE public.user_searches IS 'Historique des recherches effectuées par les utilisateurs';

-- Accorder les privilèges nécessaires
ALTER TABLE public.ai_suggestions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_searches ENABLE ROW LEVEL SECURITY;

-- Politique RLS pour ai_suggestions: les utilisateurs ne peuvent voir que leurs propres suggestions
CREATE POLICY ai_suggestions_user_policy ON public.ai_suggestions
  FOR ALL
  USING (auth.uid()::text = user_id::text);

-- Politique RLS pour user_searches: les utilisateurs ne peuvent voir que leurs propres recherches
CREATE POLICY user_searches_user_policy ON public.user_searches
  FOR ALL
  USING (auth.uid()::text = user_id::text);
""")
    
    print("\nFichier SQL complet généré: create_ai_helper_tables.sql")
    print("\nPour créer les tables, veuillez exécuter ce fichier SQL dans l'interface SQL de Supabase.")
    
    if not ai_suggestions_created or not user_searches_created:
        print("\n⚠️ Certaines tables n'ont pas pu être créées automatiquement.")
        print("⚠️ Veuillez utiliser l'interface SQL de Supabase pour exécuter le script SQL généré.")
    
    print("\nTerminé.")

if __name__ == "__main__":
    main() 