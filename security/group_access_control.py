#!/usr/bin/env python3
"""
Group Access Control System for PGP Tool
Implements secure invitation-only group access with proper authorization

This module provides:
- Invitation-only group access control
- Group admin management
- Member invitation and approval system
- Security validation for group operations
"""

import json
import time
import uuid
from typing import Dict, List, Optional, Set
from enum import Enum


class GroupRole(Enum):
    """Roles within a group"""
    CREATOR = "creator"
    ADMIN = "admin"
    MEMBER = "member"


class InvitationStatus(Enum):
    """Status of group invitations"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    REVOKED = "revoked"


class GroupInvitation:
    """Represents an invitation to join a group"""
    
    def __init__(self, group_id: str, inviter_fingerprint: str, 
                 invitee_fingerprint: str, invitee_name: str = None):
        self.invitation_id = str(uuid.uuid4())
        self.group_id = group_id
        self.inviter_fingerprint = inviter_fingerprint
        self.invitee_fingerprint = invitee_fingerprint
        self.invitee_name = invitee_name or "Unknown"
        self.status = InvitationStatus.PENDING
        self.created_at = time.time()
        self.expires_at = time.time() + (7 * 24 * 60 * 60)  # 7 days
        self.responded_at = None
        self.message = ""  # Optional invitation message
    
    def is_expired(self) -> bool:
        """Check if invitation has expired"""
        return time.time() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if invitation is valid and can be accepted"""
        return (self.status == InvitationStatus.PENDING and 
                not self.is_expired())
    
    def accept(self):
        """Accept the invitation"""
        if self.is_valid():
            self.status = InvitationStatus.ACCEPTED
            self.responded_at = time.time()
            return True
        return False
    
    def decline(self):
        """Decline the invitation"""
        if self.status == InvitationStatus.PENDING:
            self.status = InvitationStatus.DECLINED
            self.responded_at = time.time()
            return True
        return False
    
    def revoke(self):
        """Revoke the invitation (admin action)"""
        if self.status == InvitationStatus.PENDING:
            self.status = InvitationStatus.REVOKED
            return True
        return False
    
    def to_dict(self) -> dict:
        """Convert invitation to dictionary for storage"""
        return {
            'invitation_id': self.invitation_id,
            'group_id': self.group_id,
            'inviter_fingerprint': self.inviter_fingerprint,
            'invitee_fingerprint': self.invitee_fingerprint,
            'invitee_name': self.invitee_name,
            'status': self.status.value,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'responded_at': self.responded_at,
            'message': self.message
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GroupInvitation':
        """Create invitation from dictionary"""
        invitation = cls(
            data['group_id'],
            data['inviter_fingerprint'],
            data['invitee_fingerprint'],
            data.get('invitee_name', 'Unknown')
        )
        invitation.invitation_id = data['invitation_id']
        invitation.status = InvitationStatus(data['status'])
        invitation.created_at = data['created_at']
        invitation.expires_at = data['expires_at']
        invitation.responded_at = data.get('responded_at')
        invitation.message = data.get('message', '')
        return invitation


class GroupMember:
    """Represents a member of a group"""
    
    def __init__(self, fingerprint: str, name: str, role: GroupRole):
        self.fingerprint = fingerprint
        self.name = name
        self.role = role
        self.joined_at = time.time()
        self.last_active = time.time()
        self.invited_by = None  # Fingerprint of who invited this member
    
    def is_admin(self) -> bool:
        """Check if member has admin privileges"""
        return self.role in [GroupRole.CREATOR, GroupRole.ADMIN]
    
    def can_invite_members(self) -> bool:
        """Check if member can invite new members"""
        return self.is_admin()
    
    def can_remove_members(self) -> bool:
        """Check if member can remove other members"""
        return self.is_admin()
    
    def can_manage_group(self) -> bool:
        """Check if member can manage group settings"""
        return self.role == GroupRole.CREATOR
    
    def to_dict(self) -> dict:
        """Convert member to dictionary for storage"""
        return {
            'fingerprint': self.fingerprint,
            'name': self.name,
            'role': self.role.value,
            'joined_at': self.joined_at,
            'last_active': self.last_active,
            'invited_by': self.invited_by
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GroupMember':
        """Create member from dictionary"""
        member = cls(
            data['fingerprint'],
            data['name'],
            GroupRole(data['role'])
        )
        member.joined_at = data['joined_at']
        member.last_active = data['last_active']
        member.invited_by = data.get('invited_by')
        return member


class SecureGroup:
    """Represents a secure group with access control"""
    
    def __init__(self, group_id: str, name: str, creator_fingerprint: str, creator_name: str):
        self.group_id = group_id
        self.name = name
        self.description = ""
        self.created_at = time.time()
        self.creator_fingerprint = creator_fingerprint
        
        # Initialize with creator as first member
        creator = GroupMember(creator_fingerprint, creator_name, GroupRole.CREATOR)
        self.members: Dict[str, GroupMember] = {creator_fingerprint: creator}
        
        # Group settings
        self.is_private = True  # Private groups require invitations
        self.max_members = 50   # Maximum number of members
        self.allow_member_invites = True  # Allow non-admin members to invite
        
        # Encryption settings
        self.encryption_enabled = True
        self.require_pgp_verification = True
    
    def get_member(self, fingerprint: str) -> Optional[GroupMember]:
        """Get a member by fingerprint"""
        return self.members.get(fingerprint)
    
    def is_member(self, fingerprint: str) -> bool:
        """Check if fingerprint is a group member"""
        return fingerprint in self.members
    
    def is_admin(self, fingerprint: str) -> bool:
        """Check if fingerprint has admin privileges"""
        member = self.get_member(fingerprint)
        return member and member.is_admin()
    
    def can_invite_members(self, fingerprint: str) -> bool:
        """Check if fingerprint can invite new members"""
        member = self.get_member(fingerprint)
        if not member:
            return False
        
        if member.is_admin():
            return True
        
        return self.allow_member_invites and member.role == GroupRole.MEMBER
    
    def can_remove_member(self, remover_fingerprint: str, target_fingerprint: str) -> bool:
        """Check if remover can remove target member"""
        remover = self.get_member(remover_fingerprint)
        target = self.get_member(target_fingerprint)
        
        if not remover or not target:
            return False
        
        # Creator can remove anyone except themselves
        if remover.role == GroupRole.CREATOR:
            return target_fingerprint != remover_fingerprint
        
        # Admins can remove regular members but not other admins or creator
        if remover.role == GroupRole.ADMIN:
            return target.role == GroupRole.MEMBER
        
        # Regular members cannot remove anyone
        return False
    
    def add_member(self, fingerprint: str, name: str, invited_by: str = None) -> bool:
        """Add a new member to the group"""
        if self.is_member(fingerprint):
            return False  # Already a member
        
        if len(self.members) >= self.max_members:
            return False  # Group is full
        
        member = GroupMember(fingerprint, name, GroupRole.MEMBER)
        member.invited_by = invited_by
        self.members[fingerprint] = member
        
        print(f"DEBUG: Added member {name} ({fingerprint[:16]}...) to group {self.name}")
        return True
    
    def remove_member(self, fingerprint: str) -> bool:
        """Remove a member from the group"""
        if fingerprint in self.members:
            member = self.members[fingerprint]
            del self.members[fingerprint]
            print(f"DEBUG: Removed member {member.name} from group {self.name}")
            return True
        return False
    
    def promote_to_admin(self, fingerprint: str, promoter_fingerprint: str) -> bool:
        """Promote a member to admin"""
        promoter = self.get_member(promoter_fingerprint)
        target = self.get_member(fingerprint)
        
        if not promoter or not target:
            return False
        
        # Only creator can promote to admin
        if promoter.role != GroupRole.CREATOR:
            return False
        
        if target.role == GroupRole.MEMBER:
            target.role = GroupRole.ADMIN
            print(f"DEBUG: Promoted {target.name} to admin in group {self.name}")
            return True
        
        return False
    
    def demote_from_admin(self, fingerprint: str, demoter_fingerprint: str) -> bool:
        """Demote an admin to regular member"""
        demoter = self.get_member(demoter_fingerprint)
        target = self.get_member(fingerprint)
        
        if not demoter or not target:
            return False
        
        # Only creator can demote admins
        if demoter.role != GroupRole.CREATOR:
            return False
        
        if target.role == GroupRole.ADMIN:
            target.role = GroupRole.MEMBER
            print(f"DEBUG: Demoted {target.name} from admin in group {self.name}")
            return True
        
        return False
    
    def get_member_list(self) -> List[GroupMember]:
        """Get list of all members"""
        return list(self.members.values())
    
    def get_admin_list(self) -> List[GroupMember]:
        """Get list of admin members"""
        return [member for member in self.members.values() if member.is_admin()]
    
    def to_dict(self) -> dict:
        """Convert group to dictionary for storage"""
        return {
            'group_id': self.group_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'creator_fingerprint': self.creator_fingerprint,
            'members': {fp: member.to_dict() for fp, member in self.members.items()},
            'is_private': self.is_private,
            'max_members': self.max_members,
            'allow_member_invites': self.allow_member_invites,
            'encryption_enabled': self.encryption_enabled,
            'require_pgp_verification': self.require_pgp_verification
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SecureGroup':
        """Create group from dictionary"""
        # Find creator info
        creator_fp = data['creator_fingerprint']
        creator_member_data = data['members'][creator_fp]
        creator_name = creator_member_data['name']
        
        group = cls(
            data['group_id'],
            data['name'],
            creator_fp,
            creator_name
        )
        
        group.description = data.get('description', '')
        group.created_at = data['created_at']
        group.is_private = data.get('is_private', True)
        group.max_members = data.get('max_members', 50)
        group.allow_member_invites = data.get('allow_member_invites', True)
        group.encryption_enabled = data.get('encryption_enabled', True)
        group.require_pgp_verification = data.get('require_pgp_verification', True)
        
        # Load all members (including creator)
        group.members = {}
        for fp, member_data in data['members'].items():
            member = GroupMember.from_dict(member_data)
            group.members[fp] = member
        
        return group


class GroupAccessController:
    """
    Main access control system for secure groups
    Manages invitations, permissions, and group membership
    """
    
    def __init__(self):
        self.groups: Dict[str, SecureGroup] = {}
        self.invitations: Dict[str, GroupInvitation] = {}  # invitation_id -> invitation
        self.pending_invitations: Dict[str, List[str]] = {}  # fingerprint -> [invitation_ids]
    
    def create_group(self, group_id: str, name: str, creator_fingerprint: str, 
                    creator_name: str) -> SecureGroup:
        """
        Create a new secure group
        
        Args:
            group_id: Unique identifier for the group
            name: Human-readable group name
            creator_fingerprint: PGP fingerprint of the group creator
            creator_name: Name of the group creator
            
        Returns:
            SecureGroup: The created group
            
        Raises:
            ValueError: If group already exists
        """
        if group_id in self.groups:
            raise ValueError(f"Group {group_id} already exists")
        
        group = SecureGroup(group_id, name, creator_fingerprint, creator_name)
        self.groups[group_id] = group
        
        print(f"DEBUG: Created secure group '{name}' with ID {group_id}")
        print(f"DEBUG: Creator: {creator_name} ({creator_fingerprint[:16]}...)")
        
        return group
    
    def get_group(self, group_id: str) -> Optional[SecureGroup]:
        """Get a group by ID"""
        return self.groups.get(group_id)
    
    def invite_member(self, group_id: str, inviter_fingerprint: str, 
                     invitee_fingerprint: str, invitee_name: str = None,
                     message: str = "") -> Optional[GroupInvitation]:
        """
        Invite a new member to a group
        
        Args:
            group_id: The group to invite to
            inviter_fingerprint: PGP fingerprint of the person sending invitation
            invitee_fingerprint: PGP fingerprint of the person being invited
            invitee_name: Name of the person being invited
            message: Optional invitation message
            
        Returns:
            GroupInvitation: The created invitation, or None if not allowed
        """
        group = self.get_group(group_id)
        if not group:
            print(f"ERROR: Group {group_id} not found")
            return None
        
        # Check if inviter has permission to invite
        if not group.can_invite_members(inviter_fingerprint):
            print(f"ERROR: {inviter_fingerprint[:16]}... cannot invite members to group {group_id}")
            return None
        
        # Check if invitee is already a member
        if group.is_member(invitee_fingerprint):
            print(f"ERROR: {invitee_fingerprint[:16]}... is already a member of group {group_id}")
            return None
        
        # Check if there's already a pending invitation
        existing_invitation = self._get_pending_invitation(group_id, invitee_fingerprint)
        if existing_invitation:
            print(f"ERROR: Pending invitation already exists for {invitee_fingerprint[:16]}...")
            return None
        
        # Create invitation
        invitation = GroupInvitation(group_id, inviter_fingerprint, 
                                   invitee_fingerprint, invitee_name)
        invitation.message = message
        
        # Store invitation
        self.invitations[invitation.invitation_id] = invitation
        
        # Track pending invitations by invitee
        if invitee_fingerprint not in self.pending_invitations:
            self.pending_invitations[invitee_fingerprint] = []
        self.pending_invitations[invitee_fingerprint].append(invitation.invitation_id)
        
        inviter_name = group.get_member(inviter_fingerprint).name
        print(f"DEBUG: {inviter_name} invited {invitee_name or 'Unknown'} to group {group.name}")
        
        return invitation
    
    def _get_pending_invitation(self, group_id: str, invitee_fingerprint: str) -> Optional[GroupInvitation]:
        """Check if there's a pending invitation for this user to this group"""
        if invitee_fingerprint not in self.pending_invitations:
            return None
        
        for invitation_id in self.pending_invitations[invitee_fingerprint]:
            invitation = self.invitations.get(invitation_id)
            if (invitation and invitation.group_id == group_id and 
                invitation.status == InvitationStatus.PENDING):
                return invitation
        
        return None
    
    def get_pending_invitations(self, fingerprint: str) -> List[GroupInvitation]:
        """Get all pending invitations for a user"""
        if fingerprint not in self.pending_invitations:
            return []
        
        invitations = []
        for invitation_id in self.pending_invitations[fingerprint]:
            invitation = self.invitations.get(invitation_id)
            if invitation and invitation.is_valid():
                invitations.append(invitation)
        
        return invitations
    
    def accept_invitation(self, invitation_id: str, accepter_fingerprint: str) -> bool:
        """
        Accept a group invitation
        
        Args:
            invitation_id: The invitation to accept
            accepter_fingerprint: PGP fingerprint of the person accepting
            
        Returns:
            bool: True if successful, False otherwise
        """
        invitation = self.invitations.get(invitation_id)
        if not invitation:
            print(f"ERROR: Invitation {invitation_id} not found")
            return False
        
        # Verify the accepter is the invitee
        if invitation.invitee_fingerprint != accepter_fingerprint:
            print(f"ERROR: Invitation {invitation_id} is not for {accepter_fingerprint[:16]}...")
            return False
        
        # Check if invitation is valid
        if not invitation.is_valid():
            print(f"ERROR: Invitation {invitation_id} is not valid (status: {invitation.status.value})")
            return False
        
        # Get the group
        group = self.get_group(invitation.group_id)
        if not group:
            print(f"ERROR: Group {invitation.group_id} not found")
            return False
        
        # Accept the invitation
        if not invitation.accept():
            print(f"ERROR: Failed to accept invitation {invitation_id}")
            return False
        
        # Add member to group
        success = group.add_member(
            invitation.invitee_fingerprint,
            invitation.invitee_name,
            invitation.inviter_fingerprint
        )
        
        if success:
            # Remove from pending invitations
            if accepter_fingerprint in self.pending_invitations:
                if invitation_id in self.pending_invitations[accepter_fingerprint]:
                    self.pending_invitations[accepter_fingerprint].remove(invitation_id)
            
            print(f"DEBUG: {invitation.invitee_name} accepted invitation to group {group.name}")
            return True
        else:
            # Revert invitation status if adding member failed
            invitation.status = InvitationStatus.PENDING
            print(f"ERROR: Failed to add member to group {invitation.group_id}")
            return False
    
    def decline_invitation(self, invitation_id: str, decliner_fingerprint: str) -> bool:
        """
        Decline a group invitation
        
        Args:
            invitation_id: The invitation to decline
            decliner_fingerprint: PGP fingerprint of the person declining
            
        Returns:
            bool: True if successful, False otherwise
        """
        invitation = self.invitations.get(invitation_id)
        if not invitation:
            return False
        
        # Verify the decliner is the invitee
        if invitation.invitee_fingerprint != decliner_fingerprint:
            return False
        
        # Decline the invitation
        if invitation.decline():
            # Remove from pending invitations
            if decliner_fingerprint in self.pending_invitations:
                if invitation_id in self.pending_invitations[decliner_fingerprint]:
                    self.pending_invitations[decliner_fingerprint].remove(invitation_id)
            
            print(f"DEBUG: {invitation.invitee_name} declined invitation to group {invitation.group_id}")
            return True
        
        return False
    
    def revoke_invitation(self, invitation_id: str, revoker_fingerprint: str) -> bool:
        """
        Revoke a group invitation (admin action)
        
        Args:
            invitation_id: The invitation to revoke
            revoker_fingerprint: PGP fingerprint of the admin revoking
            
        Returns:
            bool: True if successful, False otherwise
        """
        invitation = self.invitations.get(invitation_id)
        if not invitation:
            return False
        
        group = self.get_group(invitation.group_id)
        if not group:
            return False
        
        # Check if revoker has admin privileges
        if not group.is_admin(revoker_fingerprint):
            print(f"ERROR: {revoker_fingerprint[:16]}... cannot revoke invitations")
            return False
        
        # Revoke the invitation
        if invitation.revoke():
            # Remove from pending invitations
            invitee_fp = invitation.invitee_fingerprint
            if invitee_fp in self.pending_invitations:
                if invitation_id in self.pending_invitations[invitee_fp]:
                    self.pending_invitations[invitee_fp].remove(invitation_id)
            
            print(f"DEBUG: Invitation {invitation_id} revoked by admin")
            return True
        
        return False
    
    def remove_member(self, group_id: str, remover_fingerprint: str, 
                     target_fingerprint: str) -> bool:
        """
        Remove a member from a group
        
        Args:
            group_id: The group to remove from
            remover_fingerprint: PGP fingerprint of the person removing
            target_fingerprint: PGP fingerprint of the person being removed
            
        Returns:
            bool: True if successful, False otherwise
        """
        group = self.get_group(group_id)
        if not group:
            return False
        
        # Check permissions
        if not group.can_remove_member(remover_fingerprint, target_fingerprint):
            print(f"ERROR: {remover_fingerprint[:16]}... cannot remove {target_fingerprint[:16]}...")
            return False
        
        # Remove the member
        return group.remove_member(target_fingerprint)
    
    def can_access_group(self, group_id: str, fingerprint: str) -> bool:
        """
        Check if a user can access a group (is a member)
        
        Args:
            group_id: The group to check
            fingerprint: PGP fingerprint to check
            
        Returns:
            bool: True if user can access the group, False otherwise
        """
        group = self.get_group(group_id)
        if not group:
            return False
        
        return group.is_member(fingerprint)
    
    def cleanup_expired_invitations(self):
        """Remove expired invitations from the system"""
        expired_invitations = []
        
        for invitation_id, invitation in self.invitations.items():
            if invitation.is_expired() and invitation.status == InvitationStatus.PENDING:
                invitation.status = InvitationStatus.EXPIRED
                expired_invitations.append(invitation_id)
        
        # Remove from pending invitations
        for invitation_id in expired_invitations:
            invitation = self.invitations[invitation_id]
            invitee_fp = invitation.invitee_fingerprint
            if invitee_fp in self.pending_invitations:
                if invitation_id in self.pending_invitations[invitee_fp]:
                    self.pending_invitations[invitee_fp].remove(invitation_id)
        
        if expired_invitations:
            print(f"DEBUG: Cleaned up {len(expired_invitations)} expired invitations")
    
    def export_data(self) -> dict:
        """Export all access control data for storage"""
        return {
            'groups': {gid: group.to_dict() for gid, group in self.groups.items()},
            'invitations': {iid: inv.to_dict() for iid, inv in self.invitations.items()},
            'pending_invitations': self.pending_invitations,
            'exported_at': time.time()
        }
    
    def import_data(self, data: dict) -> bool:
        """Import access control data from storage"""
        try:
            # Import groups
            self.groups = {}
            for gid, group_data in data.get('groups', {}).items():
                group = SecureGroup.from_dict(group_data)
                self.groups[gid] = group
            
            # Import invitations
            self.invitations = {}
            for iid, inv_data in data.get('invitations', {}).items():
                invitation = GroupInvitation.from_dict(inv_data)
                self.invitations[iid] = invitation
            
            # Import pending invitations
            self.pending_invitations = data.get('pending_invitations', {})
            
            print(f"DEBUG: Imported {len(self.groups)} groups and {len(self.invitations)} invitations")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to import access control data: {e}")
            return False

