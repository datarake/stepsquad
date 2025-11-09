#!/usr/bin/env python3
"""
Seed script for demo data - StepSquad Hackathon Demo

This script creates sample data for the hackathon demo:
- Multiple users (admin and members)
- Active competitions
- Teams with members
- Step data for multiple days
- Virtual device connections

Usage:
    python scripts/seed_demo_data.py
    or
    cd apps/api && python scripts/seed_demo_data.py
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage import (
    upsert_user,
    create_competition,
    create_team,
    join_team,
    write_daily_steps,
    get_all_users
)
from device_storage import store_device_tokens
from gcp_clients import init_clients

# Initialize GCP clients
init_clients()

# Configuration
COMP_TZ = os.getenv("COMP_TZ", "Europe/Bucharest")
TODAY = datetime.now().date()
YESTERDAY = TODAY - timedelta(days=1)
TWO_DAYS_AGO = TODAY - timedelta(days=2)
THREE_DAYS_AGO = TODAY - timedelta(days=3)

# Registration opens 3 days ago, starts 2 days ago, ends in 7 days
REG_OPEN = THREE_DAYS_AGO.strftime("%Y-%m-%d")
START_DATE = TWO_DAYS_AGO.strftime("%Y-%m-%d")
END_DATE = (TODAY + timedelta(days=7)).strftime("%Y-%m-%d")

# Users data (emails - users will be created automatically when they log in)
USERS_DATA = [
    {"email": "admin@stepsquad.club", "role": "ADMIN"},
    {"email": "alice@example.com", "role": "MEMBER"},
    {"email": "bob@example.com", "role": "MEMBER"},
    {"email": "charlie@example.com", "role": "MEMBER"},
    {"email": "diana@example.com", "role": "MEMBER"},
    {"email": "eve@example.com", "role": "MEMBER"},
    {"email": "frank@example.com", "role": "MEMBER"},
]

# Competitions data
COMPETITIONS_DATA = [
    {
        "comp_id": "hackathon2025",
        "name": "Google Cloud Run Hackathon 2025",
        "status": "ACTIVE",
        "tz": COMP_TZ,
        "registration_open_date": REG_OPEN,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "max_teams": 10,
        "max_members_per_team": 5,
    },
    {
        "comp_id": "spring2025",
        "name": "Spring Fitness Challenge 2025",
        "status": "REGISTRATION",
        "tz": COMP_TZ,
        "registration_open_date": TODAY.strftime("%Y-%m-%d"),
        "start_date": (TODAY + timedelta(days=7)).strftime("%Y-%m-%d"),
        "end_date": (TODAY + timedelta(days=30)).strftime("%Y-%m-%d"),
        "max_teams": 20,
        "max_members_per_team": 8,
    },
]

# Teams data (team_name, owner_email, comp_id, member_emails)
TEAMS_DATA = [
    ("Team Alpha", "alice@example.com", "hackathon2025", ["alice@example.com", "bob@example.com"]),
    ("Team Beta", "charlie@example.com", "hackathon2025", ["charlie@example.com", "diana@example.com"]),
    ("Team Gamma", "eve@example.com", "hackathon2025", ["eve@example.com", "frank@example.com"]),
]

# Step data (email, date, steps)
STEPS_DATA = [
    # Team Alpha members
    ("alice@example.com", THREE_DAYS_AGO.strftime("%Y-%m-%d"), 8500),
    ("alice@example.com", TWO_DAYS_AGO.strftime("%Y-%m-%d"), 9200),
    ("alice@example.com", YESTERDAY.strftime("%Y-%m-%d"), 7800),
    ("alice@example.com", TODAY.strftime("%Y-%m-%d"), 10500),
    
    ("bob@example.com", THREE_DAYS_AGO.strftime("%Y-%m-%d"), 12000),
    ("bob@example.com", TWO_DAYS_AGO.strftime("%Y-%m-%d"), 11000),
    ("bob@example.com", YESTERDAY.strftime("%Y-%m-%d"), 13500),
    ("bob@example.com", TODAY.strftime("%Y-%m-%d"), 12800),
    
    # Team Beta members
    ("charlie@example.com", THREE_DAYS_AGO.strftime("%Y-%m-%d"), 6500),
    ("charlie@example.com", TWO_DAYS_AGO.strftime("%Y-%m-%d"), 7200),
    ("charlie@example.com", YESTERDAY.strftime("%Y-%m-%d"), 6800),
    ("charlie@example.com", TODAY.strftime("%Y-%m-%d"), 7500),
    
    ("diana@example.com", THREE_DAYS_AGO.strftime("%Y-%m-%d"), 9800),
    ("diana@example.com", TWO_DAYS_AGO.strftime("%Y-%m-%d"), 10200),
    ("diana@example.com", YESTERDAY.strftime("%Y-%m-%d"), 9500),
    ("diana@example.com", TODAY.strftime("%Y-%m-%d"), 10800),
    
    # Team Gamma members
    ("eve@example.com", THREE_DAYS_AGO.strftime("%Y-%m-%d"), 15000),
    ("eve@example.com", TWO_DAYS_AGO.strftime("%Y-%m-%d"), 14500),
    ("eve@example.com", YESTERDAY.strftime("%Y-%m-%d"), 16000),
    ("eve@example.com", TODAY.strftime("%Y-%m-%d"), 15200),
    
    ("frank@example.com", THREE_DAYS_AGO.strftime("%Y-%m-%d"), 11200),
    ("frank@example.com", TWO_DAYS_AGO.strftime("%Y-%m-%d"), 11800),
    ("frank@example.com", YESTERDAY.strftime("%Y-%m-%d"), 10500),
    ("frank@example.com", TODAY.strftime("%Y-%m-%d"), 12000),
]


def get_user_by_email(email: str) -> dict | None:
    """Get user by email address"""
    all_users = get_all_users()
    for user in all_users:
        if user.get("email", "").lower() == email.lower():
            return user
    return None


def seed_users():
    """Create users (users will be created automatically when they log in)"""
    print("Checking users...")
    print("Note: Users will be created automatically when they log in with Firebase Auth")
    print("The following emails should be used for login:")
    for user in USERS_DATA:
        existing = get_user_by_email(user["email"])
        if existing:
            print(f"  ✓ User exists: {user['email']} (UID: {existing.get('uid', 'unknown')})")
        else:
            print(f"  ⚠ User not found: {user['email']} - please log in first to create Firebase Auth account")


def seed_competitions():
    """Create competitions"""
    print("\nCreating competitions...")
    # Get admin user
    admin = get_user_by_email("admin@stepsquad.club")
    admin_uid = admin["uid"] if admin else None
    
    if not admin_uid:
        print("  ⚠ Admin user not found - competitions will be created without created_by")
    
    for comp in COMPETITIONS_DATA:
        comp_data = {
            **comp,
            "created_by": admin_uid or "admin@stepsquad.club",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        create_competition(comp["comp_id"], comp_data)
        print(f"  ✓ Created competition: {comp['name']} ({comp['status']})")


def seed_teams():
    """Create teams and add members"""
    print("\nCreating teams...")
    for team_name, owner_email, comp_id, member_emails in TEAMS_DATA:
        # Look up owner by email
        owner = get_user_by_email(owner_email)
        if not owner:
            print(f"  ⚠ Skipping team {team_name}: owner {owner_email} not found (please log in first)")
            continue
        
        owner_uid = owner["uid"]
        team_id = f"team_{comp_id}_{team_name.lower().replace(' ', '_')}"
        create_team(team_id, team_name, owner_uid, comp_id)
        print(f"  ✓ Created team: {team_name} (owner: {owner_email})")
        
        # Add other members
        for member_email in member_emails:
            if member_email.lower() != owner_email.lower():
                member = get_user_by_email(member_email)
                if member:
                    join_team(team_id, member["uid"])
                    print(f"    → Added member: {member_email}")
                else:
                    print(f"    ⚠ Member {member_email} not found (please log in first)")


def seed_steps():
    """Create step data"""
    print("\nCreating step data...")
    created_count = 0
    skipped_count = 0
    for email, date, steps in STEPS_DATA:
        user = get_user_by_email(email)
        if user:
            write_daily_steps(user["uid"], date, steps)
            created_count += 1
        else:
            skipped_count += 1
            print(f"  ⚠ Skipping steps for {email}: user not found (please log in first)")
    
    print(f"  ✓ Created {created_count} step entries")
    if skipped_count > 0:
        print(f"  ⚠ Skipped {skipped_count} step entries (users not found)")


def seed_virtual_devices():
    """Connect virtual devices for demo users"""
    print("\nConnecting virtual devices...")
    demo_emails = ["alice@example.com", "bob@example.com", "charlie@example.com"]
    for email in demo_emails:
        user = get_user_by_email(email)
        if user:
            try:
                store_device_tokens(user["uid"], "virtual", None)
                print(f"  ✓ Connected virtual device for {email}")
            except Exception as e:
                print(f"  ⚠ Failed to connect virtual device for {email}: {e}")
        else:
            print(f"  ⚠ Skipping virtual device for {email}: user not found (please log in first)")


def main():
    """Main seeding function"""
    print("=" * 60)
    print("StepSquad Demo Data Seeding Script")
    print("=" * 60)
    print(f"Date: {TODAY}")
    print(f"Competition dates: {REG_OPEN} → {START_DATE} → {END_DATE}")
    print("=" * 60)
    
    try:
        seed_users()
        seed_competitions()
        seed_teams()
        seed_steps()
        seed_virtual_devices()
        
        print("\n" + "=" * 60)
        print("✅ Demo data seeding completed!")
        print("=" * 60)
        print("\n⚠️  IMPORTANT: Users must log in first!")
        print("\nTo see the data:")
        print("1. Log in with these emails (they will be created automatically):")
        print("   - Admin: admin@stepsquad.club")
        print("   - Users: alice@example.com, bob@example.com, charlie@example.com, etc.")
        print("2. After logging in, run this script again to create teams and steps")
        print("\nOr run this script after users have logged in to link the data.")
        
    except Exception as e:
        print(f"\n❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

