"""
StepSquad AI Agents using Google Agent Development Kit (ADK)

This module implements two AI agents:
1. Sync Agent - Detects missing step data and triggers synchronization
2. Fairness Agent - Analyzes step data for anomalies and flags unrealistic entries

Agents communicate with each other to complete workflows.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

# Import GCP clients (optional)
try:
    from google.cloud import firestore
except ImportError:
    firestore = None
    logging.warning("Firestore not available")

try:
    from google.cloud import bigquery
except ImportError:
    bigquery = None
    logging.warning("BigQuery not available")

# Try to import ADK
try:
    from google.adk import Agent, Tool as ADKTool, Runner
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    logging.warning("Google ADK not available. Install with: pip install google-adk")
    ADKTool = None

# Try to import Gemini
try:
    from google.generativeai import configure, GenerativeModel
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI not available. Install with: pip install google-generativeai")

# Import tools and storage helpers
from tools import Tool
from agents_storage import (
    get_competitions,
    get_user_steps,
    get_teams_for_competition,
    flag_unfair_data,
    get_flagged_data
)

# Configure Gemini API
gemini_model = None
if GEMINI_AVAILABLE:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        try:
            configure(api_key=GEMINI_API_KEY)
            gemini_model = GenerativeModel("gemini-1.5-flash")
        except Exception as e:
            logging.warning(f"Failed to configure Gemini: {e}")
            gemini_model = None
    else:
        logging.warning("GEMINI_API_KEY not set. AI features will be limited.")


class SyncAgent:
    """
    Sync Agent: Detects missing step data and triggers synchronization workflows.
    
    Responsibilities:
    - Analyze step data patterns
    - Detect missing entries (users not submitting data)
    - Identify late data submissions
    - Trigger sync workflows with fairness agent
    """
    
    def __init__(self):
        self.name = "sync_agent"
        self.description = "Detects missing step data and triggers synchronization"
        
        # Always create tools (using ADK if available, otherwise fallback Tool wrapper)
        self.tools = [
            self._create_check_missing_data_tool(),
            self._create_check_late_data_tool(),
            self._create_notify_fairness_agent_tool()
        ]
        
        # Initialize ADK Agent if available (will implement actual ADK initialization when SDK is available)
        if ADK_AVAILABLE:
            try:
                # TODO: Initialize actual ADK Agent when SDK is available
                # self.agent = Agent(name=self.name, tools=self.tools)
                self.agent = None  # Placeholder for actual ADK Agent instance
            except Exception as e:
                logging.warning(f"Failed to initialize ADK Agent: {e}")
                self.agent = None
        else:
            self.agent = None
    
    def _create_check_missing_data_tool(self):
        """Tool to check for missing step data"""
        def check_missing_data(comp_id: str, date: str) -> Dict[str, Any]:
            """Check for users who haven't submitted step data for a specific competition and date"""
            try:
                competition = None
                competitions = get_competitions(comp_id=comp_id)
                if competitions:
                    competition = competitions[0]
                
                if not competition:
                    return {"error": "Competition not found"}
                
                teams = get_teams_for_competition(comp_id)
                all_user_ids = set()
                for team in teams:
                    all_user_ids.update(team.get("members", []))
                
                users_with_data = set()
                steps_data = []
                for uid in all_user_ids:
                    user_steps = get_user_steps(uid, comp_id)
                    for step_entry in user_steps:
                        if step_entry.get("date") == date:
                            users_with_data.add(uid)
                            steps_data.append(step_entry)
                
                missing_users = list(all_user_ids - users_with_data)
                
                return {
                    "comp_id": comp_id,
                    "date": date,
                    "total_users": len(all_user_ids),
                    "users_with_data": len(users_with_data),
                    "missing_users": missing_users,
                    "missing_count": len(missing_users),
                    "status": "missing_detected" if missing_users else "all_present"
                }
            except Exception as e:
                logging.error(f"Error checking missing data: {e}")
                return {"error": str(e)}
        
        # Use ADK Tool if available, otherwise use simple Tool wrapper
        if ADK_AVAILABLE and ADKTool:
            try:
                return ADKTool(
                    name="check_missing_data",
                    description="Check for users who haven't submitted step data for a competition and date",
                    func=check_missing_data
                )
            except Exception as e:
                logging.warning(f"Failed to create ADK Tool, using fallback: {e}")
        
        return Tool(
            name="check_missing_data",
            description="Check for users who haven't submitted step data for a competition and date",
            func=check_missing_data
        )
    
    def _create_check_late_data_tool(self):
        """Tool to check for late data submissions"""
        def check_late_data(comp_id: str, grace_days: int = 2) -> Dict[str, Any]:
            """Check for data submitted after competition end date (with grace period)"""
            try:
                competition = None
                competitions = get_competitions(comp_id=comp_id)
                if competitions:
                    competition = competitions[0]
                
                if not competition:
                    return {"error": "Competition not found"}
                
                end_date = datetime.strptime(competition.get("end_date"), "%Y-%m-%d").date()
                grace_end_date = end_date + timedelta(days=grace_days)
                today = datetime.now().date()
                
                late_entries = []
                teams = get_teams_for_competition(comp_id)
                all_user_ids = set()
                for team in teams:
                    all_user_ids.update(team.get("members", []))
                
                for uid in all_user_ids:
                    user_steps = get_user_steps(uid, comp_id)
                    for step_entry in user_steps:
                        entry_date = datetime.strptime(step_entry.get("date"), "%Y-%m-%d").date()
                        if entry_date > grace_end_date:
                            late_entries.append({
                                "user_id": uid,
                                "date": step_entry.get("date"),
                                "steps": step_entry.get("steps"),
                                "days_late": (entry_date - grace_end_date).days
                            })
                
                return {
                    "comp_id": comp_id,
                    "grace_end_date": grace_end_date.isoformat(),
                    "today": today.isoformat(),
                    "late_entries": late_entries,
                    "late_count": len(late_entries),
                    "status": "late_detected" if late_entries else "no_late_entries"
                }
            except Exception as e:
                logging.error(f"Error checking late data: {e}")
                return {"error": str(e)}
        
        if ADK_AVAILABLE and ADKTool:
            try:
                return ADKTool(
                    name="check_late_data",
                    description="Check for step data submitted after competition end date (with grace period)",
                    func=check_late_data
                )
            except Exception as e:
                logging.warning(f"Failed to create ADK Tool, using fallback: {e}")
        
        return Tool(
            name="check_late_data",
            description="Check for step data submitted after competition end date (with grace period)",
            func=check_late_data
        )
    
    def _create_notify_fairness_agent_tool(self):
        """Tool to communicate with fairness agent"""
        def notify_fairness_agent(comp_id: str, user_id: str, date: str, reason: str) -> Dict[str, Any]:
            """Notify fairness agent about data quality issues"""
            # This would trigger the fairness agent to analyze the data
            # For now, return a communication acknowledgment
            return {
                "status": "notified",
                "target_agent": "fairness_agent",
                "comp_id": comp_id,
                "user_id": user_id,
                "date": date,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
        
        if ADK_AVAILABLE and ADKTool:
            try:
                return ADKTool(
                    name="notify_fairness_agent",
                    description="Communicate findings to fairness agent for further analysis",
                    func=notify_fairness_agent
                )
            except Exception as e:
                logging.warning(f"Failed to create ADK Tool, using fallback: {e}")
        
        return Tool(
            name="notify_fairness_agent",
            description="Communicate findings to fairness agent for further analysis",
            func=notify_fairness_agent
        )
    
    def run(self, comp_id: str, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Run sync agent workflow
        
        Args:
            comp_id: Competition ID to analyze
            date: Specific date to check (default: today)
        
        Returns:
            Dictionary with sync agent actions and findings
        """
        if not date:
            date = datetime.now().date().isoformat()
        
        actions = []
        findings = []
        
        # Use tools to analyze data
        if self.tools:
            # Check for missing data
            missing_data_tool = next((t for t in self.tools if t.name == "check_missing_data"), None)
            if missing_data_tool:
                missing_result = missing_data_tool.func(comp_id, date)
                findings.append(missing_result)
                
                if missing_result.get("missing_count", 0) > 0:
                    actions.append({
                        "type": "missing_data_detected",
                        "count": missing_result.get("missing_count"),
                        "users": missing_result.get("missing_users", [])
                    })
            
            # Check for late data
            late_data_tool = next((t for t in self.tools if t.name == "check_late_data"), None)
            if late_data_tool:
                late_result = late_data_tool.func(comp_id)
                findings.append(late_result)
                
                if late_result.get("late_count", 0) > 0:
                    actions.append({
                        "type": "late_data_detected",
                        "count": late_result.get("late_count"),
                        "entries": late_result.get("late_entries", [])
                    })
        
        # Use Gemini for intelligent analysis if available
        if gemini_model and findings:
            try:
                prompt = f"""
                Analyze this step competition sync data and provide recommendations:
                {findings}
                
                Provide 2-3 actionable recommendations for improving data collection.
                """
                response = gemini_model.generate_content(prompt)
                recommendations = response.text if response else None
            except Exception as e:
                logging.warning(f"Gemini analysis failed: {e}")
                recommendations = None
        else:
            recommendations = None
        
        return {
            "ok": True,
            "agent": "sync",
            "comp_id": comp_id,
            "date": date,
            "actions": actions,
            "findings": findings,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }


class FairnessAgent:
    """
    Fairness Agent: Analyzes step data for anomalies and flags unrealistic entries.
    
    Responsibilities:
    - Detect unrealistic step counts (too high, suspicious patterns)
    - Analyze data patterns for anomalies
    - Flag potentially unfair data
    - Communicate findings with sync agent
    """
    
    def __init__(self):
        self.name = "fairness_agent"
        self.description = "Analyzes step data for anomalies and flags unrealistic entries"
        
        # Always create tools (using ADK if available, otherwise fallback Tool wrapper)
        self.tools = [
            self._create_analyze_step_data_tool(),
            self._create_flag_unfair_data_tool(),
            self._create_check_patterns_tool()
        ]
        
        # Initialize ADK Agent if available (will implement actual ADK initialization when SDK is available)
        if ADK_AVAILABLE:
            try:
                # TODO: Initialize actual ADK Agent when SDK is available
                # self.agent = Agent(name=self.name, tools=self.tools)
                self.agent = None  # Placeholder for actual ADK Agent instance
            except Exception as e:
                logging.warning(f"Failed to initialize ADK Agent: {e}")
                self.agent = None
        else:
            self.agent = None
    
    def _create_analyze_step_data_tool(self):
        """Tool to analyze step data for anomalies"""
        def analyze_step_data(comp_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
            """Analyze step data for anomalies like unrealistic step counts"""
            try:
                competition = None
                competitions = get_competitions(comp_id=comp_id)
                if competitions:
                    competition = competitions[0]
                
                if not competition:
                    return {"error": "Competition not found"}
                
                start_date = datetime.strptime(competition.get("start_date"), "%Y-%m-%d").date()
                end_date = datetime.strptime(competition.get("end_date"), "%Y-%m-%d").date()
                
                teams = get_teams_for_competition(comp_id)
                all_user_ids = set()
                for team in teams:
                    all_user_ids.update(team.get("members", []))
                
                if user_id:
                    all_user_ids = {user_id} if user_id in all_user_ids else set()
                
                anomalies = []
                all_data = []
                
                for uid in all_user_ids:
                    user_steps = get_user_steps(uid, comp_id)
                    user_total = 0
                    daily_counts = []
                    
                    for step_entry in user_steps:
                        entry_date = datetime.strptime(step_entry.get("date"), "%Y-%m-%d").date()
                        if start_date <= entry_date <= end_date:
                            steps = step_entry.get("steps", 0)
                            user_total += steps
                            daily_counts.append(steps)
                            all_data.append({
                                "user_id": uid,
                                "date": step_entry.get("date"),
                                "steps": steps
                            })
                    
                    # Detect anomalies
                    if daily_counts:
                        avg_steps = sum(daily_counts) / len(daily_counts)
                        max_steps = max(daily_counts)
                        
                        # Flag if daily steps > 50,000 (unrealistic for most people)
                        if max_steps > 50000:
                            anomalies.append({
                                "user_id": uid,
                                "type": "unrealistic_daily_count",
                                "max_steps": max_steps,
                                "date": next((d["date"] for d in all_data if d["user_id"] == uid and d["steps"] == max_steps), None),
                                "severity": "high"
                            })
                        
                        # Flag if average > 30,000 (sustained high activity)
                        if avg_steps > 30000:
                            anomalies.append({
                                "user_id": uid,
                                "type": "sustained_high_activity",
                                "avg_steps": avg_steps,
                                "severity": "medium"
                            })
                
                return {
                    "comp_id": comp_id,
                    "users_analyzed": len(all_user_ids),
                    "total_data_points": len(all_data),
                    "anomalies": anomalies,
                    "anomaly_count": len(anomalies),
                    "status": "anomalies_detected" if anomalies else "no_anomalies"
                }
            except Exception as e:
                logging.error(f"Error analyzing step data: {e}")
                return {"error": str(e)}
        
        if ADK_AVAILABLE and ADKTool:
            try:
                return ADKTool(
                    name="analyze_step_data",
                    description="Analyze step data for anomalies like unrealistic step counts",
                    func=analyze_step_data
                )
            except Exception as e:
                logging.warning(f"Failed to create ADK Tool, using fallback: {e}")
        
        return Tool(
            name="analyze_step_data",
            description="Analyze step data for anomalies like unrealistic step counts",
            func=analyze_step_data
        )
    
    def _create_flag_unfair_data_tool(self):
        """Tool to flag unfair data entries"""
        def flag_unfair_data_entry(user_id: str, comp_id: str, date: str, reason: str) -> Dict[str, Any]:
            """Flag a specific data entry as potentially unfair"""
            try:
                result = flag_unfair_data(user_id, comp_id, date, reason)
                return {
                    "status": "flagged",
                    "user_id": user_id,
                    "comp_id": comp_id,
                    "date": date,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logging.error(f"Error flagging unfair data: {e}")
                return {"error": str(e)}
        
        if ADK_AVAILABLE and ADKTool:
            try:
                return ADKTool(
                    name="flag_unfair_data",
                    description="Flag a data entry as potentially unfair for admin review",
                    func=flag_unfair_data_entry
                )
            except Exception as e:
                logging.warning(f"Failed to create ADK Tool, using fallback: {e}")
        
        return Tool(
            name="flag_unfair_data",
            description="Flag a data entry as potentially unfair for admin review",
            func=flag_unfair_data_entry
        )
    
    def _create_check_patterns_tool(self):
        """Tool to check for suspicious patterns"""
        def check_patterns(comp_id: str) -> Dict[str, Any]:
            """Check for suspicious patterns across all users"""
            try:
                # Get all data for competition
                teams = get_teams_for_competition(comp_id)
                all_user_ids = set()
                for team in teams:
                    all_user_ids.update(team.get("members", []))
                
                patterns = {
                    "identical_values": [],  # Multiple users with exact same step counts
                    "round_numbers": [],  # Suspicious round numbers (10000, 20000, etc.)
                    "perfect_days": []  # Users with only perfect round numbers
                }
                
                daily_data = {}  # date -> {steps: [user_ids]}
                
                for uid in all_user_ids:
                    user_steps = get_user_steps(uid, comp_id)
                    round_count = 0
                    for step_entry in user_steps:
                        steps = step_entry.get("steps", 0)
                        date = step_entry.get("date")
                        
                        # Check for round numbers
                        if steps % 10000 == 0 and steps > 0:
                            patterns["round_numbers"].append({
                                "user_id": uid,
                                "date": date,
                                "steps": steps
                            })
                            round_count += 1
                        
                        # Track by date for identical value detection
                        if date not in daily_data:
                            daily_data[date] = {}
                        if steps not in daily_data[date]:
                            daily_data[date][steps] = []
                        daily_data[date][steps].append(uid)
                
                # Find identical values (multiple users with same steps on same day)
                for date, step_counts in daily_data.items():
                    for steps, user_ids in step_counts.items():
                        if len(user_ids) > 2 and steps > 10000:  # Suspicious if >2 users have same high count
                            patterns["identical_values"].append({
                                "date": date,
                                "steps": steps,
                                "users": user_ids,
                                "count": len(user_ids)
                            })
                
                return {
                    "comp_id": comp_id,
                    "patterns": patterns,
                    "suspicious_count": (
                        len(patterns["identical_values"]) +
                        len(patterns["round_numbers"]) +
                        len(patterns["perfect_days"])
                    ),
                    "status": "suspicious_patterns_detected" if patterns["suspicious_count"] > 0 else "no_suspicious_patterns"
                }
            except Exception as e:
                logging.error(f"Error checking patterns: {e}")
                return {"error": str(e)}
        
        if ADK_AVAILABLE and ADKTool:
            try:
                return ADKTool(
                    name="check_patterns",
                    description="Check for suspicious patterns in step data (identical values, round numbers, etc.)",
                    func=check_patterns
                )
            except Exception as e:
                logging.warning(f"Failed to create ADK Tool, using fallback: {e}")
        
        return Tool(
            name="check_patterns",
            description="Check for suspicious patterns in step data (identical values, round numbers, etc.)",
            func=check_patterns
        )
    
    def run(self, comp_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run fairness agent workflow
        
        Args:
            comp_id: Competition ID to analyze
            user_id: Optional specific user ID to analyze
        
        Returns:
            Dictionary with fairness agent flags and findings
        """
        flags = []
        findings = []
        
        # Use tools to analyze data
        if self.tools:
            # Analyze step data
            analyze_tool = next((t for t in self.tools if t.name == "analyze_step_data"), None)
            if analyze_tool:
                analysis_result = analyze_tool.func(comp_id, user_id)
                findings.append(analysis_result)
                
                # Flag anomalies
                for anomaly in analysis_result.get("anomalies", []):
                    flags.append({
                        "type": anomaly.get("type"),
                        "user_id": anomaly.get("user_id"),
                        "severity": anomaly.get("severity"),
                        "details": anomaly
                    })
            
            # Check for patterns
            pattern_tool = next((t for t in self.tools if t.name == "check_patterns"), None)
            if pattern_tool:
                pattern_result = pattern_tool.func(comp_id)
                findings.append(pattern_result)
                
                # Add suspicious patterns to flags
                patterns = pattern_result.get("patterns", {})
                for pattern_type, pattern_data in patterns.items():
                    if pattern_data:
                        flags.append({
                            "type": f"suspicious_pattern_{pattern_type}",
                            "severity": "medium",
                            "details": pattern_data
                        })
        
        # Use Gemini for intelligent analysis if available
        if gemini_model and findings:
            try:
                prompt = f"""
                Analyze this step competition data for fairness violations:
                {findings}
                
                Provide 2-3 recommendations for ensuring data integrity.
                """
                response = gemini_model.generate_content(prompt)
                recommendations = response.text if response else None
            except Exception as e:
                logging.warning(f"Gemini analysis failed: {e}")
                recommendations = None
        else:
            recommendations = None
        
        return {
            "ok": True,
            "agent": "fairness",
            "comp_id": comp_id,
            "flags": flags,
            "findings": findings,
            "flag_count": len(flags),
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }


def create_multi_agent_workflow(sync_agent: SyncAgent, fairness_agent: FairnessAgent):
    """
    Create a workflow where sync and fairness agents communicate
    
    Args:
        sync_agent: Sync agent instance
        fairness_agent: Fairness agent instance
    
    Returns:
        Workflow function that runs both agents in sequence
    """
    def run_workflow(comp_id: str, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Run multi-agent workflow:
        1. Sync agent detects missing/late data
        2. Sync agent notifies fairness agent about potential issues
        3. Fairness agent analyzes data for anomalies
        4. Both agents collaborate to provide recommendations
        """
        workflow_results = {
            "workflow_id": f"workflow_{comp_id}_{date or datetime.now().date().isoformat()}",
            "comp_id": comp_id,
            "date": date or datetime.now().date().isoformat(),
            "steps": []
        }
        
        # Step 1: Sync agent runs
        logging.info(f"Running sync agent for competition {comp_id}")
        sync_result = sync_agent.run(comp_id, date)
        workflow_results["steps"].append({
            "step": 1,
            "agent": "sync",
            "result": sync_result
        })
        
        # Step 2: If sync agent found issues, notify fairness agent
        if sync_result.get("actions"):
            logging.info(f"Sync agent found {len(sync_result.get('actions', []))} issues, notifying fairness agent")
            notify_tool = next((t for t in sync_agent.tools if t.name == "notify_fairness_agent"), None)
            if notify_tool:
                # Notify fairness agent about data quality issues
                for action in sync_result.get("actions", []):
                    if action.get("type") == "missing_data_detected":
                        # For missing users, fairness agent can't analyze, but we log it
                        workflow_results["steps"].append({
                            "step": 2,
                            "type": "agent_communication",
                            "from": "sync",
                            "to": "fairness",
                            "message": f"Missing data detected for {action.get('count')} users"
                        })
        
        # Step 3: Fairness agent runs
        logging.info(f"Running fairness agent for competition {comp_id}")
        fairness_result = fairness_agent.run(comp_id)
        workflow_results["steps"].append({
            "step": 3,
            "agent": "fairness",
            "result": fairness_result
        })
        
        # Step 4: Combine results
        workflow_results["summary"] = {
            "sync_actions": len(sync_result.get("actions", [])),
            "fairness_flags": len(fairness_result.get("flags", [])),
            "total_issues": len(sync_result.get("actions", [])) + len(fairness_result.get("flags", [])),
            "status": "issues_detected" if (sync_result.get("actions") or fairness_result.get("flags")) else "clean"
        }
        
        workflow_results["recommendations"] = {
            "sync": sync_result.get("recommendations"),
            "fairness": fairness_result.get("recommendations")
        }
        
        return workflow_results
    
    return run_workflow

