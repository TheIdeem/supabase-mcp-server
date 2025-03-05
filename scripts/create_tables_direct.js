require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { createClient } = require('@supabase/supabase-js');

// Connexion à Supabase
const supabaseUrl = `https://${process.env.SUPABASE_PROJECT_REF}.supabase.co`;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

async function createTables() {
  try {
    console.log(`Connexion à Supabase à ${supabaseUrl}`);
    
    // Lire le fichier SQL
    const sqlFilePath = path.join(__dirname, '..', 'create_ai_helper_tables.sql');
    console.log(`Lecture du fichier SQL: ${sqlFilePath}`);
    const sqlContent = fs.readFileSync(sqlFilePath, 'utf8');
    
    // Diviser le contenu SQL en instructions individuelles
    const sqlStatements = sqlContent
      .split(';')
      .map(statement => statement.trim())
      .filter(statement => statement.length > 0);
    
    console.log(`Exécution de ${sqlStatements.length} instructions SQL...`);
    
    // Exécuter chaque instruction SQL via l'API Supabase
    for (let i = 0; i < sqlStatements.length; i++) {
      const statement = sqlStatements[i];
      console.log(`\nExécution de l'instruction ${i + 1}/${sqlStatements.length}:`);
      console.log(statement.substring(0, 100) + (statement.length > 100 ? '...' : ''));
      
      try {
        // Utiliser l'API Supabase pour exécuter le SQL
        const { data, error } = await supabase.rpc('exec_sql', { query: statement });
        
        if (error) {
          console.error(`Erreur lors de l'exécution de l'instruction ${i + 1}:`, error);
        } else {
          console.log(`✅ Instruction ${i + 1} exécutée avec succès`);
        }
      } catch (err) {
        console.error(`Erreur lors de l'exécution de l'instruction ${i + 1}:`, err);
      }
    }
    
    console.log('\nExécution du fichier SQL terminée.');
    
    // Vérifier si les tables ont été créées
    console.log('\nVérification des tables créées:');
    
    const { data: aiSuggestionsData, error: aiSuggestionsError } = await supabase
      .from('ai_suggestions')
      .select('id')
      .limit(1);
    
    if (aiSuggestionsError) {
      console.error('❌ La table ai_suggestions n\'a pas été créée:', aiSuggestionsError.message);
    } else {
      console.log('✅ La table ai_suggestions a été créée avec succès');
    }
    
    const { data: userSearchesData, error: userSearchesError } = await supabase
      .from('user_searches')
      .select('id')
      .limit(1);
    
    if (userSearchesError) {
      console.error('❌ La table user_searches n\'a pas été créée:', userSearchesError.message);
    } else {
      console.log('✅ La table user_searches a été créée avec succès');
    }
    
  } catch (err) {
    console.error('Erreur générale:', err);
  }
}

// Exécuter la fonction principale
createTables(); 