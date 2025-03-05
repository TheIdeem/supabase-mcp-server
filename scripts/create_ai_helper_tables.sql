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