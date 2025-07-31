"""
Project management functions for multi-project system
"""
import logging
from typing import Optional, Dict, Any, List
from database_simple import db

logger = logging.getLogger(__name__)

class ProjectManager:
    def __init__(self):
        self.db = db

    
    async def create_project(self, user_id: str, title: str, description: str = "") -> Optional[Dict[str, Any]]:
        '''Create a new project for a user'''
        try:
            project_data = {
                'user_id': user_id,
                'title': title,
                'description': description,
                'status': 'active'
            }
            
            result = self.client.table('projects').insert(project_data).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return None
    
    async def get_user_projects(self, user_id: str) -> List[Dict[str, Any]]:
        '''Get all projects for a user'''
        try:
            result = self.client.table('projects').select('*').eq('user_id', user_id).order('updated_at', desc=True).execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting user projects: {e}")
            return []
    
    async def get_project_conversations(self, project_id: str) -> List[Dict[str, Any]]:
        '''Get all conversations for a specific project'''
        try:
            result = self.client.table('agent_conversations').select('*').eq('project_id', project_id).order('updated_at', desc=True).execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting project conversations: {e}")
            return []
    
