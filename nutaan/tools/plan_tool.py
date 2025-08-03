"""
Plan Tool - Create and manage todo lists with strikethrough completion
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool


class PlanItem(BaseModel):
    """A single plan item/todo"""
    id: str = Field(description="Unique identifier for the item")
    text: str = Field(description="The todo item text")
    completed: bool = Field(default=False, description="Whether the item is completed")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = Field(default=None, description="When the item was completed")
    subtasks: List['PlanItem'] = Field(default_factory=list, description="Sub-items under this item")


class Plan(BaseModel):
    """A complete plan/todo list"""
    id: str = Field(description="Plan identifier")
    title: str = Field(description="Plan title")
    description: str = Field(default="", description="Plan description")
    items: List[PlanItem] = Field(default_factory=list, description="Plan items")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


# Fix forward reference
PlanItem.model_rebuild()


class PlanManager:
    """Manages plans and todo lists"""
    
    def __init__(self, data_dir: str = ".nutaan_data"):
        self.data_dir = data_dir
        self.plans_file = os.path.join(data_dir, "plans.json")
        self._ensure_data_dir()
        self.plans = self._load_plans()
    
    def _ensure_data_dir(self):
        """Ensure the data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _load_plans(self) -> Dict[str, Plan]:
        """Load plans from file"""
        if os.path.exists(self.plans_file):
            try:
                with open(self.plans_file, 'r') as f:
                    data = json.load(f)
                    return {
                        plan_id: Plan(**plan_data) 
                        for plan_id, plan_data in data.items()
                    }
            except Exception:
                return {}
        return {}
    
    def _save_plans(self):
        """Save plans to file"""
        data = {
            plan_id: plan.model_dump() 
            for plan_id, plan in self.plans.items()
        }
        with open(self.plans_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_plan(self, title: str, description: str = "", items: List[str] = None) -> str:
        """Create a new plan"""
        plan_id = f"plan_{len(self.plans) + 1}_{int(datetime.now().timestamp())}"
        
        plan_items = []
        if items:
            for i, item_text in enumerate(items):
                item_id = f"{plan_id}_item_{i + 1}"
                plan_items.append(PlanItem(id=item_id, text=item_text))
        
        plan = Plan(
            id=plan_id,
            title=title,
            description=description,
            items=plan_items
        )
        
        self.plans[plan_id] = plan
        self._save_plans()
        return plan_id
    
    def add_item(self, plan_id: str, item_text: str, parent_item_id: str = None) -> str:
        """Add an item to a plan"""
        if plan_id not in self.plans:
            raise ValueError(f"Plan {plan_id} not found")
        
        plan = self.plans[plan_id]
        item_id = f"{plan_id}_item_{len(plan.items) + 1}_{int(datetime.now().timestamp())}"
        new_item = PlanItem(id=item_id, text=item_text)
        
        if parent_item_id:
            # Add as subtask
            parent_item = self._find_item(plan, parent_item_id)
            if parent_item:
                parent_item.subtasks.append(new_item)
            else:
                raise ValueError(f"Parent item {parent_item_id} not found")
        else:
            # Add as main item
            plan.items.append(new_item)
        
        plan.updated_at = datetime.now().isoformat()
        self._save_plans()
        return item_id
    
    def complete_item(self, plan_id: str, item_id: str) -> bool:
        """Mark an item as completed"""
        if plan_id not in self.plans:
            raise ValueError(f"Plan {plan_id} not found")
        
        plan = self.plans[plan_id]
        item = self._find_item(plan, item_id)
        
        if item:
            item.completed = True
            item.completed_at = datetime.now().isoformat()
            plan.updated_at = datetime.now().isoformat()
            self._save_plans()
            return True
        
        raise ValueError(f"Item {item_id} not found")
    
    def uncomplete_item(self, plan_id: str, item_id: str) -> bool:
        """Mark an item as not completed"""
        if plan_id not in self.plans:
            raise ValueError(f"Plan {plan_id} not found")
        
        plan = self.plans[plan_id]
        item = self._find_item(plan, item_id)
        
        if item:
            item.completed = False
            item.completed_at = None
            plan.updated_at = datetime.now().isoformat()
            self._save_plans()
            return True
        
        raise ValueError(f"Item {item_id} not found")
    
    def _find_item(self, plan: Plan, item_id: str) -> Optional[PlanItem]:
        """Find an item in a plan by ID"""
        def search_items(items: List[PlanItem]) -> Optional[PlanItem]:
            for item in items:
                if item.id == item_id:
                    return item
                # Search in subtasks
                result = search_items(item.subtasks)
                if result:
                    return result
            return None
        
        return search_items(plan.items)
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get a plan by ID"""
        return self.plans.get(plan_id)
    
    def list_plans(self) -> List[Plan]:
        """List all plans"""
        return list(self.plans.values())
    
    def delete_plan(self, plan_id: str) -> bool:
        """Delete a plan"""
        if plan_id in self.plans:
            del self.plans[plan_id]
            self._save_plans()
            return True
        return False
    
    def format_plan_display(self, plan_id: str, show_completed: bool = True) -> str:
        """Format a plan for display with Rich formatting and strikethrough for completed items"""
        plan = self.get_plan(plan_id)
        if not plan:
            return f"Plan {plan_id} not found"
        
        lines = []
        lines.append(f"[bold green]• {plan.title}[/bold green]")
        if plan.description:
            lines.append(f"[dim]{plan.description}[/dim]")
        lines.append("")
        
        def format_items(items: List[PlanItem], indent: int = 0) -> List[str]:
            formatted = []
            for item in items:
                if not show_completed and item.completed:
                    continue
                
                prefix = "  " * (indent + 1)
                
                if item.completed:
                    # Rich strikethrough for completed items  
                    formatted.append(f"{prefix}[green]☑ [strike]{item.text}[/strike][/green]")
                else:
                    formatted.append(f"{prefix}☐ {item.text}")
                
                # Add subtasks
                if item.subtasks:
                    formatted.extend(format_items(item.subtasks, indent + 1))
            
            return formatted
        
        lines.extend(format_items(plan.items))
        
        # Add stats
        total_items = self._count_items(plan.items)
        completed_items = self._count_completed_items(plan.items)
        
        if total_items > 0:
            percentage = (completed_items / total_items) * 100
            lines.append("")
            lines.append(f"[dim]Progress: {completed_items}/{total_items} items completed ({percentage:.1f}%)[/dim]")
        
        return "\n".join(lines)
    
    def _count_items(self, items: List[PlanItem]) -> int:
        """Count total items including subtasks"""
        count = len(items)
        for item in items:
            count += self._count_items(item.subtasks)
        return count
    
    def _count_completed_items(self, items: List[PlanItem]) -> int:
        """Count completed items including subtasks"""
        count = sum(1 for item in items if item.completed)
        for item in items:
            count += self._count_completed_items(item.subtasks)
        return count


# Global plan manager instance
plan_manager = PlanManager()


def plan_tool(tool_input: str) -> str:
    """
    Create and manage todo lists and plans with strikethrough completion tracking.
    
    Usage examples:
    - create plan "Project Setup" "Set up new web project" ["Create HTML structure", "Add CSS styling", "Implement JavaScript"]
    - add item plan_1 "Add navigation menu"
    - complete item plan_1 plan_1_item_1
    - show plan plan_1
    - list plans
    
    Args:
        tool_input: Command string with action and parameters
    
    Returns:
        String result of the operation
    """
    try:
        parts = tool_input.strip().split()
        if not parts:
            return "Please specify an action: create, add, complete, uncomplete, show, list, delete"
        
        action = parts[0].lower()
        
        if action == "create":
            # create plan "title" "description" ["item1", "item2", ...]
            if len(parts) < 3:
                return "Usage: create plan \"title\" \"description\" [\"item1\", \"item2\", ...]"
            
            # Parse title (in quotes)
            input_str = tool_input[len("create plan"):].strip()
            if not input_str.startswith('"'):
                return "Title must be in quotes"
            
            # Find title
            title_end = input_str.find('"', 1)
            if title_end == -1:
                return "Title must be in quotes"
            
            title = input_str[1:title_end]
            remaining = input_str[title_end + 1:].strip()
            
            description = ""
            items = []
            
            # Parse description if present
            if remaining.startswith('"'):
                desc_end = remaining.find('"', 1)
                if desc_end != -1:
                    description = remaining[1:desc_end]
                    remaining = remaining[desc_end + 1:].strip()
            
            # Parse items list if present
            if remaining.startswith('['):
                list_end = remaining.rfind(']')
                if list_end != -1:
                    items_str = remaining[1:list_end]
                    # Simple parsing of quoted items
                    import re
                    items = re.findall(r'"([^"]*)"', items_str)
            
            plan_id = plan_manager.create_plan(title, description, items)
            return f"Created plan: {plan_id}\n\n{plan_manager.format_plan_display(plan_id)}"
        
        elif action == "add":
            # add item plan_id "item text" [parent_item_id]
            if len(parts) < 4:
                return "Usage: add item plan_id \"item text\" [parent_item_id]"
            
            plan_id = parts[2]
            
            # Parse item text (in quotes)
            input_str = tool_input[len(f"add item {plan_id}"):].strip()
            if not input_str.startswith('"'):
                return "Item text must be in quotes"
            
            text_end = input_str.find('"', 1)
            if text_end == -1:
                return "Item text must be in quotes"
            
            item_text = input_str[1:text_end]
            remaining = input_str[text_end + 1:].strip()
            
            parent_item_id = remaining if remaining else None
            
            item_id = plan_manager.add_item(plan_id, item_text, parent_item_id)
            return f"Added item: {item_id}\n\n{plan_manager.format_plan_display(plan_id)}"
        
        elif action == "complete":
            # complete item plan_id item_id
            if len(parts) < 4:
                return "Usage: complete item plan_id item_id"
            
            plan_id = parts[2]
            item_id = parts[3]
            
            plan_manager.complete_item(plan_id, item_id)
            return f"Completed item: {item_id}\n\n{plan_manager.format_plan_display(plan_id)}"
        
        elif action == "uncomplete":
            # uncomplete item plan_id item_id
            if len(parts) < 4:
                return "Usage: uncomplete item plan_id item_id"
            
            plan_id = parts[2]
            item_id = parts[3]
            
            plan_manager.uncomplete_item(plan_id, item_id)
            return f"Uncompleted item: {item_id}\n\n{plan_manager.format_plan_display(plan_id)}"
        
        elif action == "show":
            # show plan plan_id [show_completed]
            if len(parts) < 3:
                return "Usage: show plan plan_id [show_completed]"
            
            plan_id = parts[2]
            show_completed = len(parts) < 4 or parts[3].lower() != "false"
            
            return plan_manager.format_plan_display(plan_id, show_completed)
        
        elif action == "list":
            # list plans
            plans = plan_manager.list_plans()
            if not plans:
                return "No plans found"
            
            lines = ["Available Plans:"]
            for plan in plans:
                total_items = plan_manager._count_items(plan.items)
                completed_items = plan_manager._count_completed_items(plan.items)
                percentage = (completed_items / total_items * 100) if total_items > 0 else 0
                
                lines.append(f"- {plan.id}: {plan.title} ({completed_items}/{total_items} - {percentage:.1f}%)")
            
            return "\n".join(lines)
        
        elif action == "delete":
            # delete plan plan_id
            if len(parts) < 3:
                return "Usage: delete plan plan_id"
            
            plan_id = parts[2]
            if plan_manager.delete_plan(plan_id):
                return f"Deleted plan: {plan_id}"
            else:
                return f"Plan {plan_id} not found"
        
        else:
            return f"Unknown action: {action}. Available actions: create, add, complete, uncomplete, show, list, delete"
    
    except Exception as e:
        return f"Error: {str(e)}"


class PlanTool(BaseTool):
    """LangChain tool wrapper for plan management"""
    
    name: str = "plan_tool"
    description: str = """Create and manage todo lists and plans with strikethrough completion tracking.
    
    Commands:
    - create plan "title" "description" ["item1", "item2"] - Create new plan
    - add item plan_id "item text" - Add item to plan
    - complete item plan_id item_id - Mark item as completed (strikethrough)
    - uncomplete item plan_id item_id - Mark item as not completed
    - show plan plan_id - Display plan with formatting
    - list plans - List all plans
    - delete plan plan_id - Delete a plan
    
    Examples:
    - create plan "Website Project" "Build weather app" ["HTML structure", "CSS styling", "Weather API"]
    - complete item plan_1_123 plan_1_123_item_1
    - show plan plan_1_123
    """
    
    def _run(self, tool_input: str) -> str:
        """Execute the plan tool command"""
        return plan_tool(tool_input)


if __name__ == "__main__":
    # Test the plan tool
    print("Testing Plan Tool")
    print("=" * 50)
    
    # Create a test plan
    result = plan_tool('create plan "Website Project" "Build a weather app" ["Set up HTML structure", "Add CSS styling", "Integrate weather API", "Add location search", "Test across devices"]')
    print(result)
    print("\n" + "=" * 50)
    
    # Complete an item
    result = plan_tool('complete item plan_1_1722513600 plan_1_1722513600_item_1')
    print(result)
