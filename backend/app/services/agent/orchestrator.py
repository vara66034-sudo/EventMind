

import logging
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('EventMind.Agent')


class EventMindAgent:

    def __init__(self, config_path: Optional[str] = None):
      
        self.config = self._load_config(config_path)
        self.running = False
        self.cycle_count = 0
        self.stats = self._init_stats()
        
        # Import other modules lazily to avoid circular imports
        self._tagger = None
        self._notifier = None
        
        logger.info(" EventMind AI Agent initialized")
        logger.info(f" Config: {self.config}")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            'agent': {
                'name': 'EventMind AI Agent',
                'version': '1.0.0',
                'cycle_interval': 3600,  # 1 hour
                'max_events_per_cycle': 100,
                'recommendation_limit': 20
            },
            'odoo': {
                'url': 'http://localhost:8069',
                'db': 'odoo',
                'username': 'admin',
                'password': 'admin'
            },
            'features': {
                'auto_tagging': True,
                'recommendations': True,
                'notifications': True
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key, value in loaded_config.items():
                        if key in default_config and isinstance(value, dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
                logger.info(f" Loaded config from {config_path}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        
        return default_config
    
    def _init_stats(self) -> Dict:
        """Initialize statistics counters"""
        return {
            'total_cycles': 0,
            'events_processed': 0,
            'events_tagged': 0,
            'recommendations_generated': 0,
            'notifications_sent': 0,
            'last_run': None,
            'last_run_success': None,
            'errors': []
        }
    
    def run_cycle(self) -> Dict:
        """
        Execute one full agent cycle
        
        Returns:
            Dict with cycle results and statistics
        """
        cycle_start = time.time()
        cycle_id = self.cycle_count + 1
        
        logger.info(f" Starting AI Agent cycle #{cycle_id}")
        
        try:
            # Phase 1: PERCEPTION - gather data
            perception_result = self._perception_phase()
            
            # Phase 2: DECISION - analyze and decide
            decision_result = self._decision_phase(perception_result)
            
            # Phase 3: ACTION - execute decisions
            action_result = self._action_phase(decision_result)
            
            # Update statistics
            self.cycle_count = cycle_id
            self.stats['total_cycles'] = cycle_id
            self.stats['last_run'] = datetime.now().isoformat()
            self.stats['last_run_success'] = True
            
            cycle_time = time.time() - cycle_start
            logger.info(f" Cycle #{cycle_id} completed in {cycle_time:.2f}s")
            
            return {
                'success': True,
                'cycle_id': cycle_id,
                'duration': cycle_time,
                'timestamp': datetime.now().isoformat(),
                'perception': perception_result,
                'decisions': decision_result,
                'actions': action_result,
                'stats': self.stats
            }
            
        except Exception as e:
            logger.error(f"Cycle #{cycle_id} failed: {str(e)}")
            self.stats['last_run_success'] = False
            self.stats['errors'].append({
                'cycle': cycle_id,
                'time': datetime.now().isoformat(),
                'error': str(e)
            })
            
            return {
                'success': False,
                'cycle_id': cycle_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _perception_phase(self) -> Dict:
        """
        Phase 1: Gather data from various sources
        
        Returns:
            Dict with collected data
        """
        logger.info(" Phase 1: Perception")
        
        # This would connect to Odoo, databases, etc.
        # For now, return placeholder data
        
        perception_data = {
            'timestamp': datetime.now().isoformat(),
            'events': [],
            'users': [],
            'registrations': [],
            'sources': ['odoo', 'vk_api', 'timepad_api']
        }
        
        logger.info(f" Collected: {len(perception_data['events'])} events, "
                   f"{len(perception_data['users'])} users")
        
        return perception_data
    
    def _decision_phase(self, perception_data: Dict) -> Dict:
        """
        Phase 2: Make decisions based on collected data
        
        Args:
            perception_data: Data from perception phase
            
        Returns:
            Dict with decisions to execute
        """
        logger.info("Phase 2: Decision Making")
        
        decisions = {
            'timestamp': datetime.now().isoformat(),
            'events_to_tag': [],
            'recommendations_to_generate': [],
            'reminders_to_send': []
        }
        
        # Analyze events that need tagging
        if self.config['features']['auto_tagging']:
            decisions['events_to_tag'] = self._analyze_events_for_tagging(perception_data)
        
        # Analyze users for recommendations
        if self.config['features']['recommendations']:
            decisions['recommendations_to_generate'] = self._analyze_users_for_recommendations(perception_data)
        
        # Analyze reminders
        if self.config['features']['notifications']:
            decisions['reminders_to_send'] = self._analyze_reminders(perception_data)
        
        logger.info(f"Decisions: {len(decisions['events_to_tag'])} events to tag, "
                   f"{len(decisions['recommendations_to_generate'])} users for recommendations, "
                   f"{len(decisions['reminders_to_send'])} reminders")
        
        return decisions
    
    def _analyze_events_for_tagging(self, perception_data: Dict) -> List[Dict]:
        """Determine which events need auto-tagging"""
        # This would check events without tags
        # Placeholder implementation
        return []
    
    def _analyze_users_for_recommendations(self, perception_data: Dict) -> List[int]:
        """Determine which users need recommendations updated"""
        # Placeholder
        return []
    
    def _analyze_reminders(self, perception_data: Dict) -> List[Dict]:
        """Determine which reminders need to be sent"""
        # Placeholder
        return []
    
    def _action_phase(self, decisions: Dict) -> Dict:
        """
        Phase 3: Execute decisions
        
        Args:
            decisions: Decisions from decision phase
            
        Returns:
            Dict with action results
        """
        logger.info("⚡ Phase 3: Actions")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'tagged_events': [],
            'recommendations_generated': [],
            'reminders_sent': [],
            'statistics': {}
        }
        
        # Execute tagging (calls Polina's module)
        if decisions['events_to_tag']:
            results['tagged_events'] = self._execute_tagging(decisions['events_to_tag'])
            self.stats['events_tagged'] += len(results['tagged_events'])
        

        if decisions['recommendations_to_generate']:
            results['recommendations_generated'] = self._execute_recommendations(
                decisions['recommendations_to_generate']
            )
            self.stats['recommendations_generated'] += len(results['recommendations_generated'])
        
  
        if decisions['reminders_to_send']:
            results['reminders_sent'] = self._execute_notifications(decisions['reminders_to_send'])
            self.stats['notifications_sent'] += len(results['reminders_sent'])
        
        self.stats['events_processed'] += len(perception_data.get('events', []))
        
        logger.info(f" Actions completed: {results}")
        
        return results
    
    def _execute_tagging(self, events_to_tag: List[Dict]) -> List[Dict]:
        
     
        logger.info(f"Calling tagging module for {len(events_to_tag)} events")
        return events_to_tag
    
    def _execute_recommendations(self, users: List[int]) -> List[Dict]:
        """Generate recommendations using own recommender"""
        from .recommendations import get_recommender
        
        recommender = get_recommender()
        results = []
        
        for user_id in users:
            # Get recommendations
            recs = recommender.get_recommendations(
                user_id=user_id,
                events=[],  # Would pass actual events
                limit=self.config['agent']['recommendation_limit']
            )
            results.append({
                'user_id': user_id,
                'recommendations': recs
            })
        
        return results
    
    def _execute_notifications(self, reminders: List[Dict]) -> List[Dict]:
        """Call Ksusha's notification module"""
        # This will be implemented when integrating with Ksusha's module
        logger.info(f"Calling notification module for {len(reminders)} reminders")
        return reminders
    
    def start_auto_cycle(self, interval_seconds: Optional[int] = None):
        """
        Start automatic cycling in background thread
        
        Args:
            interval_seconds: Interval between cycles (default from config)
        """
        if interval_seconds is None:
            interval_seconds = self.config['agent']['cycle_interval']
        
        def _run_loop():
            self.running = True
            logger.info(f"🔄 Auto cycle started (interval: {interval_seconds}s)")
            
            while self.running:
                self.run_cycle()
                
                # Wait for next cycle
                for _ in range(interval_seconds):
                    if not self.running:
                        break
                    time.sleep(1)
        
        thread = threading.Thread(target=_run_loop, daemon=True)
        thread.start()
    
    def stop(self):
        """Stop the agent"""
        self.running = False
        logger.info("Agent stopped")
    
    def get_stats(self) -> Dict:
        """Get agent statistics"""
        return self.stats
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            'running': self.running,
            'cycle_count': self.cycle_count,
            'last_run': self.stats['last_run'],
            'last_run_success': self.stats['last_run_success'],
            'stats': self.stats,
            'config': self.config
        }


_agent_instance = None

def get_agent(config_path: Optional[str] = None) -> EventMindAgent:
    """
    Get or create the global agent instance
    
    Args:
        config_path: Optional config path for initialization
        
    Returns:
        EventMindAgent instance
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = EventMindAgent(config_path)
    return _agent_instance
