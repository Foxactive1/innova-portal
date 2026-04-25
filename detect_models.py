#---------------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      DIONE CASTRO ALVES
#
# Created:     25/04/2026
# Copyright:   (c) DIONE CASTRO ALVES 2026
# Licence:     <your licence>
#---------------------------------------------------------------------------------------

#!/usr/bin/env python3
"""
Detectar qual modelo Groq está ativo/disponível
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Lista de modelos a testar (do mais recente ao mais antigo)
models_to_test = [
    "llama-3.3-70b-versatile",     # Mais novo (2026)
    "llama-3.3-70b-specdec",
    "llama-3.2-90b-vision-preview",
    "llama-3.2-70b-versatile",
    "llama-3.2-8b-text-preview",
    "llama2-70b-4096",             # Antigo
]

print("🔍 Testando modelos Groq...")
print("=" * 60)

working_model = None

for model in models_to_test:
    print(f"\n⏳ Testando: {model}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10,
            temperature=0.1,
        )
        print(f"✅ SUCESSO! Modelo ativo: {model}")
        working_model = model
        break
    except Exception as e:
        error_msg = str(e)
        if "decommissioned" in error_msg.lower():
            print(f"   ❌ Descontinuado")
        elif "401" in error_msg or "authentication" in error_msg.lower():
            print(f"   ❌ Erro de autenticação (chave inválida)")
            break
        else:
            print(f"   ❌ Erro: {error_msg[:60]}")

print("\n" + "=" * 60)

if working_model:
    print(f"\n✅ MODELO ATIVO ENCONTRADO: {working_model}\n")
    print("Atualize seu .env com:")
    print(f"GROQ_MODEL={working_model}")
else:
    print("\n❌ Nenhum modelo ativo encontrado!")
    print("Verifique sua GROQ_API_KEY em https://console.groq.com")