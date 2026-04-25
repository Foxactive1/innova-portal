#!/usr/bin/env python3
"""
🧪 Script de Teste — InNovaIdeia Portal
Valida configuração Groq e integração de IA
"""

import os
import sys
from pathlib import Path

def print_header(text):
    """Imprimir header formatado."""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")

def test_environment():
    """Verificar variáveis de ambiente."""
    print_header("1️⃣  VERIFICAÇÃO DE AMBIENTE")
    
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
    
    if api_key:
        masked = api_key[:10] + "..." + api_key[-5:]
        print(f"  ✓ GROQ_API_KEY: {masked}")
    else:
        print(f"  ✗ GROQ_API_KEY: NÃO ENCONTRADA")
        print(f"    → Crie arquivo .env com: GROQ_API_KEY=gsk_...")
        return False
    
    print(f"  ✓ GROQ_MODEL: {model}")
    return True

def test_groq_import():
    """Testar importação da biblioteca Groq."""
    print_header("2️⃣  VERIFICAÇÃO DE BIBLIOTECAS")
    
    try:
        from groq import Groq
        print("  ✓ groq importável")
        return True
    except ImportError as e:
        print(f"  ✗ Erro ao importar groq: {e}")
        print(f"    → Instale: pip install groq")
        return False

def test_groq_connection():
    """Testar conexão com Groq API."""
    print_header("3️⃣  TESTE DE CONEXÃO GROQ")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("  ⊘ Pulado (sem GROQ_API_KEY)")
        return False
    
    try:
        from groq import Groq
        
        print("  ⏳ Conectando à API Groq...")
        client = Groq(api_key=api_key)
        
        print("  ⏳ Enviando requisição de teste...")
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "mixtral-8x7b-32768"),
            messages=[
                {
                    "role": "system",
                    "content": "Responda com exatamente 1 palavra: 'Funcionando'"
                },
                {"role": "user", "content": "Você funciona?"}
            ],
            temperature=0.1,
            max_tokens=20,
        )
        
        reply = response.choices[0].message.content.strip()
        print(f"  ✓ Conexão bem-sucedida!")
        print(f"    Resposta: '{reply}'")
        return True
        
    except Exception as e:
        exc_type = type(e).__name__
        exc_msg = str(e)
        print(f"  ✗ Erro na conexão ({exc_type}): {exc_msg[:100]}")
        
        if "401" in exc_msg or "Unauthorized" in exc_type:
            print(f"    → GROQ_API_KEY inválida. Copie novamente de https://console.groq.com")
        elif "rate" in exc_msg.lower():
            print(f"    → Limite de requisições atingido. Aguarde alguns minutos.")
        else:
            print(f"    → Verifique conexão com internet e credenciais.")
        
        return False

def test_flask_app():
    """Testar integração com Flask app (opcional)."""
    print_header("4️⃣  TESTE DE INTEGRAÇÃO FLASK (OPCIONAL)")
    
    try:
        from app import create_app
        
        print("  ⏳ Criando Flask app...")
        app = create_app()
        
        with app.app_context():
            # Importar ai.py dentro do contexto
            from app.ai import get_groq_client, classify_lead
            
            print("  ✓ Flask app criado com sucesso")
            print("  ⏳ Testando classificação de lead...")
            
            test_message = "Estou procurando um sistema de CRM com IA"
            result = classify_lead(test_message)
            
            print(f"  ✓ Classificação funciona!")
            print(f"    Input: '{test_message}'")
            print(f"    Output: '{result[:80]}...'")
            return True
            
    except ImportError as e:
        print(f"  ⊘ Pulado (Flask app não importável): {e}")
        return False
    except Exception as e:
        exc_type = type(e).__name__
        print(f"  ✗ Erro ({exc_type}): {str(e)[:100]}")
        return False

def main():
    """Executar todos os testes."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  🚀 InNovaIdeia Portal — Teste de Configuração IA".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = {
        "Ambiente": test_environment(),
        "Bibliotecas": test_groq_import(),
        "Conexão Groq": False,  # Será atualizado abaixo
    }
    
    if results["Ambiente"] and results["Bibliotecas"]:
        results["Conexão Groq"] = test_groq_connection()
    
    # Teste Flask é opcional
    test_flask_app()
    
    # Sumário
    print_header("📊 SUMÁRIO")
    
    for name, passed in results.items():
        status = "✓ PASSOU" if passed else "✗ FALHOU"
        print(f"  {name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n" + "🎉 " * 10)
        print("\n  TUDO FUNCIONANDO! Você pode agora:")
        print("    1. Fazer login no /dashboard")
        print("    2. Usar o chat widget")
        print("    3. Gerar descrições com IA")
        print("    4. Gerar resumos semanais")
        print("\n" + "🎉 " * 10)
    else:
        print("\n" + "⚠️  " * 10)
        print("\n  FALHAS DETECTADAS. Verifique os erros acima.")
        print("  Dicas:")
        print("    - Certifique-se que .env existe e tem GROQ_API_KEY")
        print("    - Execute: pip install groq python-dotenv")
        print("    - Copie nova chave de https://console.groq.com")
        print("\n" + "⚠️  " * 10)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
