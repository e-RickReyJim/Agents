"""Task module"""

from .research_tasks import create_research_task, create_rag_task
from .writing_tasks import create_write_task, create_edit_task

__all__ = [
    'create_research_task',
    'create_rag_task', 
    'create_write_task',
    'create_edit_task'
]
