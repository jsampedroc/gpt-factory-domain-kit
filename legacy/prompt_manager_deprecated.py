# prompt_manager.py

class PromptManager:
    def __init__(self):
        pass

    def get_backend_prompt(self, layer, entity_data, arch_config):
        """
        Genera el prompt para el Agente Desarrollador.
        """
        project_name = arch_config['project']['name'].lower()
        framework = arch_config['backend']['framework']
        language = arch_config['backend']['language']
        version = arch_config['backend']['version']
        
        system = f"""
        Eres un Arquitecto de Software Senior experto en {framework} y Java {version}.
        Tu misión es generar código siguiendo estrictamente la ARQUITECTURA HEXAGONAL.
        
        REGLAS CRÍTICAS:
        1. Responde ÚNICAMENTE con el código fuente puro.
        2. NO incluyas bloques de código Markdown (sin ```java).
        3. El paquete base es: {project_name}
        4. Si la capa es 'domain_model', NO uses ninguna anotación de Spring o JPA. Debe ser Java puro.
        """
        
        user = f"""
        Genera la capa de {layer} para la entidad: {entity_data['name']}.
        ATRIBUTOS: {entity_data.get('attributes', [])}
        REGLAS DE NEGOCIO: {entity_data.get('rules', 'N/A')}
        
        Asegúrate de incluir los imports necesarios y usar Lombok si la configuración lo permite.
        """
        
        return system, user

    def get_audit_prompt(self, layer, code):
        """
        Genera el prompt para el Agente de Auditoría (QA).
        """
        system = """
        Actúa como un Arquitecto de Software Senior encargado de la Calidad (QA).
        Tu misión es revisar el código generado y asegurar que cumple con los estándares Enterprise.
        
        CRITERIOS DE RECHAZO:
        1. Si es la capa 'domain_model' y tiene imports de 'jakarta.persistence' o 'org.springframework'.
        2. Si el código tiene errores de sintaxis o llaves sin cerrar.
        3. Si faltan validaciones básicas (ej. Null checks).
        
        RESPUESTA:
        - Si el código es perfecto y cumple con Arquitectura Hexagonal, responde solo: "APROBADO".
        - Si hay errores, lista los puntos técnicos a corregir de forma breve y numerada.
        """
        
        user = f"Audita el siguiente código de la capa '{layer}':\n\n{code}"
        
        return system, user