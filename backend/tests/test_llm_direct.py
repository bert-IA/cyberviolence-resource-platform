#!/usr/bin/env python3
"""
Test direct du LLM pour voir sa réponse brute
"""

import os
import sys
from dotenv import load_dotenv

# Charger .env
load_dotenv()

# Ajouter le parent directory au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm_manager import LLMManager, LLMProvider
from core.api_adapter import LegacyAPIAdapter

def test_llm_direct():
    """Test direct du prompt procedure_plateforme"""
    
    print("\n🧪 TEST DIRECT LLM - Procedure Plateforme")
    print("="*80)
    
    # Initialiser le LLM manager
    manager = LLMManager(provider=LLMProvider.GEMINI)
    
    # Vérifier la connexion
    if not manager.test_connection():
        print("❌ Connexion LLM échouée")
        return
    
    print("✅ LLM connecté\n")
    
    # Créer l'adapter (il initialise son propre LLM en interne)
    adapter = LegacyAPIAdapter()
    
    # Générer le prompt pour procedure_plateforme
    prompt = adapter._generate_platform_procedure_prompt("France", "FR")
    
    print("📝 PROMPT ENVOYÉ:")
    print("-"*80)
    print(prompt)
    print("-"*80)
    print()
    
    # Appeler le LLM
    print("⏳ Appel LLM en cours...")
    response = manager.generate(prompt)
    
    if response.success:
        print("✅ RÉPONSE LLM REÇUE:")
        print("="*80)
        print(response.content)
        print("="*80)
        print()
        
        # Analyser la réponse
        print("📊 ANALYSE:")
        lines = response.content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Chercher l'URL
            if 'url' in line.lower() or 'http' in line.lower():
                print(f"   🔗 Ligne URL détectée: {line}")
            
            # Chercher le nom
            if 'nom' in line.lower() or 'name' in line.lower():
                print(f"   📛 Ligne Nom détectée: {line}")
            
            # Chercher la description  
            if 'description' in line.lower() or 'desc' in line.lower():
                print(f"   📝 Ligne Description détectée: {line[:80]}...")
        
        print()
        print("💡 Vérifier si l'URL est présente et complète dans la réponse")
        
        # Stats
        print(f"\n📈 Stats:")
        print(f"   - Provider: {response.provider}")
        print(f"   - Model: {response.model}")
        print(f"   - Tokens: {response.tokens_used if response.tokens_used else 'N/A'}")
        print(f"   - Durée: {response.response_time:.2f}s" if response.response_time else "")
    else:
        print(f"❌ Erreur LLM: {response.error}")

if __name__ == "__main__":
    test_llm_direct()
