require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

// Connexion à Supabase
const supabaseUrl = `https://${process.env.SUPABASE_PROJECT_REF}.supabase.co`;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

async function createTables() {
  try {
    console.log(`Connexion à Supabase à ${supabaseUrl}`);
    
    // Vérifier si les tables existent déjà
    console.log('Vérification des tables existantes...');
    
    const { data: aiSuggestionsExists, error: aiSuggestionsError } = await supabase
      .from('ai_suggestions')
      .select('id')
      .limit(1);
    
    if (aiSuggestionsError && aiSuggestionsError.code === '42P01') {
      console.log('La table ai_suggestions n\'existe pas. Création nécessaire.');
    } else if (!aiSuggestionsError) {
      console.log('La table ai_suggestions existe déjà.');
    }
    
    const { data: userSearchesExists, error: userSearchesError } = await supabase
      .from('user_searches')
      .select('id')
      .limit(1);
    
    if (userSearchesError && userSearchesError.code === '42P01') {
      console.log('La table user_searches n\'existe pas. Création nécessaire.');
    } else if (!userSearchesError) {
      console.log('La table user_searches existe déjà.');
    }
    
    // Créer la table ai_suggestions
    if (aiSuggestionsError && aiSuggestionsError.code === '42P01') {
      console.log('\nCréation de la table ai_suggestions...');
      
      // Utiliser l'API REST pour créer la table
      const response = await fetch(`${supabaseUrl}/rest/v1/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': supabaseKey,
          'Authorization': `Bearer ${supabaseKey}`,
          'Prefer': 'return=representation'
        },
        body: JSON.stringify({
          name: 'ai_suggestions',
          schema: 'public',
          columns: [
            {
              name: 'id',
              type: 'uuid',
              primaryKey: true,
              defaultValue: 'uuid_generate_v4()'
            },
            {
              name: 'user_id',
              type: 'uuid',
              notNull: true,
              references: {
                table: 'users',
                column: 'id',
                onDelete: 'CASCADE'
              }
            },
            {
              name: 'created_at',
              type: 'timestamptz',
              notNull: true,
              defaultValue: 'now()'
            },
            {
              name: 'updated_at',
              type: 'timestamptz',
              notNull: true,
              defaultValue: 'now()'
            },
            {
              name: 'user_info',
              type: 'jsonb',
              notNull: true
            },
            {
              name: 'suggestions',
              type: 'jsonb',
              notNull: true
            },
            {
              name: 'is_applied',
              type: 'boolean',
              notNull: true,
              defaultValue: 'false'
            },
            {
              name: 'applied_suggestion_index',
              type: 'integer'
            },
            {
              name: 'applied_at',
              type: 'timestamptz'
            }
          ]
        })
      });
      
      if (response.ok) {
        console.log('✅ Table ai_suggestions créée avec succès');
      } else {
        const errorText = await response.text();
        console.error('❌ Erreur lors de la création de la table ai_suggestions:', errorText);
      }
    }
    
    // Créer la table user_searches
    if (userSearchesError && userSearchesError.code === '42P01') {
      console.log('\nCréation de la table user_searches...');
      
      // Utiliser l'API REST pour créer la table
      const response = await fetch(`${supabaseUrl}/rest/v1/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': supabaseKey,
          'Authorization': `Bearer ${supabaseKey}`,
          'Prefer': 'return=representation'
        },
        body: JSON.stringify({
          name: 'user_searches',
          schema: 'public',
          columns: [
            {
              name: 'id',
              type: 'uuid',
              primaryKey: true,
              defaultValue: 'uuid_generate_v4()'
            },
            {
              name: 'user_id',
              type: 'uuid',
              notNull: true,
              references: {
                table: 'users',
                column: 'id',
                onDelete: 'CASCADE'
              }
            },
            {
              name: 'created_at',
              type: 'timestamptz',
              notNull: true,
              defaultValue: 'now()'
            },
            {
              name: 'query',
              type: 'jsonb',
              notNull: true
            },
            {
              name: 'extraction_id',
              type: 'uuid',
              references: {
                table: 'extractions',
                column: 'id'
              }
            },
            {
              name: 'ai_suggestion_id',
              type: 'uuid',
              references: {
                table: 'ai_suggestions',
                column: 'id'
              }
            },
            {
              name: 'results_count',
              type: 'integer'
            },
            {
              name: 'is_successful',
              type: 'boolean',
              notNull: true,
              defaultValue: 'true'
            }
          ]
        })
      });
      
      if (response.ok) {
        console.log('✅ Table user_searches créée avec succès');
      } else {
        const errorText = await response.text();
        console.error('❌ Erreur lors de la création de la table user_searches:', errorText);
      }
    }
    
    // Vérifier à nouveau si les tables ont été créées
    console.log('\nVérification des tables créées:');
    
    const { data: aiSuggestionsData, error: aiSuggestionsCheckError } = await supabase
      .from('ai_suggestions')
      .select('id')
      .limit(1);
    
    if (aiSuggestionsCheckError) {
      console.error('❌ La table ai_suggestions n\'a pas été créée:', aiSuggestionsCheckError.message);
    } else {
      console.log('✅ La table ai_suggestions a été créée avec succès');
    }
    
    const { data: userSearchesData, error: userSearchesCheckError } = await supabase
      .from('user_searches')
      .select('id')
      .limit(1);
    
    if (userSearchesCheckError) {
      console.error('❌ La table user_searches n\'a pas été créée:', userSearchesCheckError.message);
    } else {
      console.log('✅ La table user_searches a été créée avec succès');
    }
    
  } catch (err) {
    console.error('Erreur générale:', err);
  }
}

// Exécuter la fonction principale
createTables(); 