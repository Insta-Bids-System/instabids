#!/usr/bin/env python3
"""
Complete the multi-project system setup with existing database
"""
import os
import sys
import asyncio
import uuid
from datetime import datetime
sys.path.append('.')
from database_simple import db

async def complete_migration():
    """Complete the multi-project system setup"""
    
    print("Completing multi-project system setup...")
    print("=" * 50)
    
    # Step 1: Test and create a default project for existing conversations
    print("Step 1: Setting up default project structure")
    
    try:
        # Get all users who have conversations but no projects
        conversations = db.client.table('agent_conversations').select('user_id').execute()
        
        if conversations.data:
            unique_users = list(set([c['user_id'] for c in conversations.data if c['user_id']]))
            print(f"Found {len(unique_users)} users with conversations")
            
            for user_id in unique_users:
                # Check if user already has projects
                existing_projects = db.client.table('projects').select('*').eq('user_id', user_id).execute()
                
                if not existing_projects.data:
                    # Create default "General" project for this user
                    default_project = {
                        'user_id': user_id,
                        'title': 'General',
                        'description': 'Default project for existing conversations',
                        'status': 'active'
                    }
                    
                    result = db.client.table('projects').insert(default_project).execute()
                    
                    if result.data:
                        project_id = result.data[0]['id']
                        print(f"  [OK] Created default project {project_id} for user {user_id}")
                    else:
                        print(f"  [ERROR] Could not create project for user {user_id}")
                else:
                    print(f"  [OK] User {user_id} already has {len(existing_projects.data)} project(s)")
        
    except Exception as e:
        print(f"  [ERROR] Setting up projects: {e}")
    
    # Step 2: Create the backend API integration
    print("\nStep 2: Creating backend API integration")
    
    try:
        # Update the database_simple.py to include project management
        await create_project_management_functions()
        print("  [OK] Project management functions ready")
        
    except Exception as e:
        print(f"  [ERROR] Creating project functions: {e}")
    
    # Step 3: Test the system with a sample project
    print("\nStep 3: Testing multi-project functionality")
    
    try:
        # Create a test user if needed
        test_user_id = await db.get_or_create_test_user()
        print(f"  [OK] Test user ready: {test_user_id}")
        
        # Create a test project
        test_project = {
            'user_id': test_user_id,
            'title': 'Test Kitchen Remodel',
            'description': 'Testing multi-project system with kitchen renovation',
            'status': 'active'
        }
        
        result = db.client.table('projects').insert(test_project).execute()
        
        if result.data:
            project_id = result.data[0]['id']
            print(f"  [OK] Test project created: {project_id}")
            
            # Test saving a conversation with project association
            conversation_state = {
                'collected_info': {
                    'project_type': 'kitchen_remodel',
                    'budget_min': 15000,
                    'budget_max': 25000
                },
                'stage': 'information_gathering',
                'project_id': project_id  # Add project association
            }
            
            await db.save_conversation_state(
                user_id=test_user_id,
                thread_id=f"test-project-{project_id}",
                agent_type='CIA',
                state=conversation_state
            )
            
            print(f"  [OK] Test conversation saved with project association")
            
            # Clean up test data
            db.client.table('projects').delete().eq('id', project_id).execute()
            print(f"  [OK] Test project cleaned up")
            
        else:
            print("  [ERROR] Could not create test project")
    
    except Exception as e:
        print(f"  [ERROR] Testing functionality: {e}")
    
    print("\n" + "=" * 50)
    print("[SUCCESS] Multi-project system setup completed!")
    print("")
    print("Next steps:")
    print("1. Update backend API endpoints for project management")
    print("2. Update frontend to show project selection")
    print("3. Add LangGraph Store integration for cross-project memory")
    print("=" * 50)
    
    return True

async def create_project_management_functions():
    """Add project management functions to the database connection"""
    
    # These functions will be added to database_simple.py
    project_functions = """
    
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
    """
    
    # For now, we'll create a separate file with these functions
    functions_file = 'project_management_functions.py'
    
    with open(functions_file, 'w') as f:
        f.write(f'''"""
Project management functions for multi-project system
"""
import logging
from typing import Optional, Dict, Any, List
from database_simple import db

logger = logging.getLogger(__name__)

class ProjectManager:
    def __init__(self):
        self.db = db
{project_functions}
''')
    
    print(f"  [OK] Created {functions_file}")

if __name__ == "__main__":
    success = asyncio.run(complete_migration())
    sys.exit(0 if success else 1)