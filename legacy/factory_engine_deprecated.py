# factory_engine.py
import os
import re
import yaml
from openai import OpenAI
from dotenv import load_dotenv
from prompt_manager import PromptManager

class SoftwareFactory:
    def __init__(self):
        load_dotenv()
        
        # Validación de API KEY
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("❌ Error: No se encontró DEEPSEEK_API_KEY en el archivo .env")
            exit(1)

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        # Cargar configuraciones
        try:
            with open("config/architecture.yaml", "r") as f:
                self.arch = yaml.safe_load(f)
            with open("config/domain_kit.yaml", "r") as f:
                self.domain = yaml.safe_load(f)
        except FileNotFoundError as e:
            print(f"❌ Error: Archivo de configuración no encontrado: {e.filename}")
            exit(1)

        # Inicialización del gestor de prompts
        self.prompt_manager = PromptManager()

    def clean_code(self, raw_code):
        """
        Elimina las etiquetas Markdown (```java ... ```) que añade la IA.
        """
        # Busca contenido entre bloques de código markdown
        clean_pattern = r"```(?:java|javascript|yaml|json|text)?\n?(.*?)\n?```"
        match = re.search(clean_pattern, raw_code, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        return raw_code.strip()

    def call_ai(self, system, user):
        """Método genérico para llamar a DeepSeek"""
        try:
            response = self.client.chat.completions.create(
                model="deepseek-coder",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.1 # Temperatura muy baja para máxima precisión técnica
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Error en la llamada a la IA: {e}")
            return ""

    def run_pipeline(self, layer, entity_name, path):
        print(f"🛠️  Generando {entity_name} ({layer})...")
        
        # 0. Buscar datos de la entidad en el Domain Kit
        entity_data = next((e for e in self.domain['domain']['entities'] if e['name'] == entity_name), None)
        if not entity_data:
            print(f"❌ Error: La entidad '{entity_name}' no existe en domain_kit.yaml")
            return

        # 1. GENERACIÓN INICIAL
        system_dev, user_dev = self.prompt_manager.get_backend_prompt(layer, entity_data, self.arch)
        raw_code = self.call_ai(system_dev, user_dev)
        current_code = self.clean_code(raw_code)

        # 2. BUCLE DE AUDITORÍA (QA)
        max_retries = 3
        for attempt in range(max_retries):
            print(f"🔍 Auditoría QA - Intento {attempt + 1}...")
            
            system_qa, user_qa = self.prompt_manager.get_audit_prompt(layer, current_code)
            audit_result = self.call_ai(system_qa, user_qa)

            # Si el QA responde solo con APROBADO, salimos del bucle
            if "APROBADO" in audit_result.upper():
                print("✅ Calidad validada por el Arquitecto QA.")
                break
            else:
                print(f"⚠️ QA rechazó el código. Motivo: {audit_result[:150]}...")
                
                # 3. CORRECCIÓN (Se le pasa el error al desarrollador)
                fix_user_prompt = f"""
                El Arquitecto QA ha rechazado el código con las siguientes observaciones:
                {audit_result}
                
                Por favor, genera el código corregido siguiendo los estándares de Arquitectura Hexagonal.
                
                CÓDIGO ACTUAL:
                {current_code}
                """
                raw_code = self.call_ai(system_dev, fix_user_prompt)
                current_code = self.clean_code(raw_code)
        
        # 4. GUARDADO FINAL
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(current_code)
            print(f"🚀 Archivo final guardado profesionalmente en: {path}\n")
        except Exception as e:
            print(f"❌ Error al guardar el archivo: {e}")

if __name__ == "__main__":
    factory = SoftwareFactory()
    
    # Prueba de concepto: Generación de la Identidad de seguridad
    # Ruta profesional siguiendo la estructura de paquetes de Java
    path_identity = "output/MiAplicacionColegio/backend/src/main/java/com/miaplicacioncolegio/domain/model/Identity.java"
    
    factory.run_pipeline("domain_model", "Identity", path_identity)