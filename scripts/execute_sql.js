require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { createClient } = require('@supabase/supabase-js');

// Connexion à Supabase
const supabaseUrl = `https://${process.env.SUPABASE_PROJECT_REF}.supabase.co`;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

async function executeSqlFile(filePath) {
  try {
    console.log(`Lecture du fichier SQL: ${filePath}`);
    const sqlContent = fs.readFileSync(filePath, 'utf8');
    
    console.log('Connexion à Supabase...');
    
    // Diviser le contenu SQL en instructions individuelles
    const sqlStatements = sqlContent
      .split(';')
      .map(statement => statement.trim())
      .filter(statement => statement.length > 0);
    
    console.log(`Exécution de ${sqlStatements.length} instructions SQL...`);
    
    // Exécuter chaque instruction SQL via l'API REST
    for (let i = 0; i < sqlStatements.length; i++) {
      const statement = sqlStatements[i];
      console.log(`\nExécution de l'instruction ${i + 1}/${sqlStatements.length}:`);
      console.log(statement.substring(0, 100) + (statement.length > 100 ? '...' : ''));
      
      try {
        // Utiliser l'API REST pour exécuter le SQL
        const response = await fetch(`${supabaseUrl}/rest/v1/rpc/exec_sql`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'apikey': supabaseKey,
            'Authorization': `Bearer ${supabaseKey}`
          },
          body: JSON.stringify({ query: statement })
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error(`Erreur lors de l'exécution de l'instruction ${i + 1}: ${errorText}`);
        } else {
          console.log(`✅ Instruction ${i + 1} exécutée avec succès`);
        }
      } catch (err) {
        console.error(`Erreur lors de l'exécution de l'instruction ${i + 1}:`, err);
      }
    }
    
    console.log('\nExécution du fichier SQL terminée.');
  } catch (err) {
    console.error('Erreur générale:', err);
  }
}

// Vérifier si un chemin de fichier a été fourni en argument
const sqlFilePath = process.argv[2] || path.join(__dirname, 'create_ai_helper_tables.sql');

// Exécuter le fichier SQL
executeSqlFile(sqlFilePath); 