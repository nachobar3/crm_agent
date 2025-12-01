"""
AI Agent with tools to interact with the Leads/Contacts database
Uses LangChain for the agent framework
"""

from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from sheets_manager import SheetsManager
import json
import os


class LeadsAgent:
    """AI Agent that can search and modify leads/contacts in Google Sheets"""
    
    def __init__(self, sheets_manager: SheetsManager, openai_api_key: str):
        """
        Initialize the agent
        
        Args:
            sheets_manager: Instance of SheetsManager
            openai_api_key: OpenAI API key
        """
        self.sheets_manager = sheets_manager
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4o",
            openai_api_key=openai_api_key
        )
        
        # Create tools
        self.tools = self._create_tools()
        
        # Create the agent
        self.agent = self._create_agent()
        
    def _create_tools(self) -> list:
        """Create the tools for the agent"""
        
        def search_by_name_tool(name: str) -> str:
            """Search for contacts by name. Use this when you need to find a person."""
            results = self.sheets_manager.search_by_name(name)
            if not results:
                return f"No se encontraron contactos con el nombre '{name}'"
            return json.dumps(results, ensure_ascii=False, indent=2)
        
        def search_by_company_tool(company: str) -> str:
            """Search for contacts by company. Use this when you need to find people from a specific company."""
            results = self.sheets_manager.search_by_field('Empresa', company)
            if not results:
                return f"No se encontraron contactos de la empresa '{company}'"
            return json.dumps(results, ensure_ascii=False, indent=2)
        
        def search_by_role_tool(role: str) -> str:
            """Search for contacts by role/position. Use this when you need to find people with a specific role."""
            results = self.sheets_manager.search_by_field('Rol', role)
            if not results:
                return f"No se encontraron contactos con el rol '{role}'"
            return json.dumps(results, ensure_ascii=False, indent=2)
        
        def get_all_contacts_tool(dummy: str = "") -> str:
            """Get all contacts in the database. Use this when you need to see all available contacts."""
            results = self.sheets_manager.get_all_records()
            if not results:
                return "No hay contactos en la base de datos"
            return json.dumps(results, ensure_ascii=False, indent=2)
        
        def update_bio_tool(input_str: str) -> str:
            """
            Update or add to the bio field of a contact. 
            Input format: 'name|content|append'
            - name: The name of the contact
            - content: The bio information to add
            - append: 'true' to append, 'false' to replace (default: true)
            
            Example: 'Pablo Salomón|Tiene dos hijas llamadas Caia y Mirta|true'
            """
            try:
                parts = input_str.split('|')
                if len(parts) < 2:
                    return "Error: Formato incorrecto. Usa: 'nombre|contenido|append'"
                
                name = parts[0].strip()
                content = parts[1].strip()
                append = parts[2].strip().lower() == 'true' if len(parts) > 2 else True
                
                success = self.sheets_manager.update_field(name, 'bio', content, append=append)
                
                if success:
                    return f"Bio actualizada exitosamente para {name}"
                else:
                    return f"No se pudo actualizar la bio para {name}. Verifica que el nombre existe."
            except Exception as e:
                return f"Error al actualizar bio: {str(e)}"
        
        def update_phone_tool(input_str: str) -> str:
            """
            Update the phone number field of a contact.
            Input format: 'name|phone'
            - name: The name of the contact
            - phone: The phone number to set
            
            Example: 'Pablo Salomón|+1234567890'
            """
            try:
                parts = input_str.split('|')
                if len(parts) < 2:
                    return "Error: Formato incorrecto. Usa: 'nombre|teléfono'"
                
                name = parts[0].strip()
                phone = parts[1].strip()
                
                success = self.sheets_manager.update_field(name, 'Teléfono', phone, append=False)
                
                if success:
                    return f"Teléfono actualizado exitosamente para {name}"
                else:
                    return f"No se pudo actualizar el teléfono para {name}"
            except Exception as e:
                return f"Error al actualizar teléfono: {str(e)}"
        
        def update_email_tool(input_str: str) -> str:
            """
            Update the email field of a contact.
            Input format: 'name|email'
            - name: The name of the contact
            - email: The email address to set
            
            Example: 'Pablo Salomón|pablo@example.com'
            """
            try:
                parts = input_str.split('|')
                if len(parts) < 2:
                    return "Error: Formato incorrecto. Usa: 'nombre|email'"
                
                name = parts[0].strip()
                email = parts[1].strip()
                
                success = self.sheets_manager.update_field(name, 'Email', email, append=False)
                
                if success:
                    return f"Email actualizado exitosamente para {name}"
                else:
                    return f"No se pudo actualizar el email para {name}"
            except Exception as e:
                return f"Error al actualizar email: {str(e)}"
        
        def update_telegram_tool(input_str: str) -> str:
            """
            Update the Telegram username/handle field of a contact.
            Input format: 'name|telegram'
            - name: The name of the contact
            - telegram: The Telegram username or handle
            
            Example: 'Pablo Salomón|@pablosalomon'
            """
            try:
                parts = input_str.split('|')
                if len(parts) < 2:
                    return "Error: Formato incorrecto. Usa: 'nombre|telegram'"
                
                name = parts[0].strip()
                telegram = parts[1].strip()
                
                success = self.sheets_manager.update_field(name, 'Telegram', telegram, append=False)
                
                if success:
                    return f"Telegram actualizado exitosamente para {name}"
                else:
                    return f"No se pudo actualizar el Telegram para {name}"
            except Exception as e:
                return f"Error al actualizar Telegram: {str(e)}"
        
        def update_company_tool(input_str: str) -> str:
            """
            Update the company field of a contact.
            Input format: 'name|company'
            
            Example: 'Pablo Salomón|Tech Corp'
            """
            try:
                parts = input_str.split('|')
                if len(parts) < 2:
                    return "Error: Formato incorrecto. Usa: 'nombre|empresa'"
                
                name = parts[0].strip()
                company = parts[1].strip()
                
                success = self.sheets_manager.update_field(name, 'Empresa', company, append=False)
                
                if success:
                    return f"Empresa actualizada exitosamente para {name}"
                else:
                    return f"No se pudo actualizar la empresa para {name}"
            except Exception as e:
                return f"Error al actualizar empresa: {str(e)}"
        
        def update_role_tool(input_str: str) -> str:
            """
            Update the role field of a contact.
            Input format: 'name|role'
            
            Example: 'Pablo Salomón|CEO'
            """
            try:
                parts = input_str.split('|')
                if len(parts) < 2:
                    return "Error: Formato incorrecto. Usa: 'nombre|rol'"
                
                name = parts[0].strip()
                role = parts[1].strip()
                
                success = self.sheets_manager.update_field(name, 'Rol', role, append=False)
                
                if success:
                    return f"Rol actualizado exitosamente para {name}"
                else:
                    return f"No se pudo actualizar el rol para {name}"
            except Exception as e:
                return f"Error al actualizar rol: {str(e)}"
        
        def add_to_log_tool(input_str: str) -> str:
            """
            Add an entry to the bitácora (log) field of a contact.
            Input format: 'name|log_entry'
            
            Example: 'Pablo Salomón|Reunión el 27/11/2025 - Discutimos proyecto X'
            """
            try:
                parts = input_str.split('|')
                if len(parts) < 2:
                    return "Error: Formato incorrecto. Usa: 'nombre|entrada_bitacora'"
                
                name = parts[0].strip()
                log_entry = parts[1].strip()
                
                # Always append to log
                success = self.sheets_manager.update_field(name, 'bitácora', log_entry, append=True)
                
                if success:
                    return f"Entrada añadida a la bitácora de {name}"
                else:
                    return f"No se pudo añadir entrada a la bitácora para {name}"
            except Exception as e:
                return f"Error al actualizar bitácora: {str(e)}"
        
        def add_new_contact_tool(input_str: str) -> str:
            """
            Add a new contact to the database.
            Input format: 'nombre|teléfono|email|telegram|empresa|rol|bio'
            - nombre: Full name (required)
            - teléfono: Phone number (optional)
            - email: Email address (optional)
            - telegram: Telegram username (optional)
            - empresa: Company name (optional)
            - rol: Role/Position (optional)
            - bio: Biography or personal notes (optional)
            
            Example: 'Juan Pérez|+123456789|juan@email.com|@juanperez|Tech Corp|CEO|Fundador de la empresa'
            Minimum example: 'Juan Pérez||||||' (only name required, use empty fields for optional)
            """
            try:
                parts = input_str.split('|')
                if len(parts) < 1:
                    return "Error: Formato incorrecto. Usa: 'nombre|teléfono|email|telegram|empresa|rol|bio'"
                
                # Extract fields, using empty string for missing optional fields
                record = {
                    'Nombre': parts[0].strip() if len(parts) > 0 else '',
                    'Teléfono': parts[1].strip() if len(parts) > 1 else '',
                    'Email': parts[2].strip() if len(parts) > 2 else '',
                    'Telegram': parts[3].strip() if len(parts) > 3 else '',
                    'Empresa': parts[4].strip() if len(parts) > 4 else '',
                    'Rol': parts[5].strip() if len(parts) > 5 else '',
                    'bio': parts[6].strip() if len(parts) > 6 else '',
                    'bitácora': ''
                }
                
                # Validate that at least name is provided
                if not record['Nombre']:
                    return "Error: El nombre es obligatorio para crear un nuevo contacto"
                
                # Check if contact already exists
                existing = self.sheets_manager.search_by_name(record['Nombre'])
                if existing:
                    return f"Ya existe un contacto con el nombre '{record['Nombre']}'. Usa las herramientas de actualización si quieres modificarlo."
                
                # Add the new contact
                success = self.sheets_manager.add_record(record)
                
                if success:
                    return f"✅ Nuevo contacto '{record['Nombre']}' agregado exitosamente a la base de datos"
                else:
                    return f"No se pudo agregar el contacto '{record['Nombre']}'"
            except Exception as e:
                return f"Error al agregar nuevo contacto: {str(e)}"
        
        # Create Tool objects
        tools = [
            Tool(
                name="search_by_name",
                func=search_by_name_tool,
                description="Busca contactos por nombre. Útil cuando necesitas encontrar información sobre una persona específica."
            ),
            Tool(
                name="search_by_company",
                func=search_by_company_tool,
                description="Busca contactos por empresa. Útil cuando necesitas encontrar personas de una empresa específica."
            ),
            Tool(
                name="search_by_role",
                func=search_by_role_tool,
                description="Busca contactos por rol o posición. Útil cuando necesitas encontrar personas con un rol específico."
            ),
            Tool(
                name="get_all_contacts",
                func=get_all_contacts_tool,
                description="Obtiene todos los contactos de la base de datos. Usa esto cuando necesites ver todos los contactos disponibles."
            ),
            Tool(
                name="update_bio",
                func=update_bio_tool,
                description="Actualiza o añade información a la bio de un contacto. Formato: 'nombre|contenido|append'. Ejemplo: 'Pablo Salomón|Tiene dos hijas|true'"
            ),
            Tool(
                name="update_phone",
                func=update_phone_tool,
                description="Actualiza el número de teléfono de un contacto. Formato: 'nombre|teléfono'"
            ),
            Tool(
                name="update_email",
                func=update_email_tool,
                description="Actualiza el email de un contacto. Formato: 'nombre|email'"
            ),
            Tool(
                name="update_telegram",
                func=update_telegram_tool,
                description="Actualiza el usuario de Telegram de un contacto. Formato: 'nombre|telegram'"
            ),
            Tool(
                name="update_company",
                func=update_company_tool,
                description="Actualiza la empresa de un contacto. Formato: 'nombre|empresa'"
            ),
            Tool(
                name="update_role",
                func=update_role_tool,
                description="Actualiza el rol/posición de un contacto. Formato: 'nombre|rol'"
            ),
            Tool(
                name="add_to_log",
                func=add_to_log_tool,
                description="Añade una entrada a la bitácora de un contacto. Formato: 'nombre|entrada'"
            ),
            Tool(
                name="add_new_contact",
                func=add_new_contact_tool,
                description="Agrega un nuevo contacto a la base de datos. Formato: 'nombre|teléfono|email|telegram|empresa|rol|bio'. Solo el nombre es obligatorio. Ejemplo: 'Juan Pérez|+123456789|juan@email.com|@juanperez|Tech Corp|CEO|Bio aquí'"
            )
        ]
        
        return tools
    
    def _create_agent(self):
        """Create the agent with tools"""
        
        # System message
        system_message = """Eres un asistente inteligente que gestiona una base de datos de Leads y Contactos.

Tu trabajo es ayudar al usuario a:
1. Buscar información sobre contactos (por nombre, empresa, rol, etc.)
2. Crear nuevos contactos en la base de datos
3. Actualizar información de contactos existentes (bio, teléfono, email, telegram, empresa, rol, etc.)
4. Añadir entradas a la bitácora de contactos

La base de datos tiene los siguientes campos:
- Nombre: Nombre completo del contacto (obligatorio)
- Teléfono: Número de teléfono
- Email: Dirección de correo electrónico
- Telegram: Usuario de Telegram
- Empresa: Empresa donde trabaja
- Rol: Su rol o posición
- bio: Biografía e información personal
- bitácora: Registro de interacciones y notas

Cuando el usuario te pida agregar información:
1. Primero busca al contacto por nombre para verificar si existe
2. Si NO existe y el usuario quiere agregar información: usa add_new_contact para crearlo
3. Si ya existe: usa las herramientas de actualización apropiadas (update_phone, update_email, update_telegram, etc.)
4. Confirma al usuario que la operación fue exitosa

Responde siempre en español, de manera sucinta, sin repreguntar ni agregar información no solicitada."""

        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create the agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    def process_query(self, query: str) -> str:
        """
        Process a user query
        
        Args:
            query: The user's question or command
            
        Returns:
            The agent's response
        """
        try:
            response = self.agent.invoke({"input": query})
            return response.get("output", "Lo siento, no pude procesar tu solicitud.")
        except Exception as e:
            return f"Error al procesar la consulta: {str(e)}"

