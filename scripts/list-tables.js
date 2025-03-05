require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

// Connexion à Supabase
const supabaseUrl = `https://${process.env.SUPABASE_PROJECT_REF}.supabase.co`;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

async function listTables() {
  try {
    console.log(`Connexion à Supabase à ${supabaseUrl}`);
    
    // Récupérer les utilisateurs
    console.log('\n1. Table users:');
    const { data: users, error: usersError } = await supabase
      .from('users')
      .select('*')
      .limit(1);
    
    if (usersError) {
      console.error('Erreur lors de la récupération des utilisateurs:', usersError);
    } else {
      console.log('Structure de la table users:');
      if (users && users.length > 0) {
        const columns = Object.keys(users[0]);
        columns.forEach(column => {
          console.log(`- ${column}: ${typeof users[0][column]}`);
        });
      } else {
        console.log('Aucun utilisateur trouvé.');
      }
    }
    
    // Récupérer les extractions
    console.log('\n2. Table extractions:');
    const { data: extractions, error: extractionsError } = await supabase
      .from('extractions')
      .select('*')
      .limit(1);
    
    if (extractionsError) {
      console.error('Erreur lors de la récupération des extractions:', extractionsError);
    } else {
      console.log('Structure de la table extractions:');
      if (extractions && extractions.length > 0) {
        const columns = Object.keys(extractions[0]);
        columns.forEach(column => {
          console.log(`- ${column}: ${typeof extractions[0][column]}`);
        });
      } else {
        console.log('Aucune extraction trouvée.');
      }
    }
    
    // Essayons de récupérer d'autres tables potentielles
    const potentialTables = [
      'profiles', 
      'ai_suggestions', 
      'user_profiles', 
      'user_searches',
      'search_configurations',
      'search_results'
    ];
    
    console.log('\n3. Vérification d\'autres tables potentielles:');
    for (const table of potentialTables) {
      try {
        const { data, error } = await supabase
          .from(table)
          .select('*')
          .limit(1);
        
        if (!error) {
          console.log(`✅ Table '${table}' existe`);
          if (data && data.length > 0) {
            console.log(`   Colonnes: ${Object.keys(data[0]).join(', ')}`);
          } else {
            console.log('   Table vide');
          }
        } else {
          console.log(`❌ Table '${table}' n'existe pas ou erreur: ${error.message}`);
        }
      } catch (err) {
        console.log(`❌ Erreur lors de la vérification de la table '${table}': ${err.message}`);
      }
    }
  } catch (err) {
    console.error('Erreur générale:', err);
  }
}

listTables(); 